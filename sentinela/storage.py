"""
Persiste runs e aplica limpeza por TTL.
"""
import hashlib
import json
import os
import re
import shutil
import ctypes
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

_sentinela_dir = Path(__file__).resolve().parent
_reports_dir = _sentinela_dir / "reports"
_CONTROL_COMMANDS = {"pause", "resume", "stop"}


def _processo_ativo(pid: int) -> bool:
    """Consulta PID sem enviar sinal de encerramento no Windows."""
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel32.GetExitCodeProcess.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ulong),
        )
        kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = kernel32.OpenProcess(0x1000, 0, pid)
        if not handle:
            return ctypes.get_last_error() != 87
        try:
            exit_code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return True
            return exit_code.value == 259
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def ler_comando_controle(run_dir: Path, execution_id: str) -> str | None:
    """Lê comando válido somente do arquivo pertencente ao run e à identidade."""
    try:
        execution_id = validar_execution_id(execution_id)
        resolved_reports = _reports_dir.resolve(strict=True)
        if run_dir.is_symlink():
            return None
        resolved_run = run_dir.resolve(strict=True)
        resolved_run.relative_to(resolved_reports)
        if not resolved_run.is_dir() or not _nome_pertence_ao_id(resolved_run.name, execution_id):
            return None
        owner_path = resolved_run / ".execution-id"
        if owner_path.is_symlink() or owner_path.read_text(encoding="ascii") != execution_id:
            return None
        control_path = resolved_reports / f".gui-control-{execution_id}.json"
        if control_path.is_symlink() or not control_path.is_file():
            return None
        payload = json.loads(control_path.read_text(encoding="utf-8"))
        if (
            not isinstance(payload, dict)
            or type(payload.get("schema_version")) is not int
            or payload.get("schema_version") != 1
            or payload.get("execution_id") != execution_id
            or not isinstance(payload.get("command"), str)
            or payload.get("command") not in _CONTROL_COMMANDS
        ):
            return None
        return payload["command"]
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        # Arquivo ausente, parcial ou inválido não altera o fluxo da execução.
        return None


def limpar_runs_antigos(ttl_dias: int) -> None:
    """Remove runs antigos, preservando os que ainda têm processo proprietário vivo."""
    if not _reports_dir.exists():
        return
    limite = datetime.now() - timedelta(days=ttl_dias)
    for entry in _reports_dir.iterdir():
        if not entry.is_dir():
            continue
        data = _parsear_data_run(entry.name)
        if data is None or data >= limite:
            continue
        active_marker = entry / ".active-pid"
        if active_marker.is_file() and not active_marker.is_symlink():
            try:
                active_pid = int(active_marker.read_text(encoding="ascii"))
                if _processo_ativo(active_pid):
                    continue
            except (OSError, ValueError, UnicodeError):
                pass
        shutil.rmtree(entry, ignore_errors=True)


def marcar_run_ativo(run_dir: Path) -> Path:
    """Marca o processo proprietário para impedir limpeza TTL de run em uso."""
    marker = run_dir / ".active-pid"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".active-pid-", suffix=".tmp", dir=run_dir
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii", newline="\n") as stream:
            stream.write(str(os.getpid()))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, marker)
    finally:
        temporary_path.unlink(missing_ok=True)
    return marker


def validar_execution_id(execution_id: str) -> str:
    """Valida e normaliza um UUID usado como identidade de execução."""
    try:
        return UUID(execution_id).hex
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError("execution_id deve ser um UUID válido.") from error


def _nome_pertence_ao_id(nome: str, execution_id: str) -> bool:
    """Aceita o formato atual e pastas antigas com o UUID completo."""
    return nome.endswith(f"_{execution_id[:8]}") or nome.endswith(f"_{execution_id}")


def _escopo_run(modulo: str | None = None, path_teste: str | None = None) -> str:
    origem = path_teste or modulo or "todos_modulos"
    partes = origem.replace("\\", "/").strip("/").split("/")
    if partes and partes[0] == "tests":
        partes.pop(0)
    if path_teste and partes:
        partes[-1] = Path(partes[-1]).stem
    escopo = re.sub(r"[^a-zA-Z0-9_-]", "_", "_".join(partes)) or "todos_modulos"
    if len(escopo) > 48:
        resumo = hashlib.sha256(escopo.encode("utf-8")).hexdigest()[:6]
        escopo = f"{escopo[:41]}_{resumo}"
    return escopo


def _run_pertence_ao_cliente_e_id(path: Path, cliente_id: str, execution_id: str) -> bool:
    if (
        not path.is_dir()
        or path.is_symlink()
        or not path.name.split("_", 2)[-1].startswith(f"{cliente_id}_")
        or not _nome_pertence_ao_id(path.name, execution_id)
    ):
        return False
    try:
        owner = path / ".execution-id"
        return not owner.is_symlink() and owner.read_text(encoding="ascii") == execution_id
    except (OSError, UnicodeError):
        return False


def criar_diretorio_run(
    cliente_id: str,
    execution_id: str | None = None,
    *,
    modulo: str | None = None,
    path_teste: str | None = None,
) -> Path:
    """Cria uma pasta exclusiva identificando cliente e escopo da execução."""
    _reports_dir.mkdir(parents=True, exist_ok=True)
    execution_id = validar_execution_id(execution_id) if execution_id else None
    if execution_id and any(
        _run_pertence_ao_cliente_e_id(path, cliente_id, execution_id)
        for path in _reports_dir.iterdir()
    ):
        raise FileExistsError(f"Já existe um run para este execution_id: {execution_id}")
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    base = f"{timestamp}_{cliente_id}_{_escopo_run(modulo, path_teste)}"
    suffix = f"_{execution_id[:8]}" if execution_id else ""
    for collision in range(1000):
        extra = f"_{collision}" if collision else ""
        run_dir = _reports_dir / f"{base}{extra}{suffix}"
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        if execution_id:
            (run_dir / ".execution-id").write_text(execution_id, encoding="ascii")
        return run_dir
    raise FileExistsError(f"Não foi possível criar pasta exclusiva para: {base}")


def salvar_log(run_dir: Path, nome_teste: str, tentativa: int, conteudo: str) -> Path:
    """Salva o log de uma tentativa. Retorna o path do arquivo salvo."""
    caminho = run_dir / f"{nome_teste}_{tentativa}.log"
    caminho.write_text(conteudo, encoding="utf-8", errors="replace")
    return caminho


def _mover_artefato(destino: Path, origem: Path, rotulo: str) -> Path | None:
    """
    Move um artefato para o diretório do run. Retorna o novo path ou None se falhar.

    A sentinela MOVE o que precisa para dentro de `sentinela/reports/`, e nunca
    apaga nada em `evidencia/`, `trace/` ou `logs/` — essas pastas pertencem à
    suíte principal, que tem a própria política de retenção. Um único dono por
    pasta evita o clássico "quem apagou meu arquivo?".
    """
    if not origem.exists():
        return None

    try:
        shutil.move(str(origem), destino)
        return destino
    except OSError as e:
        # Sem isso a falha vira "sem artefato" no relatório, sem nenhuma pista.
        print(f"    ! Falha ao mover {rotulo} de {origem.name}: {e}")
        return None


def mover_trace(
    run_dir: Path,
    nome_teste: str,
    trace_origem: Path,
    tentativa: int | None = None,
) -> Path | None:
    """Move o trace .zip para o diretório do run. Retorna o novo path ou None se falhar."""
    sufixo = f"_tentativa_{tentativa}" if tentativa is not None else ""
    partes = trace_origem.stem.split("__", 2)
    chunk = f"_{partes[2][:6]}_{partes[2].rsplit('_', 1)[-1]}" if len(partes) == 3 else ""
    return _mover_artefato(run_dir / f"{nome_teste}{sufixo}{chunk}_trace.zip", trace_origem, "trace")


def mover_screenshot(
    run_dir: Path,
    nome_teste: str,
    screenshot_origem: Path,
    tentativa: int | None = None,
) -> Path | None:
    """Move o screenshot .png para o diretório do run. Retorna o novo path ou None se falhar."""
    sufixo = f"_tentativa_{tentativa}" if tentativa is not None else ""
    return _mover_artefato(run_dir / f"{nome_teste}{sufixo}_falha.png", screenshot_origem, "screenshot")


def limpar_todos_runs() -> None:
    """Remove runs sem processo proprietário ativo, independente do TTL."""
    if not _reports_dir.exists():
        return
    for entry in _reports_dir.iterdir():
        if not entry.is_dir() or entry.is_symlink():
            continue
        active_marker = entry / ".active-pid"
        if active_marker.is_file() and not active_marker.is_symlink():
            try:
                active_pid = int(active_marker.read_text(encoding="ascii"))
                if _processo_ativo(active_pid):
                    continue
            except (OSError, ValueError, UnicodeError):
                pass
        shutil.rmtree(entry, ignore_errors=True)


def _parsear_data_run(nome: str) -> datetime | None:
    # Formatos: YYYY-MM-DD_HHhMM_cliente legado ou YYYY-MM-DD_HHhMMSS_cliente_id.
    partes = nome.split("_")
    if len(partes) < 2:
        return None
    for formato in ("%Y-%m-%d_%Hh%M%S", "%Y-%m-%d_%Hh%M"):
        try:
            return datetime.strptime("_".join(partes[:2]), formato)
        except ValueError:
            continue
    return None
