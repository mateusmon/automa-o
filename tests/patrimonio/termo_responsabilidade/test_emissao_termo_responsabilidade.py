from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.termo_responsabilidade.emissao_termo_responsabilidade.navegando_para_emissao_termo_responsabilidade_flow import (
    acessar_emissao_termo_responsabilidade,
)
from flows.patrimonio.termo_responsabilidade.emissao_termo_responsabilidade.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_emissao_termo_responsabilidade(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Emissão de Termo de Responsabilidade.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    ua = contexto_cliente.ua()

    login(page, dados_cliente)
    acessar_emissao_termo_responsabilidade(page)
    preencher_dados_gerais(page, ug, ua)
    imprimir_relatorio(page, "input[name='listaRelatorios-1-3']", timeout_geracao=60_000)
    logout(page)
    
    logger.success("Finalizou teste de Emissão de Termo de Responsabilidade.")