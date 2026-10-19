import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.alterar_definicao_flow import (
    alterar_definicao,
)
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.consultar_definicao_flow import (
    consultar_definicao,
)
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.navegar_para_definicao_motivos_saida_temporaria_flow import (
    acessar_definicao_motivos,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_alteracao_definicao_motivos_saida_temporaria(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Definição de Motivos de Saída Temporária.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_motivos(page)

    if not consultar_definicao(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    alterar_definicao(page)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Definição de Motivos de Saída Temporária.")
