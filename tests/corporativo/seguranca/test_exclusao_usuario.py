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
from flows.corporativo.funcionario.cadastro_funcionario.selecionar_funcionario_flow import (
    selecionar_funcionario,
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
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_usuario(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Usuário.")

    dados_cliente = contexto_cliente.dados_cliente()
    usuario = contexto_cliente.funcionario_usuario_cr()

    login(page, dados_cliente)

    # 1. Remove o usuário (se existir)
    acessar_usuario(page)
    # Se não existe funcionário, não tem como existir usuário
    if consultar_usuario(page, usuario):
        if selecionar_usuario(page, usuario):
            excluir_movimento(page, esperar_sucesso=True)
    else:
        logger.info("Funcionário e usuário não existem.")
        logger.warning("Pulando teste.")
        pytest.skip()

    # 2. Remove o funcionário (criado só por causa do usuário).
    acessar_funcionario(page)
    consultar_funcionario(page, usuario)
    if selecionar_funcionario(page, usuario):
        excluir_movimento(page, esperar_sucesso=True)

    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Usuário.")
