import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.valor_mercado.consultar_modificacao_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.valor_mercado.navegar_para_valor_mercado_flow import (
    acessar_valor_mercado,
)
from flows.patrimonio.modificacao.valor_mercado.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


# OBS: Só é possível fazer a exclusão de um movimento não alterado. Se o patrimônio
# foi alterado mais do que uma vez, não é possível excluir o primeiro movimento.
# A exclusão precisa ser feita de baixo pra cima, do mais velho ao mais novo
def test_exclusao_valor_mercado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Modificação do Valor do Mercado.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_valor_mercado(page)
    consultar_modificacao(page, ug)

    if not selecionar_modificacao(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    excluir_movimento(page)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Modificação do Valor do Mercado.")
