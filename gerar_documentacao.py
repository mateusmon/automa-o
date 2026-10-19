"""
gerar_documentacao.py

Gera fluxogramas HTML (Mermaid) para:
  - Testes:  percorre tests/ e gera documentacao/fluxogramas/testes/
  - Genesis: percorre genesis/flows/ e gera documentacao/fluxogramas/genesis/,
             agrupando por rotina na ordem lida de genesis/routines/*.py

Um index.html unificado é gerado em documentacao/fluxogramas/ com abas
separando Testes e Genesis.

O mermaid.js vem de documentacao/fluxogramas/mermaid.min.js se o arquivo
existir; caso contrário, do CDN (nesse caso as páginas exigem internet).

Uso:
    python gerar_documentacao.py           # regenera tudo
    python gerar_documentacao.py testes    # somente testes
    python gerar_documentacao.py genesis   # somente genesis
"""

import ast
import sys
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuração de caminhos
#
# Ancorados na pasta do próprio script: rodar de outro diretório não pode
# fazer o gerador varrer o nada e reescrever o índice vazio em silêncio.
# ---------------------------------------------------------------------------

RAIZ               = Path(__file__).resolve().parent
TESTS_DIR          = RAIZ / "tests"
GENESIS_DIR        = RAIZ / "genesis" / "flows"
OUTPUT_DIR         = RAIZ / "documentacao" / "fluxogramas"
TESTS_OUTPUT_DIR   = OUTPUT_DIR / "testes"
GENESIS_OUTPUT_DIR = OUTPUT_DIR / "genesis"
CATALOG_PATH       = RAIZ / "gui" / "catalog" / "modules_catalog.py"

# Mermaid: usa a copia local se ela existir (funciona offline / sem CDN liberado),
# senao cai no CDN. Baixar com:
#   curl -o documentacao/fluxogramas/mermaid.min.js #        https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js
MERMAID_CDN   = "https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"
MERMAID_LOCAL = OUTPUT_DIR / "mermaid.min.js"


# ---------------------------------------------------------------------------
# Rotinas do Genesis
#
# A ordem dos flows NAO e mantida a mao aqui: ela e lida de
# genesis/routines/*.py, que e o que o Genesis executa de verdade. Uma lista
# fixa envelhece calada — flows novos somem no "Sem rotina definida" e flows
# removidos continuam aparecendo.
# ---------------------------------------------------------------------------

GENESIS_ROUTINES_DIR = RAIZ / "genesis" / "routines"

# Titulo exibido no indice para cada arquivo de rotina
_TITULO_ROTINA: dict[str, str] = {
    "link_user":  "Link User",
    "teste_user": "Teste User",
}

SEM_ROTINA = "Sem rotina definida"


# ---------------------------------------------------------------------------
# Utilitários gerais
# ---------------------------------------------------------------------------

_ACRONIMOS = {
    "ug", "ua", "ur", "ul", "cc", "um", "cr", "nf", "sei", "pdf",
    "asi", "cpf", "cnpj", "ir", "ui",
}


def snake_para_label(nome: str) -> str:
    partes = [p for p in nome.lstrip("_").split("_") if p]
    if not partes:
        return nome
    palavras = []
    for i, parte in enumerate(partes):
        if parte.lower() in _ACRONIMOS:
            palavras.append(parte.upper())
        elif i == 0:
            palavras.append(parte.capitalize())
        else:
            palavras.append(parte.lower())
    return " ".join(palavras)


def _esc(texto) -> str:
    """Rotulo seguro para Mermaid: aspas duplas + entidades para o que quebra o parser."""
    txt = " ".join(str(texto).split())
    txt = txt.replace("#", "#35;").replace('"', "#quot;")
    return f'"{txt}"'


def _mermaid_src(profundidade: int) -> str:
    """Caminho do mermaid.js para uma pagina a `profundidade` niveis do OUTPUT_DIR."""
    if MERMAID_LOCAL.exists():
        return "../" * profundidade + "mermaid.min.js"
    return MERMAID_CDN


def _nome_call(call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        obj = _nome_expr(call.func.value)
        return f"{obj}.{call.func.attr}" if obj else None
    return None


def _nome_expr(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_nome_expr(node.value)}.{node.attr}"
    return ""


# ===========================================================================
# TESTES — extração de passos
# ===========================================================================

def _coletar_funcoes(tree: ast.Module) -> dict:
    """Funcoes de nivel superior do modulo, na ordem em que aparecem no arquivo."""
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def extrair_funcoes_teste(filepath: Path) -> list[tuple[str, list[dict]]]:
    """Devolve [(nome_da_funcao_test, passos)] para TODAS as funcoes test_* do arquivo."""
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel parsear {filepath}: {e}")
        return []

    funcoes = _coletar_funcoes(tree)
    resultado: list[tuple[str, list[dict]]] = []
    for nome, node in funcoes.items():
        # Mesmo criterio do pytest (python_functions padrao = "test*"):
        # pega test_* e tambem os "teste_*" que existem na suite.
        if not nome.startswith("test"):
            continue
        passos: list[dict] = []
        _processar_body_teste(node.body, passos, funcoes, frozenset({nome}))
        resultado.append((nome, passos))
    return resultado


def _processar_body_teste(stmts, passos: list, funcoes: dict, expandindo: frozenset) -> None:
    for stmt in stmts:
        _processar_stmt_teste(stmt, passos, funcoes, expandindo)


def _processar_stmt_teste(stmt, passos: list, funcoes: dict, expandindo: frozenset) -> None:
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        _processar_call_teste(stmt.value, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) and isinstance(stmt.value, ast.Call):
        _processar_call_teste(stmt.value, passos, funcoes, expandindo)

    elif isinstance(stmt, ast.If):
        _processar_if_teste(stmt, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
        _processar_loop_teste(stmt, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.With, ast.AsyncWith)):
        _processar_body_teste(stmt.body, passos, funcoes, expandindo)

    elif isinstance(stmt, ast.Assert):
        msg = ""
        if stmt.msg and isinstance(stmt.msg, ast.Constant):
            msg = str(stmt.msg.value)[:60]
        cond = _label_condicao_teste(stmt.test)
        passos.append({"tipo": "assert", "condicao": cond, "mensagem": msg or "Assercao falhou"})

    elif isinstance(stmt, ast.Raise):
        passos.append({"tipo": "erro", "label": _label_raise(stmt)})

    elif isinstance(stmt, ast.Return):
        # `return` dentro de um helper expandido encerra o helper, nao o teste:
        # o fluxo volta para o chamador em vez de morrer ali.
        if len(expandindo) == 1:
            passos.append({"tipo": "terminal", "label": "Retorno antecipado"})
        else:
            passos.append({"tipo": "retorno_sub"})

    elif isinstance(stmt, ast.Try):
        _processar_body_teste(stmt.body, passos, funcoes, expandindo)
        _processar_body_teste(stmt.finalbody, passos, funcoes, expandindo)


def _processar_call_teste(call, passos: list, funcoes: dict, expandindo: frozenset) -> None:
    nome = _nome_call(call)
    if not nome:
        return

    if nome in ("pytest.skip", "pytest.xfail"):
        passos.append({"tipo": "terminal", "label": "Teste ignorado"})
        return
    if nome == "pytest.fail":
        passos.append({"tipo": "terminal", "label": "Teste falhou"})
        return

    if not _e_flow_teste(nome):
        return

    # Helper definido no proprio arquivo de teste -> expandir como sub-rotina.
    # `expandindo` corta recursao direta e mutua.
    if nome in funcoes and nome not in expandindo and not nome.startswith("test"):
        corpo: list[dict] = []
        _processar_body_teste(funcoes[nome].body, corpo, funcoes, expandindo | {nome})
        passos.append({"tipo": "sub", "label": snake_para_label(nome), "corpo": corpo})
        return

    passos.append({"tipo": "passo", "nome": nome})


def _processar_if_teste(stmt: ast.If, passos: list, funcoes: dict, expandindo: frozenset) -> None:
    cond = _label_condicao_teste(stmt.test)

    sim: list[dict] = []
    _processar_body_teste(stmt.body, sim, funcoes, expandindo)
    nao: list[dict] = []
    _processar_body_teste(stmt.orelse, nao, funcoes, expandindo)

    # Padrao "precondition skip": if not existe: pytest.skip() -> atalho lateral
    if not nao and len(sim) == 1 and sim[0]["tipo"] == "terminal":
        passos.append({"tipo": "gateway", "condicao": cond, "saida": sim[0]["label"]})
        return

    if not sim and not nao:
        return

    passos.append({"tipo": "ramo", "condicao": cond, "sim": sim, "nao": nao})


def _processar_loop_teste(stmt, passos: list, funcoes: dict, expandindo: frozenset) -> None:
    corpo: list[dict] = []
    _processar_body_teste(stmt.body, corpo, funcoes, expandindo)
    if not corpo:
        return
    passos.append({"tipo": "loop", "label": _label_loop(stmt), "corpo": corpo})


def _label_loop(stmt) -> str:
    if isinstance(stmt, ast.While):
        return f"Enquanto {_label_condicao_teste(stmt.test)}"
    if isinstance(stmt.iter, ast.Name):
        return f"Para cada {snake_para_label(stmt.iter.id)}"
    if isinstance(stmt.iter, ast.Attribute):
        return f"Para cada {snake_para_label(stmt.iter.attr)}"
    if isinstance(stmt.iter, ast.Call):
        nome = _nome_call(stmt.iter)
        if nome in ("enumerate", "reversed", "sorted") and stmt.iter.args:
            inner = stmt.iter.args[0]
            if isinstance(inner, ast.Name):
                return f"Para cada {snake_para_label(inner.id)}"
        if nome:
            return f"Para cada {snake_para_label(nome.split('.')[-1])}"
    return "Para cada item"


def _e_flow_teste(nome: str) -> bool:
    ignorar = {"contexto_cliente", "pytest", "logger", "page", "expect",
               "print", "len", "str", "int", "float", "list", "dict", "set", "tuple",
               "range", "enumerate", "zip", "sorted", "any", "all", "isinstance", "open"}
    raiz = nome.split(".")[0]
    return raiz not in ignorar and "." not in nome


_OPS_COMPARACAO = {
    ast.In: "contem", ast.NotIn: "nao contem",
    ast.Eq: "igual a", ast.NotEq: "diferente de",
    ast.Gt: ">", ast.GtE: ">=", ast.Lt: "<", ast.LtE: "<=",
    ast.Is: "e", ast.IsNot: "nao e",
}


def _label_operando(node) -> str:
    if isinstance(node, ast.Constant):
        return f"'{node.value}'" if isinstance(node.value, str) else str(node.value)
    if isinstance(node, ast.Name):
        return snake_para_label(node.id)
    if isinstance(node, ast.Attribute):
        return snake_para_label(node.attr)
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return str(node.slice.value)
    if isinstance(node, ast.Call):
        nome = _nome_call(node)
        if nome:
            return snake_para_label(nome.split(".")[-1])
    return ""


def _label_condicao_teste(test) -> str:
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        interno = _label_condicao_teste(test.operand)
        return f"nao {interno}" if interno != "condicao" else "condicao"

    if isinstance(test, ast.Name):
        return snake_para_label(test.id)

    if isinstance(test, ast.Attribute):
        return snake_para_label(test.attr)

    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        op = _OPS_COMPARACAO.get(type(test.ops[0]))
        esq = _label_operando(test.left)
        dir_ = _label_operando(test.comparators[0])
        if op and esq and dir_:
            # `x in y` le melhor como "y contem x"
            if isinstance(test.ops[0], (ast.In, ast.NotIn)):
                esq, dir_ = dir_, esq
            return f"{esq} {op} {dir_}"

    if isinstance(test, ast.Call):
        nome = _nome_call(test)
        # any(...)/all(...) sobre um gerador: usar a condicao de dentro
        if nome in ("any", "all") and test.args and isinstance(test.args[0], ast.GeneratorExp):
            interno = _label_condicao_teste(test.args[0].elt)
            if interno != "condicao":
                return f"{'algum' if nome == 'any' else 'todo'}: {interno}"
        return snake_para_label(nome.split(".")[-1]) if nome else "condicao"

    if isinstance(test, ast.BoolOp):
        juncao = " e " if isinstance(test.op, ast.And) else " ou "
        partes = [_label_condicao_teste(v) for v in test.values]
        if all(p != "condicao" for p in partes):
            return juncao.join(partes)

    return "condicao"


# ===========================================================================
# GENESIS — descoberta das rotinas
# ===========================================================================

def _resolver_fonte_flow(modulo: str) -> Path | None:
    """Modulo importado por uma rotina -> arquivo com a implementacao do flow.

    Duas formas convivem em genesis/flows/:
      flows.garantir_ua.dispatcher -> garantir_ua/v3.py   (pacote versionado)
      flows.garantir_uf_flow       -> garantir_uf_flow.py (arquivo unico)
    """
    if not modulo.startswith("flows."):
        return None

    partes = modulo.split(".")[1:]
    if partes and partes[-1] == "dispatcher":
        partes = partes[:-1]
    if not partes:
        return None

    alvo = GENESIS_DIR.joinpath(*partes)
    if alvo.is_dir():
        for candidato in ("v3.py", "v4.py", "dispatcher.py"):
            if (alvo / candidato).exists():
                return alvo / candidato
        return None

    arquivo = alvo.with_suffix(".py")
    return arquivo if arquivo.exists() else None


def _stmts_em_ordem(stmts):
    """Percorre um corpo de funcao em ordem de codigo, entrando em if/for/try."""
    for stmt in stmts:
        yield stmt
        for campo in ("body", "orelse", "finalbody"):
            filhos = getattr(stmt, campo, None)
            if isinstance(filhos, list):
                yield from _stmts_em_ordem(filhos)


def _nome_flow_de_arquivo(fonte: Path) -> str:
    """Nome do flow = primeira funcao publica do arquivo (o que a rotina importa)."""
    try:
        tree = ast.parse(fonte.read_text(encoding="utf-8"))
    except Exception:
        tree = None
    if tree is not None:
        for nome in _coletar_funcoes(tree):
            if not nome.startswith("_"):
                return nome
    stem = fonte.stem
    return stem[:-5] if stem.endswith("_flow") else stem


def _rotulo_fonte(fonte: Path) -> str:
    """Caminho do fonte relativo a genesis/flows/ — 'v3.py' sozinho e ambiguo."""
    try:
        return fonte.relative_to(GENESIS_DIR).as_posix()
    except ValueError:
        return fonte.name


def flows_genesis_em_disco() -> dict[str, Path]:
    """{nome_do_flow: arquivo_fonte} para tudo que existe em genesis/flows/."""
    encontrados: dict[str, Path] = {}
    if not GENESIS_DIR.is_dir():
        return encontrados

    for item in sorted(GENESIS_DIR.iterdir()):
        fonte = None
        if item.is_dir() and not item.name.startswith("__"):
            for candidato in ("v3.py", "v4.py"):
                if (item / candidato).exists():
                    fonte = item / candidato
                    break
        elif item.suffix == ".py" and not item.name.startswith("__"):
            fonte = item
        if fonte is not None:
            encontrados[_nome_flow_de_arquivo(fonte)] = fonte

    return encontrados


def descobrir_rotinas_genesis() -> dict[str, list[tuple[str, Path]]]:
    """{rotina: [(nome_do_flow, arquivo_fonte)]} na ordem em que run() os chama."""
    rotinas: dict[str, list[tuple[str, Path]]] = {}
    if not GENESIS_ROUTINES_DIR.is_dir():
        print(f"  [AVISO] Rotinas do Genesis nao encontradas em {GENESIS_ROUTINES_DIR}.")
        return rotinas

    for arquivo in sorted(GENESIS_ROUTINES_DIR.glob("*.py")):
        if arquivo.name.startswith("__"):
            continue
        try:
            tree = ast.parse(arquivo.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [AVISO] Nao foi possivel ler a rotina {arquivo.name}: {e}")
            continue

        # nome importado -> modulo de origem
        origem: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("flows."):
                for alias in node.names:
                    origem[alias.asname or alias.name] = node.module

        run = _coletar_funcoes(tree).get("run")
        if not run:
            continue

        ordem: list[tuple[str, Path]] = []
        vistos: set[str] = set()
        for stmt in _stmts_em_ordem(run.body):
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
                continue
            nome = _nome_call(stmt.value)
            if not nome or nome in vistos or nome not in origem:
                continue
            fonte = _resolver_fonte_flow(origem[nome])
            if fonte is None:
                print(f"  [AVISO] Flow '{nome}' da rotina {arquivo.stem} sem fonte em disco.")
                continue
            vistos.add(nome)
            ordem.append((nome, fonte))

        if ordem:
            rotinas[_TITULO_ROTINA.get(arquivo.stem, snake_para_label(arquivo.stem))] = ordem

    return rotinas


# ===========================================================================
# GENESIS — extração de passos
# ===========================================================================

_UTIL_LABELS: dict[str, str] = {
    "esperar_pagina_carregar":       "Esperar pagina carregar",
    "esperar_sucesso_ou_erro":       "Verificar sucesso ou erro",
    "preencher_autocomplete":        "Preencher autocomplete",
    "preencher_autocomplete_select": "Preencher autocomplete",
    "clicar_menu_com_retry":         "Abrir menu principal",
    "aguardar_ajax_global":          "Aguardar requisicao",
    "esperar_elemento_visivel":      "Verificar elemento visivel",
}

_GENESIS_IGNORAR = {
    "logger", "print", "len", "enumerate", "str", "int", "float",
    "list", "dict", "set", "tuple", "range", "isinstance",
}


def extrair_passos_genesis(filepath: Path) -> list[dict]:
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel parsear {filepath}: {e}")
        return []

    funcoes = _coletar_funcoes(tree)

    funcao_principal = next(
        (node for nome, node in funcoes.items() if not nome.startswith("_")),
        None
    )
    if not funcao_principal:
        return []

    passos: list[dict] = []
    _processar_body_genesis(funcao_principal.body, passos, funcoes,
                            frozenset({funcao_principal.name}))
    return passos


def _processar_body_genesis(stmts, passos: list, funcoes: dict, expandindo: frozenset):
    for stmt in stmts:
        _processar_stmt_genesis(stmt, passos, funcoes, expandindo)


def _processar_stmt_genesis(stmt, passos: list, funcoes: dict, expandindo: frozenset):
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        _processar_call_genesis(stmt.value, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) and isinstance(stmt.value, ast.Call):
        val = stmt.value
        if not _e_infra(val):
            _processar_call_genesis(val, passos, funcoes, expandindo)

    elif isinstance(stmt, ast.If):
        _processar_if_genesis(stmt, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
        _processar_for_genesis(stmt, passos, funcoes, expandindo)

    elif isinstance(stmt, (ast.With, ast.AsyncWith)):
        _processar_body_genesis(stmt.body, passos, funcoes, expandindo)

    elif isinstance(stmt, ast.Raise):
        passos.append({"tipo": "erro", "label": _label_raise(stmt)})

    elif isinstance(stmt, ast.Return):
        # Igual ao lado dos testes: `return` dentro de um helper expandido
        # encerra o helper, nao o flow — o fluxo volta para o chamador.
        if len(expandindo) == 1:
            passos.append({"tipo": "terminal", "label": "Ignorar flow"})
        else:
            passos.append({"tipo": "retorno_sub"})

    elif isinstance(stmt, ast.Continue):
        passos.append({"tipo": "terminal", "label": "Proximo item"})

    elif isinstance(stmt, ast.Try):
        _processar_body_genesis(stmt.body, passos, funcoes, expandindo)
        _processar_body_genesis(stmt.finalbody, passos, funcoes, expandindo)


def _processar_call_genesis(call, passos: list, funcoes: dict, expandindo: frozenset):
    nome = _nome_call(call)
    if not nome:
        return

    raiz = nome.split(".")[0]

    if raiz in _GENESIS_IGNORAR or "logger." in nome:
        return

    # Funcao privada do mesmo arquivo -> expandir como sub-rotina.
    # `expandindo` corta recursao direta e mutua (senao: RecursionError).
    if raiz.startswith("_") and raiz in funcoes and raiz not in expandindo:
        corpo: list[dict] = []
        _processar_body_genesis(funcoes[raiz].body, corpo, funcoes, expandindo | {raiz})
        passos.append({"tipo": "sub", "label": snake_para_label(raiz), "corpo": corpo})
        return

    # Utilitario conhecido
    if nome in _UTIL_LABELS:
        passos.append({"tipo": "passo", "nome": _UTIL_LABELS[nome]})
        return

    # Chamada Playwright
    label = _label_page_genesis(call)
    if label:
        passos.append({"tipo": "passo", "nome": label})
        return

    # Servicos externos (verificacoes de existencia) -> viram condicoes nos ifs
    if "existe" in nome or "service" in nome.lower():
        return

    # Qualquer outra funcao nao-trivial
    if "." not in nome:
        passos.append({"tipo": "passo", "nome": snake_para_label(nome)})


def _processar_if_genesis(stmt: ast.If, passos: list, funcoes: dict, expandindo: frozenset):
    cond = _label_condicao_genesis(stmt.test)

    sim: list[dict] = []
    _processar_body_genesis(stmt.body, sim, funcoes, expandindo)
    nao: list[dict] = []
    _processar_body_genesis(stmt.orelse, nao, funcoes, expandindo)

    # Guarda simples ("if nao ha dado: return" / "if invalido: raise"):
    # cabe num atalho lateral em vez de um ramo cheio.
    if not nao and len(sim) == 1:
        if sim[0]["tipo"] == "terminal":
            passos.append({"tipo": "gateway", "condicao": cond, "saida": sim[0]["label"]})
            return
        if sim[0]["tipo"] == "erro":
            passos.append({"tipo": "gateway_erro", "condicao": cond, "label_erro": sim[0]["label"]})
            return

    if not sim and not nao:
        return

    passos.append({"tipo": "ramo", "condicao": cond, "sim": sim, "nao": nao})


def _processar_for_genesis(stmt, passos: list, funcoes: dict, expandindo: frozenset):
    corpo: list[dict] = []
    _processar_body_genesis(stmt.body, corpo, funcoes, expandindo)
    if not corpo:
        return
    passos.append({"tipo": "loop", "label": _label_loop(stmt), "corpo": corpo})


def _e_infra(call) -> bool:
    nome = _nome_call(call)
    if not nome:
        return False
    return (nome.startswith("context.") or nome.startswith("blueprint.")
            or nome in {"next", "iter", "blueprint.get", "context.runtime_config"})


def _label_raise(stmt: ast.Raise) -> str:
    if stmt.exc and isinstance(stmt.exc, ast.Call) and stmt.exc.args:
        arg = stmt.exc.args[0]
        if isinstance(arg, ast.Constant):
            return str(arg.value)[:70]
        if isinstance(arg, ast.JoinedStr):
            return "Erro de validacao"
    return "Erro"


def _label_condicao_genesis(test) -> str:
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        inner = test.operand
        if isinstance(inner, ast.Name):
            return f"nao {snake_para_label(inner.id)}"
        if isinstance(inner, ast.Call):
            nome = _nome_call(inner)
            if nome:
                return f"nao {snake_para_label(nome.split('.')[-1])}"
    if isinstance(test, ast.Name):
        return snake_para_label(test.id)
    if isinstance(test, ast.Call):
        nome = _nome_call(test)
        if nome:
            return snake_para_label(nome.split(".")[-1])
    return "condicao"


def _label_page_genesis(call) -> str | None:
    func = call.func
    if not isinstance(func, ast.Attribute):
        return None

    method = func.attr
    obj = func.value

    # page.goto / page.fill / page.click diretos
    if isinstance(obj, ast.Name) and obj.id == "page":
        mapa = {"goto": "Navegar para URL", "fill": "Preencher campo",
                "click": "Clicar elemento", "check": "Marcar opcao", "type": "Digitar em campo"}
        return mapa.get(method)

    # Encadeado
    if isinstance(obj, ast.Call):
        if _get_root(obj) != "page":
            return None

        inner_func = obj.func
        if not isinstance(inner_func, ast.Attribute):
            return "Clicar elemento" if method == "click" else None

        inner_method = inner_func.attr

        if inner_method == "get_by_role":
            role = obj.args[0].value if obj.args and isinstance(obj.args[0], ast.Constant) else ""
            name_kw = next((kw.value for kw in obj.keywords if kw.arg == "name"), None)
            name = name_kw.value if isinstance(name_kw, ast.Constant) else ""
            if method == "click":
                if role == "link":
                    return f"Navegar: {name}" if name else "Navegar"
                if role == "button":
                    return f"Clicar: {name}" if name else "Clicar botao"
                return f"Interagir: {name}" if name else "Interagir"
            if method in ("fill", "type"):
                return "Preencher campo"
            if method == "check":
                return "Marcar opcao"
            return None

        if inner_method == "locator":
            mapa = {"click": "Clicar elemento", "fill": "Preencher campo",
                    "type": "Digitar em campo", "check": "Marcar opcao"}
            return mapa.get(method)

        if inner_method == "get_by_text" and method == "click":
            text = obj.args[0].value if obj.args and isinstance(obj.args[0], ast.Constant) else ""
            return f"Navegar: {text}" if text else "Clicar texto"

        if inner_method == "get_by_title" and method == "click":
            text = obj.args[0].value if obj.args and isinstance(obj.args[0], ast.Constant) else ""
            return f"Clicar: {text}" if text else "Clicar"

        # Cadeia mais profunda
        if method == "click":
            return "Clicar elemento"
        if method in ("fill", "type"):
            return "Preencher campo"

    return None


def _get_root(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _get_root(node.value)
    if isinstance(node, ast.Call):
        return _get_root(node.func)
    return ""


# ===========================================================================
# Geração de diagramas Mermaid
# ===========================================================================

def _conectar(linhas: list, fontes: list, alvo: str) -> None:
    for src, lbl in fontes:
        if lbl:
            linhas.append(f"    {src} -->|{_esc(lbl)}| {alvo}")
        else:
            linhas.append(f"    {src} --> {alvo}")


def _render_passos(passos: list[dict], linhas: list, nid, fontes: list,
                   genesis: bool, retornos: list | None = None) -> list:
    """Renderiza uma sequencia de passos. Devolve as pontas soltas do fluxo
    ([] quando todos os caminhos terminaram em skip/raise).

    `retornos` acumula as pontas de um `return` dentro de uma sub-rotina
    expandida: elas nao morrem, voltam para o chamador."""
    for passo in passos:
        tipo = passo["tipo"]

        if tipo == "passo":
            curr = nid()
            label = passo["nome"] if genesis else snake_para_label(passo["nome"])
            linhas.append(f"    {curr}[{_esc(label)}]")
            _conectar(linhas, fontes, curr)
            fontes = [(curr, None)]

        elif tipo == "sub":
            curr = nid()
            linhas.append(f"    {curr}[[{_esc(passo['label'])}]]")
            _conectar(linhas, fontes, curr)
            saidas: list = []
            pontas = _render_passos(passo.get("corpo") or [], linhas, nid,
                                    [(curr, None)], genesis, saidas)
            fontes = pontas + saidas

        elif tipo == "retorno_sub":
            if retornos is None:
                curr = nid()
                linhas.append(f'    {curr}(["Retorno antecipado"])')
                _conectar(linhas, fontes, curr)
            else:
                retornos.extend(fontes)
            return []

        elif tipo == "loop":
            curr = nid()
            linhas.append(f"    {curr}[/{_esc(passo['label'])}/]")
            _conectar(linhas, fontes, curr)
            corpo = passo.get("corpo") or []
            if corpo:
                pontas = _render_passos(corpo, linhas, nid,
                                        [(curr, "Para cada")], genesis, retornos)
                for src, _lbl in pontas:
                    linhas.append(f"    {src} --> {curr}")
                fontes = [(curr, "Concluido")]
            else:
                fontes = [(curr, None)]

        elif tipo == "ramo":
            curr = nid()
            linhas.append(f"    {curr}{{{_esc(str(passo['condicao']) + '?')}}}")
            _conectar(linhas, fontes, curr)
            f_sim = _render_passos(passo.get("sim") or [], linhas, nid,
                                   [(curr, "Sim")], genesis, retornos)
            f_nao = _render_passos(passo.get("nao") or [], linhas, nid,
                                   [(curr, "Nao")], genesis, retornos)
            fontes = f_sim + f_nao

        elif tipo == "gateway":
            curr = nid()
            saida_node = nid()
            linhas.append(f"    {curr}{{{_esc(str(passo['condicao']) + '?')}}}")
            _conectar(linhas, fontes, curr)
            linhas.append(f"    {saida_node}([{_esc(passo.get('saida', 'Saida'))}])")
            linhas.append(f'    {curr} -->|"Sim"| {saida_node}')
            fontes = [(curr, "Nao")]

        elif tipo == "gateway_erro":
            curr = nid()
            erro_node = nid()
            linhas.append(f"    {curr}{{{_esc(str(passo['condicao']) + '?')}}}")
            _conectar(linhas, fontes, curr)
            linhas.append(f"    {erro_node}([{_esc('Erro: ' + str(passo.get('label_erro', 'Erro')))}])")
            linhas.append(f'    {curr} -->|"Sim"| {erro_node}')
            fontes = [(curr, "Nao")]

        elif tipo == "assert":
            curr = nid()
            falha_node = nid()
            linhas.append(f"    {curr}{{{_esc(str(passo['condicao']) + '?')}}}")
            _conectar(linhas, fontes, curr)
            linhas.append(f"    {falha_node}([{_esc(passo.get('mensagem', 'Falha'))}])")
            linhas.append(f'    {curr} -->|"Nao"| {falha_node}')
            fontes = [(curr, "Sim")]

        elif tipo == "terminal":
            curr = nid()
            linhas.append(f"    {curr}([{_esc(passo['label'])}])")
            _conectar(linhas, fontes, curr)
            return []

        elif tipo == "erro":
            curr = nid()
            linhas.append(f"    {curr}([{_esc('Erro: ' + str(passo['label']))}])")
            _conectar(linhas, fontes, curr)
            return []

    return fontes


def passos_para_mermaid(passos: list[dict], genesis: bool = False) -> str:
    linhas = ["flowchart TD"]
    contador = [0]

    def nid() -> str:
        contador[0] += 1
        return f"N{contador[0]}"

    inicio = nid()
    linhas.append(f'    {inicio}(["Inicio"])')

    fontes = _render_passos(passos, linhas, nid, [(inicio, None)], genesis)

    if fontes:
        fim = nid()
        linhas.append(f'    {fim}(["Fim"])')
        _conectar(linhas, fontes, fim)

    return "\n".join(linhas)


# ===========================================================================
# TESTES — geração de HTML individual
# ===========================================================================

HTML_TESTE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<script src="{mermaid_src}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #222; padding: 40px 32px; }}
  .card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 32px; max-width: 900px; margin: 0 auto; }}
  .breadcrumb {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
  h1 {{ font-size: 22px; font-weight: 500; margin-bottom: 4px; }}
  .meta {{ font-size: 13px; color: #666; margin-bottom: 28px; border-bottom: 1px solid #eee; padding-bottom: 16px; }}
  .mermaid {{ display: flex; justify-content: center; margin-top: 8px; }}
  .fn {{ font-size: 13px; font-weight: 500; color: #888; font-family: monospace; margin: 24px 0 4px; }}
  .vazio {{ font-size: 13px; color: #b58900; background: #fffdf0; border: 1px solid #f0c040; border-radius: 6px; padding: 10px 14px; }}
  .back {{ display: inline-block; margin-top: 28px; font-size: 13px; color: #555; text-decoration: none; }}
  .back:hover {{ color: #000; }}
</style>
</head>
<body>
<div class="card">
  <p class="breadcrumb">{caminho}</p>
  <h1>{titulo}</h1>
  <p class="meta">Arquivo: <code>{arquivo}</code> &nbsp;.&nbsp; Gerado em {data}</p>
{diagramas}
  <a class="back" href="{link_index}">Voltar ao indice</a>
</div>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: 'default', flowchart: {{ curve: 'basis', useMaxWidth: true }} }});
</script>
</body>
</html>
"""


def gerar_html_teste(filepath: Path, tests_root: Path) -> str:
    funcoes = extrair_funcoes_teste(filepath)

    blocos: list[str] = []
    if not funcoes:
        blocos.append('  <p class="vazio">Nenhuma funcao <code>test_*</code> encontrada '
                      'neste arquivo.</p>')
    for nome_fn, passos in funcoes:
        if len(funcoes) > 1:
            blocos.append(f'  <p class="fn">{nome_fn}()</p>')
        if not passos:
            blocos.append('  <p class="vazio">Nenhum passo reconhecido — '
                          'o teste nao chama flows diretamente.</p>')
            continue
        blocos.append('  <div class="mermaid">\n'
                      + passos_para_mermaid(passos, genesis=False)
                      + '\n  </div>')
    diagramas = "\n".join(blocos)

    nome = filepath.stem
    titulo_raw = nome[5:] if nome.startswith("test_") else nome
    titulo = snake_para_label(titulo_raw)

    rel = filepath.relative_to(tests_root)
    partes = list(rel.parts[:-1])
    caminho = " > ".join(p.replace("_", " ").capitalize() for p in partes) or "Testes"

    # profundidade = partes de pasta + 1 (pela pasta testes/ acima)
    profundidade = len(rel.parts)
    link_index = "../" * profundidade + "index.html"

    return HTML_TESTE.format(
        titulo=titulo,
        caminho=caminho,
        arquivo=filepath.name,
        data=datetime.now().strftime("%d/%m/%Y %H:%M"),
        diagramas=diagramas,
        link_index=link_index,
        mermaid_src=_mermaid_src(profundidade),
    )


# ===========================================================================
# GENESIS — geração de HTML individual
# ===========================================================================

HTML_GENESIS = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<script src="{mermaid_src}"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #222; padding: 40px 32px; }}
  .card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 32px; max-width: 900px; margin: 0 auto; }}
  .badge {{ display: inline-block; font-size: 11px; font-weight: 500; background: #e8f0fe; color: #1a56cc; border-radius: 4px; padding: 2px 8px; margin-bottom: 10px; }}
  h1 {{ font-size: 22px; font-weight: 500; margin-bottom: 4px; }}
  .meta {{ font-size: 13px; color: #666; margin-bottom: 28px; border-bottom: 1px solid #eee; padding-bottom: 16px; }}
  .mermaid {{ display: flex; justify-content: center; margin-top: 8px; }}
  .legenda {{ font-size: 12px; color: #999; margin-top: 20px; border-top: 1px solid #f0f0f0; padding-top: 12px; }}
  .back {{ display: inline-block; margin-top: 16px; font-size: 13px; color: #555; text-decoration: none; }}
  .back:hover {{ color: #000; }}
</style>
</head>
<body>
<div class="card">
  <span class="badge">Genesis . {rotina}</span>
  <h1>{titulo}</h1>
  <p class="meta">Arquivo: <code>{arquivo}</code> &nbsp;.&nbsp; Gerado em {data}</p>
  <div class="mermaid">
{diagrama}
  </div>
  <p class="legenda">[[subroutine]] = funcao interna &nbsp;|&nbsp; /loop/ = iteracao &nbsp;|&nbsp; Erro = falha critica</p>
  <a class="back" href="../index.html">Voltar ao indice</a>
</div>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: 'default', flowchart: {{ curve: 'basis', useMaxWidth: true }} }});
</script>
</body>
</html>
"""


def gerar_html_genesis(flow_name: str, fonte: Path, rotina: str) -> str:
    passos = extrair_passos_genesis(fonte)
    diagrama = passos_para_mermaid(passos, genesis=True)
    titulo = snake_para_label(flow_name)

    return HTML_GENESIS.format(
        titulo=titulo,
        rotina=rotina,
        arquivo=_rotulo_fonte(fonte),
        data=datetime.now().strftime("%d/%m/%Y %H:%M"),
        diagrama=diagrama,
        mermaid_src=_mermaid_src(1),
    )


# ===========================================================================
# Catalogo de testes (para ordenacao do indice)
# ===========================================================================

def carregar_catalogo() -> dict:
    if not CATALOG_PATH.exists():
        print(f"  [AVISO] Catalogo nao encontrado em {CATALOG_PATH}. Indice sem ordenacao.")
        return {}
    try:
        spec = importlib.util.spec_from_file_location("modules_catalog", CATALOG_PATH)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "MODULES", {})
    except Exception as e:
        print(f"  [AVISO] Nao foi possivel carregar o catalogo: {e}.")
        return {}


def construir_indice_catalogo(modules: dict) -> dict[str, dict]:
    indice = {}
    for mi, (mn, md) in enumerate(modules.items()):
        for si, (sn, testes) in enumerate(md.get("sections", {}).items()):
            for ti, teste in enumerate(testes):
                path_raw = teste.get("path", "")
                if not path_raw:
                    continue
                indice[path_raw.replace("\\", "/")] = {
                    "modulo": mn, "secao": sn,
                    "nome": teste.get("name", ""),
                    "modulo_idx": mi, "secao_idx": si, "teste_idx": ti,
                }
    return indice


# ===========================================================================
# INDEX — HTML unificado com abas Testes / Genesis
# ===========================================================================

def gerar_index(
    tests_root: Path,
    arquivos_teste: list[Path],
    genesis_gerados: list[dict],
):
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_testes  = len(arquivos_teste)
    total_genesis = len(genesis_gerados)

    conteudo_testes  = _html_testes(tests_root, arquivos_teste)
    conteudo_genesis = _html_genesis(genesis_gerados)

    html = f"""\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fluxogramas - ASI Automacao</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #222; padding: 40px 32px; }}
  .header {{ max-width: 960px; margin: 0 auto 24px; }}
  .header h1 {{ font-size: 26px; font-weight: 500; }}
  .header p {{ font-size: 14px; color: #666; margin-top: 6px; }}
  .tabs {{ max-width: 960px; margin: 0 auto 24px; display: flex; gap: 8px; }}
  .tab-btn {{
    padding: 8px 20px; font-size: 14px; font-family: inherit;
    border: 1px solid #ddd; border-radius: 8px; background: #fff;
    cursor: pointer; color: #555; transition: all 0.15s;
  }}
  .tab-btn:hover {{ border-color: #aaa; color: #222; }}
  .tab-btn.ativo {{ background: #222; color: #fff; border-color: #222; }}
  .tab-count {{ font-size: 11px; opacity: 0.7; margin-left: 4px; }}
  .busca-wrap {{ max-width: 960px; margin: 0 auto 24px; }}
  .busca-wrap input {{
    width: 100%; padding: 10px 16px; font-size: 14px;
    border: 1px solid #ddd; border-radius: 8px; outline: none;
    font-family: inherit; background: #fff; color: #222;
  }}
  .busca-wrap input:focus {{ border-color: #888; }}
  .sem-resultado {{ display: none; max-width: 960px; margin: 0 auto 16px; font-size: 14px; color: #888; }}
  .lista {{ max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }}
  .modulo {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 24px 28px; }}
  .sem-categoria {{ border-color: #f0c040; background: #fffdf0; }}
  .modulo h2 {{ font-size: 17px; font-weight: 500; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
  .modulo h3 {{ font-size: 12px; font-weight: 500; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px; }}
  .modulo h3:first-of-type {{ margin-top: 4px; }}
  .modulo ul {{ list-style: none; }}
  .item {{ display: flex; align-items: baseline; justify-content: space-between; gap: 16px; padding: 7px 0; border-bottom: 1px solid #f2f2f2; }}
  .item:last-child {{ border-bottom: none; }}
  .item a {{ font-size: 14px; color: #1a1a1a; text-decoration: none; flex: 1; }}
  .item a:hover {{ color: #0055cc; text-decoration: underline; }}
  .arquivo {{ font-size: 11px; color: #bbb; white-space: nowrap; font-family: monospace; flex-shrink: 0; }}
  .footer {{ max-width: 960px; margin: 32px auto 0; font-size: 12px; color: #aaa; }}
  .oculto {{ display: none !important; }}
  .tab-panel {{ display: none; }}
  .tab-panel.ativo {{ display: block; }}
</style>
</head>
<body>
<div class="header">
  <h1>Fluxogramas - ASI Automacao</h1>
  <p>Ultima atualizacao: {data}</p>
</div>
<div class="tabs">
  <button class="tab-btn ativo" onclick="trocarAba('testes', this)">
    Testes <span class="tab-count">({total_testes})</span>
  </button>
  <button class="tab-btn" onclick="trocarAba('genesis', this)">
    Genesis <span class="tab-count">({total_genesis})</span>
  </button>
</div>
<div class="busca-wrap">
  <input type="text" id="busca" placeholder="Pesquisar..." autocomplete="off">
</div>
<p class="sem-resultado" id="sem-resultado">Nenhum resultado encontrado.</p>

<div id="tab-testes" class="tab-panel ativo">
  <div class="lista" id="lista-testes">
{conteudo_testes}
  </div>
</div>
<div id="tab-genesis" class="tab-panel">
  <div class="lista" id="lista-genesis">
{conteudo_genesis}
  </div>
</div>

<p class="footer">Gerado automaticamente por gerar_documentacao.py</p>
<script>
  let abaAtiva = 'testes';

  function trocarAba(aba, btn) {{
    abaAtiva = aba;
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('ativo'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('ativo'));
    document.getElementById('tab-' + aba).classList.add('ativo');
    btn.classList.add('ativo');
    document.getElementById('busca').value = '';
    document.getElementById('sem-resultado').style.display = 'none';
    filtrar('');
  }}

  function filtrar(termo) {{
    const lista = document.getElementById('lista-' + abaAtiva);
    if (!lista) return;
    let totalVisiveis = 0;

    lista.querySelectorAll('.modulo').forEach(modulo => {{
      const itens = modulo.querySelectorAll('.item');
      let visiveis = 0;
      itens.forEach(item => {{
        const bate = !termo || item.textContent.toLowerCase().includes(termo);
        item.classList.toggle('oculto', !bate);
        if (bate) visiveis++;
      }});
      modulo.querySelectorAll('h3').forEach(h3 => {{
        let ul = h3.nextElementSibling;
        while (ul && ul.tagName !== 'UL') ul = ul.nextElementSibling;
        if (!ul) return;
        h3.classList.toggle('oculto', !ul.querySelector('.item:not(.oculto)'));
      }});
      modulo.classList.toggle('oculto', visiveis === 0);
      totalVisiveis += visiveis;
    }});

    document.getElementById('sem-resultado').style.display =
      (termo && totalVisiveis === 0) ? 'block' : 'none';
  }}

  document.getElementById('busca').addEventListener('input', function() {{
    filtrar(this.value.trim().toLowerCase());
  }});
</script>
</body>
</html>
"""
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"  index.html atualizado ({total_testes} testes, {total_genesis} flows Genesis)")


def _html_testes(tests_root: Path, arquivos: list[Path]) -> str:
    modules = carregar_catalogo()
    indice_cat = construir_indice_catalogo(modules)

    entradas = []
    for filepath in arquivos:
        rel = filepath.relative_to(tests_root)
        path_cat = f"tests/{rel.as_posix()}"          # chave do modules_catalog
        href     = f"testes/{rel.with_suffix('.html').as_posix()}"
        nome = filepath.stem
        titulo_raw = nome[5:] if nome.startswith("test_") else nome

        if path_cat in indice_cat:
            meta = indice_cat[path_cat]
            entradas.append({
                "modulo": meta["modulo"], "secao": meta["secao"],
                "titulo": meta["nome"] or snake_para_label(titulo_raw),
                "href": href, "arquivo": filepath.name,
                "modulo_idx": meta["modulo_idx"], "secao_idx": meta["secao_idx"],
                "teste_idx": meta["teste_idx"], "sem_categoria": False,
            })
        else:
            partes = list(rel.parts)
            modulo_p = partes[0].replace("_", " ").capitalize() if len(partes) > 1 else "Raiz"
            secao_p  = " > ".join(p.replace("_", " ").capitalize() for p in partes[1:-1])
            entradas.append({
                "modulo": modulo_p, "secao": secao_p,
                "titulo": snake_para_label(titulo_raw),
                "href": href, "arquivo": filepath.name,
                "modulo_idx": 99999, "secao_idx": 99999,
                "teste_idx": 99999, "sem_categoria": True,
            })

    entradas.sort(key=lambda e: (
        e["sem_categoria"], e["modulo_idx"], e["secao_idx"], e["teste_idx"]
    ))

    hier: dict[str, dict[str, list]] = {}
    mod_order: list[str] = []
    sec_order: dict[str, list] = {}

    for e in entradas:
        mod = e["modulo"] + (" [Sem catalogo]" if e["sem_categoria"] else "")
        sec = e["secao"] or e["modulo"]
        if mod not in hier:
            hier[mod] = {}
            mod_order.append(mod)
            sec_order[mod] = []
        if sec not in hier[mod]:
            hier[mod][sec] = []
            sec_order[mod].append(sec)
        hier[mod][sec].append(e)

    linhas = []
    for mod in mod_order:
        eh_sc = "Sem catalogo" in mod
        linhas.append(f'<div class="{"modulo sem-categoria" if eh_sc else "modulo"}">')
        linhas.append(f'  <h2>{mod}</h2>')
        for sec in sec_order[mod]:
            itens = hier[mod][sec]
            nome_sec = sec if sec != mod.split(" [")[0] else ""
            if nome_sec:
                linhas.append(f'  <h3>{nome_sec}</h3>')
            linhas.append('  <ul>')
            for item in itens:
                linhas.append(
                    f'    <li class="item"><a href="{item["href"]}">{item["titulo"]}</a>'
                    f'<span class="arquivo">{item["arquivo"]}</span></li>'
                )
            linhas.append('  </ul>')
        linhas.append('</div>')

    return "\n".join(linhas)


def _html_genesis(genesis_gerados: list[dict]) -> str:
    # `genesis_gerados` ja vem na ordem das rotinas (a mesma que o Genesis executa),
    # com "Sem rotina definida" por ultimo — basta agrupar preservando essa ordem.
    rotinas: dict[str, list] = {}
    for g in genesis_gerados:
        rotinas.setdefault(g["rotina"], []).append(g)

    linhas = []
    for rotina, itens in rotinas.items():
        classe = "modulo sem-categoria" if rotina == SEM_ROTINA else "modulo"
        linhas.append(f'<div class="{classe}">')
        linhas.append(f'  <h2>{rotina}</h2>')
        linhas.append('  <ul>')
        for item in itens:
            linhas.append(
                f'    <li class="item"><a href="{item["href"]}">{item["titulo"]}</a>'
                f'<span class="arquivo">{item["arquivo"]}</span></li>'
            )
        linhas.append('  </ul>')
        linhas.append('</div>')

    return "\n".join(linhas)


# ===========================================================================
# Execucao principal
# ===========================================================================

def _entradas_genesis() -> list[tuple[str, Path, str]]:
    """[(nome_do_flow, fonte, rotina)] — rotinas primeiro, na ordem de execucao;
    depois o que existe em disco e nenhuma rotina chama."""
    entradas: list[tuple[str, Path, str]] = []
    vistos: set[str] = set()

    for rotina, itens in descobrir_rotinas_genesis().items():
        for nome, fonte in itens:
            if nome in vistos:
                continue
            vistos.add(nome)
            entradas.append((nome, fonte, rotina))

    por_nome = {nome: fonte for nome, fonte, _ in entradas}
    for nome, fonte in flows_genesis_em_disco().items():
        if nome in vistos:
            # Mesmo nome vindo de outro arquivo sobrescreveria o HTML do primeiro.
            if por_nome.get(nome) != fonte:
                print(f"  [AVISO] Dois flows chamados '{nome}': "
                      f"{_rotulo_fonte(por_nome[nome])} e {_rotulo_fonte(fonte)}. "
                      f"Documentando so o primeiro.")
            continue
        vistos.add(nome)
        entradas.append((nome, fonte, SEM_ROTINA))

    return entradas


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if modo not in ("tudo", "testes", "genesis"):
        print(f"[ERRO] Argumento invalido: '{modo}'. Use: testes, genesis, ou nenhum argumento.")
        sys.exit(1)

    rodar_testes  = modo in ("tudo", "testes")
    rodar_genesis = modo in ("tudo", "genesis")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GENESIS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    todos_testes    = sorted(TESTS_DIR.rglob("test_*.py")) if TESTS_DIR.exists() else []
    genesis_gerados: list[dict] = []

    # --- TESTES ---
    if rodar_testes:
        if not TESTS_DIR.exists():
            print(f"[AVISO] Pasta nao encontrada: {TESTS_DIR}")
        else:
            arquivos = sorted(TESTS_DIR.rglob("test_*.py"))
            print(f"Testes: {len(arquivos)} arquivos em '{TESTS_DIR}'\n")
            # Limpa a saida anterior: testes renomeados/removidos deixavam HTML
            # orfao para sempre, e o indice continuava apontando para eles.
            shutil.rmtree(TESTS_OUTPUT_DIR, ignore_errors=True)
            TESTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            ok, err = 0, 0
            for filepath in arquivos:
                rel = filepath.relative_to(TESTS_DIR)
                out = TESTS_OUTPUT_DIR / rel.with_suffix(".html")
                out.parent.mkdir(parents=True, exist_ok=True)
                try:
                    out.write_text(gerar_html_teste(filepath, TESTS_DIR), encoding="utf-8")
                    print(f"  + testes/{rel}")
                    ok += 1
                except Exception as e:
                    print(f"  x testes/{rel} - {e}")
                    err += 1
            print(f"\nTestes: {ok} gerados, {err} erros.\n")

    # --- GENESIS ---
    if rodar_genesis:
        if not GENESIS_DIR.exists():
            print(f"[AVISO] Pasta nao encontrada: {GENESIS_DIR}")
        else:
            entradas = _entradas_genesis()

            print(f"Genesis: {len(entradas)} flows em '{GENESIS_DIR}'\n")
            shutil.rmtree(GENESIS_OUTPUT_DIR, ignore_errors=True)
            GENESIS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            ok, err = 0, 0

            for flow_name, fonte, rotina in entradas:
                out = GENESIS_OUTPUT_DIR / f"{flow_name}.html"
                try:
                    out.write_text(gerar_html_genesis(flow_name, fonte, rotina), encoding="utf-8")
                    genesis_gerados.append({
                        "flow_name": flow_name,
                        "rotina":    rotina,
                        "titulo":    snake_para_label(flow_name),
                        "href":      f"genesis/{flow_name}.html",
                        "arquivo":   _rotulo_fonte(fonte),
                    })
                    print(f"  + genesis/{flow_name}.html   [{rotina}]")
                    ok += 1
                except Exception as e:
                    print(f"  x genesis/{flow_name} - {e}")
                    err += 1

            print(f"\nGenesis: {ok} gerados, {err} erros.\n")
    else:
        # Reconstruir lista Genesis a partir dos HTMLs existentes para o indice
        for flow_name, fonte, rotina in _entradas_genesis():
            if not (GENESIS_OUTPUT_DIR / f"{flow_name}.html").exists():
                continue
            genesis_gerados.append({
                "flow_name": flow_name,
                "rotina":    rotina,
                "titulo":    snake_para_label(flow_name),
                "href":      f"genesis/{flow_name}.html",
                "arquivo":   _rotulo_fonte(fonte),
            })

    # --- INDICE ---
    # Rodando so 'genesis', os HTMLs de teste sao os da rodada anterior: listar
    # um teste sem HTML gerado produziria link quebrado no indice.
    if not rodar_testes:
        todos_testes = [
            f for f in todos_testes
            if (TESTS_OUTPUT_DIR / f.relative_to(TESTS_DIR).with_suffix(".html")).exists()
        ]

    print("Atualizando indice...")
    gerar_index(
        tests_root=TESTS_DIR,
        arquivos_teste=todos_testes,
        genesis_gerados=genesis_gerados,
    )
    print("\nConcluido.")


if __name__ == "__main__":
    main()
