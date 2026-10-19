from loguru import logger
from playwright.sync_api import Page, expect

from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def preencher_dados_gerais_ua(page: Page, ua: dict, ug: dict) -> bool:
    """
    Preenche os dados gerais da UA, os responsáveis e confirma o cadastro.

    Cenário A: os mesmos seletores valem para v3 e v4; a única diferença é o
    escopo (page na v3, iframe na v4), resolvido por `escopo(page)`.

    Ordem obrigatória confirmada ao vivo: a U.G. precisa ser informada **antes**
    de abrir a aba "Responsáveis" — caso contrário o sistema exibe o alerta
    "É necessário informar primeiro uma U.G.!" e não abre a aba.

    A sigla (chave única) vem do blueprint (`unidade_administrativa_cr`) por ser
    o registro `_cr` usado pelos futuros testes de Consulta/Alteração/Exclusão —
    portanto NÃO é gerada dinamicamente. O registro deve ser removido ao final da
    validação para permitir reexecução.

    :param ua: dict do blueprint com sigla, nome e responsavel{nome, funcao}.
    :param ug: dict da U.G. do cliente (contexto_cliente.ug()); usa a sigla.
    """
    logger.info("Iniciou preenchimento de dados gerais de UA: '{}'.", ua["sigla"])

    ctx = escopo(page)

    # Garante que o formulário (dentro do iframe na v4) terminou de carregar.
    aguardar_ajax_global(page)
    ctx.locator("input[name='sgUa']").wait_for(state="visible")

    responsavel = ua["responsavel"]

    # --- Dados Gerais - preenchendo código de UA caso necessário
    campo_codigo = ctx.locator("input[name='cdUa']")
    digitos = int(campo_codigo.get_attribute("maxlength")) if campo_codigo.is_enabled() else 4

    if campo_codigo.is_enabled():
        codigo = gerar_numero_com_digitos(digitos)
        logger.info("Preenchendo campo de Código da UA: '{}'.", codigo)
        campo_codigo.fill(f"{codigo}")

    logger.info("Preenchendo campo de Sigla UA: '{}'.", ua["sigla"])
    ctx.locator("input[name='sgUa']").fill(ua["sigla"])
    logger.info("Preenchendo campo de Nome da UA: '{}'.", ua["nome"])
    ctx.locator("input[name='nmUa']").fill(ua["nome"])
    campo_ug = ctx.locator("input[name='ug']")
    if campo_ug.is_enabled():
        preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    # --- Responsáveis (só abre depois da U.G. preenchida) ---
    btn_tab = ctx.locator("button[name='submitTabResponsaveis']")
    clicar_com_ajax(ctx, btn_tab)
    aguardar_ajax_global(page)
    tabela_responsaveis = ctx.locator("table.tabela:has-text('Responsável da U.A.')")

    try:
        expect(tabela_responsaveis).to_be_visible(timeout=3000)
    except AssertionError:
        try:
            esperar_sucesso_ou_erro(ctx, timeout=3000)
        except RuntimeError as e:
            mensagem_erro = str(e).lower()
            termos_skip = [
                "mesmo nome",
                "já existe uma ua",
                "sigla já cadastrada",
                "informar primeiro uma u.g.",
            ]
            if any(termo in mensagem_erro for termo in termos_skip):
                logger.warning(f"Cadastro abortado por regra de negócio: {e}")
                return False
            raise
        raise

    preencher_campo(ctx, "input[name='funcionario-1-2']", responsavel["nome"])
    preencher_campo(ctx, "input[name='tipoFuncao-1-3']", responsavel["funcao"])
    ctx.locator("input[name='hierarquia-1-5']").check()

    btn_finish = ctx.locator("button[name='submitFinish']")
    clicar_com_ajax(ctx, btn_finish)

    tentativa = 0
    while True and campo_codigo.is_visible():
        tentativa += 1

        if campo_codigo.is_enabled():
            codigo = gerar_numero_com_digitos(digitos)
            campo_codigo.fill(f"{codigo}")

        clicar_com_ajax(ctx, btn_finish)

        try:
            esperar_sucesso_ou_erro(ctx)
            logger.info(
                f"U.A. cadastrada com sucesso na tentativa {tentativa}! Código utilizado: '{codigo}'"
            )
            break
        except RuntimeError as e:
            mensagem_erro = str(e).lower()
            termos_codigo_existente = [
                "já foi cadastrado",
                "código informado",
                "já existe",
            ]
            termos_skip = ["mesmo nome", "sigla já cadastrada"]

            if any(termo in mensagem_erro for termo in termos_codigo_existente):
                if tentativa >= 3:
                    raise
                logger.warning(
                    f"Tentativa {tentativa}: Código '{codigo}' já cadastrado para esta U.A. Gerando novo código..."
                )
                btn_fechar = page.get_by_role("button", name="Fechar")
                if btn_fechar.is_visible():
                    btn_fechar.click()
                    aguardar_ajax_global(page)
            elif any(termo in mensagem_erro for termo in termos_skip):
                logger.warning(f"Cadastro abortado por regra de negócio: {e}")
                return False
            else:
                raise

    logger.info("Finalizou preenchimento de dados gerais de UA: '{}'.", ua["sigla"])
    return True
