from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.seguranca.cadastro_usuario.consultar_usuario_flow import consultar_usuario
from flows.genesis.perfil.consultar_perfis_usuario_flow import consultar_perfis_do_usuario
from flows.genesis.shared.obter_usuario_logado_flow import obter_nome_usuario_logado
from flows.genesis.usuario.navegar_para_perfil_flow import acessar_perfil
from flows.genesis.usuario.navegar_para_usuario_flow import acessar_usuario
from flows.genesis.usuario.preencher_dados_gerais_usuario_flow import preencher_dados_gerais_usuario
from flows.genesis.usuario.preencher_sistemas_usuario_flow import preencher_sistemas_usuario
from flows.genesis.usuario.sistemas_usuario import montar_sistemas_usuario
from flows.genesis.usuario.verificar_usuario_existente_flow import verificar_usuario_existente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_usuarios(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante os Usuários do blueprint com os Perfis derivados do Link autenticado."""
    logger.info("Iniciou teste Genesis para garantir Usuários.")
    usuarios = contexto_cliente.usuarios()
    if not usuarios:
        logger.info("Finalizou sem criação: nenhum usuário definido no blueprint.")
        return
    prefixo = contexto_cliente.prefixo_perfil(obrigatorio=False)
    if not prefixo:
        logger.info("Finalizou sem criação: nenhum 'prefixo_perfil' definido no blueprint.")
        return

    dados_link = contexto_cliente.dados_usuario("link")
    login(page, dados_link)
    nome_usuario = obter_nome_usuario_logado(page)
    if not acessar_perfil(page):
        logger.warning("Menu 'Perfil' não disponível; sem perfis para vincular.")
        logout(page)
        logger.info("Finalizou teste Genesis sem criação de Usuários.")
        return
    perfis = consultar_perfis_do_usuario(page, nome_usuario)
    sistemas = montar_sistemas_usuario(perfis, prefixo, nome_usuario)
    logger.info("{} perfil(is) serão vinculados a cada usuário.", len(sistemas))
    if not acessar_usuario(page):
        logger.warning("Menu 'Usuário' não disponível; pulando fluxo de usuários.")
        logout(page)
        logger.info("Finalizou teste Genesis sem criação de Usuários.")
        return

    for atual, usuario in enumerate(usuarios, start=1):
        nome = usuario["nome"]
        logger.info("Garantindo Usuário {}/{}: '{}'.", atual, len(usuarios), nome)
        existe = False
        if acessar_usuario(page) and consultar_usuario(page, usuario):
            existe = verificar_usuario_existente(page, nome)
        if existe:
            logger.info("Usuário '{}' já existe. Nenhuma criação necessária.", nome)
            continue

        if acessar_usuario(page):
            preencher_dados_gerais_usuario(page, usuario)
            preencher_sistemas_usuario(page, sistemas)
        else:
            logger.warning("Menu 'Usuário' não disponível. Impossível criar usuário.")

        existe = False
        if acessar_usuario(page) and consultar_usuario(page, usuario):
            existe = verificar_usuario_existente(page, nome)
        if not existe:
            raise RuntimeError(f"Falha ao validar criação do usuário '{nome}'.")
        logger.success("Usuário '{}' criado com sucesso.", nome)

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Usuários.")
