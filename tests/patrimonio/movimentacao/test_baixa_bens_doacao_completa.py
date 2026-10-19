import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.baixa_bens.doacao.mudar_situacao_itens_flow import (
    mudar_situacao_itens,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.navegar_para_baixa_bens_flow import (
    acessar_baixa_bens,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_dados_gerais_completo_flow import (
    preencher_dados_gerais_completo,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.patrimonio.movimentacao.baixa_bens.doacao.preencher_tramitacoes_flow import (
    preencher_tramitacoes,
)
from flows.patrimonio.movimentacao.baixa_bens.editar_primeiro_documento_com_anexo_flow import (
    editar_primeiro_documento_com_anexo,
)
from flows.patrimonio.movimentacao.baixa_bens.preencher_todos_documentos_flow import (
    preencher_todos_documentos,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_baixa_bens_doacao(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Baixa de Bens.")

    dados_cliente = contexto_cliente.dados_cliente()
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()
    usuario = contexto_cliente.funcionario_padrao()

    login(page, dados_cliente)
    acessar_baixa_bens(page)
    preencher_dados_gerais_completo(page, ug)
    preencher_todos_documentos(page)
    editar_primeiro_documento_com_anexo(page)
    preencher_observacoes(page)
    preencher_tramitacoes(page, usuario)

    if not mudar_situacao_itens(page, ug, bem):
        logger.warning("Pulando teste.")
        pytest.skip()

    imprimir_relatorio(page, timeout_geracao=250_000)
    logout(page)

    logger.success("Finalizou teste de Baixa de Bens.")
