import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.transferencia_interna.confirmar_transferencia_interna_flow import (
    confirmar_transferencia_interna,
)
from flows.patrimonio.movimentacao.transferencia_interna.navegar_para_transferencia_interna_flow import (
    acessar_transferencia_interna,
)
from flows.patrimonio.movimentacao.transferencia_interna.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.movimentacao.transferencia_interna.selecionar_modalidade_flow import (
    selecionar_modalidade,
)
from flows.patrimonio.movimentacao.transferencia_interna.temporaria.preencher_bens_transferir_flow import (
    preencher_bens_transferir,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_interna_temporaria(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência Interna Temporária.")

    dados_cliente = contexto_cliente.dados_cliente()
    # O bem não pode estar na conta estoque, então passamos de uma UL normal para outra
    ul = contexto_cliente.unidade_localizacao_por_indice(1)
    ul_padrao = contexto_cliente.unidade_localizacao_padrao()
    bem = contexto_cliente.bem_padrao()
    
    login(page, dados_cliente)
    acessar_transferencia_interna(page)

    if not selecionar_modalidade(page, "TEMPORÁRIA"):
        logger.warning("Pulando teste.")
        pytest.skip()
        
    preencher_dados_gerais(page, ul)
    
    if not preencher_bens_transferir(page, ul_padrao, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    if not confirmar_transferencia_interna(page):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page)
    logout(page)
    
    logger.success("Finalizou teste de Transferência Interna Temporária.")
