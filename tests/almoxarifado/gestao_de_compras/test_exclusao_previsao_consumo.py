import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.consultar_cadastro_previsao_flow import (
    consultar_cadastro,
)
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.navegar_para_cadastro_previsao_consumo_flow import (
    acessar_cadastro_previsao_consumo,
)
from flows.almoxarifado.gestao_de_compras.cadastro_previsao_consumo.selecionar_cadastro_flow import (
    selecionar_cadastro,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_cadastro_previsao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Cadastro de Previsão de Consumo da UR.")

    dados_cliente = contexto_cliente.dados_cliente()
    ur_data = contexto_cliente.ur_padrao()
    material = contexto_cliente.material_padrao()
    
    login(page, dados_cliente)
    acessar_cadastro_previsao_consumo(page)
    consultar_cadastro(page, ur_data, material)

    if not selecionar_cadastro(page, ur_data):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Cadastro de Previsão de Consumo da UR.")
