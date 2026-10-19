import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.seguranca.cadastro_perfil.alterar_perfil_flow import (
    alterar_perfil,
)
from flows.corporativo.seguranca.cadastro_perfil.consultar_perfil_flow import (
    consultar_perfil,
)
from flows.corporativo.seguranca.cadastro_perfil.navegar_para_perfil_flow import (
    acessar_perfil,
)
from flows.corporativo.seguranca.cadastro_perfil.selecionar_perfil_flow import (
    selecionar_perfil,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_perfil(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Perfil.")

    dados_cliente = contexto_cliente.dados_cliente()
    perfil = contexto_cliente.perfil_cr()

    login(page, dados_cliente)
    acessar_perfil(page)
    consultar_perfil(page, perfil)

    if not selecionar_perfil(page, perfil):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_perfil(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Perfil.")
