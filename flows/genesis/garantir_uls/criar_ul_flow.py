from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.estrutura_organizacional.cadastro_ul.navegar_para_ul_flow import (
    acessar_ul,
)
from utils.erros_input import logar_erros_de_campos
from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def criar_ul(page: Page, uls_faltantes: list[dict[str, Any]]) -> None:
    """Fluxo para cadastro sequencial das ULs faltantes."""
    if not uls_faltantes:
        return

    logger.info(
        f"Iniciando criação de {len(uls_faltantes)} Unidade(s) de Localização..."
    )

    for ul in uls_faltantes:
        _preencher_formulario_ul(page, ul)

    logger.info("Criação de ULs concluída.")


def _preencher_formulario_ul(page: Page, ul_data: dict[str, Any]) -> None:
    acessar_ul(page)

    ctx = escopo(page)

    if ctx.locator("input[name='sgUl']").input_value() != "":
        ctx.locator("button[name='submitNew']").click()
        aguardar_ajax_global(page)

    sigla_ul = ul_data["sigla"]
    endereco_ul = ul_data["endereco"]
    ua_ul = ul_data["unidade_administrativa"]
    responsavel_ul = ul_data.get("responsavel", {})
    nome_responsavel_ul = responsavel_ul.get("nome", "")
    funcao_responsavel_ul = responsavel_ul.get("funcao", "")

    campo_codigo = ctx.locator("input[name='cdUl']")
    if campo_codigo.is_enabled():
        codigo = gerar_numero_com_digitos(digitos=4)
        ctx.locator("input[name='cdUl']").fill(f"{codigo}")

    field_sigla = ctx.locator("input[name='sgUl']")
    field_sigla.click()
    field_sigla.fill(sigla_ul)

    preencher_campo(ctx, "input[name='ua']", ua_ul)
    preencher_campo(ctx, "input[name='centroCusto']", ul_data["centro_custo"])

    field_endereco = ctx.locator("input[name='local']")
    field_endereco.click()
    field_endereco.fill(endereco_ul)
    ctx.locator("button[name='lookup-local']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitTabResponsaveis']").click()
    aguardar_ajax_global(page)

    tbody = ctx.locator("table.tabela tbody")
    tbody.wait_for(state="visible")

    preencher_campo(ctx, "input[name='hierarquia-1-2']", nome_responsavel_ul)
    preencher_campo(ctx, "input[name='tipoFuncao-1-3']", funcao_responsavel_ul)

    ctx.locator("input[name='hierarquia-1-5']").click()
    ctx.locator("button[name='submitFinish']").click()

    aguardar_ajax_global(page)
    tentativa = 0
    while True and campo_codigo.is_visible():
        tentativa += 1

        if campo_codigo.is_enabled():
            codigo = gerar_numero_com_digitos(digitos=4)
            campo_codigo.fill(f"{codigo}")

        ctx.locator("button[name='submitFinish']").click()
        aguardar_ajax_global(page)

        try:
            esperar_sucesso_ou_erro(ctx)
            logger.info(
                f"U.L. cadastrada com sucesso na tentativa {tentativa}!"
            )
            break  # Cadastro concluído com sucesso, encerra o loop
        except RuntimeError as e:
            msg_erro = str(e)
            if "já foi cadastrado" in msg_erro:
                if tentativa >= 3:
                    raise
                logger.warning(
                    f"Tentativa {tentativa}: Código já cadastrado para este Órgão. Gerando novo código..."
                )

                btn_fechar = page.get_by_role("button", name="Fechar")
                if btn_fechar.is_visible():
                    btn_fechar.click()
                    aguardar_ajax_global(page)
            else:
                logar_erros_de_campos(page)
                raise
