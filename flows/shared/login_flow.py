import unicodedata

from loguru import logger
from playwright.sync_api import Page, Response
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.versao import get_versao
from utils.waits import aguardar_ajax_global

MAX_TENTATIVAS = 3

# Teto para o campo de login aparecer.
TIMEOUT_CAMPO = 10_000

# Teto para o handler de clique ser vinculado pelo require.js.
TIMEOUT_HANDLER = 10_000

# Teto para a resposta do gateway de login chegar. Generoso de propósito: já foi
# medido em 11s num cliente lento, e o custo no caminho feliz é zero, porque o
# expect_response retorna assim que a resposta chega.
TIMEOUT_RESPOSTA = 30_000

# Teto para o desfecho renderizar no DOM após a resposta do submit.
TIMEOUT_DESFECHO = 10_000

# Mensagem de erro da tela de login.
SELETOR_ERRO_LOGIN = ".alert-danger"

SELETOR_CAMPO_LOGIN = "input[name='nmLogin']"
SELETOR_CAMPO_SENHA = "input[name='nmSenha']"
SELETOR_SUBMIT = "#elSubmit"

TRECHO_GATEWAY = "LoginGateway"

# O servidor responde 'text/json', não 'application/json' — por isso a busca é
# pela substring. Qualquer coisa sem 'json' é HTML, ou seja, submit nativo.
TIPO_RESPOSTA_ESPERADO = "json"

# Trechos que identificam um veredito definitivo do servidor. Só estes
# interrompem: o padrão é retentar, porque a maioria dos erros desta tela é
# timing nosso (submit antes do JS ligar, campo apagado, o próprio JS do ASI
# estourando com "Unexpected token '<'") e se resolve na tentativa seguinte.
# Retentar uma senha de fato errada, por outro lado, queima uma das 5 tentativas
# que o sistema permite antes de bloquear a conta.
# Escritos sem acento de propósito: a comparação normaliza os dois lados.
TRECHOS_DEFINITIVOS = ("nao confere", "nao encontrado", "bloquead", "expirad")


def _normalizar(texto: str) -> str:
    """Devolve o texto em minúsculas e sem acento.

    A comparação não pode depender de acentuação: a mensagem chega do servidor e
    varia entre clientes e versões. Errar para o lado do 'retentar' seria queimar
    tentativas de uma senha que o servidor já recusou.
    """
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def _e_definitivo(mensagem: str) -> bool:
    """Diz se a mensagem é veredito do servidor — isto é, se retentar não adianta."""
    normalizada = _normalizar(mensagem)
    return any(trecho in normalizada for trecho in TRECHOS_DEFINITIVOS)


def _ler_veredito(resposta: Response | None) -> tuple[str, str] | None:
    """Lê o JSON do gateway de login e traduz para uma decisão.

    O gateway devolve o desfecho completo no corpo, incluindo a mensagem real
    ("Senha de acesso não confere. Tentativa 1 de 5") — bem mais útil que o
    alerta genérico que aparece na tela.

    Args:
        resposta: resposta capturada do gateway, ou None se não veio nenhuma.

    Returns:
        Tupla (desfecho, mensagem), onde desfecho é 'sucesso', 'recusado' ou
        'retentar'. Devolve None quando não há veredito legível — aí quem decide
        é o DOM. O corpo costuma estar disponível justamente quando importa: o
        login que falha não navega; o que navega é o de sucesso, e nesse caso o
        próprio DOM já mostra o resultado.
    """
    if resposta is None:
        return None

    # Sem o handler AJAX vinculado, o <button> sem type faz POST comum e o
    # servidor devolve HTML. Sempre retentável: na próxima o JS já estará ligado.
    tipo = resposta.headers.get("content-type") or ""
    if TIPO_RESPOSTA_ESPERADO not in tipo.lower():
        return ("retentar", "o servidor devolveu HTML em vez de JSON (submit nativo)")

    try:
        corpo = resposta.json()
    except Exception:
        return None

    if not isinstance(corpo, dict):
        return None

    if corpo.get("success"):
        return ("sucesso", "")

    mensagem = " | ".join(
        m.get("message", "") for m in corpo.get("msgs", []) if m.get("message")
    ) or "sem mensagem"

    return ("recusado" if _e_definitivo(mensagem) else "retentar", mensagem)


def _aguardar_handler_submit(page: Page) -> None:
    """Garante que o evento de clique do jQuery/RequireJS já foi anexado ao botão.

    O handler é delegado no <form>, não no próprio botão — por isso a subida
    pela árvore até encontrar quem escuta o clique.
    """
    try:
        page.wait_for_function(
            """(seletor) => {
                const $ = window.jQuery;
                if (!$) return false;
                let no = document.querySelector(seletor);
                while (no) {
                    const eventos = $._data(no, 'events');
                    if (eventos && eventos.click && eventos.click.length) return true;
                    no = no.parentNode;
                }
                return false;
            }""",
            arg=SELETOR_SUBMIT,
            timeout=TIMEOUT_HANDLER,
        )
    except PlaywrightTimeoutError:
        logger.warning(
            "Handler do submit não detectado em {}ms; seguindo mesmo assim.",
            TIMEOUT_HANDLER,
        )


def login(page: Page, dados_cliente: dict[str, str]) -> None:
    """Autentica o usuário no sistema.

    Preenche as credenciais e submete o formulário. O desfecho é lido, quando
    possível, do JSON que o gateway de login devolve; quando não há resposta
    legível, cai para a leitura do DOM (elemento de sucesso, alerta de erro ou o
    próprio formulário de volta).

    A regra de retentativa é a mesma nos dois caminhos: só um veredito
    reconhecido do servidor interrompe (ver TRECHOS_DEFINITIVOS). Todo o resto é
    retentado, porque a maior parte das falhas desta tela é instabilidade de
    carregamento e passa na tentativa seguinte.

    Args:
        page: página do Playwright.
        dados_cliente: dict com as chaves 'usuario', 'senha' e 'url'.

    Raises:
        KeyError: se faltar alguma chave obrigatória em dados_cliente.
        RuntimeError: se o servidor recusar as credenciais ou se o login não for
            confirmado após MAX_TENTATIVAS tentativas.
    """
    logger.info("Iniciou login.")

    for chave in ("usuario", "senha", "url"):
        if chave not in dados_cliente:
            raise KeyError(f"Chave '{chave}' ausente em dados_cliente")

    usuario = dados_cliente["usuario"]
    senha = dados_cliente["senha"]

    page.goto(dados_cliente["url"], wait_until="load")
    aguardar_ajax_global(page)

    # A versão não muda entre tentativas — resolve o alvo de sucesso uma vez só.
    if get_versao() >= 4:
        sucesso = page.get_by_role("heading", name="Home")
    else:
        sucesso = page.get_by_role("button", name="Menu")

    erro = page.locator(SELETOR_ERRO_LOGIN).first
    campo_login = page.locator(SELETOR_CAMPO_LOGIN)

    ultimo_erro = "nenhum desfecho confirmado"

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        campo_login.wait_for(state="visible", timeout=TIMEOUT_CAMPO)

        campo_login.fill(usuario)
        page.locator(SELETOR_CAMPO_SENHA).fill(senha)

        # O campo tem maxlength, então input_value() vem capado. Comparamos
        # contra o valor já truncado — não contra o usuario inteiro do configs.
        maxlength = campo_login.get_attribute("maxlength")
        esperado = usuario[: int(maxlength)] if maxlength and maxlength.isdigit() else usuario

        if campo_login.input_value() != esperado:
            ultimo_erro = "campos apagados antes do submit"
            logger.warning(
                "Campos apagados pela página antes do submit. Tentativa {}/{}.",
                tentativa, MAX_TENTATIVAS,
            )
            continue

        # Espera o script da página ligar o evento de clique ao botão
        _aguardar_handler_submit(page)

        # Submete e aguarda a resposta do gateway
        resposta = None
        try:
            with page.expect_response(
                lambda r: TRECHO_GATEWAY in r.url and r.request.method == "POST",
                timeout=TIMEOUT_RESPOSTA,
            ) as info:
                page.locator(SELETOR_SUBMIT).click(no_wait_after=True)
            resposta = info.value
        except PlaywrightTimeoutError:
            logger.warning("Sem resposta do gateway; seguindo pelo desfecho no DOM.")

        # Veredito do servidor, quando disponível. Sucesso segue adiante para a
        # confirmação no DOM: a página ainda precisa terminar de navegar.
        veredito = _ler_veredito(resposta)

        if veredito is not None and veredito[0] != "sucesso":
            decisao, mensagem = veredito

            if decisao == "recusado":
                raise RuntimeError(
                    f"Login recusado pelo sistema: {mensagem}. "
                    "Verifique as credenciais no arquivo 'configs.yaml'."
                )

            ultimo_erro = mensagem
            logger.warning(
                "Login não aceito: {}. Tentativa {}/{}.",
                mensagem, tentativa, MAX_TENTATIVAS,
            )
            continue

        # Aguarda as requisições AJAX em segundo plano finalizarem
        aguardar_ajax_global(page)

        # Tenta aguardar uma resposta definitiva do servidor (Home, Alerta de Erro ou Recarga)
        desfecho = sucesso.or_(erro).first if resposta else sucesso.or_(erro).or_(campo_login).first
        try:
            desfecho.wait_for(state="visible", timeout=TIMEOUT_DESFECHO)
        except PlaywrightTimeoutError:
            ultimo_erro = "nenhum desfecho renderizou após o submit"
            logger.warning(
                "Nenhum desfecho após o submit. Tentativa {}/{}.",
                tentativa, MAX_TENTATIVAS,
            )
            continue

        # Sucesso é checado antes do alerta: como agora o padrão é retentar, um
        # alerta perdido numa tela já logada faria o flow submeter de novo.
        if sucesso.is_visible():
            logger.info("Finalizou login.")
            return

        # Sem veredito do gateway, o alerta é a única pista. Só interrompe se for
        # veredito de verdade — "O formulário contém erros" e o "Unexpected
        # token '<'" do próprio JS do ASI são transitórios e passam retentando.
        if erro.is_visible():
            mensagem = erro.inner_text().strip() or "sem mensagem"

            if _e_definitivo(mensagem):
                raise RuntimeError(
                    f"Login recusado pelo sistema: {mensagem}. "
                    "Verifique as credenciais no arquivo 'configs.yaml'."
                )

            ultimo_erro = mensagem
            logger.warning(
                "Login não aceito: {}. Tentativa {}/{}.",
                mensagem, tentativa, MAX_TENTATIVAS,
            )
            continue

        # Formulário de volta, sem mensagem: a página rejeitou o post e se
        # redesenhou. Retentativa imediata — não há o que esperar.
        ultimo_erro = "página recarregou e voltou ao formulário de login"
        logger.warning(
            "Página voltou ao formulário de login sem mensagem. Tentativa {}/{}.",
            tentativa, MAX_TENTATIVAS,
        )

    raise RuntimeError(
        f"Falha no login: {ultimo_erro} após {MAX_TENTATIVAS} tentativas."
    )
