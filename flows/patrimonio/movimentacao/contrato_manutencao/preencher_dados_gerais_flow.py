from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import preencher_campo, select_tipo


def preencher_dados_gerais(page: Page, ug: dict[str, str], fornecedor: dict[str, str], finalidade: str) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais de seleção de bens para a unidade gestora '{}'.", ug["nome"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])
    preencher_campo(ctx, "input[name='cdAgente']", fornecedor["nome"])
    
    campo_contrato = ctx.locator("input[name='cdContrato']")
    max_length = int(campo_contrato.get_attribute("maxlength") or "10")
    campo_contrato.type(gerar_numero_com_digitos(max_length))

    campo_processo = ctx.locator("input[name='nrProcesso']")
    max_length = int(campo_contrato.get_attribute("maxlength") or "10")
    campo_processo.type(gerar_numero_com_digitos(max_length))

    ano_atual = obter_data_patrimonio(page, formato="YYYY/MM").split("/")[0]

    ctx.locator("input[name='dtVigenciaIni']").type("0101" + ano_atual)
    ctx.locator("input[name='dtVigenciaFim']").type("3112" + ano_atual)
    # 90 dias deprazo de atendimento
    ctx.locator("input[name='qtPrazoAtendimento']").type("90")
    
    # Descrição do objeto
    ctx.locator("textarea[name='dsObjeto']").type("UM CONTRATO MUITISSIMO IMPORTANTE!")

    select_tipo(ctx, "tpContrato", finalidade)

    logger.info("Finalizou o preenchimento dos dados gerais de seleção de bens para a unidade gestora '{}'.", ug["nome"])
