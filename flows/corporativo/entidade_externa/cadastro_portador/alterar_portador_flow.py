from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
    preencher_autocomplete,
    proximo_nome,
)


def alterar_portador(page: Page, portador: dict) -> None:
    """
    Altera o Nome/Registro Civil do Portador (`nmRegistroCivil`) e confirma UMA vez.

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta (que filtra pelo CPF) e o
    teste re-executável. Ao carregar o registro via Anexar, os lookups da Cidade (`cdCidade`)
    e do Fornecedor/Órgão Externo (`agenteFornecedorOrgaoExterno`, autocomplete especial) não
    repopulam, então são reinformados antes do submit — sem isso a validação falha. Não mexe
    em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_portador`).
    """
    logger.info("Iniciou alteração de Portador '{}'.", portador["nome"])

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmRegistroCivil']")
    logger.info("Iniciou preenchimento do Nome/Registro Civil do Portador '{}'.", portador["nome"])
    campo.fill(proximo_nome(campo.input_value()))

    campo_cidade = ctx.locator("input[name='cdCidade']")
    if not campo_cidade.input_value().strip():
        escolher_cidade(ctx, portador["cidade"])

    preencher_autocomplete(ctx, "input[name='agenteFornecedorOrgaoExterno']", portador["fornecedor"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Portador '{}'.", portador["nome"])
