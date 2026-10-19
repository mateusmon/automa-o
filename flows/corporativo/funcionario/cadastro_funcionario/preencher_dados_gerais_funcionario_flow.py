from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_funcionario(page: Page, funcionario: dict) -> None:
    """
    Preenche o Funcionário e confirma. Cenário A (só muda o escopo via `escopo(page)`).

    Obrigatórios: Matrícula (`cdFuncionario`) e Nome (`nmRegistroCivil`); o Órgão é
    pré-preenchido (varia por cliente). CPF, U.A. e e-mail são opcionais, mas
    preenchidos para um cadastro completo. O CPF é derivado da matrícula (que é um
    CPF válido de 11 dígitos), formatado. A U.A. usa o botão de lookup `lookup-ccdUa`
    e referencia a U.A. padrão (`sigla_ua`), que deve estar provisionada no ambiente.

    :param funcionario: dict do blueprint (matricula, nome, email, sigla_ua).
    """
    logger.info(
        "Iniciou preenchimento de dados gerais de Funcionário '{}'.",
        funcionario["matricula"],
    )

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='cdFuncionario']").wait_for(state="visible")

    matricula = funcionario["matricula"]
    cpf = f"{matricula[:3]}.{matricula[3:6]}.{matricula[6:9]}-{matricula[9:]}"

    logger.info("Preenchendo Matrícula de Funcionário: '{}'.", matricula)
    ctx.locator("input[name='cdFuncionario']").fill(matricula)
    preencher_campo(ctx, "input[name='cdUa']", "   ", lookup_name="lookup-ccdUa")
    logger.info("Preenchendo Nome de Funcionário: '{}'.", funcionario["nome"])
    ctx.locator("input[name='nmRegistroCivil']").fill(funcionario["nome"])
    logger.info("Preenchendo CPF de Funcionário: '{}'.", cpf)
    ctx.locator("input[name='nrCpf']").fill(cpf)
    logger.info("Preenchendo E-mail de Funcionário: '{}'.", funcionario["email"])
    ctx.locator("input[name='nmEmail']").fill(funcionario["email"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou preenchimento de dados gerais de Funcionário. Matrícula: '{}', Nome: '{}', CPF: '{}', E-mail: '{}'",
        funcionario["matricula"],
        funcionario["nome"],
        cpf,
        funcionario["email"],
    )
