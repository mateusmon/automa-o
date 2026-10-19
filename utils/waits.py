import re
import time
import unicodedata
from datetime import datetime

from loguru import logger
from playwright.sync_api import Frame, Locator, Page, TimeoutError, expect

from utils.erros_input import logar_erros_de_campos


# ---------------------------------------------------------
# Espera de ajax global (similar ao método do
# último projeto de automação)
# ---------------------------------------------------------
def aguardar_ajax_global(page: Page | Frame | None, timeout=120_000):
    """
    Aguarda a animação do ajax começar e depois parar.

    Esta função é ideal para esperar que uma página carregue completamente.
    """
    if page is None or isinstance(page, Frame):
        logger.warning("'page' é Frame ou None. Pulando carregamento ajax.")
        return

    try:
        page.wait_for_selector(
            "#ajaxStatusLoadingBackground",
            state="visible",
            timeout=700,  # esperar pouco até aparecer
        )
        apareceu = True
    except Exception:
        # ajaxStatusLoadingBackground nunca apareceu — OK, não houve ajax
        apareceu = False

    if apareceu:
        try:
            page.wait_for_selector(
                "#ajaxStatusLoadingBackground",
                state="hidden",
                timeout=timeout,
            )
        except Exception:
            # O overlay subiu e não desceu dentro do teto. Este caso era engolido
            # junto com o de cima: a espera queimava o timeout inteiro em silêncio
            # e o teste quebrava depois, em outro ponto, sem relação aparente.
            # O comportamento continua o mesmo (seguir em frente); o que muda é
            # que agora fica registrado.
            logger.warning(
                "O overlay de ajax apareceu e não sumiu em {}ms. Seguindo mesmo assim.",
                timeout,
            )

    _verificar_erro_java(page)


def _verificar_erro_java(page: Page) -> None:
    # v3: erro renderizado diretamente na page
    titulos = page.locator("h1, h2, h3, h4, h5, h6")
    erro_java = titulos.filter(has_text="Ops!").is_visible()
    if (
        erro_java
        or titulos.filter(has_text="HTTP Status 500").is_visible()
        or page.get_by_text("404 - Not Found", exact=True).is_visible()
    ):
        mensagem = "ERRO JAVA!" if erro_java else "ERRO!"
        logger.error(mensagem)
        raise RuntimeError(f"{mensagem} Verifique manualmente!")

    # v4: erro renderizado dentro do frame
    frame = page.frame(name="iframe-context")
    if frame is not None:
        titulos = frame.locator("h1, h2, h3, h4, h5, h6")
        erro_java = titulos.filter(has_text="Ops!").is_visible()
        if (
            erro_java
            or titulos.filter(has_text="HTTP Status 500").is_visible()
            or frame.get_by_text("404 - Not Found", exact=True).is_visible()
        ):
            mensagem = "ERRO JAVA!" if erro_java else "ERRO!"
            logger.error(mensagem)
            raise RuntimeError(f"{mensagem} Verifique manualmente!")


def esperar_sucesso_ou_erro(page: Page | Frame, timeout: int = 60_000) -> None:
    """
    Esta função espera por uma mensagem de sucesso ou erro, que é mostrada ao
    fazer algum movimento dentro do Almoxarifado, e ela também espera pela página
    de relatórios disponíveis, que é mostrada ao fazer cadastros ou alterações no
    Patrimônio.
    """
    sucesso = page.locator(".alert-success")
    erro = page.locator(".alert-danger")

    pagina_relatorios = (
        page.get_by_text("Relatórios", exact=True)
        .or_(
            page.get_by_role(
                "heading", name=re.compile(r"^Relatórios solicitados$", re.IGNORECASE)
            )
        )
        .filter(visible=True)
    )

    expect(sucesso.or_(erro).or_(pagina_relatorios).first).to_be_visible(
        timeout=timeout
    )

    if erro.first.is_visible():
        erros_campos = logar_erros_de_campos(page)
        msg_alerta = erro.first.inner_text().strip()

        if erros_campos:
            detalhe_campos = "; ".join(erros_campos)
            raise RuntimeError(f"{msg_alerta} | Detalhes: {detalhe_campos}")

        raise RuntimeError(msg_alerta)

    if not sucesso.first.is_visible():
        # da página de relatórios. No Patrimônio isso é o comportamento esperado; em telas
        # que deveriam exibir alerta, significa que a operação foi dada como boa
        # sem confirmação nenhuma. Fica registrado para não passar silencioso.
        logger.warning(
            "Nenhum alerta de sucesso ou erro apareceu. A espera foi satisfeita "
            "pela página de relatórios."
        )


# Verifique se esta função é verdadeiramente válida e necessária
def esperar_valor_input_estabilizar(
    page,
    input_selector: str,
    timeout: int = 10_000,
    stable_ms: int = 500,
):
    """
    Aguarda até que:
    - o input exista
    - não seja recriado no DOM
    - o valor permaneça inalterado por stable_ms
    """

    page.wait_for_function(
        """
        ({ selector, stableMs }) => {
            let input = document.querySelector(selector);
            if (!input) return false;

            let lastValue = input.value;
            let stableSince = Date.now();

            return new Promise(resolve => {
                const interval = setInterval(() => {
                    const currentInput = document.querySelector(selector);

                    // Input foi recriado → resetar estabilidade
                    if (currentInput !== input) {
                        input = currentInput;
                        if (!input) return;
                        lastValue = input.value;
                        stableSince = Date.now();
                        return;
                    }

                    const currentValue = input.value;

                    if (currentValue !== lastValue) {
                        lastValue = currentValue;
                        stableSince = Date.now();
                    }

                    if (Date.now() - stableSince >= stableMs) {
                        clearInterval(interval);
                        resolve(true);
                    }
                }, 50);
            });
        }
        """,
        arg={
            "selector": input_selector,
            "stableMs": stable_ms,
        },
        timeout=timeout,
    )


def esperar_campo_ficar_pronto(
    page,
    selector: str,
    timeout: int = 10_000,
    stable_ms: int = 500,
):
    """
    Aguarda até que o campo esteja pronto para uso.

    Considera como "pronto" quando:
    - o elemento existe
    - não está sendo recriado continuamente
    - o valor parou de mudar
    - OU o tipo do elemento mudou (ex: input → select)
    """

    page.wait_for_function(
        """
        ({ selector, stableMs }) => {
        let element = document.querySelector(selector);
        if (!element) return false;

        let tag = element.tagName;
        let lastValue = element.value || "";
        let stableSince = Date.now();

        return new Promise(resolve => {
                const interval = setInterval(() => {
                    const current = document.querySelector(selector);

                    // elemento sumiu → continua esperando
                    if (!current) return;

                    const currentTag = current.tagName;

                    // mudou de tipo
                    if (currentTag !== tag) {
                        clearInterval(interval);
                        resolve(true);
                        return;
                    }

                    // elemento recriado (mesmo tipo)
                    if (current !== element) {
                        element = current;
                        lastValue = element.value || "";
                        stableSince = Date.now();
                        return;
                    }

                    const currentValue = element.value || "";

                    // valor mudou → ainda processando
                    if (currentValue !== lastValue) {
                        lastValue = currentValue;
                        stableSince = Date.now();
                    }

                    // ficou estável → pronto
                    if (Date.now() - stableSince >= stableMs) {
                        clearInterval(interval);
                        resolve(true);
                    }
                }, 50);
            });

        }
        """,
        arg={"selector": selector, "stableMs": stable_ms},
        timeout=timeout,
    )


def esperar_pagina_carregar(
    page: Page | Frame, mensagem_caso_erro: str = "", timeout: int = 60_000
) -> None:
    """
    Aguarda a página estar pronta com base em um sinal funcional,
    não técnico. Basicamente, ela espera até o nome do usuário aparecer
    no topo da página, que é um dos indícios de que a página foi carregada.
    """

    aguardar_ajax_global(page, timeout=timeout)

    expect(page.locator("#centralHeaderUserName"), mensagem_caso_erro).not_to_have_text(
        "", timeout=30_000
    )

    aguardar_ajax_global(page, timeout=timeout)


# ---------------------------------------------------------
# Safe autocomplete interaction
# ---------------------------------------------------------
def preencher_autocomplete(
    page: Page | Frame,
    input_selector: str,
    texto_digitado: str,
    delay_digitacao: int = 100,
    timeout: int = 15_000,
):
    # Aceita tanto Page (v3) quanto Frame (v4): o `aguardar_ajax_global` espera
    # sempre no Page raiz, enquanto os locators/teclado usam o escopo recebido.
    _page = page if isinstance(page, Page) else page.page

    aguardar_ajax_global(_page)

    field = page.locator(input_selector)

    field.wait_for(state="visible", timeout=timeout)
    field.click()
    field.clear()
    field.press("Control+A")
    field.press("Delete")
    field.type(texto_digitado, delay=delay_digitacao)

    # Wait for dropdown
    menu = page.locator(".ui-autocomplete:visible")
    try:
        menu.wait_for(timeout=timeout)
    except Exception:
        raise TimeoutError(
            f"Nenhum resultado encontrado para '{texto_digitado}'. "
            f"Verifique se o item está cadastrado na base de dados e se o nome está correto."
        )

    # Wait for options
    try:
        menu.locator("li.ui-menu-item").first.wait_for()
    except Exception:
        raise TimeoutError(
            f"O dropdown abriu masn não retornou opções para '{texto_digitado}'. "
            f"Verifique se o item está cadastrado na base de dados."
        )

    # Select first option
    field.press("ArrowDown")
    field.press("Enter")

    # Wait for dropdown to close (selection accepted)
    menu.wait_for(state="hidden", timeout=timeout)

    # Wait for AJAX triggered by autocomplete selection
    aguardar_ajax_global(_page)

    esperar_valor_input_estabilizar(page, input_selector)

    # Small buffer to ensure page is fully stable before next interaction
    aguardar_ajax_global(_page)


def preencher_autocomplete_select(
    ctx: Page | Frame,
    input_selector: str,
    texto_digitado: str,
    delay_digitacao: int = 100,
    timeout: int = 15_000,
):
    _page = ctx if isinstance(ctx, Page) else ctx.page

    aguardar_ajax_global(_page)

    field = ctx.locator(input_selector)

    field.wait_for(state="visible", timeout=timeout)
    field.click()
    field.clear()
    field.press("Control+A")
    field.press("Delete")
    field.type(texto_digitado, delay=delay_digitacao)

    # Wait for dropdown
    menu = ctx.locator(".ui-autocomplete:visible")
    try:
        menu.wait_for(timeout=timeout)
    except Exception:
        raise TimeoutError(
            f"Nenhum resultado encontrado para '{texto_digitado}'. "
            f"Verifique se o item está cadastrado na base de dados e se o nome está correto."
        )

    # Wait for options
    try:
        menu.locator("li.ui-menu-item").first.wait_for()
    except Exception:
        raise TimeoutError(
            f"O dropdown abriu mas não retornou opções para '{texto_digitado}. "
            f"Verifique se o item está cadastrado na base de dados do sistema."
        )

    # Select first option
    field.press("ArrowDown")
    field.press("Enter")

    # Wait for dropdown to close (selection accepted)
    menu.wait_for(state="hidden", timeout=timeout)

    # Wait for AJAX triggered by autocomplete selection
    aguardar_ajax_global(_page)


def preencher_autocampo(
    page: Page,
    input_selector: str,
    selector: str,
    texto_digitado: str,
    delay_digitacao: int = 100,
    timeout: int = 15_000,
):
    aguardar_ajax_global(page)

    field = page.locator(input_selector)

    field.wait_for(state="visible", timeout=timeout)
    field.click()
    field.clear()
    field.press("Control+A")
    field.press("Delete")
    field.type(texto_digitado, delay=delay_digitacao)

    # Wait for dropdown
    menu = page.locator(".ui-autocomplete:visible")
    try:
        menu.wait_for(timeout=timeout)
    except Exception:
        raise TimeoutError(
            f"Nenhum resultado encontrado para '{texto_digitado}'. "
            f"Verifique se o item está cadastrado na base de dados e se o nome está correto."
        )

    # Wait for options
    try:
        menu.locator("li.ui-menu-item").first.wait_for()
    except Exception:
        raise TimeoutError(
            f"O dropdown abriu mas não retornou opções para '{texto_digitado}. "
            f"Verifique se o item está cadastrado na base de dados do sistema."
        )

    # Select first option
    field.press("ArrowDown")
    field.press("Enter")

    # Wait for dropdown to close (selection accepted)
    menu.wait_for(state="hidden", timeout=timeout)

    # Wait for AJAX triggered by autocomplete selection
    aguardar_ajax_global(page)

    esperar_campo_ficar_pronto(page, selector)

    # Small buffer to ensure page is fully stable before next interaction
    aguardar_ajax_global(page)


def esperar_com_refresh(
    page: Page | Frame,
    locator: str,
    timeout_total_sec: int = 240,
    refresh_interval_sec: int = 15,
    wait_each_try_ms: int = 3_000,
    check_interval_ms: int = 500,
):

    inicio = time.time()

    while time.time() - inicio < timeout_total_sec:
        try:
            page.wait_for_selector(locator, state="visible", timeout=wait_each_try_ms)
            return True

        except TimeoutError:
            tempo_refresh = time.time()

            while time.time() - tempo_refresh < refresh_interval_sec:
                if page.locator(locator).is_visible():
                    return True

                page.wait_for_timeout(check_interval_ms)

            clicar_com_ajax(page, "button[name='submitFinish']")

    return False


def clicar_menu_com_retry(page, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        page.get_by_role("button", name="Menu").click()

        try:
            page.get_by_role("link", name="Almoxarifado").wait_for(timeout=3_000)
            break
        except TimeoutError:
            logger.warning("Menu não carregou corretamente. Tentando novamente...")

            if tentativa == tentativas:
                raise RuntimeError("Falha ao abrir menu após múltiplas tentativas.")

            page.reload()


def clicar_home_com_retry(page, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        page.get_by_title("Home").click()

        try:
            page.get_by_text("Módulos").wait_for(timeout=3_000)

        except TimeoutError:
            logger.warning("Menu não carregou corretamente. Tentando novamente...")

            if tentativa == tentativas:
                raise RuntimeError("Faha ao abrir menu após múltiplas tentativas.")

            page.reload()


# Verifique se isso é realmente necessário
def esperar_elemento_visivel(
    page, selector, timeout: int = 30_000
):  # tempo em milissegundos
    """
    Localiza um elemento por qualquer seletor (XPath, CSS, Role, Text)
    e valida se ele está visível.
    """
    locator = page.locator(selector)
    expect(locator).to_be_visible(timeout=timeout)
    return locator


def select_tipo(ctx: Page | Frame, select_name: str, texto: str) -> bool:
    """
    Seleciona uma opção de um elemento <select> por correspondência parcial de
    texto, ignorando diferenças de acentuação e capitalização.

    Percorre as opções do <select> cujo atributo `name` seja igual a
    `select_name` e seleciona a primeira cujo texto contenha `texto`.

    Args:
        ctx: Instância de `Page` ou `Frame` onde o select está localizado.
        select_name: Valor do atributo `name` do elemento <select>.
        texto: Texto parcial a ser buscado entre as opções disponíveis.

    Returns:
        True se uma opção correspondente for encontrada e selecionada.
        False se nenhuma opção correspondente existir.
    """

    _page = ctx if isinstance(ctx, Page) else ctx.page

    if ctx.locator(f"select[name='{select_name}']").is_disabled():
        logger.warning("O campo de select está desativado.")
        return False

    opcao = ctx.eval_on_selector(
        f"select[name='{select_name}']",
        """(select, texto) => {

            const normalizar = valor =>
                valor
                    .normalize("NFD")
                    .replace(/[\\u0300-\\u036f]/g, "")
                    .toUpperCase()
                    .trim();

            const textoBusca = normalizar(texto);

            const option = Array.from(select.options).find(o =>
                normalizar(o.text).includes(textoBusca)
            );

            return option ? option.value : null;
        }""",
        texto,
    )

    if opcao is None:
        return False

    ctx.locator(f"select[name='{select_name}']").select_option(value=opcao)
    aguardar_ajax_global(_page)

    return True


def obter_frame_conteudo(
    page: Page, tentativas: int = 10, intervalo_ms: int = 500
) -> Frame:
    """
    Obtém o frame de conteúdo principal da página (iframe-context) e aguarda
    que ele esteja completamente carregado antes de retornar.

    Estratégia:
    1. Aguarda o elemento <iframe> estar no DOM da page.
    2. Resolve o objeto Frame pelo nome.
    3. Aguarda o AJAX global da page resolver.
    4. Aguarda o frame atingir o estado "load" (timeout curto — AJAX já resolveu).
    5. Aguarda que o frame tenha ao menos um elemento visível no <body>,
       evitando retornar um frame vazio durante navegação.

    Args:
        page: Objeto da página do Playwright.
        tentativas: Número máximo de tentativas antes de lançar exceção. Padrão: 5.
        intervalo_ms: Intervalo em milissegundos entre tentativas. Padrão: 500.

    Returns:
        O frame de conteúdo pronto para interação.

    Raises:
        RuntimeError: Se o frame não for encontrado ou não carregar após todas as tentativas.
    """
    for tentativa in range(1, tentativas + 1):
        # Passo 1: aguardar o elemento <iframe> estar no DOM da page
        try:
            page.wait_for_selector(
                "#iframe-context",
                state="attached",
                timeout=2_000,
            )
        except Exception:
            logger.debug(
                "Elemento iframe ainda não está no DOM. Aguardando... ({}/{})",
                tentativa,
                tentativas,
            )
            page.wait_for_timeout(intervalo_ms)
            continue

        # Passo 2: resolver o objeto Frame
        frame = page.frame(name="iframe-context")

        if frame is None:
            logger.debug(
                "Frame encontrado no DOM mas não resolvido ainda. Aguardando... ({}/{})",
                tentativa,
                tentativas,
            )
            page.wait_for_timeout(5_000)
            continue

        # Passo 3: aguardar AJAX global da page resolver
        try:
            page.wait_for_selector(
                "#ajaxStatusLoadingBackground", state="visible", timeout=1000
            )
            page.wait_for_selector(
                "#ajaxStatusLoadingBackground", state="hidden", timeout=300_000
            )
        except Exception:
            pass

        # Passo 4: load state com timeout curto — AJAX já resolveu, frame deve estar pronto
        try:
            frame.wait_for_load_state("load", timeout=2_000)
        except Exception:
            logger.debug(
                "load state não confirmado após AJAX — prosseguindo. ({}/{})",
                tentativa,
                tentativas,
            )

        # Passo 5: garantir que o frame não está vazio (evita frame de transição)
        try:
            frame.locator("body > *").first.wait_for(state="attached", timeout=3_000)
        except Exception:
            logger.debug(
                "Frame carregado mas body ainda vazio. Aguardando... ({}/{})",
                tentativa,
                tentativas,
            )
            page.wait_for_timeout(intervalo_ms)
            continue

        return frame

    raise RuntimeError(
        "Frame de conteúdo não encontrado ou não carregou após todas as tentativas. "
        "A navegação ocorreu corretamente?"
    )


def selecionar_resultado(
    page: Page | Frame, locator_tabela: str, coluna: int, texto: str
) -> None:
    """
    Seleciona uma linha da tabela com base no texto exato de uma coluna.

    A função localiza uma linha da tabela cujo valor da coluna informada
    corresponde exatamente ao texto fornecido, ignorando espaços antes
    e depois do conteúdo.

    Após encontrar a linha correspondente, clica no botão de seleção
    da linha e aguarda o carregamento da página.

    Args:
        page (Page):
            Instância da página do Playwright.

        locator_tabela (str):
            Locator das linhas da tabela que serão pesquisadas.

        coluna (int):
            Índice da coluna utilizada na validação do texto.

        texto (str):
            Texto esperado na coluna da tabela.

    Returns:
        None
    """
    logger.info("Selecionando resultado.")

    linha = page.locator(locator_tabela).filter(
        has=page.locator("td")
        .nth(coluna)
        .filter(has_text=re.compile(rf"^\s*{re.escape(texto)}\s*$"))
    )

    linha.locator("button[name='submitUse']").click()
    esperar_pagina_carregar(page)

    logger.info("Resultado selecionado.")


def preencher_campo(
    ctx: Page | Frame,
    locator: str | Locator,
    texto: str,
    lookup_name: str | None = None,
    igual: bool = False,
) -> None:
    """
    Preenche um campo de lookup (busca por código/nome) e confirma a seleção.

    Funciona tanto com `Page` (v3) quanto com `Frame` (v4). O alerta de erro
    é buscado no mesmo escopo recebido, que é onde ele é renderizado em ambas
    as versões.

    Args:
        ctx: Instância de `Page` ou `Frame` onde o campo está localizado.
        locator: Seletor CSS (str) ou `Locator` já resolvido do campo de input.
        texto: Texto a preencher. Use `"   "` ou `"%"` para abrir a listagem
            completa e selecionar automaticamente o primeiro resultado.
        lookup_name: Nome do botão de lookup. Se omitido, deriva de
            `"lookup-{name}"` onde `name` é o atributo do input.
        page: `Page` raiz, necessário para `aguardar_ajax_global` em contextos
            onde `ctx` é um `Frame` (v4). Se omitido, usa `ctx`.
    """
    if isinstance(locator, Locator):
        field = locator
    else:
        field = ctx.locator(locator)

    # Obtendo o page a partir do frame para o aguardar_ajax_global
    _page = ctx if isinstance(ctx, Page) else ctx.page

    aguardar_ajax_global(_page)
    field.wait_for(state="visible")

    # Caso especial: texto vago abre listagem completa — o lookup é acionado
    # diretamente sem fill, e o primeiro resultado é selecionado na tabela
    if texto in ("   ", "%"):
        input_name = field.get_attribute("name")
        button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"
        ctx.locator(f"button[name='{button_name}']").click()
        aguardar_ajax_global(_page)

        ctx.get_by_title("Consultar novo registro").last.click()
        aguardar_ajax_global(_page)

        tbody = ctx.locator("table[name='paginationTable'] tbody")
        tbody.wait_for(state="visible")

        primeira_linha = tbody.locator("tr").first
        # cell-1-2 e cell-1-3 podem ambas trazer texto; basta uma célula com conteúdo
        # para caracterizar resultado. O .first colapsa o match e evita o strict
        # mode violation.
        celula_com_conteudo = (
            primeira_linha.locator('td[name="cell-1-2"], td[name="cell-1-3"]')
            .filter(has_text=re.compile(r"\S"))
            .first
        )
        try:
            celula_com_conteudo.wait_for(state="visible")
        except TimeoutError:
            raise ValueError("Nenhum resultado encontrado") from None
        primeira_linha.locator("button[name='submitUse']").click()
        aguardar_ajax_global(_page)
        return

    # `aguardar_ajax_global` sozinho não garante que o valor buscado pelo lookup
    # foi de fato gravado no campo: o overlay pode sumir antes do JS terminar de
    # repopular o input. Por isso as checagens abaixo confirmam explicitamente
    # o valor, em vez de assumir sucesso só porque o AJAX terminou.
    field.fill(texto)

    # Enquanto o campo estiver vazio ele vai preencher o valor.
    # Isso foi necessário, pois no TJDFT o teste de Entrada Extra Orçamentaria e a Entrada Doação está dando erro.
    while field.input_value() == "":
        field.fill(texto)
        aguardar_ajax_global(_page)

    input_name = field.get_attribute("name")
    button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"
    button_locator = ctx.locator(f"button[name='{button_name}']")
    button_locator.click()

    aguardar_ajax_global(_page)

    # Verifica se surgiu um alerta
    try:
        alerta = ctx.locator(".alert-danger, .alert-warning")
        alerta.wait_for(state="visible", timeout=100)
        raise RuntimeError(f"Autocomplete falhou para '{texto}': {alerta.inner_text()}")
    except TimeoutError:
        pass  # Nenhum alerta novo apareceu — tudo certo

    # Seleciona a primeira linha encontrada cuja célula contenha exatamente o texto informado.
    esta_na_consulta = ctx.get_by_text("Total de itens consultados:").is_visible()
    if esta_na_consulta:
        if igual:
            linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
                has=ctx.locator("td", has_text=re.compile(f"^{re.escape(texto)}$"))
            )
            linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(_page)
        else:
            primeira_linha = ctx.locator("table[name='paginationTable'] tbody tr").first
            primeira_linha.wait_for(state="visible")
            expect(
                primeira_linha.locator('td[name="cell-1-2"], td[name="cell-1-3"]')
                .filter(has_text=re.compile(r"\S"))
                .first
            ).to_be_visible()
            primeira_linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(_page)

    # Confirma que o lookup gravou um valor no campo (atributo HTML "value", não
    # a propriedade .value ao vivo). Timeout curto porque, se a busca já
    # resolveu, o valor aparece quase junto com o fim do AJAX.
    try:
        expect(field).to_have_attribute("value", re.compile(r".+"), timeout=200)
    except Exception:
        # O campo original ficou vazio: em algumas grades o ASI grava o
        # resultado numa linha nova, uma posição abaixo, e deixa a linha em que
        # você digitou como placeholder vazio pra próxima inserção. Antes de
        # tratar isso como falha de verdade e preencher tudo de novo (o que
        # dispara outro clique no lookup e duplica o item), confirma se o valor
        # não foi só pra linha seguinte. Cobre "algo-N-M" (linha-coluna, ex.:
        # cdBemServico-1-3) e "algo-N" (só linha, ex.: bemServico-1).
        match_linha_coluna = re.match(r"^(.+)-(\d+)-(\d+)$", input_name)
        match_so_linha = re.match(r"^(.+)-(\d+)$", input_name)
        proxima_linha = None
        if match_linha_coluna:
            base, linha, coluna = match_linha_coluna.groups()
            proxima_linha = f"{base}-{int(linha) + 1}-{coluna}"
        elif match_so_linha:
            base, linha = match_so_linha.groups()
            proxima_linha = f"{base}-{int(linha) + 1}"

        # `.count()` é síncrono (não espera nada) — usado pra não gastar o
        # timeout inteiro do `expect` quando o elemento nem existe no DOM. O
        # AJAX já foi esperado antes desse ponto, então, se o valor foi
        # gravado em outro lugar, ele já está lá; não é uma corrida contra o
        # tempo, é só confirmar onde parou.
        confirmado = False
        if proxima_linha:
            linha_abaixo = ctx.locator(f"[name='{proxima_linha}']")
            if linha_abaixo.count() > 0:
                try:
                    expect(linha_abaixo).to_have_attribute(
                        "value", re.compile(r".+"), timeout=200
                    )
                    confirmado = True
                except Exception:
                    pass

        # Só agora, depois de confirmar que o valor realmente não foi gravado
        # em nenhum lugar (nem no campo, nem na linha de baixo, nem virou
        # select), preenche de novo e clica no lookup outra vez.
        if not confirmado and field.is_visible():
            field.fill(texto)

            clicar_com_ajax(ctx, f"button[name='{button_name}']")


def clicar_com_ajax(
    ctx: Page | Frame,
    locator: str | Locator,
    timeout_clique_ms: int = 180_000,
) -> None:
    """Clica em um elemento e aguarda a conclusão do AJAX.

    Aplica a estratégia `no_wait_after=True` no método `click()` para instruir o
    Playwright a não aguardar as navegações ou eventos de carregamento padrão da
    página pós-clique. Isso impede que o Playwright trave esperando por navegações,
    delegando o controle de sincronização do estado da aplicação à função
    `aguardar_ajax_global`.

    Args:
        ctx (Page | Frame): Contexto de execução do Playwright (Page ou Frame).
        locator (str | Locator): Seletor CSS/XPath ou instância de Locator do elemento a ser clicado.
        timeout_clique_ms (int, optional): Tempo máximo de espera em milissegundos para
            a conclusão das requisições AJAX. Padrão: 180.000 ms (3 minutos).

    Returns:
        None
    """
    if isinstance(locator, Locator):
        btn = locator
    else:
        btn = ctx.locator(locator)

    # Obtendo o page a partir do frame para o aguardar_ajax_global
    _page = ctx if isinstance(ctx, Page) else ctx.page

    btn.click(no_wait_after=True)
    aguardar_ajax_global(_page, timeout=timeout_clique_ms)


def preencher_campos_erros(page: Page | Frame) -> None:
    """
    Identifica e preenche os campos que possuem erro de validação.

    Procura inputs com as classes `tdError` e `inputError` e utiliza
    o atributo `vtype` para determinar o valor a ser preenchido.

    Campos do tipo `date` são preenchidos com a data atual. Os demais
    campos são preenchidos com `%`.

    Args:
        page: Página ou frame onde os campos serão procurados.
    """

    data = datetime.now().strftime("%d/%m/%Y")

    nomes = page.eval_on_selector_all(
        "input.tdError.inputError",
        """
            elements => elements
                .map(el => el.getAttribute('name') || '')
                .filter(name => name.trim() !== '')
            """,
    )

    for nome in nomes:
        campo = page.locator(f"input[name='{nome}']")
        vtype = campo.get_attribute("vtype")

        if vtype == "date":
            campo.fill(data)
        else:
            botao = campo.locator("xpath=..").locator("button").get_attribute("name")
            preencher_campo(page, campo, "%", lookup_name=botao)

    if page.locator("button[name='submitFinish']").is_visible():
        clicar_com_ajax(page, "button[name='submitFinish']")


def gerar_variacoes_nome(texto: str) -> list[str]:
    """
    Gera variações para busca (com e sem acento), removendo
    prefixos de blueprint (Ex: 'B01 BRASÍLIA' -> 'BRASÍLIA' e 'BRASILIA').
    """
    if not texto:
        return [texto]

    # Remove qualquer prefixo de blueprint como 'B01 ', 'T01 ', 'A1 ', etc. e sufixos de UF como ' - DISTRITO FEDERAL'
    texto_sem_prefixo = (
        re.sub(r"^[A-Za-z]\d{1,2}\s+", "", texto.strip()).split(" - ")[0].upper()
    )

    # Versão sem acento
    sem_acento = "".join(
        c
        for c in unicodedata.normalize("NFD", texto_sem_prefixo)
        if unicodedata.category(c) != "Mn"
    )

    mapa_conhecido = {
        "BRASILIA": "BRASÍLIA",
        "GOIANIA": "GOIÂNIA",
        "SAO PAULO": "SÃO PAULO",
        "BELEM": "BELÉM",
        "MACEIO": "MACEIÓ",
        "CUIABA": "CUIABÁ",
        "FLORIANOPOLIS": "FLORIANÓPOLIS",
        "VITORIA": "VITÓRIA",
        "SAO LUIS": "SÃO LUÍS",
        "JOAO PESSOA": "JOÃO PESSOA",
        "MACAPA": "MACAPÁ",
        "AMAPA": "AMAPÁ",
    }

    candidatos = [texto_sem_prefixo, sem_acento]

    # Se a entrada estiver sem acento, também testa as acentuações conhecidas
    for sem_ac, com_ac in mapa_conhecido.items():
        if sem_ac in sem_acento and com_ac not in texto_sem_prefixo:
            candidatos.append(sem_acento.replace(sem_ac, com_ac))

    resultado = []
    for c in candidatos:
        if c and c not in resultado:
            resultado.append(c)

    return resultado


def escolher_cidade(
    ctx: Page | Frame,
    nome_cidade: str,
    locator_campo: str | Locator = "input[name='cdCidade']",
    lookup_name: str | None = None,
) -> None:
    """
    Helper para selecionar uma cidade em campos de formulário/lookup,
    utilizando algoritmo de variações e tolerância a acentos.

    :param ctx: Instância de Page ou Frame (v3 ou v4).
    :param nome_cidade: Nome da cidade (com ou sem prefixo do blueprint).
    :param locator_campo: Seletor de input da cidade (padrão: "input[name='cdCidade']").
    :param lookup_name: Nome do botão de lookup (se None, usa lookup-{name}).
    """

    field = (
        locator_campo
        if isinstance(locator_campo, Locator)
        else ctx.locator(locator_campo)
    )
    _page = ctx if isinstance(ctx, Page) else ctx.page

    aguardar_ajax_global(_page)
    field.wait_for(state="visible")

    variacoes = gerar_variacoes_nome(nome_cidade)

    # Ao carregar o registro via Anexar, o campo às vezes já traz um valor válido
    # (confirmado via trace: "Cancelar" restaura o valor original do campo, e esse
    # valor original já era correto). Evita limpar e re-buscar à toa — e evita cair
    # no fluxo de lookup, que não reabre de forma confiável numa segunda tentativa.
    valor_atual = field.input_value().strip().upper()
    if valor_atual in variacoes:
        logger.success(
            "Cidade '{}' já estava correta no campo ('{}'). Nenhuma ação necessária.",
            nome_cidade,
            valor_atual,
        )
        return

    field.clear()

    input_name = field.get_attribute("name")
    button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"

    btn_lookup = ctx.locator(f"button[name='{button_name}']")
    btn_lookup.wait_for(state="visible")
    btn_lookup.click()
    aguardar_ajax_global(_page)

    logger.info(
        "Consultando cidade via lookup para '{}' com variações: {}",
        nome_cidade,
        variacoes,
    )

    btn_search = (
        ctx.locator("button[name='submitSearch']")
        .or_(ctx.get_by_title("Consultar novo registro"))
        .first
    )
    campo_filtro = ctx.locator(
        "input[name='model-3'], input[name='model-0'], input[name='model-1'], input[name='model-2'], #model-3, #model-0"
    ).first

    for tentativa, var_texto in enumerate(variacoes, start=1):
        logger.debug("Tentativa {}: consultando variação '{}'.", tentativa, var_texto)

        try:
            campo_filtro.wait_for(state="visible", timeout=5_000)
            campo_filtro.clear()
            campo_filtro.fill(var_texto)
        except TimeoutError:
            logger.warning(
                "Campo de filtro não apareceu para a variação '{}'.", var_texto
            )

        try:
            btn_search.wait_for(state="visible", timeout=5_000)
            btn_search.click()
            aguardar_ajax_global(_page)
        except TimeoutError:
            logger.warning(
                "Botão de busca não apareceu para a variação '{}'.", var_texto
            )

        tabela = ctx.locator("table[name='paginationTable']")
        try:
            tabela.wait_for(state="visible", timeout=3_000)
        except Exception:
            pass

        # Se não houver resultados (ou a consulta nem rodar de fato), tenta a
        # próxima variação em vez de seguir com uma tabela que não reflete a
        # busca atual.
        try:
            # Esse span apresenta o total de itens consultados
            span_resultado = ctx.locator("span[name='searchResultSize']")
            span_resultado.wait_for(state="visible", timeout=10_000)

            if span_resultado.inner_text() == "0":
                logger.debug(
                    "Total de itens consultados: {}", span_resultado.inner_text()
                )
                clicar_com_ajax(ctx, "button[name='submitCancel']")
                clicar_com_ajax(ctx, btn_lookup)
                continue
        except TimeoutError:
            logger.warning(
                "Timeout esperando 'searchResultSize' para a variação '{}'.",
                var_texto,
            )
            clicar_com_ajax(ctx, "button[name='submitCancel']")
            clicar_com_ajax(ctx, btn_lookup)
            continue

        linhas = ctx.locator("table[name='paginationTable'] tbody tr").all()
        linha_selecionada = None
        var_alvo = var_texto.strip().lower()

        for tr in linhas:
            celulas = [td.inner_text().strip().lower() for td in tr.locator("td").all()]
            if any(var_alvo in c for c in celulas):
                linha_selecionada = tr
                break

        if not linha_selecionada and linhas:
            linha_selecionada = linhas[0]

        if linha_selecionada:
            btn_use = linha_selecionada.locator("button[name='submitUse']").first
            if btn_use.is_visible():
                btn_use.click()
                aguardar_ajax_global(_page)
                logger.success(
                    "Cidade '{}' selecionada via lookup (usando '{}').",
                    nome_cidade,
                    var_texto,
                )
                return

    primeira_linha = ctx.locator("table[name='paginationTable'] tbody tr").first
    if primeira_linha.is_visible():
        btn_use = primeira_linha.locator("button[name='submitUse']").first
        if btn_use.is_visible():
            btn_use.click()
            aguardar_ajax_global(_page)
            logger.success("Primeira cidade da tabela selecionada via lookup.")
            return

    raise RuntimeError(
        f"Não foi possível selecionar a cidade '{nome_cidade}' via lookup após todas as variações."
    )


def proximo_nome(atual: str) -> str:
    """
    Devolve o próximo valor do Nome, sempre por ADIÇÃO de sufixo: alterna " ALT" <-> " TLA"
    (se já terminar com um deles) ou acrescenta " ALT". A alteração é real a cada execução,
    o nome não cresce indefinidamente e a Consulta pelo nome-base continua encontrando.
    """
    atual = atual.rstrip()
    if atual.endswith(" ALT"):
        return atual[:-4] + " TLA"
    if atual.endswith(" TLA"):
        return atual[:-4] + " ALT"
    return atual + " ALT"
