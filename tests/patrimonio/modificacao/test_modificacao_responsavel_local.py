from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.modificacao_responsavel_local.navegar_para_modificacao_responsavel_local_flow import (
    acessar_modificacao_responsavel_local,
)
from flows.patrimonio.modificacao.modificacao_responsavel_local.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.modificacao.modificacao_responsavel_local.preencher_novos_responsaveis_flow import (
    preencher_novos_responsaveis,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_modificacao_responsavel_local(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Modificação de Responsável do Local.")

    dados_cliente = contexto_cliente.dados_cliente()
    ua = contexto_cliente.ua()
    ul = contexto_cliente.unidade_localizacao_padrao()

    login(page, dados_cliente)
    acessar_modificacao_responsavel_local(page)
    preencher_dados_gerais(page, ua)
    preencher_novos_responsaveis(page, ul)
    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Modificação de Responsável do Local.")
