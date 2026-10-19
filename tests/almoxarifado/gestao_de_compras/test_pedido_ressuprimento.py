from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.navegar_para_pedido_ressuprimento_flow import (
    acessar_pedido_ressuprimento,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.preencher_itens_flow import (
    preencher_itens,
)
from flows.almoxarifado.gestao_de_compras.pedido_de_ressuprimento.preencher_parametros_flow import (
    preencher_parametros,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_pedido_ressuprimento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Pedido de Ressuprimento.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_pedido_ressuprimento(page)
    preencher_dados_gerais(page, almoxarifado)
    preencher_parametros(page)
    preencher_itens(page, material)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Pedido de Ressuprimento.")
