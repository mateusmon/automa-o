"""Leitura e seleção da ordem de execução por módulos lógicos."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ModuloOrdem:
    """Bloco lógico e ordenado de testes da Sentinela."""

    modulo: str
    ordem: list[str]
    somente_explicito: bool = False


def normalizar_modulo(modulo: str) -> str:
    """Normaliza separadores e remove a barra final de um módulo CLI."""
    return modulo.replace("\\", "/").rstrip("/")


def ler_modulos(caminho: Path | None = None) -> list[ModuloOrdem]:
    """Carrega e valida os módulos lógicos definidos em ``ordem.yaml``."""
    ordem_path = caminho or Path(__file__).resolve().parent / "ordem.yaml"
    with open(ordem_path, encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)

    if not isinstance(dados, dict) or not isinstance(dados.get("modulos"), list):
        raise ValueError("ordem.yaml deve conter a chave 'modulos' como lista.")

    modulos: list[ModuloOrdem] = []
    nomes: set[str] = set()
    for indice, bloco in enumerate(dados["modulos"], 1):
        if not isinstance(bloco, dict):
            raise ValueError(f"Bloco {indice} de ordem.yaml deve ser um mapa.")

        modulo = bloco.get("modulo")
        ordem = bloco.get("ordem")
        somente_explicito = bloco.get("somente_explicito", False)
        if not isinstance(modulo, str) or not modulo:
            raise ValueError(
                f"Bloco {indice} de ordem.yaml deve ter 'modulo' não vazio."
            )
        if modulo != normalizar_modulo(modulo):
            raise ValueError(f"Módulo inválido em ordem.yaml: '{modulo}'.")
        if not isinstance(ordem, list):
            raise ValueError(f"Módulo '{modulo}' deve ter 'ordem' como lista.")
        if not isinstance(somente_explicito, bool):
            raise ValueError(
                f"Módulo '{modulo}' deve ter 'somente_explicito' como booleano."
            )
        if modulo in nomes:
            raise ValueError(f"Módulo duplicado em ordem.yaml: '{modulo}'.")

        paths: list[str] = []
        for posicao, entrada in enumerate(ordem, 1):
            if (
                not isinstance(entrada, dict)
                or not isinstance(entrada.get("path"), str)
                or not entrada["path"]
            ):
                raise ValueError(
                    f"Módulo '{modulo}', entrada {posicao}: 'path' não vazio é obrigatório."
                )
            paths.append(entrada["path"])

        nomes.add(modulo)
        modulos.append(
            ModuloOrdem(
                modulo=modulo,
                ordem=paths,
                somente_explicito=somente_explicito,
            )
        )

    return modulos


def selecionar_modulos(
    modulos: list[ModuloOrdem], modulo: str | None = None
) -> list[ModuloOrdem]:
    """Seleciona a ordem padrão ou módulos exatos/descendentes explícitos.

    Sem módulo informado, blocos ``somente_explicito`` não fazem parte da
    execução global. Com ``--modulo``, o prefixo solicitado sempre prevalece.
    """
    if modulo is None:
        return [bloco for bloco in modulos if not bloco.somente_explicito]

    modulo_normalizado = normalizar_modulo(modulo)
    return [
        bloco
        for bloco in modulos
        if bloco.modulo == modulo_normalizado
        or bloco.modulo.startswith(f"{modulo_normalizado}/")
    ]


def achatar_modulos(modulos: list[ModuloOrdem]) -> list[str]:
    """Retorna os paths dos blocos na ordem declarada, preservando duplicatas."""
    return [path for bloco in modulos for path in bloco.ordem]


def ler_ordem() -> list[str]:
    """Retorna a ordem padrão de paths definida em ``ordem.yaml``."""
    return achatar_modulos(selecionar_modulos(ler_modulos()))


def modulos_disponiveis(modulos: list[ModuloOrdem]) -> list[str]:
    """Retorna os identificadores de módulos lógicos na ordem do YAML."""
    return [bloco.modulo for bloco in modulos]


def filtrar_para_cliente(ordem: list[str], disponiveis: set[str]) -> list[str]:
    """Remove paths indisponíveis ao cliente, preservando ordem e duplicatas."""
    return [path for path in ordem if path in disponiveis]


def paths_invalidos(ordem: list[str]) -> list[str]:
    """Retorna paths da ordem que não existem no disco."""
    raiz = Path(__file__).resolve().parent.parent
    return [path for path in ordem if not (raiz / path).exists()]


def entradas_globais(modulos: list[ModuloOrdem]) -> list[tuple[str, str, int]]:
    """(modulo, path, posição_global) para cada entrada do ordem.yaml completo,
    na ordem do arquivo. A posição é a ocorrência do path considerando TODOS os
    módulos — não é renumerada quando um módulo é filtrado depois."""
    contagem: dict[str, int] = {}
    resultado: list[tuple[str, str, int]] = []
    for bloco in modulos:
        for path in bloco.ordem:
            contagem[path] = contagem.get(path, 0) + 1
            resultado.append((bloco.modulo, path, contagem[path]))
    return resultado


def filtrar_por_modulo(
    entradas: list[tuple[str, str, int]], modulo: str | None
) -> list[tuple[str, str, int]]:
    """Restringe entradas globais a um módulo exato ou seus descendentes,
    preservando a posição global já calculada em cada uma."""
    if modulo is None:
        return entradas

    modulo_normalizado = normalizar_modulo(modulo)
    return [
        (m, path, posicao)
        for m, path, posicao in entradas
        if m == modulo_normalizado or m.startswith(f"{modulo_normalizado}/")
    ]
