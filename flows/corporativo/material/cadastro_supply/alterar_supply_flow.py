from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_supply(page: Page) -> None:
    """
    Altera o Nome do subgrupo carregado do Supply e confirma UMA vez (sem desfazer).

    ⚠️ O campo é o **`grupoDsExemplo`**, não o `subgrupoDsExemplo` — apesar do nome. Os campos
    `grupo*` do form são genéricos: recebem **o nó carregado da árvore**, seja ele grupo ou
    subgrupo (confirmado ao vivo — ao carregar o subgrupo 10099, `grupoCdExemplo`='10099' e
    `grupoDsExemplo`='SUBGRUPO CR', enquanto os campos `subgrupo*`/`material*` ficam vazios e
    desabilitados). O `grupoDsExemplo` é o único habilitado e não tem `maxlength`.

    Convenção vigente: uma única confirmação (sem desfazer) e alteração do Nome por ADIÇÃO de
    sufixo (" ALT"/" TLA"). É seguro renomear porque a Consulta do Supply filtra pelo **código**
    do subgrupo (`subgrupo_codigo`), não pelo nome, e a Exclusão localiza o nó pelo ícone da
    árvore e o grupo pelo texto `grupo_codigo - grupo_nome` (que não é tocado aqui).
    Não mexe em checkbox/radio.

    Cenário A. Pressupõe que o subgrupo já foi carregado (ver `consultar_subgrupo_supply`).
    """
    logger.info("Iniciou alteração de Supply.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='grupoDsExemplo']")
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Supply.")
