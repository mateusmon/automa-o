"""Login do Genesis.

Cópia deliberada da lógica de `flows/shared/login_flow.py`. O Genesis roda como
script (`python genesis/main.py`), então `genesis/` é o `sys.path[0]` e o `utils/`
da raiz não é alcançável — por isso a cópia, e não um import. Ver a seção
"Genesis e Sentinela — imports e sys.path" no CLAUDE.md.

Diferenças em relação à suíte, todas por causa do contexto do Genesis:
    - a versão chega por parâmetro (vem do runtime_config, não do utils.versao);
    - em v3 há a confirmação extra pelo #centralHeaderUserName, que o Genesis
      sempre teve e que a suíte não faz.
"""

import unicodedata

from loguru import logger
from playwright.sync_api import Page, Response
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.espera import aguardar_ajax_global

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

SELETOR_ERRO_LOGIN = ".alert-danger"
SELETOR_CAMPO_LOGIN = "input[name='nmLogin']"
SELETOR_CAMPO_SENHA = "input[name='nmSenha']"
SELETOR_SUBMIT = "#elSubmit"
SELETOR_USUARIO_HEADER = "#centralHeaderUserName"

TRECHO_GATEWAY = "LoginGateway"

# O servidor responde 'text/json', não 'application/json' — por isso a busca é
# pela substring. Qualquer coisa sem 'json' é HTML, ou seja, submit nativo.
TIPO_RESPOSTA_ESPERADO = "json"

# Trechos que identificam um veredito definitivo do servidor. Só estes
# interrompem: o padrão é retentar, porque a maioria dos erros desta tela é
# timing (submit antes do JS ligar, campo apagado, o próprio JS do ASI estourando
# com "Unexpected token '<'") e se resolve na tentativa seguinte. Retentar uma
# senha de fato errada, por outro lado, queima uma das 5 tentativas que o sistema
# permite antes de bloquear a conta.
# Escritos sem acento de propósito: a comparação normaliza os dois lados.
TRECHOS_DEFINITIVOS = ("nao confere", "nao encontrado", "bloquead", "expirad")


def _normalizar(texto: str) -> str:
    """Devolve o texto em minúsculas e sem acento."""
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def _e_definitivo(mensagem: str) -> bool:
    """Diz se a mensagem é veredito do servidor — isto é, se retentar não adianta."""
    normalizada = _normalizar(mensagem)
    return any(trecho in normalizada for trecho in TRECHOS_DEFINITIVOS)


def _ler_veredito(resposta: Response | None) -> tuple[str, str] | None:
    """Lê o JSON do gateway de login e traduz para uma decisão.

    Returns:
        Tupla (desfecho, mensagem), onde desfecho é 'sucesso', 'recusado' ou
        'retentar'. None quando não há veredito legível — aí quem decide é o DOM.
    """
    if resposta is None:
        return None

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


def login(page: Page, config: dict, chave_usuario: str = "link") -> None:
    """Autentica no sistema usando o runtime_config do Genesis.

    Args:
        page: página do Playwright.
        config: runtime_config, com 'url', 'usuarios' e 'versao'.
        chave_usuario: qual usuário de 'usuarios' usar.

    Raises:
        RuntimeError: se o servidor recusar as credenciais ou se o login não for
            confirmado após MAX_TENTATIVAS tentativas.
    """
    usuario_config = config["usuarios"][chave_usuario]

    url = config["url"]
    usuario = usuario_config["usuario"]
    senha = usuario_config["senha"]
    versao = config.get("versao")

    logger.info("Acessando URL do sistema: {}", url)

    page.goto(url, wait_until="load")
    aguardar_ajax_global(page)

    # A versão não muda entre tentativas — resolve o alvo de sucesso uma vez só.
    if versao == 4:
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

        _aguardar_handler_submit(page)

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

        aguardar_ajax_global(page)

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

        # Sucesso é checado antes do alerta: como o padrão é retentar, um alerta
        # perdido numa tela já logada faria o login submeter de novo.
        if sucesso.is_visible():
            # Confirmação em dois passos que o Genesis sempre teve em v3.
            if versao != 4:
                page.wait_for_selector(SELETOR_USUARIO_HEADER, timeout=TIMEOUT_DESFECHO)
            logger.success("Login realizado com sucesso.")
            return

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

        ultimo_erro = "página recarregou e voltou ao formulário de login"
        logger.warning(
            "Página voltou ao formulário de login sem mensagem. Tentativa {}/{}.",
            tentativa, MAX_TENTATIVAS,
        )

    raise RuntimeError(
        f"Falha no login: {ultimo_erro} após {MAX_TENTATIVAS} tentativas."
    )
