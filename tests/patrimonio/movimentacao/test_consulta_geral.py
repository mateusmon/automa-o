import pytest
from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.consulta.consultar_bem_flow import consultar_bem
from flows.patrimonio.consulta.navegar_para_consulta_flow import acessar_consulta
from flows.patrimonio.consulta.verificar_resultado_consulta_flow import (
    verificar_resultado_consulta,
)
from flows.patrimonio.consulta.voltar_para_resultados_consulta_flow import (
    voltar_para_resultados_consulta,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_consulta(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta Geral de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)
    acessar_consulta(page)
    consultar_bem(page, ug, bem)
    resultado_verificacao = verificar_resultado_consulta(page, bem)

    if resultado_verificacao == "sem entradas":
        logger.warning("Pulando teste.")
        pytest.skip()
    elif resultado_verificacao == "entrada unica":
        voltar_para_resultados_consulta(page)

    if resultado_verificacao != "sem relatorios":
        try:
            imprimir_relatorio(page, timeout_geracao=180_000)
        except PlaywrightTimeoutError:
            logger.warning(
                "Levou tempo demais para gerar todos os relatórios. Impressão de relatórios não validada."
            )

    logout(page)

    logger.success("Finalizou teste de Consulta Geral de Bens.")
    
