import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.seguranca.cadastro_usuario.alterar_usuario_flow import (
    alterar_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.consultar_usuario_flow import (
    consultar_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.navegar_para_usuario_flow import (
    acessar_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.selecionar_usuario_flow import (
    selecionar_usuario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_usuario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Usuário.")

    dados_cliente = contexto_cliente.dados_cliente()
    usuario = contexto_cliente.funcionario_usuario_cr()

    login(page, dados_cliente)
    acessar_usuario(page)

    # Se o funcionário não existe, não tem como o usuário existir
    if not consultar_usuario(page, usuario):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not selecionar_usuario(page, usuario):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_usuario(page, usuario)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Usuário.")
