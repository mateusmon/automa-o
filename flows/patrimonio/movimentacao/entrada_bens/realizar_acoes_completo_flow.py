
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    preencher_campos_erros,
)


def realizar_acoes_completo(page: Page) -> None:
    logger.info("Iniciou realização de ações.")

    ctx = escopo(page)
    data_hoje = obter_data_patrimonio(page)
    ano_atual = obter_data_patrimonio(page, "YYYY/MM").split("/")[0]

    # 1. Edição do Bem / Serviço
    clicar_com_ajax(ctx, "button[name='edit-bemServOrgao-1-8']")

    # 2. Verificação e preenchimento dinâmico das características (se houver)
    inputs_caracteristicas = ctx.locator("tbody tr[model='model1'] td.campo input[type='text']")
    total_caracteristicas = inputs_caracteristicas.count()

    if total_caracteristicas > 0:
        logger.info(f"Encontrado(s) {total_caracteristicas} campo(s) de característica(s).")
        for idx in range(total_caracteristicas):
            campo_input = inputs_caracteristicas.nth(idx)
            if campo_input.is_visible() and campo_input.is_enabled():
                max_len = campo_input.get_attribute("maxlength")
                valor = ano_atual if max_len == "4" else "1"
                logger.info(f"Preenchendo campo de característica {idx + 1} com valor '{valor}'.")
                campo_input.fill(valor)
                aguardar_ajax_global(page)

    # 3. Navegação para a aba Bens Físicos
    clicar_com_ajax(ctx, "button[name='submitTabBensFisico']")

    # 4. Geração do tombamento
    btn_gerar_num = ctx.get_by_role("button", name="Gera o último número disponí")
    clicar_com_ajax(ctx, btn_gerar_num)

    # 5. Preenchimento do período de garantia (busca resiliente por bind)
    input_garantia_ini = ctx.locator("input[bind='dtGarantiaIni'], input[name^='dtGarantiaIni']").first
    input_garantia_ini.wait_for(state="visible")
    logger.info("Preenchendo campo de início da garantia com a data '{}'.", data_hoje)
    input_garantia_ini.fill(data_hoje)
    aguardar_ajax_global(page)

    input_garantia_fim = ctx.locator("input[bind='dtGarantiaFim'], input[name^='dtGarantiaFim']").first
    input_garantia_fim.wait_for(state="visible")
    input_garantia_fim.fill(data_hoje)
    aguardar_ajax_global(page)

    # 6. Retorno e tratamento de duplicidade do tombamento
    btn_retornar = ctx.get_by_role("button", name="Retornar")
    clicar_com_ajax(ctx, btn_retornar)

    vezes = 0
    while ctx.locator(".alert-danger").is_visible() and vezes < 31:
        clicar_com_ajax(ctx, btn_gerar_num)
        clicar_com_ajax(ctx, btn_retornar)
        vezes += 1

    # 7. Finalização
    clicar_com_ajax(ctx, "button[name='submitFinish']")
    preencher_campos_erros(ctx)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou realização de ações.")
