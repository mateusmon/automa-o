"""
Utilitário para inspecionar campos de formulário com erro de validação.

No sistema ASI, quando uma movimentação é finalizada com campos inválidos,
a página permanece na mesma tela e os campos problemáticos recebem as classes
CSS `tdError` e `inputError`. O atributo `title` de cada campo indica
a mensagem de erro correspondente.

Este módulo coleta essas mensagens para facilitar o diagnóstico de falhas.

--- Onde usar ---

Use este módulo nos flows de finalização, dentro do bloco except, logo antes
de re-lançar a exceção:

    try:
        esperar_sucesso_ou_erro(page)
    except RuntimeError:
        logar_erros_de_campos(page)
        raise

--- Onde NÃO usar ---

Não use este módulo dentro de `evidencia.py`.

Pode parecer tentador centralizá-lo lá, já que o hook `pytest_runtest_makereport`
do conftest.py já aciona o evidencia.py automaticamente em caso de falha.
Mas isso exigiria que evidencia.py importasse field_errors.py, misturando
responsabilidades: evidencia.py lida com capturas de tela e PDFs — não com
validação de campos de formulário.

Também não registre a `page` como estado global neste módulo (no estilo do
`evidencia.set_page`) para tentar chamá-lo direto do hook do pytest. O hook
opera fora do ciclo de vida dos fixtures e conectar os dois exige estado global
implícito. O evidencia.py já faz isso por necessidade — não vale replicar
o padrão sem necessidade.

O flow de finalização tem a `page` disponível no momento exato da falha,
sem precisar de nenhum desses artifícios.
"""

from loguru import logger
from playwright.sync_api import Page, Frame


def coletar_erros_de_campos(page: Page | Frame) -> list[str]:
    """
    Coleta as mensagens de erro de todos os campos inválidos visíveis na página.

    Percorre todos os inputs que possuem as classes `tdError` e `inputError`
    e retorna os valores do atributo `title` de cada um.

    :param page: Objeto de página do Playwright
    :type page: Page
    :return: Lista de mensagens de erro encontradas (sem duplicatas, sem vazios)
    :rtype: list[str]
    """
    erros = page.eval_on_selector_all(
        "input.tdError.inputError",
        """
        elements => elements
            .map(el => el.getAttribute('title') || '')
            .filter(title => title.trim() !== '')
        """
    )

    # Remove duplicatas preservando a ordem
    vistos = set()
    erros_unicos = []
    for erro in erros:
        if erro not in vistos:
            vistos.add(erro)
            erros_unicos.append(erro)

    return erros_unicos


def logar_erros_de_campos(page: Page | Frame) -> list[str]:
    """
    Coleta e loga as mensagens de erro dos campos inválidos.

    Útil para registrar automaticamente os erros de validação nos logs
    antes de lançar uma exceção ou encerrar um flow.

    :param page: Objeto de página do Playwright
    :type page: Page
    :return: Lista de mensagens de erro encontradas
    :rtype: list[str]
    """
    erros = coletar_erros_de_campos(page)

    if erros:
        logger.warning("Campos com erro de validação encontrados:")
        for erro in erros:
            logger.warning("  • {}", erro)
    else:
        logger.debug("Nenhum campo com erro de validação encontrado.")

    return erros


def assert_sem_erros_de_campos(page: Page) -> None:
    """
    Verifica que não há campos com erro de validação na página.

    Lança uma exceção detalhada caso existam campos inválidos,
    listando todas as mensagens de erro encontradas.

    :param page: Objeto de página do Playwright
    :type page: Page
    :raises AssertionError: Se houver ao menos um campo com erro de validação
    """
    erros = coletar_erros_de_campos(page)

    if erros:
        mensagens = "\n  • ".join(erros)
        raise AssertionError(
            f"Formulário contém {len(erros)} campo(s) com erro de validação:\n"
            f"  • {mensagens}"
        )
