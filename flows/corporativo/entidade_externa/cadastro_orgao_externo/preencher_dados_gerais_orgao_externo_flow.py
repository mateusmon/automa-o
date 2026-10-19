from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro


def preencher_dados_gerais_orgao_externo(page: Page, orgao: dict) -> bool:
    """
    Preenche os dados gerais do Órgão Externo e confirma o cadastro.

    Cenário A: mesmos seletores em v3 e v4; só muda o escopo via `escopo(page)`.

    Campos obrigatórios: Identificação/CNPJ (`nrIdentAgente`, chave única,
    formatado), Nome (`nmAgente`), Endereço (`edAgente`), Bairro (`nmBairro`) e
    Cidade (`cdCidade`, lookup). Sigla (`sgOrgaoExterno`), UASG (`cdUasg`), CEP
    (`nrCep`), telefone (`nrDdd1`/`nrFone1`) e e-mail (`nmEmail`) completam. País
    e Código vêm do sistema. O checkbox "Validar CNPJ" fica marcado (CNPJ válido).

    :param orgao: dict do blueprint (nome, sigla, cnpj, uasg, endereco, bairro, cidade, cep, fone, email).
    """
    logger.info("Iniciou preenchimento de dados gerais de Órgão Externo '{}'.", orgao["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nrIdentAgente']").wait_for(state="visible")
    logger.info("Preenchendo CNPJ de Órgão Externo: '{}'.", orgao["cnpj"])
    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cnpj(orgao["cnpj"]))
    logger.info("Preenchendo UASG de Órgão Externo: '{}'.", orgao["uasg"])
    ctx.locator("input[name='cdUasg']").fill(orgao["uasg"])
    logger.info("Preenchendo Nome de Órgão Externo: '{}'.", orgao["nome"])
    ctx.locator("input[name='nmAgente']").fill(orgao["nome"])
    logger.info("Preenchendo Sigla de Órgão Externo: '{}'.", orgao["sigla"])
    ctx.locator("input[name='sgOrgaoExterno']").fill(orgao["sigla"])
    logger.info("Preenchendo Endereço de Órgão Externo: '{}'.", orgao["endereco"])
    ctx.locator("input[name='edAgente']").fill(orgao["endereco"])
    logger.info("Preenchendo Bairro de Órgão Externo: '{}'.", orgao["bairro"])
    ctx.locator("input[name='nmBairro']").fill(orgao["bairro"])
    escolher_cidade(ctx, orgao["cidade"])

    logger.info("Preenchendo CEP de Órgão Externo: '{}'.", orgao["cep"])
    ctx.locator("input[name='nrCep']").fill(_formatar_cep(orgao["cep"]))
    logger.info("Preenchendo Telefone de Órgão Externo: DDD '{}', Fone '{}'.", "61", orgao["fone"])
    ctx.locator("input[name='nrDdd1']").fill("61")
    logger.info("Preenchendo Fone de Órgão Externo: '{}'.", orgao["fone"])
    ctx.locator("input[name='nrFone1']").fill(orgao["fone"])
    logger.info("Preenchendo E-mail de Órgão Externo: '{}'.", orgao["email"])
    ctx.locator("input[name='nmEmail']").fill(orgao["email"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    try:
        esperar_sucesso_ou_erro(ctx)       
    except RuntimeError as e:
        mensagem_erro = str(e).lower()
        termos_skip = ["já"]
        if any(termo in mensagem_erro for termo in termos_skip):
            return False
        raise
    logger.info("Finalizou preenchimento de dados gerais de Órgão Externo '{}'.", orgao["nome"])
    return True


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def _formatar_cep(cep: str) -> str:
    """Formata 8 dígitos como XXXXX-XXX."""
    if not cep.isdigit() or len(cep) != 8:
        raise ValueError(f"CEP inválido para formatação: {cep}")
    return f"{cep[:5]}-{cep[5:]}"
