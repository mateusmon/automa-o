from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.navegar_para_cadastro_previsao_consumo_flow import (
    acessar_cadastro_previsao_consumo,
)
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.preencher_itens_flow import (
    preencher_itens,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_previsao_consumo(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Previsão de Consumo da UR.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur_data = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()
    
    login(page, dados_cliente)
    acessar_cadastro_previsao_consumo(page)
    preencher_dados_gerais(page, ur_data)
    preencher_itens(page, material)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Previsão de Consumo da UR.")
