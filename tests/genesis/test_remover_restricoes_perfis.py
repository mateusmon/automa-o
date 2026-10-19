from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.genesis.perfil.consultar_perfis_por_usuario_flow import (
    consultar_perfis_por_usuario,
)
from flows.genesis.perfil.contar_perfis_consultados_flow import (
    contar_perfis_consultados,
)
from flows.genesis.perfil.remover_restricoes_perfil_flow import (
    remover_restricoes_perfil,
)
from flows.genesis.usuario.navegar_para_perfil_flow import acessar_perfil
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_remover_restricoes_perfis(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Remove as restrições de funcionalidades de todos os Perfis do primeiro usuário do blueprint."""
    logger.info("Iniciou teste Genesis para remover restrições dos perfis.")

    usuarios = contexto_cliente.usuarios()

    if not usuarios:
        logger.info("Nenhum usuário definido no blueprint. Ignorando teste.")
        return

    # Todos os usuários do blueprint compartilham os mesmos perfis; o legado filtra pelo primeiro.
    nome_usuario = usuarios[0]["nome"]
    dados_link = contexto_cliente.dados_usuario("link")

    login(page, dados_link)
    acessar_perfil(page)
    consultar_perfis_por_usuario(page, nome_usuario)

    total = contar_perfis_consultados(page)
    assert total > 0, "Falha ao remover restrições de perfis."

    for indice in range(total):
        remover_restricoes_perfil(page, indice, total)
        consultar_perfis_por_usuario(page, nome_usuario)

    logout(page)
    logger.success("Finalizou teste Genesis para remover restrições dos perfis.")
