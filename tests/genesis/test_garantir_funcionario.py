from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.corporativo.funcionario.cadastro_funcionario.consultar_funcionario_flow import (
    consultar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.navegar_para_funcionario_flow import (
    acessar_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.preencher_dados_gerais_funcionario_flow import (
    preencher_dados_gerais_funcionario,
)
from flows.corporativo.funcionario.cadastro_funcionario.verificar_funcionario_existente_flow import (
    verificar_funcionario_existente,
)
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_funcionarios(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante que os Funcionários da massa-base existam, criando somente os ausentes."""
    logger.info("Iniciou teste Genesis para garantir Funcionários.")

    funcionarios = contexto_cliente.funcionarios()

    if not funcionarios:
        logger.info("Nenhum funcionário definido no blueprint. Ignorando teste.")
        return

    dados_link = contexto_cliente.dados_usuario("link")
    login(page, dados_link)
    acessar_funcionario(page)

    total = len(funcionarios)
    logger.info("Foi encontrado um total de {} funcionários no blueprint.", total)

    for atual, funcionario in enumerate(funcionarios, start=1):
        matricula = funcionario["matricula"]
        cpf_formatado = _formatar_cpf(matricula)

        logger.info("Funcionário {}/{}: matrícula '{}'.", atual, total, matricula)

        consultar_funcionario(page, funcionario)

        if verificar_funcionario_existente(page, cpf_formatado):
            logger.info("Funcionário '{}' já existe. Nenhuma ação necessária.", matricula)
            continue

        preencher_dados_gerais_funcionario(page, funcionario)

        acessar_funcionario(page)
        consultar_funcionario(page, funcionario)
        assert verificar_funcionario_existente(page, cpf_formatado), (
            f"Funcionário '{matricula}' não foi encontrado após o cadastro."
        )

        logger.success("Funcionário '{}' criado com sucesso.", matricula)

    logout(page)
    logger.success("Finalizou teste Genesis para garantir Funcionários.")


def _formatar_cpf(matricula: str) -> str:
    """Deriva o CPF (identidade usada na consulta e na comparação) a partir da matrícula."""
    return f"{matricula[:3]}.{matricula[3:6]}.{matricula[6:9]}-{matricula[9:]}"
