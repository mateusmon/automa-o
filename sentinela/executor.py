"""
Executa um único teste via subprocess + pytest.
Gerencia escrita/restauração do configs.local.yaml.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

from models import ResultadoTeste

_raiz = Path(__file__).resolve().parent.parent
_config_local = _raiz / "configs" / "configs.local.yaml"
_trace_dir = _raiz / "trace"
_evidencia_dir = _raiz / "evidencia"


def _decodificar(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


_PREFIXOS_EXCECAO = (
    "RuntimeError:",
    "AssertionError:",
    "TimeoutError:",
    "Failed",  # pytest.fail(), com ou sem mensagem
    "playwright._impl",
)

# Linha do "short test summary info": `FAILED <nodeid> - <erro>`.
_PREFIXOS_RESUMO_PYTEST = ("FAILED ", "ERROR ")


def executar_teste(
    path_teste: str,
    cliente_id: str,
    tentativa: int,
    max_tentativas: int,
    headless: bool = False,
    pausa: bool = False,
    ocorrencia: int = 1,
    execution_id: str | None = None,
) -> ResultadoTeste:
    nome = Path(path_teste).stem

    inicio = time.perf_counter()
    inicio_unix = time.time()
    saida = ""
    codigo_saida = 1

    try:
        cmd = [sys.executable, "-m", "pytest", path_teste, "-s", "--tb=long"]
        if headless:
            cmd.append("--headless")

        env = os.environ.copy()
        env["ASI_PAUSAR_NA_FALHA"] = "1" if pausa else "0"
        env["ASI_POSICAO_ORDEM"] = str(ocorrencia)
        env["ASI_CLIENTE_ATIVO"] = cliente_id
        capture_id = uuid4().hex[:12]
        env["ASI_TRACE_CAPTURE_ID"] = capture_id
        if execution_id:
            env["ASI_EXECUTION_ID"] = execution_id

        resultado = subprocess.run(
            cmd,
            cwd=str(_raiz),
            capture_output=True,
            env=env,
        )
        saida = _decodificar(resultado.stdout) + _decodificar(resultado.stderr)
        codigo_saida = resultado.returncode

    finally:
        duracao = time.perf_counter() - inicio

    if codigo_saida == 0:
        if " skipped" in saida:
            status = "skip"
        else:
            status = "passou"
    else:
        status = "falhou"

    screenshot_path: Path | None = None
    erro_resumo = ""

    prefixo = _prefixo_artefato(path_teste)
    trace_root = _trace_dir / execution_id if execution_id else _trace_dir
    trace_paths = _encontrar_artefatos(trace_root, f"{prefixo}*.zip", inicio_unix, capture_id)

    if status == "falhou":
        evidence_root = _evidencia_dir / execution_id if execution_id else _evidencia_dir
        if not trace_paths and "Trace salvo em:" in saida:
            trace_global = _encontrar_artefato(trace_root, f"{prefixo}*.zip", inicio_unix)
            if trace_global:
                trace_paths = [trace_global]
        screenshot_path = _encontrar_artefato(evidence_root, f"falha-{prefixo}*.png", inicio_unix)
        erro_resumo = _extrair_erro_resumo(saida)

    return ResultadoTeste(
        path=path_teste,
        nome=nome,
        status=status,
        duracao=duracao,
        tentativa=tentativa,
        max_tentativas=max_tentativas,
        saida=saida,
        trace_paths=trace_paths,
        screenshot_path=screenshot_path,
        erro_resumo=erro_resumo,
    )


def _prefixo_artefato(path_teste: str) -> str:
    """
    Reproduz o nome que o conftest dá aos artefatos de falha desse teste.

    O conftest deriva o nome do nodeid (`_nome_do_artefato`): troca "::" por "__"
    e separadores de path por "_". Como aqui só conhecemos o arquivo, e não a
    função de teste, devolvemos o prefixo até o "__" e deixamos o resto para o glob.
    """
    return path_teste.replace("\\", "/").replace("/", "_") + "__"


def _encontrar_artefato(base: Path, padrao: str, desde: float) -> Path | None:
    """
    Localiza o artefato deste teste, gerado nesta execução.

    O casamento é por NOME, não por "o mais recente da pasta": a heurística
    antiga pegava o arquivo de outro teste sempre que houvesse execução paralela.
    O filtro por mtime continua, mas agora só serve para descartar artefatos de
    tentativas anteriores do mesmo teste.
    """
    if not base.exists():
        return None

    candidatos = [p for p in base.rglob(padrao) if p.stat().st_mtime >= desde]

    if not candidatos:
        return None

    return max(candidatos, key=lambda p: p.stat().st_mtime)


def _encontrar_artefatos(base: Path, padrao: str, desde: float, capture_id: str) -> list[Path]:
    """Encontra todos os traces deste teste produzidos durante a tentativa."""
    if not base.exists():
        return []
    return sorted(
        (
            p for p in base.rglob(padrao)
            if p.is_file() and not p.is_symlink()
            and p.stat().st_mtime >= desde
            and (p.stem.endswith(f"_{capture_id}") or f"_{capture_id}_" in p.stem)
        ),
        key=lambda p: (p.stat().st_mtime, p.name),
    )


def _sem_marcador_pytest(linha: str) -> str:
    """
    Remove o "E" que o pytest põe na frente das linhas de exceção do traceback.

    O pytest escreve `E       RuntimeError: boom`. Sem tirar esse marcador nenhum
    padrão de `_PREFIXOS_EXCECAO` casava, e o resumo caía sempre no fallback — a
    última linha da saída, ou seja o inútil "1 failed in 35.38s".
    """
    texto = linha.strip()

    if texto == "E" or texto.startswith("E "):
        texto = texto[1:].strip()

    return texto


def _extrair_erro_resumo(saida: str) -> str:
    """
    Extrai a mensagem de erro de uma execução que falhou.

    Prioriza a linha do "short test summary info" do próprio pytest
    (`FAILED <nodeid> - <erro>`): ela já vem pronta e cobre qualquer tipo de
    exceção, sem depender de manter uma lista de prefixos em dia. O rastreio do
    traceback fica como plano B, para saídas truncadas ou sem o sumário.
    """
    linhas = [linha for linha in saida.splitlines() if linha.strip()]

    for linha in reversed(linhas):
        texto = linha.strip()
        if texto.startswith(_PREFIXOS_RESUMO_PYTEST) and " - " in texto:
            return texto.split(" - ", 1)[1][:200]

    for linha in reversed(linhas):
        texto = _sem_marcador_pytest(linha)
        if texto.startswith(_PREFIXOS_EXCECAO):
            return texto[:200]

    return linhas[-1].strip()[:200] if linhas else ""
