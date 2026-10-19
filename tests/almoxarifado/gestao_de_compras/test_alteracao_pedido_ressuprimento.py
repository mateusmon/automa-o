import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.alteracao_pedido_ressuprimento.alterar_pedido_ressuprimento_flow import (
    alterar_pedido_ressuprimento,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.consulta_pedido_ressuprimento.consultar_pedido_ressuprimento_flow import (
    consultar_pedido_ressuprimento,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.navegar_para_pedido_ressuprimento_flow import (
    acessar_pedido_ressuprimento,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_pedido_ressuprimento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Pedido de Ressuprimento.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_pedido_ressuprimento(page)

    if not consultar_pedido_ressuprimento(page, almoxarifado, material):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_pedido_ressuprimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Pedido de Ressuprimento.")