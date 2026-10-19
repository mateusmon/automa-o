from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.classificacao_material.classificacao_material_consumo.escolher_consumo_flow import (
    escolher_consumo,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.escolher_classificacao_flow import (
    escolher_classificacao,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.preencher_consulta_flow import (
    preencher_consulta,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.navegar_para_classificacao_material_flow import (
    acessar_classificacao_material,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.selecionar_material_flow import (
    selecionar_material,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_classificacao_material_consumo(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Classificação de Material Quanto ao Consumo.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_classificacao_material(page)
    escolher_classificacao(page, "CONSUMO")
    preencher_consulta(page, almoxarifado, material)
    selecionar_material(page, material)
    escolher_consumo(page, "ALTA")

    logger.info("Desfazendo mudanças.")
    selecionar_material(page, material)
    escolher_consumo(page, "NÃO")
    logout(page)
    
    logger.success("Finalizou teste de Classificação de Material Quanto ao Consumo.")
