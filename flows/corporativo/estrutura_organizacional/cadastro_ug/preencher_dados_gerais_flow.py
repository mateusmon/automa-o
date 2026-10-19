from loguru import logger
from playwright.sync_api import Page

from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, ug: dict) -> None:
    """
    Preenche os dados gerais da UG e confirma o cadastro.

    Os valores vêm do blueprint (`unidade_gestora_cr`) via `contexto_cliente`.
    O código da UG é a chave única: quando o blueprint o deixa vazio (padrão do
    `_cr`), é gerado a cada execução — um valor fixo causaria "código já
    cadastrado" na segunda execução.

    :param ug: dict com codigo, nome, sigla, cidade e administracao_direta.
    """
    logger.info("Iniciou preenchimento de dados gerais de UG - Unidade Gestora: '{}'.", ug["codigo"])

    ctx = escopo(page)

    # Garante que o formulário (dentro do iframe na v4) terminou de carregar.
    aguardar_ajax_global(page)
    ctx.locator("input[name='cdUg']").wait_for(state="visible")

    codigo = ug.get("codigo") or gerar_numero_com_digitos(6)
    adm_direta = "S" if ug["administracao_direta"] == "sim" else "N"

    # Órgão (cdOrgao) já vem preenchido e desabilitado — não é preenchido aqui.
    ctx.locator("input[name='cdUg']").fill(codigo)
    logger.info("Preenchendo campo de Nome da UG - Unidade Gestora: '{}'.", ug["nome"])
    ctx.locator("input[name='nmUg']").fill(ug["nome"])
    logger.info("Preenchendo campo de Sigla da UG - Unidade Gestora: '{}'.", ug["sigla"])
    ctx.locator("input[name='sgUg']").fill(ug["sigla"])

    # Cidade é campo de lookup; ao selecionar, a U.F. é preenchida automaticamente.
    escolher_cidade(ctx, ug["cidade"])

    ctx.locator(f"input[name='inAdmDireta'][value='{adm_direta}']").check()

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de UG - Unidade Gestora: '{}'.", ug["codigo"])
