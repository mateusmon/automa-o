import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcionario.consultar_funcionario_flow import (
    consultar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.navegar_para_funcionario_flow import (
    acessar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.preencher_dados_gerais_funcionario_flow import (
    preencher_dados_gerais_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.selecionar_funcionario_flow import (
    selecionar_funcionario,
)
from flows.corporativo.seguranca.cadastro_usuario.consultar_usuario_flow import (
    consultar_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.navegar_para_usuario_flow import (
    acessar_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.preencher_usuario_flow import (
    preencher_usuario,
)
from flows.corporativo.seguranca.cadastro_usuario.selecionar_usuario_flow import (
    selecionar_usuario,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_usuario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Usuário.")

    dados_cliente = contexto_cliente.dados_cliente()
    usuario = contexto_cliente.funcionario_usuario_cr()

    login(page, dados_cliente)
    _criar_funcionario(page, usuario)
    _criar_usuario(page, usuario)
    logout(page)

    logger.success("Finalizou teste de Cadastro de Usuário.")


def _criar_funcionario(page, usuario):
    acessar_funcionario(page)
    consultar_funcionario(page, usuario)

    if selecionar_funcionario(page, usuario):
        logger.info("Já existe funcionário.")
        return

    acessar_funcionario(page)
    preencher_dados_gerais_funcionario(page, usuario)


def _criar_usuario(page, usuario):
    acessar_usuario(page)
    consultar_usuario(page, usuario)

    if selecionar_usuario(page, usuario):
        logger.info("Já existe usuário.")
        logger.warning("Pulando teste.")
        pytest.skip()

    acessar_usuario(page)
    preencher_usuario(page, usuario)
