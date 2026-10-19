import ctypes
import re
import time
import unicodedata

from loguru import logger
from playwright.sync_api import Frame, Locator, Page, TimeoutError, expect


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
            # 700ms para o overlay aparecer. Era 100ms, apertado demais: o overlay
            # foi medido subindo ~210ms depois do clique, então a espera quase nunca
            # engatava e a função retornava antes de o ajax começar.
            timeout=700,
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
            # O overlay subiu e não desceu dentro do teto. Seguir em frente é o
            # comportamento de sempre; o que muda é que agora fica registrado.
            logger.warning(
                "O overlay de ajax apareceu e não sumiu em {}ms. Seguindo mesmo assim.",
                timeout,
            )

    # Fora do except: antes só rodava quando o overlay nunca aparecia, então no
    # caminho normal o genesis não checava a tela de erro Java.
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
    if frame is not None:  # noqa: SIM102
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
    sucesso = page.locator(".alert-success")
    erro = page.locator(".alert-danger")

    expect(sucesso.or_(erro)).to_be_visible(timeout=timeout)

    if erro.first.is_visible():
        mensagem = erro.first.inner_text()
        raise RuntimeError(mensagem)


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
        arg={
            "selector": selector,
            "stableMs": stable_ms
        },
        timeout=timeout,
    )


def esperar_pagina_carregar(page: Page | Frame, mensagem_caso_erro: str = "", timeout: int = 60_000) -> None:
    """
    Aguarda a página estar pronta com base em um sinal funcional,
    não técnico. Basicamente, ela espera até o nome do usuário aparecer
    no topo da página, que é um dos indícios de que a página foi carregada.
    """

    aguardar_ajax_global(page, timeout=timeout)
    
    expect(
        page.locator("#centralHeaderUserName"),
        mensagem_caso_erro
    ).not_to_have_text("", timeout=30_000)

    aguardar_ajax_global(page, timeout=timeout)


# ---------------------------------------------------------
# Safe autocomplete interaction
# ---------------------------------------------------------
def preencher_autocomplete(
    page: Page | Frame,
    input_selector: str | Locator,
    texto_digitado: str,
    delay_digitacao: int = 50,
    timeout: int = 30_000, 
):
    aguardar_ajax_global(page)

    field = page.locator(input_selector) if isinstance(input_selector, str) else input_selector
    field.wait_for(state="visible", timeout=timeout)

    eh_busca_coringa = texto_digitado == "   " or (texto_digitado and not texto_digitado.strip())

    if eh_busca_coringa:
        variacoes = ["   "]
        logger.info("Executando busca coringa no autocomplete (3 espaços)...")
    else:
        variacoes = gerar_variacoes_nome(texto_digitado)
        
    timeout_tentativa = 2_500 if len(variacoes) > 1 else timeout
    menu = page.locator(".ui-autocomplete:visible")

    for tentativa, texto in enumerate(variacoes, start=1):
        is_ultima = (tentativa == len(variacoes))
        t_espera = timeout if is_ultima else timeout_tentativa

        field.click()
        field.clear()
        field.press("Control+A")
        field.press("Delete")
        field.type(texto, delay=delay_digitacao)

        try:
            menu.wait_for(timeout=t_espera)
            menu.locator("li.ui-menu-item").first.wait_for(timeout=t_espera)
            if texto != texto_digitado:
                logger.info("Autocomplete encontrou opções com a variação '{}' (busca original '{}')", texto, texto_digitado)
            break
        except Exception:
            if not is_ultima:
                logger.debug("Autocomplete sem opções para '{}'. Tentando próxima variação...", texto)
                continue
            raise TimeoutError(
                f"Nenhum resultado encontrado para '{texto_digitado}' (e suas variações). "
                f"Verifique se o item está cadastrado na base de dados."
            )

    # Select first option
    field.press("ArrowDown")
    field.press("Enter")

    # Wait for dropdown to close (selection accepted)
    menu.wait_for(state="hidden", timeout=timeout)

    # Wait for AJAX triggered by autocomplete selection
    aguardar_ajax_global(page)

    esperar_valor_input_estabilizar(page, input_selector)

    # Small buffer to ensure page is fully stable before next interaction

    aguardar_ajax_global(page)


def preencher_autocampo(
    page: Page,
    input_selector: str,
    selector: str,
    texto_digitado: str,
    delay_digitacao: int = 100,
    timeout: int = 30_000, 
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
    menu.wait_for(timeout=timeout)

    # Wait for options
    menu.locator("li.ui-menu-item").first.wait_for()

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
    page, 
    locator, 
    timeout_total_sec=180, 
    refresh_interval_sec=15, 
    wait_each_try_ms=3_000, 
    check_interval_ms=500
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

            page.get_by_role("button", name="Confirmar").click()

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


def mostrar_popup(titulo: str, mensagem: str, icon):
    ctypes.windll.user32.MessageBoxW(
        0,
        mensagem,
        titulo,
        icon | 0x1000
    )


def obter_frame_conteudo(page: Page, tentativas: int = 10, intervalo_ms: int = 500) -> Frame:
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
        # Move o mouse para fora do menu antes de cada tentativa,
        # evitando que o menu de navegação fique sobreposto ao frame.
        page.mouse.move(960, 540)

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
        aguardar_ajax_global(page)

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


def autocomplete(
    page,
    locator,
    texto: str,
    delay_digitacao: int = 50,
    timeout: int = 30_000,
):
    if isinstance(locator, Locator):
        field = locator
    else:
        field = page.locator(locator)
    
    aguardar_ajax_global(page)

    field.wait_for(state="visible", timeout=timeout)
    field.click()
    field.clear()
    field.press("Control+A")
    field.press("Delete")
    field.type(texto, delay=delay_digitacao)

    menu = page.locator(".ui-autocomplete:visible")
    menu.wait_for(timeout=timeout)
    menu.locator("li.ui-menu-item").first.wait_for()

    field.press("ArrowDown")
    field.press("Enter")

    menu.wait_for(state="hidden", timeout=timeout)

    aguardar_ajax_global(page)


def _esperar_valor_mudar(
    page,
    field,
    texto_digitado: str,
    timeout: int = 10_000,
    poll_ms: int = 50,
):
    import time

    deadline = time.time() + timeout / 1000

    while time.time() < deadline:
        valor_atual = field.input_value()

        if texto_digitado in valor_atual:
            return

        page.wait_for_timeout(poll_ms)


def preencher_campo(
    ctx: Page | Frame,
    locator: str | Locator,
    texto: str,
    lookup_name: str | None = None,
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

    # aguardar_ajax_global(_page)
    field.wait_for(state="visible")

    # Caso especial: texto vago abre listagem completa — o lookup é acionado
    # diretamente sem fill, e o primeiro resultado é selecionado na tabela
    if texto in ("   ", "%"):
        input_name = field.get_attribute("name")
        button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"
        ctx.locator(f"button[name='{button_name}']").click()
        aguardar_ajax_global(_page)

        ctx.get_by_title("Consultar novo registro").last.click(no_wait_after=True)
        aguardar_ajax_global(_page)

        tbody = ctx.locator("table[name='paginationTable'] tbody")
        tbody.wait_for(state="visible")
        tbody.locator("tr").first.locator("button[name='submitUse']").click(no_wait_after=True)
        aguardar_ajax_global(_page)
        return

    variacoes = gerar_variacoes_nome(texto)
    input_name = field.get_attribute("name")
    button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"

    for tentativa, var_texto in enumerate(variacoes, start=1):
        is_ultima = (tentativa == len(variacoes))
        field.fill(var_texto)
        ctx.locator(f"button[name='{button_name}']").click()
        aguardar_ajax_global(_page)

        # Aguarda um tempo até que o valor correto (no formato código - nome) seja puxado
        try:
            expect(field).to_have_value(re.compile(r"^\d+"), timeout=1_000)
        except Exception:
            pass  # Casos sem código numérico — segue normalmente

        # Verifica se surgiu um alerta
        alerta_erro = False
        msg_alerta = ""
        try:
            alerta = ctx.locator(".alert-danger, .alert-warning")
            alerta.wait_for(state="visible", timeout=200)
            alerta_erro = True
            msg_alerta = alerta.inner_text()
        except TimeoutError:
            pass

        if alerta_erro:
            if not is_ultima:
                logger.debug("Lookup com '{}' retornou alerta ('{}'). Tentando próxima variação...", var_texto, msg_alerta)
                continue
            raise RuntimeError(
                f"Autocomplete falhou para '{texto}' (última tentativa '{var_texto}'): {msg_alerta}"
            )

        # Escolhe o primeiro resultado, caso encontre mais do que um resultado
        esta_na_consulta = ctx.get_by_text("Total de itens consultados:").is_visible()
        if esta_na_consulta:
            span_size = ctx.locator("span[name='searchResultSize']")
            try:
                if span_size.is_visible() and int(span_size.inner_text()) == 0:
                    if not is_ultima:
                        logger.debug("Lookup com '{}' retornou 0 resultados. Tentando próxima variação...", var_texto)
                        continue
            except Exception:
                pass
            primeira_linha = ctx.locator("table[name='paginationTable'] tbody tr").first
            primeira_linha.wait_for(state="visible")
            primeira_linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(_page)

        if var_texto != texto:
            logger.info("Lookup selecionado com sucesso usando a variação '{}' para '{}'", var_texto, texto)
        return


def select_tipo(ctx: Page | Frame, select_name: str, texto: str) -> None:
    """
    Seleciona uma opção em um elemento <select> por correspondência parcial de texto.

    Percorre as opções do select cujo atributo `name` seja igual a `select_name`
    e seleciona a primeira opção cujo texto contenha `texto`.

    :param page: Objeto da página ou frame do Playwright
    :type page: Union[Page, Frame]

    :param select_name: Valor do atributo `name` do elemento <select>
    :type select_name: str

    :param texto: Texto parcial a ser buscado entre as opções disponíveis
    :type texto: str

    :raises Error: Se nenhuma opção contiver o texto informado
    """

    _page = ctx if isinstance(ctx, Page) else ctx.page

    ctx.locator(f"select[name='{select_name}']").select_option(
        label=ctx.eval_on_selector(
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

                if (!option) {
                    throw new Error(
                        `Nenhuma opção encontrada com texto: ${texto}`
                    );
                }

                return option.text;
            }""",
            texto
        )
    )

    aguardar_ajax_global(_page)

def gerar_variacoes_nome(texto: str) -> list[str]:
    """
    Gera variações para busca (com e sem acento),
    testando sem prefixos de blueprint (ex: 'B01 BRASÍLIA' -> 'BRASÍLIA' e 'BRASILIA').
    """
    if not texto:
        return [texto]

    # Remove qualquer prefixo de blueprint como 'B01 ', 'T01 ', 'A1 ', etc.
    texto_sem_prefixo = re.sub(r"^[A-Za-z]\d{1,2}\s+", "", texto.strip()).upper()

    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto_sem_prefixo)
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

    # Se o texto de entrada estiver sem acento, tenta aplicar a acentuação conhecida
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
    abrindo a consulta do lookup, buscando pela cidade e selecionando o registro.

    :param ctx: Instância de Page ou Frame (v3 ou v4).
    :param nome_cidade: Nome da cidade (com ou sem prefixo do blueprint).
    :param locator_campo: Seletor de input da cidade (padrão: "input[name='cdCidade']").
    :param lookup_name: Nome do botão de lookup (se None, usa lookup-{name}).
    """
    field = locator_campo if isinstance(locator_campo, Locator) else ctx.locator(locator_campo)
    _page = ctx if isinstance(ctx, Page) else ctx.page

    aguardar_ajax_global(_page)
    field.wait_for(state="visible")
    field.clear()

    input_name = field.get_attribute("name")
    button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"

    btn_lookup = ctx.locator(f"button[name='{button_name}']")
    btn_lookup.wait_for(state="visible")
    btn_lookup.click()
    aguardar_ajax_global(_page)

    variacoes = gerar_variacoes_nome(nome_cidade)
    logger.info("Consultando cidade via lookup para '{}' com variações: {}", nome_cidade, variacoes)

    for tentativa, var_texto in enumerate(variacoes, start=1):
        campo_filtro = ctx.locator("input[name='model-1']")
        btn_search = ctx.locator("button[name='submitSearch']")

        campo_filtro.wait_for(state="visible")
        campo_filtro.fill(var_texto)
        btn_search.click()
        aguardar_ajax_global(_page)

        tabela = ctx.locator("table[name='paginationTable']")
        try:
            tabela.wait_for(state="visible", timeout=3_000)
        except Exception:
            pass

        linhas = ctx.locator("table[name='paginationTable'] tbody tr").all()
        linha_selecionada = None
        var_alvo = var_texto.strip().lower()

        for tr in linhas:
            celulas = [td.inner_text().strip().lower() for td in tr.locator("td").all()]
            if any(var_alvo in c for c in celulas):
                linha_selecionada = tr
                break

        if linha_selecionada:
            btn_use = linha_selecionada.locator("button[name='submitUse']").first
            if btn_use.is_visible():
                btn_use.click()
                aguardar_ajax_global(_page)
                logger.success("Cidade '{}' selecionada via lookup (usando '{}').", nome_cidade, var_texto)
                return

        if tentativa < len(variacoes):
            ctx.locator("button[name='submitTabSearchData']").click()
            aguardar_ajax_global(_page)

    raise RuntimeError(f"Não foi possível selecionar a cidade '{nome_cidade}' via lookup após todas as variações.")
