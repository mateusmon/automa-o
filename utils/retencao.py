"""
Política de retenção de artefatos: um sweeper só e uma fonte única de TTLs.

Antes desta unificação existiam quatro implementações quase idênticas de
"varre pasta, parseia o nome como data, apaga se for velha" — em `evidencia.py`,
`trace.py`, `logging_manager.py` e `genesis/utils/trace.py` — com números
diferentes e duas delas fazendo remoção manual arquivo a arquivo.

Os TTLs vivem em `configs/retencao.yaml` para poderem ser compartilhados com o
Genesis, que não consegue importar este módulo (roda com `genesis/` no sys.path).
"""
import shutil

from datetime import datetime, timedelta
from pathlib import Path

import yaml

from loguru import logger


# Formatos de nome de pasta usados pelos artefatos do projeto.
FORMATO_DIARIO = "%Y-%m-%d"              # logs/2026-07-31
FORMATO_TIMESTAMP = "%Y-%m-%d_%H-%M-%S"  # evidencia/2026-07-31_10-45-13

_ARQUIVO_CONFIG = Path(__file__).resolve().parent.parent / "configs" / "retencao.yaml"

# Usados quando o YAML não existe ou está inválido: a limpeza nunca pode
# impedir a execução dos testes.
_PADRAO = {
    "logs_dias": 7,
    "evidencias_dias": 7,
    "traces_dias": 3,
    "temporarias_horas": 12,
}

_config: dict | None = None


def _carregar_config() -> dict:
    """Lê o YAML uma vez por processo, caindo no padrão se algo der errado."""
    global _config

    if _config is not None:
        return _config

    _config = dict(_PADRAO)

    try:
        dados = yaml.safe_load(_ARQUIVO_CONFIG.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        logger.warning("Não foi possível ler {}: {}. Usando padrões.", _ARQUIVO_CONFIG.name, e)
        return _config

    if isinstance(dados, dict):
        for chave in _PADRAO:
            if isinstance(dados.get(chave), int):
                _config[chave] = dados[chave]

    return _config


def dias(chave: str) -> timedelta:
    """
    Retorna o TTL configurado, em dias.

    Args:
        chave (str): Nome da chave no retencao.yaml (ex.: "traces_dias").
    """
    return timedelta(days=_carregar_config()[chave])


def horas(chave: str) -> timedelta:
    """
    Retorna o TTL configurado, em horas.

    Args:
        chave (str): Nome da chave no retencao.yaml (ex.: "temporarias_horas").
    """
    return timedelta(hours=_carregar_config()[chave])


def varrer_por_data(
    base_path: Path,
    formato: str,
    idade: timedelta,
    prefixo: str = "",
) -> int:
    """
    Remove subpastas de `base_path` cujo nome codifica uma data mais velha que `idade`.

    Pastas com nome fora do padrão são ignoradas de propósito: se não foi este
    projeto que criou, não é este projeto que apaga.

    Args:
        base_path (Path): Diretório onde varrer.
        formato (str): Formato strptime da data no nome (ver FORMATO_*).
        idade (timedelta): Idade a partir da qual a pasta é considerada velha.
        prefixo (str): Prefixo antes da data no nome (ex.: "_temp_").

    Returns:
        int: Quantidade de pastas removidas.
    """
    if not base_path.exists():
        return 0

    limite = datetime.now() - idade

    # Os formatos usados aqui têm largura fixa, então dá para recortar a data
    # do início do nome e ignorar o que vier depois (ex.: o uuid das temporárias).
    tamanho = len(datetime(2000, 1, 1).strftime(formato))

    removidas = 0

    for pasta in base_path.glob(f"{prefixo}*"):
        if not pasta.is_dir():
            continue

        recorte = pasta.name[len(prefixo):len(prefixo) + tamanho]

        try:
            data_pasta = datetime.strptime(recorte, formato)
        except ValueError:
            continue  # nome fora do padrão: não é nossa, não mexe

        if data_pasta < limite:
            shutil.rmtree(pasta, ignore_errors=True)
            removidas += 1
            logger.debug("Artefato expirado removido: {}", pasta.name)

    return removidas
