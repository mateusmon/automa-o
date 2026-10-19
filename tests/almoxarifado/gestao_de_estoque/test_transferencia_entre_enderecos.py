from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.transferencia_entre_enderecos.navegar_para_transferencia_enderecos_flow import (
    acessar_transferencia_enderecos,
)
from flows.almoxarifado.gestao_de_estoque.transferencia_entre_enderecos.preencher_dados_flow import (
    preencher_dados,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_enderecos(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência entre Endereços.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_transferencia_enderecos(page)
    preencher_dados(page, almoxarifado, material)
    logout(page)

    logger.success("Finalizou teste de Transferência entre Endereços.")
