from loguru import logger
from playwright.sync_api import Page

from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_ul(page: Page, ul: dict) -> None:
    """
    Preenche os dados da UL, o responsável e confirma o cadastro.

    Cenário A: os mesmos seletores valem para v3 e v4; a única diferença é o
    escopo (page na v3, iframe na v4), resolvido por `escopo(page)`.

    Campos obrigatórios (confirmados ao vivo): Sigla (`sgUl`), U.A. (`ua`),
    C.C. (`centroCusto`) e Endereço (`local`). O código da UL é gerado pelo
    sistema. A U.G. é preenchida automaticamente a partir da U.A.

    A chave única da UL é (U.A., Endereço); o `unidade_localizacao_cr` usa um
    endereço dedicado (não usado por nenhuma UL) para não colidir com as ULs
    padrão. O registro deve ser removido ao final da validação.

    :param ul: dict do blueprint com sigla, unidade_administrativa, centro_custo,
        endereco e responsavel{nome, funcao}.
    """
    logger.info("Iniciou preenchimento de dados gerais de UL: '{}'.", ul["sigla"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='sgUl']").wait_for(state="visible")

    responsavel = ul["responsavel"]

    # --- Dados Gerais ---
    campo_codigo = ctx.locator("input[name='cdUl']")

    if campo_codigo.is_enabled():
        codigo = gerar_numero_com_digitos(4)
        logger.info("Preenchendo campo de Código da UL: '{}'.", codigo)
        campo_codigo.fill(f"{codigo}")

    logger.info("Preenchendo campos de Sigla, U.A., C.C. e Endereço da UL: '{}'.", ul["sigla"])
    ctx.locator("input[name='sgUl']").fill(ul["sigla"])
    preencher_campo(ctx, "input[name='ua']", ul["unidade_administrativa"])
    try:
        preencher_campo(ctx, "input[name='centroCusto']", ul["centro_custo"])
    except Exception:
        logger.warning(
            "Não foi possível selecionar o Centro de Custo '{}'. "
            "Cancelando a seleção e tentando o primeiro disponível.",
            ul["centro_custo"],
        )
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        preencher_campo(ctx, "input[name='centroCusto']", "   ")
    preencher_campo(ctx, "input[name='local']", ul["endereco"])

    # --- Responsáveis ---
    ctx.locator("button[name='submitTabResponsaveis']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='hierarquia-1-2']", responsavel["nome"])
    preencher_campo(ctx, "input[name='tipoFuncao-1-3']", responsavel["funcao"])
    ctx.locator("input[name='hierarquia-1-5']").check()

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de UL: '{}'.", ul["sigla"])
