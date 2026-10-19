from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.classificacao_material.classificacao_material_natureza.escolher_natureza_flow import (
    escolher_natureza,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.por_entidade.preecher_almoxarifado_flow import (
    preencher_almoxarifado,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.navegar_para_classificacao_material_flow import (
    acessar_classificacao_material,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.selecionar_material_flow import (
    selecionar_material,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_classificacao_material_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Classificação de Material por Almoxarifado.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_classificacao_material(page)
    preencher_almoxarifado(page, almoxarifado)
    selecionar_material(page, material)
    escolher_natureza(page, "NÃO ESTOCÁVEL")

    logger.info("Desfazendo mudanças.")
    selecionar_material(page, material)
    escolher_natureza(page, "ESTOCÁVEL")

    logout(page)
    logger.success("Finalizou teste de Classificação de Material por Almoxarifado.")
