"""
Servidor MCP do ASI Automação — dá ao agente controle do navegador reutilizando
os próprios flows/utils do projeto (login, esperas, escopo v3/v4).

Objetivo: acelerar a criação de testes. Com este MCP o agente consegue:
  - abrir o navegador e logar em qualquer cliente do configs.yaml
  - navegar por texto/role/título (menus v3 e v4)
  - INSPECIONAR a página/iframe e listar os seletores reais (input/select/
    button/radio/heading) — é o que permite descobrir os `name` dos campos
  - preencher campos (inclusive lookups) e clicar
  - tirar screenshots (retornados como imagem)

Arquitetura: o Playwright síncrono é preso a uma única thread. Todas as
operações são despachadas para uma thread trabalhadora dedicada (PWWorker),
o que permite reutilizar os flows síncronos do projeto com segurança.

Registro no Claude Code: ver mcps/asi/README.md (ou o arquivo .mcp.json na raiz).
"""
from __future__ import annotations

import queue
import sys
import threading
from concurrent.futures import Future
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page, Playwright

# server.py está em mcps/asi/, então a raiz do projeto é 3 níveis acima.
RAIZ = Path(__file__).resolve().parent.parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from mcp.server.fastmcp import FastMCP, Image

from utils import versao
from utils.data_loader import load_data
from utils.waits import (
    aguardar_ajax_global,
    clicar_home_com_retry,
    preencher_campo,
)

mcp = FastMCP("asi-automacao")

EscopoMCP = Literal["conteudo", "page"]


# ---------------------------------------------------------------------------
# Thread trabalhadora que possui o Playwright síncrono
# ---------------------------------------------------------------------------
class PWWorker:
    def __init__(self) -> None:
        self._fila: "queue.Queue" = queue.Queue()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.pw: "Playwright | None" = None
        self.browser: "Browser | None" = None
        self.context: "BrowserContext | None" = None
        self.page: "Page | None" = None
        self.cliente: "str | None" = None

    def _loop(self) -> None:
        while True:
            fn, fut = self._fila.get()
            if fn is None:
                break
            try:
                fut.set_result(fn())
            except Exception as e:  # noqa: BLE001 — propaga ao chamador
                fut.set_exception(e)

    def run(self, fn):
        fut: Future = Future()
        self._fila.put((fn, fut))
        return fut.result()


worker = PWWorker()


# ---------------------------------------------------------------------------
# Helpers (executam SEMPRE dentro da thread do worker)
# ---------------------------------------------------------------------------
def _carregar_cliente(cliente: str, ambiente: str):
    config = load_data(RAIZ / "configs" / "configs.yaml")
    local = RAIZ / "configs" / "configs.local.yaml"
    if local.exists():
        loc = load_data(local) or {}
        for chave in ("cliente_ativo", "ambiente"):
            if chave in loc:
                config[chave] = loc[chave]

    cliente = cliente or config.get("cliente_ativo")
    clientes = config.get("clientes", {})
    if cliente not in clientes:
        raise ValueError(f"Cliente '{cliente}' não encontrado no configs.yaml. Disponíveis: {list(clientes)}")

    cc = clientes[cliente]
    v = int(cc.get("versao", 3))
    ambientes = cc.get("ambientes", {})
    if ambiente not in ambientes:
        raise ValueError(f"Ambiente '{ambiente}' inexistente para '{cliente}'. Disponíveis: {list(ambientes)}")

    amb = ambientes[ambiente]
    usuarios = amb.get("usuarios", {})
    primeiro = next(iter(usuarios.values()))
    dados = {"url": amb.get("url"), "usuario": primeiro.get("usuario"), "senha": primeiro.get("senha")}
    return dados, v, cliente


def _exige_pagina() -> "Page":
    if worker.page is None:
        raise RuntimeError("Navegador não iniciado. Use 'iniciar_navegador' primeiro.")
    return worker.page


def _escopo():
    """page na v3, frame de conteúdo na v4."""
    return versao.escopo(_exige_pagina())


def _resolver_escopo(escopo: EscopoMCP):
    """Resolve explicitamente o page externo ou o conteúdo principal do ASI."""
    if escopo == "page":
        return _exige_pagina()
    if escopo == "conteudo":
        return _escopo()
    raise ValueError("Escopo inválido. Use 'conteudo' ou 'page'.")


def _fmt_interativos(dados: list[dict]) -> str:
    linhas = []
    for d in dados:
        if d["tag"] in ("h1", "h2", "h3", "h4"):
            linhas.append(f"HEADING <{d['tag']}> {d['text']!r}")
        else:
            linhas.append(
                f"<{d['tag']}> type={d['type']!r} name={d['name']!r} id={d['id']!r} "
                f"disabled={d['disabled']} value={d['value']!r} label={d['label']!r} "
                f"title={d['title']!r} text={d['text']!r}"
            )
    return "\n".join(linhas) if linhas else "(nenhum elemento interativo encontrado)"


_JS_INTERATIVOS = r"""
() => Array.from(document.querySelectorAll('input, select, textarea, button, h1, h2, h3, h4')).map(el => {
    let label = '';
    if (el.id) { const l = document.querySelector(`label[for="${el.id}"]`); if (l) label = l.innerText.trim(); }
    return {
        tag: el.tagName.toLowerCase(), type: el.getAttribute('type')||'', name: el.getAttribute('name')||'',
        id: el.id||'', disabled: el.disabled||false, value:(el.value||'').slice(0,40),
        title: el.getAttribute('title')||'', label, text:(el.innerText||'').trim().slice(0,50)
    };
})
"""

_JS_TEXTOS = r"""
() => Array.from(new Set(Array.from(document.querySelectorAll('a, span, li, td, div, h1, h2, h3'))
    .filter(e => e.offsetParent !== null && e.children.length === 0)
    .map(e => (e.innerText||'').trim())
    .filter(t => t && t.length < 60)))
"""


# ---------------------------------------------------------------------------
# Ferramentas MCP
# ---------------------------------------------------------------------------
@mcp.tool()
def iniciar_navegador(cliente: str = "", ambiente: str = "qas", headless: bool = False, logar_auto: bool = True) -> str:
    """Abre o navegador e (opcionalmente) faz login. cliente vazio = cliente_ativo do configs.yaml."""
    def _do():
        from playwright.sync_api import sync_playwright
        from flows.shared.login_flow import login

        if worker.pw is None:
            worker.pw = sync_playwright().start()
        if worker.browser is None:
            worker.browser = worker.pw.chromium.launch(headless=headless, args=["--start-maximized"])
        if worker.context is not None:
            worker.context.close()
        worker.context = worker.browser.new_context(no_viewport=True, accept_downloads=True)
        worker.page = worker.context.new_page()
        worker.page.set_default_timeout(60_000)

        dados, v, nome = _carregar_cliente(cliente, ambiente)
        versao.set_versao(v)
        worker.cliente = nome
        if logar_auto:
            login(worker.page, dados)
        return f"Navegador iniciado. cliente={nome} versao={v} ambiente={ambiente} logado={logar_auto} url={dados['url']}"
    return worker.run(_do)


@mcp.tool()
def estado() -> str:
    """Retorna o estado atual: cliente, versão, URL e título."""
    def _do():
        if worker.page is None:
            return "Navegador não iniciado."
        return f"cliente={worker.cliente} versao={versao.get_versao()} url={worker.page.url} titulo={worker.page.title()!r}"
    return worker.run(_do)


@mcp.tool()
def ir_home() -> str:
    """(v4) Clica em Home para voltar à tela de módulos."""
    def _do():
        page = _exige_pagina()
        clicar_home_com_retry(page)
        aguardar_ajax_global(page)
        return "Home acionado."
    return worker.run(_do)


@mcp.tool()
def clicar_texto(texto: str, exato: bool = True, indice: int = 0) -> str:
    """Clica em um elemento pelo texto visível (útil para módulos e itens de menu)."""
    def _do():
        page = _exige_pagina()
        page.get_by_text(texto, exact=exato).nth(indice).click()
        aguardar_ajax_global(page)
        return f"Clicou no texto {texto!r} (indice={indice})."
    return worker.run(_do)


@mcp.tool()
def clicar_role(role: str, nome: str, indice: int = 0) -> str:
    """Clica por role acessível (ex.: role='link' nome='Corporativo')."""
    def _do():
        page = _exige_pagina()
        page.get_by_role(role, name=nome).nth(indice).click()
        aguardar_ajax_global(page)
        return f"Clicou em role={role!r} nome={nome!r}."
    return worker.run(_do)


@mcp.tool()
def clicar_titulo(titulo: str) -> str:
    """Clica por atributo title (ex.: 'Abrir menu')."""
    def _do():
        page = _exige_pagina()
        page.get_by_title(titulo).click()
        aguardar_ajax_global(page)
        return f"Clicou no título {titulo!r}."
    return worker.run(_do)


@mcp.tool()
def clicar_seletor(seletor: str, escopo: EscopoMCP = "conteudo") -> str:
    """Clica por CSS no conteúdo ou no page externo (cabeçalho da v4)."""
    def _do():
        page = _exige_pagina()
        _resolver_escopo(escopo).locator(seletor).click()
        aguardar_ajax_global(page)
        return f"Clicou no seletor {seletor!r} em escopo={escopo!r}."
    return worker.run(_do)


@mcp.tool()
def duplo_clique(seletor: str) -> str:
    """Duplo clique por seletor CSS no escopo atual (page na v3, iframe na v4). Útil para selecionar nós de árvore (ex.: grupo/subgrupo do Supply)."""
    def _do():
        page = _exige_pagina()
        _escopo().locator(seletor).dblclick()
        aguardar_ajax_global(page)
        return f"Duplo clique no seletor {seletor!r}."
    return worker.run(_do)


@mcp.tool()
def inspecionar(escopo: EscopoMCP = "conteudo") -> str:
    """Lista elementos interativos do conteúdo ou do page externo."""
    def _do():
        return _fmt_interativos(_resolver_escopo(escopo).evaluate(_JS_INTERATIVOS))
    return worker.run(_do)


@mcp.tool()
def inspecionar_seletor(seletor: str, escopo: EscopoMCP = "conteudo") -> str:
    """Inspeciona elementos por CSS, inclusive quando estão ocultos."""
    def _do():
        locator = _resolver_escopo(escopo).locator(seletor)
        quantidade = locator.count()
        elementos = []
        for indice in range(quantidade):
            elemento = locator.nth(indice)
            elementos.append(
                {
                    "indice": indice,
                    "tag": elemento.evaluate("el => el.tagName.toLowerCase()"),
                    "id": elemento.get_attribute("id") or "",
                    "name": elemento.get_attribute("name") or "",
                    "visivel": elemento.is_visible(),
                    "texto": (elemento.text_content() or "").strip(),
                    "valor": elemento.input_value() if elemento.evaluate(
                        "el => ['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)"
                    ) else "",
                }
            )
        return f"escopo={escopo!r} seletor={seletor!r} elementos={elementos!r}"
    return worker.run(_do)


@mcp.tool()
def textos_visiveis(escopo: EscopoMCP = "page") -> str:
    """Lista textos curtos visíveis no conteúdo ou no page externo."""
    def _do():
        textos = _resolver_escopo(escopo).evaluate(_JS_TEXTOS)
        return "\n".join(sorted(set(textos)))
    return worker.run(_do)


@mcp.tool()
def preencher(seletor: str, valor: str) -> str:
    """Preenche um campo simples (fill) no escopo atual."""
    def _do():
        page = _exige_pagina()
        ctx = _escopo()
        ctx.locator(seletor).fill(valor)
        aguardar_ajax_global(page)
        return f"Preencheu {seletor!r} com {valor!r}."
    return worker.run(_do)


@mcp.tool()
def preencher_lookup(seletor: str, valor: str) -> str:
    """Preenche um campo de lookup (busca por código/nome) usando o helper do projeto (preencher_campo)."""
    def _do():
        _exige_pagina()
        preencher_campo(_escopo(), seletor, valor)
        return f"Lookup {seletor!r} preenchido com {valor!r}."
    return worker.run(_do)


@mcp.tool()
def marcar_radio(name: str, value: str) -> str:
    """Marca um radio pelo name+value (ex.: name='inAdmDireta' value='S')."""
    def _do():
        _exige_pagina()
        _escopo().locator(f"input[name='{name}'][value='{value}']").check()
        return f"Radio {name}={value} marcado."
    return worker.run(_do)


@mcp.tool()
def screenshot() -> Image:
    """Captura a tela atual e retorna a imagem."""
    def _do():
        page = _exige_pagina()
        return page.screenshot(type="png")
    png = worker.run(_do)
    return Image(data=png, format="png")


@mcp.tool()
def fechar_navegador() -> str:
    """Fecha o contexto e o navegador."""
    def _do():
        if worker.context is not None:
            worker.context.close()
            worker.context = None
        if worker.browser is not None:
            worker.browser.close()
            worker.browser = None
        if worker.pw is not None:
            worker.pw.stop()
            worker.pw = None
        worker.page = None
        return "Navegador fechado."
    return worker.run(_do)


if __name__ == "__main__":
    mcp.run()
