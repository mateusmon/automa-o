from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.seguranca.cadastro_perfil.consultar_perfil_flow import (
    consultar_perfil,
)
from flows.genesis.usuario.navegar_para_perfil_flow import (
    acessar_perfil,
)
from flows.genesis.perfil.consultar_perfis_usuario_flow import (
    consultar_perfis_do_usuario,
)
from flows.genesis.perfil.copiar_perfil_flow import copiar_perfil
from flows.genesis.shared.obter_usuario_logado_flow import (
    obter_nome_usuario_logado,
)
from flows.genesis.shared.perfis_origem import (
    derivar_nome_perfil,
    selecionar_perfis_origem,
)
from flows.genesis.shared.selecionar_registro_exato_flow import (
    selecionar_registro_exato,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_perfis(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante uma cópia de Perfil por Sistema disponível ao usuário Link."""
    logger.info("Iniciou teste Genesis para garantir Perfis.")

    prefixo = contexto_cliente.prefixo_perfil(obrigatorio=False)
    if not prefixo:
        logger.info("Finalizou sem criação: nenhum 'prefixo_perfil' definido no blueprint.")
        return

    dados_link = contexto_cliente.dados_usuario("link")

    login(page, dados_link)
    nome_usuario = obter_nome_usuario_logado(page)
    if not acessar_perfil(page):
        logger.warning("Menu 'Perfil' não disponível; pulando fluxo de perfis.")
        logout(page)
        logger.info("Finalizou teste Genesis sem criação de Perfis.")
        return
    perfis = consultar_perfis_do_usuario(page, nome_usuario)
    origens = selecionar_perfis_origem(perfis, prefixo)
    total = len(origens)

    for atual, origem in enumerate(origens, start=1):
        nome_perfil = derivar_nome_perfil(prefixo, origem["sistema"])
        perfil_destino = {"nome": nome_perfil}
        logger.info(
            "Garantindo Perfil {}/{}: '{}' a partir de '{}'.",
            atual,
            total,
            nome_perfil,
            origem["nome"],
        )

        existe = False
        if acessar_perfil(page):
            consultar_perfil(page, perfil_destino)
            existe = selecionar_registro_exato(page, nome_perfil)
        if existe:
            logger.info("Perfil '{}' já existe; nenhuma criação necessária.", nome_perfil)
            continue

        if not acessar_perfil(page):
            logger.warning("Menu 'Perfil' não disponível. Impossível criar perfil.")
            continue
        if not copiar_perfil(page, nome_usuario, origem, nome_perfil):
            logger.warning(
                "Perfil de origem '{}' sem módulos; Sistema '{}' ignorado.",
                origem["nome"],
                origem["sistema"],
            )
            continue

        existe = False
        if acessar_perfil(page):
            consultar_perfil(page, perfil_destino)
            existe = selecionar_registro_exato(page, nome_perfil)
        assert existe, (
            f"Perfil '{nome_perfil}' não encontrado após a cópia."
        )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Perfis.")
