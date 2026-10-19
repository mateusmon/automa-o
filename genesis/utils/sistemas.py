def sigla_do_sistema(sistema: str) -> str:
    """
    Extrai a sigla do sistema: "AX - ALMOXARIFADO" -> "AX".
    """
    return _partes_do_sistema(sistema)[0]


def nome_do_sistema(sistema: str) -> str:
    """
    Extrai o nome do sistema: "AX - ALMOXARIFADO" -> "ALMOXARIFADO".

    """
    return _partes_do_sistema(sistema)[1]


def derivar_nome_perfil(prefixo: str, sistema: str) -> str:
    """
    Monta o nome do perfil de teste a partir do sistema de origem.

    Ex.: prefixo "ADM AUTOMATIZADO" + "AX - ALMOXARIFADO"
         -> "ADM AUTOMATIZADO AX"
    """
    return f"{prefixo.strip()} {sigla_do_sistema(sistema)}"


def _partes_do_sistema(sistema: str) -> tuple[str, str]:
    """
    Quebra "AX - ALMOXARIFADO" em ("AX", "ALMOXARIFADO").
    
    """
    partes = [parte.strip() for parte in sistema.split(" - ", 1)]

    if len(partes) != 2 or not partes[0] or not partes[1]:
        raise RuntimeError(
            f"Sistema '{sistema}' não está no formato esperado 'SIGLA - NOME'. "
            "Não é possível derivar o nome do perfil."
        )

    return partes[0], partes[1]