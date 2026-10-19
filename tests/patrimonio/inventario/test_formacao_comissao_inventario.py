from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.inventario.formacao_comissao_inventario.navegar_para_formacao_comissao_inventario_flow import (
    acessar_formacao_comissao_inventario,
)
from flows.patrimonio.inventario.formacao_comissao_inventario.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.inventario.formacao_comissao_inventario.preencher_representantes_flow import (
    preencher_representantes,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_formacao_comissao_inventario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Formação de comissão de Inventário.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    funcionario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_formacao_comissao_inventario(page)
    preencher_dados_gerais(page, ug)
    preencher_representantes(page, funcionario)
    logout(page)

    logger.success("Finalizou teste de Formação de comissão de Inventário.")
