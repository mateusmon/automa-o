import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.navegar_para_cadastro_transferencia_almoxarifado_flow import (
    acessar_cadastro_transferencia_almoxarifado,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.preencher_almoxarifado_atendimento_flow import (
    preencher_almoxarifado_atendimento,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.preencher_almoxarifado_solicitante_completa_flow import (
    preencher_almoxarifado_solicitante,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.preencher_evento_flow import (
    preencher_evento,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.preencher_material_solicitante_flow import (
    preencher_material_solicitante,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.validar_botoes_comuns_flow import (
    validar_botoes_comuns,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.validar_botoes_comuns_recarregar_flow import (
    validar_botoes_comuns_recarregar,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.preencher_data_transferencia_flow import (
    preencher_data_transferencia,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.consultar_cadastro_transferencia_entre_almoxarifados_completa_flow import (
    consultar_cadastro_transferencia_completa,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.selecionar_transferencia_flow import (
    selecionar_transferencia,
)
from flows.almoxarifado.movimentacao_externa.cadastro_transferencia_almoxarifado.consultar_cadastro_transferencia_entre_almoxarifados_flow import (
    consultar_cadastro_transferencia,
)
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.shared.retornar_duas_vezes_flow import retornar_duas_vezes
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_cadastro_transferencia_almoxarifado(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro Completo de Transferência entre Almoxarifados.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    almoxarifado_solicitante = contexto_cliente.almoxarifado_por_indice(1)
    material = contexto_cliente.material_padrao()
    evento = contexto_cliente.evento()


    login(page, dados_cliente)
    acessar_cadastro_transferencia_almoxarifado(page)
    preencher_almoxarifado_atendimento(page, almoxarifado)
    validar_botoes_comuns_recarregar(page)
    preencher_data_transferencia(page),
    preencher_almoxarifado_atendimento(page, almoxarifado)
    preencher_almoxarifado_solicitante(page, almoxarifado_solicitante)
    preencher_evento(page, evento)
    preencher_material_solicitante(page,material)
    validar_botoes_comuns(page)
    consultar_cadastro_transferencia_completa(page, almoxarifado, almoxarifado_solicitante, material)
    imprimir_relatorio(page)
    retornar_duas_vezes(page)
    consultar_cadastro_transferencia(page, almoxarifado, almoxarifado_solicitante, material)

    if not selecionar_transferencia(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, True)

    logout(page)

    logger.success("Finalizou teste de Cadastro Completo de Transferência entre Almoxarifados.")
