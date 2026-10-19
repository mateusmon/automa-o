from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_pais(page: Page) -> None:
    """
    Altera o Nome do País (`nmPais`) e confirma UMA vez (sem desfazer).

    Confirma só uma vez porque, ao salvar, algumas telas recarregam e limpam os dados
    (como se fossem cadastrar uma nova entidade), o que impediria reabrir o registro para
    desfazer. A alteração é sempre uma ADIÇÃO ao Nome (sufixo alternando " ALT"/" TLA"),
    então a Consulta pelo nome-base continua localizando o registro e o teste é
    re-executável sem o nome crescer. Não mexe em checkbox/radio (evita disparar campos
    obrigatórios extras).

    Cenário A. Pressupõe que o registro já foi carregado (ver `selecionar_pais`).
    """
    logger.info("Iniciou alteração de País.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmPais']")
    logger.info("Alterando o Nome do País: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de País.")
