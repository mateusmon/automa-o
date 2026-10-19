from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcionario.associar_ua_funcionario_flow import (
    associar_ua_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.consultar_funcionario_flow import (
    consultar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.navegar_para_funcionario_flow import (
    acessar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.verificar_associacao_ua_existente_flow import (
    verificar_associacao_ua_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_associacao_funcionarios_ua(
    page: Page, contexto_cliente: ContextoCliente
) -> None:
    """Garante que cada Funcionário da massa-base esteja associado à U.A., criando só as ausentes."""
    logger.info("Iniciou teste Genesis para garantir associação Funcionário/UA.")

    funcionarios = contexto_cliente.funcionarios()

    if not funcionarios:
        logger.info("Nenhum funcionário definido no blueprint. Ignorando teste.")
        return

    dados_link = contexto_cliente.dados_usuario("link")
    ua = contexto_cliente.ua()

    login(page, dados_link)

    total = len(funcionarios)
    logger.info("Foi encontrado um total de {} funcionários no blueprint.", total)

    for atual, funcionario in enumerate(funcionarios, start=1):
        matricula = funcionario["matricula"]

        logger.info(
            "Funcionário {}/{}: matrícula '{}', U.A. '{}'.",
            atual, total, matricula, ua["sigla"],
        )

        acessar_funcionario(page)
        consultar_funcionario(page, funcionario)

        if verificar_associacao_ua_existente(page):
            logger.info(
                "Associação entre funcionário '{}' e U.A. '{}' já existe. Nenhuma ação necessária.",
                matricula, ua["sigla"],
            )
            continue

        acessar_funcionario(page)
        consultar_funcionario(page, funcionario)
        associar_ua_funcionario(page, ua)

        acessar_funcionario(page)
        consultar_funcionario(page, funcionario)
        assert verificar_associacao_ua_existente(page), (
            f"Associação entre funcionário '{matricula}' e U.A. '{ua['sigla']}' "
            "não foi encontrada após o cadastro."
        )

        logger.success(
            "Associação entre funcionário '{}' e U.A. '{}' feita com sucesso.",
            matricula, ua["sigla"],
        )

    logout(page)
    logger.success("Finalizou teste Genesis para garantir associação Funcionário/UA.")
