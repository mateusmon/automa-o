"""Gravação e persistência de traces do Genesis por etapa de execução.

Este módulo é o GÊMEO de ``utils/trace.py`` da raiz, e não uma duplicação por
descuido: o Genesis roda como ``python genesis/main.py``, com ``genesis/`` no
``sys.path``, e por isso não alcança o ``utils/`` da raiz. O que os dois
compartilham é o arquivo ``configs/retencao.yaml``, nunca código.

O Genesis abre uma sessão de tracing para cada flow ou etapa. Sessões concluídas
são descartadas; somente a sessão que falha é salva.
"""

import re
import shutil

from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypeVar

import yaml
from loguru import logger
from playwright.sync_api import BrowserContext


T = TypeVar("T")

_base_dir: Path | None = None


def iniciar(base_path: Path) -> None:
    """Prepara o diretório de destino e aplica a política de retenção."""
    global _base_dir

    base_path.mkdir(parents=True, exist_ok=True)
    cleanup_old_runs(base_path)
    _base_dir = base_path


def garantir_inicializacao() -> None:
    """Inicializa o trace no diretório padrão quando o runner não o fez."""
    if _base_dir is not None:
        return

    base = Path("trace")
    base.mkdir(exist_ok=True)
    logger.debug("Trace não inicializado. Usando o diretório padrão.")
    iniciar(base)


def executar_com_trace(
    context: BrowserContext,
    nome_etapa: str,
    acao: Callable[[], T],
) -> T:
    """Executa uma etapa e salva somente a sua sessão quando ela falha.

    Falhas do próprio mecanismo de trace são apenas registradas: a coleta de
    evidência nunca pode impedir a etapa nem mascarar sua exceção original.
    """
    trace_ativo = _iniciar_trace(context, nome_etapa)

    try:
        resultado = acao()
    except BaseException:
        if trace_ativo:
            _salvar_trace_com_seguranca(context, nome_etapa)
        raise

    if trace_ativo:
        _descartar_trace_com_seguranca(context, nome_etapa)

    return resultado


def _iniciar_trace(context: BrowserContext, nome_etapa: str) -> bool:
    """Inicia a sessão e informa se o trace ficou disponível para a etapa."""
    if not context:
        return False

    try:
        context.tracing.start(
            title=nome_etapa,
            name=_nome_seguro(nome_etapa),
            screenshots=True,
            snapshots=True,
            sources=True,
        )
        return True
    except Exception as e:
        logger.warning("Não foi possível iniciar o trace de '{}': {}", nome_etapa, e)
        return False


def _salvar_trace_com_seguranca(context: BrowserContext, nome_etapa: str) -> None:
    """Salva a sessão atual sem propagar falhas da coleta de evidência."""
    try:
        salvar_trace(context, nome_etapa)
    except Exception as e:
        logger.warning("Não foi possível salvar o trace de '{}': {}", nome_etapa, e)


def _descartar_trace_com_seguranca(
    context: BrowserContext,
    nome_etapa: str,
) -> None:
    """Descarta a sessão concluída sem afetar a execução do Genesis."""
    try:
        context.tracing.stop()
    except Exception as e:
        logger.warning("Não foi possível descartar o trace de '{}': {}", nome_etapa, e)


def salvar_trace(context: BrowserContext, nome_etapa: str) -> Path:
    """Persiste a sessão atual com o nome da etapa que falhou."""
    garantir_inicializacao()

    if _base_dir is None:
        raise RuntimeError("Trace path não foi inicializado.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = _base_dir / timestamp
    destino.mkdir(parents=True, exist_ok=True)

    trace_file = destino / f"{_nome_seguro(nome_etapa)}.zip"
    context.tracing.stop(path=trace_file)

    logger.error("Trace da etapa '{}' salvo em: {}", nome_etapa, trace_file)
    return trace_file


def _nome_seguro(nome: str) -> str:
    """Converte o nome lógico da etapa em um nome de arquivo seguro."""
    seguro = re.sub(r"[^A-Za-z0-9._-]+", "_", nome).strip("._")
    return seguro or "etapa_desconhecida"


def cleanup() -> None:
    """Limpa o estado do módulo ao final da execução."""
    global _base_dir
    _base_dir = None


def _dias_de_retencao(padrao: int = 3) -> int:
    """Lê ``traces_dias`` da configuração compartilhada de retenção."""
    caminho = Path(__file__).resolve().parents[2] / "configs" / "retencao.yaml"

    try:
        dados = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        logger.warning("Não foi possível ler retencao.yaml: {}. Usando {} dias.", e, padrao)
        return padrao

    valor = dados.get("traces_dias") if isinstance(dados, dict) else None
    return valor if isinstance(valor, int) else padrao


def cleanup_old_runs(base_path: Path) -> None:
    """Remove pastas de trace expiradas conforme ``configs/retencao.yaml``."""
    if not base_path.exists():
        return

    limite = datetime.now() - timedelta(days=_dias_de_retencao())

    for entry in base_path.iterdir():
        if not entry.is_dir():
            continue

        folder_date = _parse_daily_folder_name(entry.name)
        if folder_date is None:
            continue

        if folder_date < limite:
            shutil.rmtree(entry, ignore_errors=True)
            logger.debug("Trace expirado removido: {}", entry.name)


def _parse_daily_folder_name(name: str) -> datetime | None:
    try:
        return datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None
