from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
    preencher_autocomplete,
)


def preencher_dados_gerais_portador(page: Page, portador: dict) -> None:
    """
    Preenche os dados gerais do Portador e confirma o cadastro.

    Cenário A: mesmos seletores em v3 e v4; só muda o escopo via `escopo(page)`.

    Campos obrigatórios: Nome/Registro Civil (`nmRegistroCivil`), CPF
    (`nrIdentAgente`, chave única, formatado), R.G. (`nrRG`), Endereço
    (`edAgente`), Cidade (`cdCidade`, lookup), Telefone (`nrDdd1`/`nrFone1`) e
    Fornecedor/Órgão Externo (`agenteFornecedorOrgaoExterno`, lookup — referencia
    um fornecedor padrão). CEP (`nrCep`) e e-mail (`nmEmail`) completam. Órgão vem
    pré-preenchido pelo sistema (varia por cliente).

    :param portador: dict do blueprint (nome, cpf, rg, endereco, cidade, cep, fone, fornecedor, email).
    """
    logger.info("Iniciou preenchimento de dados gerais de Portador '{}'.", portador["nome"])
 
    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmRegistroCivil']").wait_for(state="visible")
    logger.info("Preenchendo Registro Civil de Portador: '{}'.", portador["nome"])
    ctx.locator("input[name='nmRegistroCivil']").fill(portador["nome"])
    logger.info("Preenchendo CPF de Portador: '{}'.", portador["cpf"])
    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cpf(portador["cpf"]))
    logger.info("Preenchendo R.G. de Portador: '{}'.", portador["rg"])
    ctx.locator("input[name='nrRG']").fill(portador["rg"])
    logger.info("Preenchendo Endereço de Portador: '{}'.", portador["endereco"])
    ctx.locator("input[name='edAgente']").fill(portador["endereco"])

    escolher_cidade(ctx, portador["cidade"])

    logger.info("Preenchendo CEP de Portador: '{}'.", portador["cep"])
    ctx.locator("input[name='nrCep']").fill(_formatar_cep(portador["cep"]))
    logger.info("Preenchendo DDD de Portador: '{}'.", portador["fone"])
    ctx.locator("input[name='nrDdd1']").fill("61")
    logger.info("Preenchendo Telefone de Portador: '{}'.", portador["fone"])
    ctx.locator("input[name='nrFone1']").fill(portador["fone"])

    # Caso especial SÓ desta página: o `preencher_campo` (lookup) tem o clique do
    # botão interceptado pelo dropdown de autocomplete aberto. Aqui o campo é um
    # ui-autocomplete puro — digita-se e seleciona-se com teclado (ArrowDown+Enter),
    # sem clicar no botão lookup nem na sugestão. Em todo o resto do projeto o
    # `preencher_campo` continua sendo o padrão.
    preencher_autocomplete(ctx, "input[name='agenteFornecedorOrgaoExterno']", portador["fornecedor"])

    logger.info("Preenchendo E-mail de Portador: '{}'.", portador["email"])
    ctx.locator("input[name='nmEmail']").fill(portador["email"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Portador '{}'.", portador["nome"])


def _formatar_cpf(cpf: str) -> str:
    """Formata 11 dígitos como XXX.XXX.XXX-XX."""
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError(f"CPF inválido para formatação: {cpf}")
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def _formatar_cep(cep: str) -> str:
    """Formata 8 dígitos como XXXXX-XXX."""
    if not cep.isdigit() or len(cep) != 8:
        raise ValueError(f"CEP inválido para formatação: {cep}")
    return f"{cep[:5]}-{cep[5:]}"
