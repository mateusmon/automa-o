from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_multiplos_materiais(page: Page, materiais: list[dict[str, str]], quantidade: str = "1") -> None:
    """
    Preenche múltiplos materiais na tabela de itens do Cadastro de Requisição (Almoxarifado).
    No Almoxarifado, a linha de input de material fica no topo (linha 0).
    Ao selecionar o material via lookup, o sistema insere automaticamente uma nova linha em branco no topo,
    empurrando o material selecionado para a linha 1 (imediatamente abaixo do topo).
    Portanto:
    - O material é sempre preenchido na linha do topo (índice 0).
    - A quantidade é sempre preenchida na linha do material recém-selecionado (índice 1).
    """
    logger.info("Iniciou preenchimento de múltiplos materiais no Cadastro de Requisição. Total de itens: {}", len(materiais))

    ctx = escopo(page)
    _preencher(ctx, page, materiais, quantidade)

    logger.info("Finalizou preenchimento de múltiplos materiais no Cadastro de Requisição.")


def _preencher(ctx, page: Page, materiais: list[dict[str, str]], quantidade: str) -> None:
    total_itens = len(materiais)

    for i, material in enumerate(materiais, start=1):
        nome_material = material["nome"]
        complemento_material = material.get("complemento", "")
        nome_completo = f"{nome_material} {complemento_material}".strip()

        logger.info("Preenchendo material {}/{}: {}", i, total_itens, nome_completo)

        linha_input = ctx.locator("table.tabela tbody[name='tboItens'] tr").first
        campo_mat = linha_input.locator("input[name*='bemServico']").first
        btn_lookup = linha_input.locator("button[name*='lookup-bemServico'], button[name*='lookup']").first
        lookup_name = btn_lookup.get_attribute("name") if btn_lookup.count() > 0 else None

        # Preenche o material no topo
        logger.info("Preenchendo material '{}'.", nome_completo)
        preencher_campo(ctx, campo_mat, nome_completo, lookup_name=lookup_name)

        # Após o AJAX da seleção, o ASI cria uma nova linha em branco no topo (índice 0)
        # e o material recém-escolhido passa para a segunda linha (índice 1)
        linha_selecionada = ctx.locator("table.tabela tbody[name='tboItens'] tr").nth(1)
        campo_qtd = linha_selecionada.locator("input[name*='qtRequisicao']").first

        logger.info("Preenchendo quantidade '{}'.", quantidade)
        campo_qtd.wait_for(state="visible", timeout=10_000)
        campo_qtd.select_text()
        campo_qtd.fill(quantidade)

    # Confirma a Requisição após todos os itens preenchidos
    logger.info("Confirmando o cadastro de requisição com '{}' itens.", total_itens)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
