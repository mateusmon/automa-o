import random

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, esperar_sucesso_ou_erro


def alterar_calendario(page: Page) -> bool:
    "Retorna False se o campo de escrita estiver desabilitado."

    logger.info("Iniciou alteração de calendário de requisição.")

    ctx = escopo(page)
    td = ctx.locator("table.tabela tbody[name='tboItens'] tr").first.locator("td").count()

    if td == 2:
        resultado = _alterar_calendario_duas_colunas(ctx)
    else:
        resultado = _alterar_calendario_tres_colunas(ctx)

    logger.info("Finalizou alteração de calendário de requisição.")
    return resultado


def _alterar_calendario_tres_colunas(ctx) -> bool:
    "Retorna False se o campo de escrita estiver desabilitado."

    num = random.randint(1, 10)
    campos = ctx.locator("table.tabela tbody tr").first.locator("input[type='text']").all()

    if any(campo.is_disabled() for campo in campos):
        logger.info("Campo de escrita desabilitado.")
        return False

    for campo in campos:
        campo.fill(str(num))

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    esperar_sucesso_ou_erro(ctx)

    return True


def _alterar_calendario_duas_colunas(ctx) -> bool:
    "Retorna False se todos os campos estiverem desabilitados."

    campos = ctx.locator("table.tabela tbody tr input[type='text']").all()

    valores_usados = set()
    campos_habilitados = []
    for campo in campos:
        valor = campo.input_value().strip()
        if valor:
            valores_usados.add(int(valor))
        if not campo.is_disabled():
            campos_habilitados.append((campo, valor))

    if not campos_habilitados:
        logger.info("Nenhum campo de escrita habilitado.")
        return False

    campo, valor_atual_str = random.choice(campos_habilitados)
    valor_atual = int(valor_atual_str)

    numeros_disponiveis = [
        numero
        for numero in range(1, 28)
        if numero not in valores_usados and numero != valor_atual
    ]
    novo_valor = random.choice(numeros_disponiveis)
    campo.fill(str(novo_valor))

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    esperar_sucesso_ou_erro(ctx)

    return True