import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.modificacao.detentor_bem_cadastro.navegar_para_detentor_bem_cadastro_flow import (
    acessar_detentor_bem_cadastro,
)
from flows.patrimonio.modificacao.detentor_bem_cadastro.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.patrimonio.modificacao.detentor_bem_cadastro.selecionar_bem_flow import (
    selecionar_bem,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_detentor_bem_cadastro(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de Detentor do Bem.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_por_indice(0)
    funcionario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_detentor_bem_cadastro(page)
    preencher_dados_gerais(page, ug, funcionario)
    
    if not selecionar_bem(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page, timeout_geracao= 240000)
    logout(page)
    
    logger.success("Finalizou teste de Cadastro de Detentor do Bem.")
