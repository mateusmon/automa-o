from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.inventario.finalizar_inventario_flow import (
    finalizar_inventario,
)
from flows.almoxarifado.gestao_de_estoque.inventario.navegar_para_pagina_inventario_flow import (
    acessar_inventario,
)
from flows.almoxarifado.gestao_de_estoque.inventario.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_inventario_por_levantamento(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Inventário por Levantamento.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()
    ua = contexto_cliente.ua()

    login(page, dados_cliente)
    acessar_inventario(page)
    preencher_dados_gerais(page, almoxarifado, ua, "LEVANTAMENTO")
    finalizar_inventario(page, material)
    logout(page)

    logger.success("Finalizou teste de Invetário por Levantamento.")