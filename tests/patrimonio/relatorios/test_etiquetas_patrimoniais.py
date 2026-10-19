import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.consulta.navegar_para_consulta_flow import acessar_consulta
from flows.patrimonio.relatorios.etiquetas_patrimoniais.navegar_para_etiquetas_patrimoniais_flow import (
    acessar_etiquetas_patrimoniais,
)
from flows.patrimonio.relatorios.etiquetas_patrimoniais.pegar_num_patrimonial_flow import (
    pegar_num_patrimonial,
)
from flows.patrimonio.relatorios.etiquetas_patrimoniais.preencher_etiquetas_flow import (
    preencher_etiquetas,
)
from flows.patrimonio.relatorios.etiquetas_patrimoniais.preencher_opcoes_relatorio_flow import (
    preencher_opcoes_relatorio,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_etiquetas_patrimoniais(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Etiquetas Patrimoniais.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)
    acessar_consulta(page)

    ha_patrimonios = pegar_num_patrimonial(page, ug, bem)
    if not ha_patrimonios:
        logger.warning("Pulando teste.")
        pytest.skip()

    acessar_etiquetas_patrimoniais(page)
    preencher_etiquetas(page, ug, ha_patrimonios)
    preencher_opcoes_relatorio(page)
    imprimir_relatorio(page)
    logout(page)

    logger.success("Finalizou teste de Etiquetas Patrimoniais.")
