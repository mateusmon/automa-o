from loguru import logger
from playwright.sync_api import Page

from utils.erros_input import logar_erros_de_campos
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


# Referência para o dev: se este erro aparecer, o flow não rodou naquele cliente
# porque o perfil ainda restringe o status (o material fica preso em ANÁLISE). O
# flow do Genesis que garante o perfil sem restrições já cobre isso.
_MSG_STATUS_INVALIDO = (
    "Status do material indisponível/em ANÁLISE — o perfil do usuário ainda "
    "restringe o cadastro. Remova a restrição de 'CADASTRO MATERIAL EM ANÁLISE' "
    "da permissão de MATERIAL / SERVIÇO em Corporativo > Segurança > Perfil "
    "(ou rode o Genesis que garante o perfil)."
)

# Único erro que o teste pode dar skip
_MSG_MATERIAL_DUPLICADO = "já existe um material com essa descrição"


def confirmar_material(page: Page) -> bool:
    """
    Define o status "Ativo" e confirma o cadastro do material (form `bemser`,
    compartilhado por Consumo/Permanente/Serviço). É o flow final da sequência (faz o
    submit e valida o sucesso). Cenário A (escopo via `escopo(page)`).

    Retorna:
        True  -> cadastro confirmado com sucesso.
        False -> o material já existe (`_MSG_MATERIAL_DUPLICADO`); o teste deve dar skip.

    Levanta erro se o status estiver desabilitado ou preso em ANÁLISE — sinal de que
    o perfil do usuário ainda tem restrição (ver `_MSG_STATUS_INVALIDO`) — ou se o
    sistema exibir qualquer outro erro na confirmação.
    """
    logger.info("Iniciou confirmação de material.")

    ctx = escopo(page)

    status = ctx.locator("select[name='tdStatus']")
    if status.is_disabled():
        raise ValueError(_MSG_STATUS_INVALIDO)
    selecionado = status.locator("option:checked").inner_text().strip().upper()
    if "ANÁLISE" in selecionado or "ANALISE" in selecionado:
        raise ValueError(_MSG_STATUS_INVALIDO)

    status.select_option(value="01")  # Ativo

    ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)
    aguardar_ajax_global(page)

    alerta = ctx.locator("div[name='divErrorMsg']")
    if alerta.is_visible():
        erros = logar_erros_de_campos(ctx)

        if any(_MSG_MATERIAL_DUPLICADO in erro.casefold() for erro in erros):
            return False

        detalhe = "; ".join(erros) if erros else alerta.inner_text().strip()
        raise ValueError(f"Erro ao confirmar o cadastro do material: {detalhe}")

    try:
        esperar_sucesso_ou_erro(ctx)
    except Exception:
        logar_erros_de_campos(ctx)
        raise

    logger.info("Finalizou confirmação de material.")
    return True
