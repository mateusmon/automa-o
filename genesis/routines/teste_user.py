from loguru import logger

from utils.login_gen import login

from engine.execution_context import ExecutionContext
from engine.execution_step import executar_etapa
from flows.garantir_almoxarifados_flow import garantir_almoxarifados
from flows.garantir_fornecedores_flow import garantir_fornecedores
from flows.garantir_orgao_externo_flow import garantir_orgao_externo
from flows.garantir_um_flow import garantir_um
from flows.garantir_grupos_subgrupos_flow import garantir_subgrupos
from flows.garantir_materiais_flow import garantir_materiais
from flows.garantir_endereco_material_flow import garantir_endereco_material
from flows.garantir_enderecamentos_flow import garantir_enderecamentos
from flows.garantir_uls_flow import garantir_uls
from flows.garantir_catalogos_flow import garantir_catalogos
from flows.garantir_bens_flow import garantir_bens
from flows.garantir_caracteristica_flow import garantir_caracteristica
from flows.garantir_evento_flow import garantir_evento



def run(context: ExecutionContext) -> None:
    """
    Executes provisioning routine as Teste user.

    Responsibilities:
        - Perform login
        - Execute ordered flows
    """

    logger.info("Iniciando rotina do usuário Teste.")

    executar_etapa(context, _login, "login_teste")

    flows = (
        garantir_almoxarifados,
        garantir_fornecedores,
        garantir_orgao_externo,
        garantir_um,
        garantir_subgrupos,
        garantir_materiais,
        garantir_endereco_material,
        garantir_enderecamentos,
        garantir_uls,
        garantir_catalogos,
        garantir_bens,
        garantir_caracteristica,
        garantir_evento,
    )

    for flow in flows:
        executar_etapa(context, flow)

    executar_etapa(context, _logout, "logout_teste")

    logger.info("Rotina do usuário Teste finalizada.")


def _login(context: ExecutionContext) -> None:
    """
    Performs login using runtime configuration.

    Fails fast if authentication is unsuccessful after retries.
    """
    # O usuário 'teste' é o mesmo que a suíte usa (o conftest pega o primeiro de
    # 'usuarios'), então a massa provisionada aqui nasce com o dono que os testes
    # esperam. A r64853 havia trocado para 'link' junto com um conserto de login;
    # com o login corrigido, o 'teste' entra normalmente e a troca foi revertida.
    login(context.browser_manager.page, context.runtime_config, chave_usuario="teste")


def _logout(context: ExecutionContext) -> None:
    page = context.browser_manager.page
    if context.runtime_config.get("versao") == 4:
        page.click("button[title='Sair'].btn-toolbar")
        return
    page.click("#appLogout")
