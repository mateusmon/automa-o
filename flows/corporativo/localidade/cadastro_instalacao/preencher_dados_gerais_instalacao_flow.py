from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro


def preencher_dados_gerais_instalacao(page: Page, instalacao: dict) -> None:
    """
    Preenche a Instalação e confirma. Cenário A.
    Campos: Nome (`nmInstalacao`), Endereço (`dsEndereco`), Cidade (`cidade`,
    lookup), Bairro (`nmBairro`) e CEP (`nrCep`, formatado). Órgão pré-preenchido
    (varia por cliente) e Código gerado.

    :param instalacao: dict do blueprint (nome, endereco, cidade, bairro, cep).
    """
    logger.info("Iniciou preenchimento de dados gerais de Instalação '{}'.", instalacao["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmInstalacao']").wait_for(state="visible")
    logger.info("Preenchendo Nome de Instalação: '{}'.", instalacao["nome"])
    ctx.locator("input[name='nmInstalacao']").fill(instalacao["nome"])
    logger.info("Preenchendo Endereço de Instalação: '{}'.", instalacao["endereco"])
    ctx.locator("input[name='dsEndereco']").fill(instalacao["endereco"])
    
    escolher_cidade(ctx, instalacao["cidade"], locator_campo="input[name='cidade']")

    logger.info("Preenchendo Bairro de Instalação: '{}'.", instalacao["bairro"])
    ctx.locator("input[name='nmBairro']").fill(instalacao["bairro"])
    logger.info("Preenchendo CEP de Instalação: '{}'.", instalacao["cep"])
    ctx.locator("input[name='nrCep']").fill(_formatar_cep(instalacao["cep"]))

    page.once("dialog", _aceitar_confirmacao)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Instalação '{}'.", instalacao["nome"])


def _formatar_cep(cep: str) -> str:
    """Formata 8 dígitos como XXXXX-XXX."""
    if not cep.isdigit() or len(cep) != 8:
        raise ValueError(f"CEP inválido para formatação: {cep}")
    return f"{cep[:2]}.{cep[2:5]}-{cep[5:]}"


def _aceitar_confirmacao(dialog) -> None:
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")
