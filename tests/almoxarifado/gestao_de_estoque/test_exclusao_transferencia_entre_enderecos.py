import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.almoxarifado.gestao_de_estoque.transferencia_entre_enderecos.consulta_transferencia_entre_enderecos.consultar_transferencia_entre_enderecos_flow import (
    consultar_transferencia_entre_enderecos,
)
from flows.almoxarifado.gestao_de_estoque.transferencia_entre_enderecos.consulta_transferencia_entre_enderecos.selecionar_transferencia_entre_enderecos_flow import (
    selecionar_transferencia_entre_enderecos,
)
from flows.almoxarifado.gestao_de_estoque.transferencia_entre_enderecos.navegar_para_transferencia_enderecos_flow import (
    acessar_transferencia_enderecos,
)
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_exclusao_transferencia_enderecos(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de Transferência entre Endereços.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_transferencia_enderecos(page)
    consultar_transferencia_entre_enderecos(page, almoxarifado, material)

    if not selecionar_transferencia_entre_enderecos(page, almoxarifado):
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)
    logout(page)
    
    logger.success("Finalizou teste de Exclusão de Transferência entre Endereços.")
