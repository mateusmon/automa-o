from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.consultar_definicao_flow import (
    consultar_definicao,
)
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.navegar_para_definicao_motivos_saida_temporaria_flow import (
    acessar_definicao_motivos,
)
from flows.patrimonio.auxiliares.definicao_motivos_saida_temporaria.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_definicao_motivos_saida_temporaria(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Definição de Motivos de Saída Temporária Interna.")

    dados_cliente = contexto_cliente.dados_cliente()

    login(page, dados_cliente)
    acessar_definicao_motivos(page)
    preencher_dados_gerais(page, "INTERNA")

    logger.info("Desfazendo movimento.")
    consultar_definicao(page)
    excluir_movimento(page)
    logout(page)

    logger.success("Finalizou teste de Definição de Motivos de Saída Temporária Interna.")
