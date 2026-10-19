import os
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from loguru import logger

from utils import retencao

_base_dir: Path | None = None  # Diretório base onde os traces finais serão salvos
_temp_ctx: TemporaryDirectory | None = None  # Contexto da pasta temporária
_temp_dir: Path | None = None  # Caminho da pasta temporária


def iniciar(base_path: Path):
    """
    Chamado um vez na inicialização do pytest
    Prepara um diretório temporário seguro para armazenar evidências.
    """

    global _base_dir, _temp_ctx, _temp_dir

    base_path.mkdir(parents=True, exist_ok=True)
    cleanup_old_runs(base_path)

    _base_dir = base_path

    # Cria um ID único para esta execução; timestamp + primeiros 8 dígitos de um UUID
    run_id = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:8]}"

    # Cria a pasta temporário para armazenar o trace desta execução
    _temp_ctx = TemporaryDirectory(prefix=f"trace_{run_id}_")
    _temp_dir = Path(_temp_ctx.name)


def garantir_inicializacao():
    global _temp_dir

    if _temp_dir is None:
        base = Path("trace")
        base.mkdir(exist_ok=True)

        logger.debug(
            "Cleanup aconteceu e iniciar() não foi chamado. Inicializando trace novamente."
        )
        iniciar(base)


def iniciar_trace(context):
    """
    Inicia a gravação do trace.
    """
    if not context:
        return

    garantir_inicializacao()

    context.tracing.start(screenshots=True, snapshots=True, sources=True)


def salvar_trace(context, nome_test: str):
    if not _base_dir:
        raise RuntimeError("Trace path não foi inicializado.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = _base_dir / timestamp
    destino.mkdir(parents=True, exist_ok=True)

    trace_file = destino / f"{nome_test}.zip"

    context.tracing.stop(path=trace_file)

    logger.error("Trace salvo em: {}", trace_file)


def nome_seguro(texto: str, limite: int = 80) -> str:
    """Converte um texto em nome de arquivo válido no Windows."""
    return re.sub(r'[<>:"/\\|?*\s]+', "_", texto).strip("_")[:limite]


def id_captura() -> str:
    """Identifica a tentativa de Pytest iniciada pela Sentinela, se houver."""
    return nome_seguro(os.environ.get("ASI_TRACE_CAPTURE_ID", ""), 12)


def _nome_teste_atual() -> str:
    atual = os.environ.get("PYTEST_CURRENT_TEST", "teste")
    nodeid = atual.rsplit(" ", 1)[0]  # remove o sufixo " (call)"
    return nome_seguro(nodeid.replace("::", "__"), 90)


def _iniciar_chunk(context) -> bool:
    try:
        context.tracing.start_chunk()
        return True
    except Exception as e:
        logger.warning("Não foi possível iniciar o chunk de trace: {}", e)
        return False


def _descartar_chunk(context) -> None:
    try:
        context.tracing.stop_chunk()  # sem path = descarta
    except Exception as e:
        logger.warning("Não foi possível descartar o chunk de trace: {}", e)


def _salvar_chunk(context, rotulo: str) -> None:
    try:
        if not _base_dir:
            raise RuntimeError("Trace path não foi inicializado.")

        destino = _base_dir / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        destino.mkdir(parents=True, exist_ok=True)

        tentativa = id_captura()
        capture_id = f"_{tentativa}" if tentativa else ""
        trace_file = destino / f"{_nome_teste_atual()}__{nome_seguro(rotulo, 24)}{capture_id}_{uuid4().hex[:8]}.zip"
        context.tracing.stop_chunk(path=trace_file)

        logger.error("Trace da combinação '{}' salvo em: {}", rotulo, trace_file)
    except Exception as e:
        logger.warning(
            "Não foi possível salvar o trace da combinação '{}': {}", rotulo, e
        )


def _deve_salvar(excecao: BaseException, salvar_se) -> bool:
    if isinstance(excecao, pytest.skip.Exception):
        return False

    if salvar_se is None:
        return True

    try:
        return bool(salvar_se(excecao))
    except Exception as e:
        logger.warning("Critério salvar_se falhou ({}). Salvando o trace.", e)
        return True


@contextmanager
def trecho(page, rotulo: str, salvar_se=None):
    """
    Grava o trace apenas deste trecho do teste.

    Sem erro no bloco: o trecho é descartado. Com exceção: o trecho é salvo e
    a exceção segue adiante, exceto em skip (nunca salva) ou quando `salvar_se`
    (função que recebe a exceção e devolve bool) retornar False, caso de falhas
    esperadas.
    """
    context = page.context
    iniciado = _iniciar_chunk(context)

    try:
        yield
    except BaseException as e:
        if iniciado:
            if _deve_salvar(e, salvar_se):
                _salvar_chunk(context, rotulo)
            else:
                _descartar_chunk(context)
        raise
    else:
        if iniciado:
            _descartar_chunk(context)


def cleanup():
    """
    Limpa recursos temporários utilizados durante a execução dos testes.

    Funcionalidade:
    - Chama a função interna `_cleanup_temp()` para remover arquivos temporários.

    Observações:
    - Esta função geralmente é chamada ao final da sessão de testes, por exemplo,
      no hook `pytest_sessionfinish`.
    - `_cleanup_temp()` é uma função privada responsável pela lógica real de limpeza.
    """
    _cleanup_temp()


def _cleanup_temp():
    """
    Função interna privada.

    Limpa de forma segura o diretório temporário.
    TemporaryDirectory garante que a exclusão seja controlada.
    """
    global _temp_ctx, _temp_dir

    if _temp_ctx:
        _temp_ctx.cleanup()

    _temp_ctx = None
    _temp_dir = None


def cleanup_old_runs(base_path: Path) -> None:
    """
    Remove pastas de trace expiradas, conforme `configs/retencao.yaml`.

    Antes esta função apagava tudo que não fosse de hoje, enquanto a evidência
    era guardada por 5 dias. O resultado é que um teste que falhava na sexta
    chegava na segunda com o screenshot preservado e o trace — o artefato mais
    útil dos dois — já apagado. Agora ambos seguem o mesmo arquivo de política.
    """
    retencao.varrer_por_data(
        base_path,
        retencao.FORMATO_TIMESTAMP,
        retencao.dias("traces_dias"),
    )
