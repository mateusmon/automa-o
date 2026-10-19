from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def preencher_dados_gerais_sem_autocomplete(
    page: Page, 
    ug: dict[str, str], 
    fornecedor: dict[str, str]
) -> None:
    logger.info("Iniciou o preenchimento do UG e do Fornecedor.")

    ctx = escopo(page)
    _page = page

    # 1. Seleção do UG via Consulta Avançada
    logger.info("Selecionando UG via Consulta Avançada...")
    clicar_com_ajax(ctx, "button[name='lookup-ug']")
    
    # Aguarda o campo de busca da modal e preenche
    input_ug = ctx.locator("#model-3")
    input_ug.wait_for(state="visible")
    
    # Define o valor do filtro (prioriza 'nome', se houver; caso contrário, usa 'sigla')
    logger.info("Preenchendo campo de busca da UG com '{}'.", ug["sigla"])
    input_ug.fill(ug["sigla"])

        
    clicar_com_ajax(ctx, "button[name='submitSearch']")
    
    # Seleciona o resultado na modal
    btn_usar_ug = ctx.locator("button[name='submitUse']").first
    btn_usar_ug.wait_for(state="visible")
    clicar_com_ajax(ctx, btn_usar_ug)

    # Garante que a modal fechou e os campos vinculados (ex: UG) foram atualizados
    expect(ctx.locator("input[name='ug']")).not_to_have_value("")

    # 2. Seleção do Fornecedor
    preencher_campo(ctx, 'input[name="agente"]', fornecedor["nome"])
    
    data = obter_data_patrimonio(page)

    # 1. Obtém o valor atual do input de aquisição
    input_aquisicao = ctx.locator("input[name='dtAquisicao']")
    input_aquisicao.wait_for(state="visible")
    logger.info("Preenchendo campo de Data de Aquisição com '{}'.", data)
    input_aquisicao.fill(data)

    # 2. Localiza o input de contabilização e realiza o preenchimento
    input_contabil = ctx.locator("input[name='txDtContabil'], input[name='dtContabil']")
    input_contabil.wait_for(state="visible")
    logger.info("Preenchendo campo de Data de Contabilização com '{}'.", data)
    input_contabil.fill(data)

    # 3. Como o input possui um acionador 'onchange="submitAction('setDtContabil');"', 
    aguardar_ajax_global(_page)
    ctx.get_by_text("Dados gerais").click()

    logger.info("Finalizou o preenchimento do UG e do Fornecedor.")