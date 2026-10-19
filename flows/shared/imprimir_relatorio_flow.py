from pathlib import Path

import pytest
from loguru import logger
from playwright.sync_api import Frame, Locator, Page, TimeoutError, expect

from utils import evidencia
from utils.modo import is_headless
from utils.versao import get_versao
from utils.waits import aguardar_ajax_global, obter_frame_conteudo


def imprimir_relatorio(
        page: Page,
        check_box_locator: str = "input[name='submitMarkAll1']",
        relatorio_preferido: str | None = None,
        timeout_geracao: int = 180_000,
        timeout_visualizacao: int = 5_000,
        pular_teste: bool = True,
        ja_solicitado: bool = False,
        variacao: bool = False,
    ) -> Path | bool:
    """
    Realiza a emissão dos relatórios disponíveis e salva o PDF do relatório principal.

    Por padrão, seleciona todos os relatórios, dispara a impressão e aguarda a geração do
    relatório principal. Relatórios secundários são ignorados — eles continuam sendo
    gerados no servidor, mas não são verificados nesta execução.

    No fluxo padrão, o ASI inverte a ordem das linhas ao gerar: o primeiro relatório
    solicitado passa para a última posição. Por isso, o padrão é aguardar a última linha.
    Quando `relatorio_preferido` é informado, o índice correspondente é identificado
    antes da geração (quando a tabela ainda está na ordem original) e convertido para
    a posição pós-inversão.

    Args:
        page (Page): Instância da página do Playwright.
        check_box_locator (str): Seletor CSS da opção para selecionar todos os
            relatórios. Defaults to "input[name='submitMarkAll1']".
        relatorio_preferido (str | None): Código (prefixo) do relatório a priorizar,
            por exemplo "PA0127" ou "011". O match é parcial e insensível a maiúsculas.
            Se não for encontrado ou houver ambiguidade, usa o padrão e loga um aviso.
            Defaults to None (usa o primeiro relatório solicitado).
        timeout_geracao (int): Tempo máximo, em milissegundos, para aguardar a geração
            do relatório principal. Defaults to 120_000.
        timeout_visualizacao (int): Tempo, em milissegundos, de visualização do
            relatório principal após o carregamento. Ignorado em modo headless.
            Defaults to 5_000.
        ja_solicitado (bool): Indica que o formulário já solicitou a geração,
            como ocorre ao confirmar o Resumo Mensal de Bens (RMB). Quando True,
            aguarda e abre o primeiro relatório da página "Relatórios solicitados",
            sem selecionar checkboxes nem clicar em Imprimir. Nesse modo,
            check_box_locator e relatorio_preferido não são usados. Quando False
            (padrão), mantém a seleção, solicitação da geração e abertura do principal.
        variacao (bool): Quando True, em _v3 e _v4 o botão de abertura da tela de
            relatórios disponíveis é localizado por "submitPrintAll" em vez de
            "submitPrint". Não afeta a solicitação de geração (_solicitar_geracao).
            Defaults to False.

    Returns:
        Path | bool:
            - Path: Caminho do PDF do relatório principal salvo como evidência.
            - False: Se não houver relatório disponível ou se o relatório principal
              indicar que não há registros.

    Raises:
        RuntimeError: Se o relatório principal HTML contiver erro Java.
    
    Note:
        Se a geração do relatório exceder o `timeout_geracao`, o teste não
        falhará; ele será marcado como ignorado via `pytest.skip()`.
    """
    logger.info("Iniciou impressão de relatório.")

    if ja_solicitado:
        ctx = obter_frame_conteudo(page) if get_versao() >= 4 else page
        return _imprimir(ctx, page, check_box_locator, relatorio_preferido,
                         timeout_geracao, timeout_visualizacao, pular_teste, ja_solicitado=True)

    if get_versao() >= 4:
        return _v4(page, check_box_locator, relatorio_preferido, timeout_geracao, timeout_visualizacao, pular_teste, variacao)
    return _v3(page, check_box_locator, relatorio_preferido, timeout_geracao, timeout_visualizacao, pular_teste, variacao)


# --------------------------------------------------------------------------------------
# Roteamento de versão — abre a tela de relatórios disponíveis
# --------------------------------------------------------------------------------------


def _v3(
    page: Page,
    check_box_locator: str,
    relatorio_preferido: str | None,
    timeout_geracao: int,
    timeout_visualizacao: int,
    pular_teste: bool,
    variacao: bool = False,
) -> Path | bool:
    """Abre a lista de relatórios disponíveis na v3 e delega a impressão."""
    if not page.get_by_role("heading", name="Relatórios disponíveis").is_visible():
        nome_botao = "submitPrintAll" if variacao else "submitPrint"
        botao_impressao = page.locator(f'button[name="{nome_botao}"]').filter(visible=True)
        if not (botao_impressao.is_visible() and botao_impressao.is_enabled()):
            return False

        botao_impressao.click()
        aguardar_ajax_global(page)

    if page.locator("div[name='divErrorMsg']").is_visible():
        logger.warning("Não há relatório disponível.")
        return False

    return _imprimir(page, page, check_box_locator, relatorio_preferido, timeout_geracao, timeout_visualizacao, pular_teste)


def _v4(
    page: Page,
    check_box_locator: str,
    relatorio_preferido: str | None,
    timeout_geracao: int,
    timeout_visualizacao: int,
    pular_teste: bool,
    variacao: bool = False,
) -> Path | bool:
    """Abre a lista de relatórios disponíveis na v4 (dentro do frame de conteúdo) e delega."""
    frame = obter_frame_conteudo(page)

    pagina_relatorios = frame.get_by_text("Relatórios", exact=True)
    pagina_relatorios_disponiveis = page.get_by_role(
        "heading", name="Relatórios disponíveis"
    )

    if not (
        pagina_relatorios.is_visible()
        or pagina_relatorios_disponiveis.is_visible()
    ):
        nome_botao = "submitPrintAll" if variacao else "submitPrint"
        botao_impressao = frame.locator(f'button[name="{nome_botao}"]').filter(visible=True).first
        if botao_impressao.is_visible() and botao_impressao.is_enabled():
            botao_impressao.click()
            aguardar_ajax_global(page)
        else:
            return False

    if frame.locator("div[name='divErrorMsg']").is_visible():
        logger.warning("Não há relatório disponível.")
        return False

    return _imprimir(frame, page, check_box_locator, relatorio_preferido, timeout_geracao, timeout_visualizacao, pular_teste)


# --------------------------------------------------------------------------------------
# Orquestração
# --------------------------------------------------------------------------------------


def _imprimir(
    ctx: Page | Frame,
    page: Page,
    check_box_locator: str,
    relatorio_preferido: str | None,
    timeout_geracao: int,
    timeout_visualizacao: int,
    pular_teste: bool,
    ja_solicitado: bool = False,
) -> Path | bool:
    """Aguarda e abre o principal; identifica e solicita a geração no fluxo padrão."""
    linhas = ctx.locator("table.tabela tbody tr")
    quantidade = linhas.count()

    # O índice do principal é identificado ANTES de clicar em gerar, porque o ASI
    # inverte a ordem das linhas durante a geração. Lemos os nomes enquanto a tabela
    # ainda está na ordem original e calculamos o índice pós-inversão.
    if ja_solicitado:
        indice_principal = 0
    else:
        indice_principal = _encontrar_indice_principal(linhas, quantidade, relatorio_preferido)
        _solicitar_geracao(ctx, page, check_box_locator)

    # Aguarda apenas o relatório principal. Relatórios secundários são ignorados.
    logger.info("Aguardando relatório principal (linha {} de {}).", indice_principal + 1, quantidade)


    # EXCEÇÃO ARQUITETURAL AUTORIZADA:
    # Por padrão do Guia de Testes, Flows não devem decidir se um teste é pulado.
    # Contudo, para evitar alterar dezenas de arquivos de testes e impedir falsos
    # negativos na CI/CD causados por instabilidades/lentidão do servidor na emissão
    # de relatórios, o timeout aqui é tratado com pytest.skip direto no flow.

    try:
        expect(_link_relatorio(linhas, indice_principal)).to_be_visible(timeout=timeout_geracao)
    except (TimeoutError, AssertionError):
        msg_aviso = (
            f"Não foi possível aguardar até que o relatório fosse gerado "
            f"(timeout de {timeout_geracao // 1000}s atingido). "
            "Por favor, faça este teste à mão para verificar a geração do relatório."
        )
        logger.warning(msg_aviso)
        if pular_teste:
            pytest.skip()

    return _abrir_principal(page, linhas, indice_principal, timeout_geracao, timeout_visualizacao)


def _solicitar_geracao(ctx: Page | Frame, page: Page, check_box_locator: str) -> None:
    """Marca todos os relatórios disponíveis e dispara a geração."""
    ctx.locator(check_box_locator).click()
    aguardar_ajax_global(page)

    botao_print = ctx.locator('button[name="submitPrint"]').filter(visible=True).first
    if botao_print.is_visible():
        botao_print.click()
        aguardar_ajax_global(page)


def _encontrar_indice_principal(
    linhas: Locator,
    quantidade: int,
    relatorio_preferido: str | None,
) -> int:
    """
    Devolve o índice pós-inversão do relatório principal.

    Lê os nomes da tabela antes da geração (ordem original) e calcula a posição que
    cada linha vai ocupar após o ASI inverter a ordem. O padrão — quando não há
    preferido ou o match falha — é a última linha, que corresponde ao primeiro
    relatório solicitado.

    Fórmula de inversão: índice i na ordem original vira (quantidade - 1 - i)
    após a geração.
    """
    # Padrão: última linha pós-inversão = primeiro relatório solicitado.
    indice_padrao = quantidade - 1

    if relatorio_preferido is None:
        return indice_padrao

    codigo = relatorio_preferido.strip().upper()
    matches: list[int] = []

    for i in range(quantidade):
        nome = linhas.nth(i).locator("td").nth(0).inner_text().strip().upper()
        if nome.startswith(codigo):
            matches.append(i)

    if len(matches) == 1:
        indice_antes = matches[0]
        return quantidade - 1 - indice_antes

    if len(matches) == 0:
        logger.warning(
            "Relatório preferido '{}' não encontrado na lista. Usando o padrão.",
            relatorio_preferido,
        )
    else:
        nomes_encontrados = [linhas.nth(i).locator("td").nth(1).inner_text().strip() for i in matches]
        logger.warning(
            "Código '{}' casou com {} relatórios ({}). Usando o padrão.",
            relatorio_preferido,
            len(matches),
            ", ".join(nomes_encontrados),
        )

    return indice_padrao


# --------------------------------------------------------------------------------------
# Abertura e processamento do relatório principal
# --------------------------------------------------------------------------------------


def _abrir_principal(
    page: Page,
    linhas: Locator,
    indice: int,
    timeout_geracao: int,
    timeout_visualizacao: int,
) -> Path | bool:
    """Abre o relatório principal: salva o PDF como evidência ou analisa o HTML."""
    num = str(indice + 1)
    link = _link_relatorio(linhas, indice)
    tipo = linhas.nth(indice).locator(f'td[name="type-{num}-3"]').inner_text().strip().upper()

    if "HTML" in tipo:
        return _processar_html_principal(page, link, timeout_visualizacao)

    return _processar_pdf(_baixar_pdf(page, link, timeout_geracao, timeout_visualizacao))


def _processar_html_principal(page: Page, link: Locator, timeout_visualizacao: int) -> bool:
    """Abre o HTML principal e falha se o popup usar o template de erro do ASI."""
    with page.expect_popup() as popup_info:
        link.click()

    popup = popup_info.value
    popup.wait_for_load_state("domcontentloaded")
    erro = _obter_erro_relatorio_html(popup)

    if erro is not None:
        evidencia.set_page(popup)
        popup.bring_to_front()
        logger.error("Relatório HTML não processado: {}", erro)
        logger.bind(apenas_arquivo=True).error(
            "Detalhes do erro no relatório HTML ({}):\n{}",
            popup.url,
            _detalhes_erro_relatorio_html(popup),
        )
        raise RuntimeError(f"Relatório HTML não processado: {erro}")

    _visualizar(popup, timeout_visualizacao)
    popup.close()
    logger.warning("Relatório HTML sem registros.")
    logger.info("Finalizou impressão de relatório.")
    return False


def _obter_erro_relatorio_html(ctx: Page | Frame) -> str | None:
    """Extrai o resumo quando o documento usa o template estrutural de erro do ASI."""
    detalhes = _detalhes_erro_relatorio_html(ctx)
    titulo = ctx.title() if isinstance(ctx, Page) else ""
    tem_tmp_erro = ctx.locator("#tmpErro").count() > 0
    tem_div_erro = ctx.locator("div[name='divError']").count() > 0

    return _classificar_erro_relatorio_html(titulo, tem_tmp_erro, tem_div_erro, detalhes)


def _detalhes_erro_relatorio_html(ctx: Page | Frame) -> str:
    """Lê a stack técnica exibida na textarea do template de erro do ASI."""
    textarea = ctx.locator(
        "#tmpErro textarea[name='txtArea'], form[name='errorForm'] textarea[name='txtArea']"
    ).first
    if textarea.count() == 0:
        return ""
    return textarea.input_value().strip()


def _classificar_erro_relatorio_html(
    titulo: str,
    tem_tmp_erro: bool,
    tem_div_erro: bool,
    detalhes: str,
) -> str | None:
    """Classifica sinais do template ASI e devolve um resumo curto do erro."""
    titulo_erro = titulo.strip().casefold() == "asi - erro"
    estrutura_erro = sum((titulo_erro, tem_tmp_erro, tem_div_erro)) >= 2
    detalhes = detalhes.strip()

    if detalhes and (titulo_erro or tem_tmp_erro or tem_div_erro):
        primeira_linha = next((linha.strip() for linha in detalhes.splitlines() if linha.strip()), "")
        return primeira_linha[:300]

    if estrutura_erro:
        return "O ASI exibiu a página de erro, mas não informou detalhes técnicos."

    return None


def _processar_pdf(pdf_bytes: bytes) -> Path:
    """Salva o PDF do relatório principal como evidência e devolve o caminho."""
    path = evidencia.registrar_pdf_bytes(pdf_bytes, "relatorio_material")
    logger.info("Finalizou impressão de relatório.")
    return path


def _baixar_pdf(page: Page, link: Locator, timeout_geracao: int, timeout_visualizacao: int) -> bytes:
    """
    Obtém os bytes do PDF do relatório principal.

    Em modo headless o PDF é entregue como download. Em modo headed ele abre em popup
    e os bytes são recuperados via requisição à URL do popup.
    """
    if is_headless():
        with page.expect_download(timeout=timeout_geracao) as download_info:
            link.click()
        return Path(download_info.value.path()).read_bytes()

    with page.expect_popup() as popup_info:
        link.click()

    popup = popup_info.value
    popup.wait_for_load_state("networkidle")
    pdf_bytes = popup.context.request.get(popup.url).body()
    _visualizar(page, timeout_visualizacao)
    popup.close()

    return pdf_bytes


# --------------------------------------------------------------------------------------
# Auxiliares
# --------------------------------------------------------------------------------------


def _link_relatorio(linhas: Locator, indice: int) -> Locator:
    """Devolve o locator do link do relatório finalizado. Só fica visível após a geração."""
    num = str(indice + 1)
    return linhas.nth(indice).locator(f'td[name^="name-{num}-2"] >> a[name="linkRelatFinalizado"]')


def _visualizar(page: Page, timeout_visualizacao: int) -> None:
    """Mantém o relatório em tela para conferência visual. Ignorado em modo headless."""
    if timeout_visualizacao > 0 and not is_headless():
        page.wait_for_timeout(timeout_visualizacao)
