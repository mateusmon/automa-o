from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro, select_tipo


def preencher_dados_gerais_fornecedor(page: Page, fornecedor: dict) -> None:
    """
    Preenche os dados gerais do Fornecedor e confirma o cadastro.

    Cenário A: mesmos seletores em v3 e v4; só muda o escopo (page/iframe) via
    `escopo(page)`.

    Campos obrigatórios: Tipo (`situacaoJuridica`), CNPJ (`nrIdentAgente`, chave
    única, formatado), Razão Social (`nmRazaoSocialGeral`), Nome Fantasia
    (`nmAgente`), Cidade (`cdCidade`, lookup) e Fone (`nrDdd1`/`nrFone1`). Porte
    (`cdTpForPorte`), Endereço (`edAgente`) e Bairro (`nmBairro`) completam o
    cadastro. País vem pré-preenchido pelo sistema. DDD = "61" (Brasília, padrão
    do Genesis para os fornecedores de teste).

    :param fornecedor: dict do blueprint (tipo, porte, nome, cnpj, endereco, bairro, cidade, fone).
    """
    logger.info("Iniciou preenchimento de dados gerais de Fornecedor '{}'.", fornecedor["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("select[name='situacaoJuridica']").wait_for(state="visible")

    select_tipo(ctx, "situacaoJuridica", fornecedor["tipo"])
    select_tipo(ctx, "cdTpForPorte", fornecedor["porte"])

    ctx.locator("input[name='inCartorio'][value='N']").check()
    aguardar_ajax_global(page)

    logger.info("Preenchendo CNPJ de Fornecedor: '{}'.", fornecedor["cnpj"])
    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cnpj(fornecedor["cnpj"]))
    logger.info("Preenchendo Razão Social de Fornecedor: '{}'.", fornecedor["nome"])
    ctx.locator("input[name='nmRazaoSocialGeral']").fill(fornecedor["nome"])
    logger.info("Preenchendo Nome do Fornecedor: '{}'.", fornecedor["nome"])
    ctx.locator("input[name='nmAgente']").fill(fornecedor["nome"])
    logger.info("Preenchendo Endereço do Fornecedor: '{}'.", fornecedor["endereco"])
    ctx.locator("input[name='edAgente']").fill(fornecedor["endereco"])
    logger.info("Preenchendo Bairro do Fornecedor: '{}'.", fornecedor["bairro"])
    ctx.locator("input[name='nmBairro']").fill(fornecedor["bairro"])

    escolher_cidade(ctx, fornecedor["cidade"])

    logger.info("Preenchendo DDD de Fornecedor: '{}'.", "61")
    ctx.locator("input[name='nrDdd1']").fill("61")
    logger.info("Preenchendo Fone de Fornecedor: DDD '{}', Fone '{}'.", "61", fornecedor["fone"])
    ctx.locator("input[name='nrFone1']").fill(fornecedor["fone"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Fornecedor '{}'.", fornecedor["nome"])


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX (o campo exige CNPJ formatado)."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
