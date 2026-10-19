from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def preencher_multiplos_bens_transferir(
    page: Page,
    ug: dict[str, str],
    bens: list[dict[str, str]],
) -> int:
    """
    Preenche múltiplos bens na aba 'Itens' da Transferência Interna.

    Para cada bem informado:
    - Clica no botão de lookup de patrimônio da linha correspondente.
    - Executa a busca e seleção através do flow utilitário consultar_bem.
    - Aguarda o processamento AJAX para liberação da próxima linha.

    Returns:
        int: Quantidade de bens selecionados com sucesso.
    """
    logger.info("Iniciou preenchimento de múltiplos bens na Transferência Interna. Total: {}", len(bens))

    ctx = escopo(page)

    ctx.locator("button[name='submitTabItens']").click()
    aguardar_ajax_global(page)

    total_adicionados = 0

    for i, bem in enumerate(bens, start=1):
        nome_bem = bem.get("nome", "")
        complemento_bem = bem.get("complemento", "")
        logger.info("Preenchendo bem {}/{}: {} {}", i, len(bens), nome_bem, complemento_bem)

        # Localiza o botão de lookup correspondente à linha atual
        botao_lookup = ctx.locator(f"button[name='lookup-cdBemPerm-{i}-3']")
        try:
            botao_lookup.wait_for(state="visible", timeout=3_000)
        except Exception:
            # Fallback para linha vazia na tabela com rolagem
            linhas = ctx.locator("table.tabelaComRolagem tbody tr")
            linha_vazia = linhas.filter(
                has=ctx.locator("td").nth(2).locator("input:not([disabled])")
            ).first
            if linha_vazia.is_visible():
                botao_lookup = linha_vazia.locator("button[name^='lookup-cdBemPerm']")

        if not botao_lookup.is_visible():
            logger.warning("Botão de lookup para o item {} não está visível.", i)
            break

        clicar_com_ajax(ctx, botao_lookup)

        encontrou_bem = consultar_bem(page, ug, bem)

        if not encontrou_bem:
            logger.warning("Bem '{}' não encontrado.", nome_bem)
            # Fecha a janela de consulta caso tenha permanecido aberta
            btn_cancelar = ctx.locator("button[name='submitCancel'], button[name='submitClose']").first
            if btn_cancelar.is_visible():
                btn_cancelar.click()
                aguardar_ajax_global(page)
            continue

        aguardar_ajax_global(page)
        total_adicionados += 1

    logger.info("Finalizou preenchimento de múltiplos bens. Total adicionados: {}", total_adicionados)
    return total_adicionados
