import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.status_bem.confirmar_modificacao_flow import (
    confirmar_modificacao,
)
from flows.patrimonio.modificacao.status_bem.consultar_modificacao_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.status_bem.navegar_para_status_bem_flow import (
    acessar_status_bem,
)
from flows.patrimonio.modificacao.status_bem.preencher_bem_flow import preencher_bem
from flows.patrimonio.modificacao.status_bem.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.modificacao.status_bem.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.patrimonio.modificacao.status_bem.selecionar_status_flow import (
    selecionar_status,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_status_bem(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação do Status de Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(9)

    login(page, dados_cliente)
    acessar_status_bem(page)
    preencher_dados_gerais(page, ug)

    if not preencher_bem(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    selecionar_status(page, "DISPONÍVEL")
    confirmar_modificacao(page)
    consultar_modificacao(page, ug)
    selecionar_modificacao(page, ug)

    if not imprimir_relatorio(page):
        logger.warning("Pulando teste.")
        pytest.skip()
    logout(page)

    logger.success("Finalizou teste de Modificação do Status de Bem.")
