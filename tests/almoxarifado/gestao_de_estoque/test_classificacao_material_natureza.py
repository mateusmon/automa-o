from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.classificacao_material.classificacao_material_natureza.mudar_natureza_flow import (
    mudar_natureza,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.classificacao_material_natureza.selecionar_natureza_flow import (
    selecionar_natureza,
)
from flows.almoxarifado.gestao_de_estoque.classificacao_material.classificacao_material_natureza.voltar_natureza_original_flow import (
    voltar_natureza_original,
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


def test_classificacao_material_natureza(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Classificação de Material quanto à Natureza.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_classificacao_material(page)
    preencher_consulta(page, almoxarifado, material)
    selecionar_material(page, material)
    natureza = selecionar_natureza(page)
    mudar_natureza(page)

    logger.info("Desfazendo mudanças.")
    selecionar_material(page, material)
    voltar_natureza_original(page, natureza)
    logout(page)
    
    logger.success("Finalizou teste de Classificação de Material quanto à Natureza.")
