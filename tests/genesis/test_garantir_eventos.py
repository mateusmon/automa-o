from flows.genesis.garantir_eventos.criar_evento_flow import criar_evento
from flows.genesis.garantir_eventos.verificar_evento_existente_flow import (
    verificar_evento_existente,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_eventos(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante a existência dos eventos informados na massa."""
    logger.info("Iniciou teste Genesis para garantir Eventos.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    evento_data = contexto_cliente.evento()

    if not evento_data:
        logger.info("Nenhum evento definido no arquivo yaml. Ignorando fluxo.")
        return

    login(page, dados_usuario)

    tem_evento = verificar_evento_existente(page, evento_data)

    if tem_evento:
        logger.info(
            "Evento '{}' já existe. Nenhuma ação necessária.",
            evento_data.get("nome"),
        )
        logger.success("Finalizou teste Genesis para garantir Eventos com sucesso.")
        logout(page)
        return

    logger.info(
        "Evento '{}' não encontrado. Iniciando criação...",
        evento_data.get("nome"),
    )
    criar_evento(page=page, evento_data=evento_data)

    # Validação pós-criação no DOM
    validacao_pos = verificar_evento_existente(page, evento_data)

    assert validacao_pos is True, (
        f"Falha ao validar a criação do evento '{evento_data.get('nome')}' após o cadastro."
    )

    logger.success("Finalizou teste Genesis para garantir Eventos com sucesso.")
    logout(page)
