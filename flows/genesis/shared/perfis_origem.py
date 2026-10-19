"""Regras puras para derivar Perfis Genesis dos Perfis do usuário Link."""

from loguru import logger


def selecionar_perfis_origem(perfis: list[dict], prefixo: str) -> list[dict]:
    """Remove cópias anteriores e garante uma única origem por Sistema.

    :param perfis: Perfis associados ao usuário Link autenticado.
    :param prefixo: Prefixo reservado aos Perfis gerados pelo Genesis.
    :return: Perfis de origem que devem ser copiados.
    :raises RuntimeError: Quando não há origem válida ou um Sistema está duplicado.
    """
    if not perfis:
        raise RuntimeError("O usuário logado não possui Perfis para usar como origem.")

    prefixo_normalizado = prefixo.strip().upper()
    origens = [
        perfil
        for perfil in perfis
        if not perfil["nome"].strip().upper().startswith(prefixo_normalizado)
    ]
    descartados = len(perfis) - len(origens)
    if descartados:
        logger.info(
            "{} Perfil(is) ignorado(s) por já usarem o prefixo '{}'.",
            descartados,
            prefixo,
        )
    if not origens:
        raise RuntimeError(
            f"Todos os Perfis do usuário logado já usam o prefixo '{prefixo}'."
        )

    vistos: dict[str, str] = {}
    for perfil in origens:
        sistema = perfil["sistema"]
        if sistema in vistos:
            raise RuntimeError(
                f"Mais de um Perfil de origem encontrado para o Sistema '{sistema}': "
                f"'{vistos[sistema]}' e '{perfil['nome']}'."
            )
        vistos[sistema] = perfil["nome"]
    return origens


def derivar_nome_perfil(prefixo: str, sistema: str) -> str:
    """Combina o prefixo com a sigla de ``SIGLA - NOME DO SISTEMA``."""
    partes = [parte.strip() for parte in sistema.split(" - ", 1)]
    if len(partes) != 2 or not partes[0] or not partes[1]:
        raise RuntimeError(
            f"Sistema '{sistema}' fora do formato esperado 'SIGLA - NOME'."
        )
    return f"{prefixo.strip()} {partes[0]}"
