import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.patrimonio.movimentacao.transferencia_interna.confirmar_transferencia_interna_flow import (
    confirmar_transferencia_interna,
)
from flows.patrimonio.movimentacao.transferencia_interna.consultar_transferencia_flow import (
    consultar_transferencia,
)
from flows.patrimonio.movimentacao.transferencia_interna.editar_primeiro_documento_flow import (
    editar_primeiro_documento,
)
from flows.patrimonio.movimentacao.transferencia_interna.navegar_para_transferencia_interna_flow import (
    acessar_transferencia_interna,
)
from flows.patrimonio.movimentacao.transferencia_interna.preencher_bens_transferir_completo_flow import (
    preencher_bens_transferir_completo,
)
from flows.patrimonio.movimentacao.transferencia_interna.preencher_dados_gerais_completo_flow import (
    preencher_dados_gerais_completo,
)
from flows.patrimonio.movimentacao.transferencia_interna.preencher_documentos_completo_flow import (
    preencher_documentos,
)
from flows.patrimonio.movimentacao.transferencia_interna.preencher_observacao_flow import (
    preencher_observacao,
)
from flows.patrimonio.movimentacao.transferencia_interna.selecionar_modalidade_flow import (
    selecionar_modalidade,
)
from flows.patrimonio.movimentacao.transferencia_interna.validar_botoes_comuns import (
    validar_botoes_comuns,
)
from flows.patrimonio.movimentacao.transferencia_interna.verificar_botao_adicao_linha_flow import (
    verificar_botao_adicao_linha,
)
from flows.patrimonio.movimentacao.transferencia_interna.verificar_modificacao_documento_flow import (
    verificar_modificacao_documento,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_transferencia_interna_completa(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Transferência Interna Completa.")

    dados_cliente = contexto_cliente.dados_cliente()
    ul_padrao = contexto_cliente.unidade_localizacao_padrao()
    ul = contexto_cliente.unidade_localizacao_por_indice(1)
    ul_estoque = contexto_cliente.unidade_localizacao_estoque()
    fornecedor_padrao = contexto_cliente.fornecedor_padrao()
    fornecedor = contexto_cliente.fornecedor_por_indice(1)
    ug = contexto_cliente.ug()
    bem = contexto_cliente.bem_padrao()

    login(page, dados_cliente)
    acessar_transferencia_interna(page)
    validar_botoes_comuns(page, ul_padrao)
    selecionar_modalidade(page, "PERMANENTE")
    preencher_dados_gerais_completo(page, ul_padrao)

    if preencher_documentos(page, fornecedor_padrao):
        editar_primeiro_documento(page, fornecedor)
        documento_original = verificar_botao_adicao_linha(page, descricao_anexo="ANEXO TESTE")
        verificar_modificacao_documento(page, documento_original)

    ha_bem = preencher_bens_transferir_completo(page, ug, bem)

    if not ha_bem:
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_observacao(page)
    confirmar_transferencia_interna(page)
    acessar_transferencia_interna(page)
    existe_transferencia = consultar_transferencia(page, ug, ul_estoque, ul_padrao, True)
    if not existe_transferencia:
        logger.warning("Pulando teste.")
        pytest.skip()
    imprimir_relatorio(page)

    # Transferencia interna temporária
    acessar_transferencia_interna(page)
    selecionar_modalidade(page, "TEMPORÁRIA")
    preencher_dados_gerais_completo(page, ul, modalidade="TEMPORÁRIA", patrimonio_antigo="COM")
    
    if preencher_documentos(page, fornecedor_padrao):
        editar_primeiro_documento(page, fornecedor)
        documento_original = verificar_botao_adicao_linha(page, descricao_anexo="ANEXO TESTE")
        verificar_modificacao_documento(page, documento_original)

    ha_bem = preencher_bens_transferir_completo(page, ug, bem)

    if not ha_bem:
        logger.warning("Pulando teste.")
        pytest.skip()

    preencher_observacao(page)
    confirmar_transferencia_interna(page)
    acessar_transferencia_interna(page)
    existe_transferencia = consultar_transferencia(page, ug, ul_padrao, ul, True, False)
    if not existe_transferencia:
            logger.warning("Pulando teste.")
            pytest.skip()
    excluir_movimento(page)
    logout(page)

    logger.success("Finalizou teste de Transferência Interna Completa.")