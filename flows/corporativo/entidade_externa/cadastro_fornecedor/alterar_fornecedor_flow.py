from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro, proximo_nome


def alterar_fornecedor(page: Page, fornecedor: dict) -> None:
    """
    Altera o Nome Fantasia do Fornecedor (`nmAgente`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"). Ao carregar o registro via Anexar, o lookup da Cidade (`cdCidade`) não
    repopula, então é re-selecionado antes do submit — sem isso a validação falha. Não mexe
    em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_fornecedor`).
    """
    logger.info("Iniciou alteração de Fornecedor '{}'.", fornecedor["nome"])

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmAgente']")
    logger.info("Alterando o Nome do fornecedor: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    escolher_cidade(ctx, fornecedor["cidade"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Fornecedor '{}'.", fornecedor["nome"])
