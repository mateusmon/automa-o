"""Derivação dos vínculos de Usuário a partir dos Perfis do Link."""

from flows.genesis.shared.perfis_origem import derivar_nome_perfil


def montar_sistemas_usuario(
    perfis: list[dict], prefixo: str, nome_usuario: str
) -> list[dict[str, str]]:
    """Deriva os pares Sistema/Perfil, preservando ordem e repetições do legado.

    A regra de Usuários não rejeita Sistemas repetidos, diferentemente da cópia
    de Perfis. Descarta somente nomes que já começam com o prefixo reservado.
    """
    prefixo_normalizado = prefixo.strip().upper()
    origens = [
        perfil for perfil in perfis
        if not perfil["nome"].strip().upper().startswith(prefixo_normalizado)
    ]
    if not origens:
        raise RuntimeError(
            f"Nenhum perfil de origem encontrado para o usuário logado "
            f"'{nome_usuario}'. Não há perfis para vincular."
        )
    return [
        {
            "perfil": derivar_nome_perfil(prefixo, perfil["sistema"]),
            "nome": perfil["sistema"].split(" - ", 1)[1].strip(),
        }
        for perfil in origens
    ]
