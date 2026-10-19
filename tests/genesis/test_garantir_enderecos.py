from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.localidade.cadastro_endereco.consultar_endereco_flow import (
    consultar_endereco,
)
from flows.corporativo.localidade.cadastro_endereco.navegar_para_endereco_flow import (
    acessar_endereco,
)
from flows.corporativo.localidade.cadastro_endereco.preencher_dados_basicos_endereco_flow import (
    preencher_dados_basicos_endereco,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_enderecos(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os Endereços da massa-base existam, criando somente os ausentes."""
    logger.info("Iniciou teste Genesis para garantir Endereços.")

    enderecos = contexto_cliente.enderecos()

    if not enderecos:
        logger.info("Nenhum endereço definido no blueprint. Ignorando teste.")
        return

    dados_link = contexto_cliente.dados_usuario("link")
    login(page, dados_link)
    acessar_endereco(page)

    total = len(enderecos)
    logger.info("Foi encontrado um total de {} endereços no blueprint.", total)

    for atual, endereco in enumerate(enderecos, start=1):
        nome = endereco["nome"]

        logger.info("Endereço {}/{}: '{}'.", atual, total, nome)

        consultar_endereco(page, endereco)

        if selecionar_registro_exato(page, nome):
            logger.info("Endereço '{}' já existe. Nenhuma ação necessária.", nome)
            continue

        acessar_endereco(page)
        preencher_dados_basicos_endereco(page, endereco)

        acessar_endereco(page)
        consultar_endereco(page, endereco)
        assert selecionar_registro_exato(page, nome), (
            f"Endereço '{nome}' não foi encontrado após o cadastro."
        )

        logger.success("Endereço '{}' criado com sucesso.", nome)

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Endereços.")
