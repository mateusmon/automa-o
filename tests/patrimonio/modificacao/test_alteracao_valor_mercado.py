import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.valor_mercado.alterar_valor_mercado_flow import (
    alterar_valor_mercado,
)
from flows.patrimonio.modificacao.valor_mercado.consultar_modificacao_flow import (
    consultar_modificacao,
)
from flows.patrimonio.modificacao.valor_mercado.navegar_para_valor_mercado_flow import (
    acessar_valor_mercado,
)
from flows.patrimonio.modificacao.valor_mercado.selecionar_modificacao_flow import (
    selecionar_modificacao,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


# OBS: Só é possível fazer a alteração de um movimento não alterado. Se o patrimônio
# foi alterado mais do que uma vez, não é possível alterar o primeiro movimento.
# A alteração precisa ser feita de baixo pra cima, do mais velho ao mais novo
def test_alteracao_valor_mercado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Alteração de Valor do Mercado.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()

    login(page, dados_cliente)
    acessar_valor_mercado(page)
    consultar_modificacao(page, ug)

    if not selecionar_modificacao(page, ug):
        logger.warning("Pulando teste.")
        pytest.skip()
    
    alterar_valor_mercado(page)

    logger.info("Desfazendo modificação.")
    consultar_modificacao(page, ug)
    selecionar_modificacao(page, ug)
    alterar_valor_mercado(page, True)
    logout(page)
    
    logger.success("Finalizou teste de Alteração de Valor do Mercado.")
