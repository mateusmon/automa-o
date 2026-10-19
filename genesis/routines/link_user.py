from engine.execution_context import ExecutionContext
from engine.execution_step import executar_etapa
from flows.garantir_associacao_funcionarios_ua_flow import (
    garantir_associacao_funcionarios_ua,
)
from flows.garantir_centro_custo_flow import garantir_centro_custo
from flows.garantir_cidade_flow import garantir_cidade
from flows.garantir_enderecos_flow import garantir_enderecos
from flows.garantir_funcao_flow import garantir_funcao
from flows.garantir_funcionarios_flow import garantir_funcionarios
from flows.garantir_instalacao_flow import garantir_instalacao
from flows.garantir_perfis_flow import garantir_perfis
from flows.garantir_ua_flow import garantir_ua
from flows.garantir_urs_flow import garantir_urs
from flows.garantir_usuarios_flow import garantir_usuarios
from flows.remover_restricoes_perfis_flow import remover_restricoes_perfis
from loguru import logger
from utils.login_gen import login


def run(context: ExecutionContext) -> None:
    """
    Executes provisioning routine as Link user.

    Responsibilities:
        - Perform login
        - Execute ordered flows
    """

    logger.info("Iniciando rotina do usuário Link.")

    executar_etapa(context, _login, "login_link")

    flows = (
        garantir_cidade,
        garantir_funcionarios,
        garantir_funcao,
        garantir_centro_custo,
        garantir_ua,
        garantir_associacao_funcionarios_ua,
        garantir_instalacao,
        garantir_enderecos,
        garantir_urs,
        garantir_perfis,
        garantir_usuarios,
        remover_restricoes_perfis,
    )

    for flow in flows:
        executar_etapa(context, flow)

    executar_etapa(context, _logout, "logout_link")

    logger.info("Rotina do usuário da Link finalizada.")


def _login(context: ExecutionContext) -> None:
    """
    Performs login using runtime configuration.

    Fails fast if authentication is unsuccessful after retries.
    """
    login(context.browser_manager.page, context.runtime_config, chave_usuario="link")


def _logout(context: ExecutionContext) -> None:
    page = context.browser_manager.page
    if context.runtime_config.get("versao") == 4:
        page.click("button[title='Sair'].btn-toolbar")
        return
    page.click("#appLogout")
