def _visivel_para(item: dict, client_id: str, client_versao: int | None) -> bool:
    """
    Resolve a visibilidade de um módulo/teste a partir das chaves opcionais:

    - ``clients`` / ``exclude_clients``: por cliente específico (exceções de negócio).
    - ``versao_minima`` / ``versao_maxima``: por versão do GRP (mesma semântica de
      ``get_versao()`` em ``utils/versao.py`` — ``versao_minima`` é inclusivo, ex.:
      ``versao_minima: 4`` cobre v4, v5, v6...).

    As duas famílias de chave são independentes e podem coexistir; o item só é
    visível se passar em todas as que estiverem presentes.
    """
    clientes = item.get("clients")
    excluir_clientes = item.get("exclude_clients")
    versao_minima = item.get("versao_minima")
    versao_maxima = item.get("versao_maxima")

    if clientes is not None and client_id not in clientes:
        return False

    if excluir_clientes is not None and client_id in excluir_clientes:
        return False

    if client_versao is not None:
        if versao_minima is not None and client_versao < versao_minima:
            return False

        if versao_maxima is not None and client_versao > versao_maxima:
            return False

    return True


def filtrar_modulos_por_cliente(modules: dict, client_id: str, client_versao: int | None = None) -> dict:
    """
    Filtra o catálogo de módulos com base no cliente ativo.

    Percorre todos os módulos e seus testes, removendo os que não devem
    aparecer para o cliente informado. A visibilidade é controlada por
    chaves opcionais em cada módulo (via ``meta``) e em cada teste:

    - ``clients`` (lista): o item aparece **somente** para os clientes listados.
    - ``exclude_clients`` (lista): o item aparece para **todos**, exceto os clientes listados.
    - ``versao_minima`` (int): o item aparece **somente** para clientes com versão >= esta.
    - ``versao_maxima`` (int): o item aparece **somente** para clientes com versão <= esta.

    Use ``clients``/``exclude_clients`` para exceções de um cliente específico (ex.:
    integração financeira própria de um órgão). Use ``versao_minima``/``versao_maxima``
    quando a restrição é sobre a versão do GRP (v3 vs. v4+) — assim o item passa a
    valer automaticamente para qualquer cliente novo daquela versão, sem precisar
    listar cada cliente à mão.

    Módulos e seções que ficarem sem nenhum teste após a filtragem são
    removidos do resultado final.

    Exemplos de uso no catálogo::
        # Somente para PCDF
        "meta": {"clients": ["pcdf"]}

        # Para todos, exceto PCDF
        "meta": {"exclude_clients": ["pcdf"]}

        # Teste exclusivo do TSE
        {"name": "Teste X", "path": "...", "clients": ["tse"]}

        # Teste padrão — aparece para todos, exceto PCDF
        {"name": "Fechar Mês", "path": "...", "exclude_clients": ["pcdf"]}

        # Só existe na v3 (qualquer cliente v3, presente ou futuro)
        {"name": "Relatório de Empenho (v3)", "path": "...", "versao_maxima": 3}

        # Só existe na v4+
        {"name": "Relatório de Empenho (v4)", "path": "...", "versao_minima": 4}

    :param modules: Catálogo completo de módulos (estrutura de ``MODULES`` em ``modules_catalog.py``).
    :param client_id: Identificador do cliente ativo (ex: ``"pcdf"``, ``"tse"``).
    :param client_versao: Versão do GRP do cliente ativo (``clientes[client_id]["versao"]``
        em ``configs.yaml``). Se ``None``, as chaves ``versao_minima``/``versao_maxima``
        são ignoradas (comportamento equivalente a não filtrar por versão).
    :return: Subconjunto do catálogo contendo apenas os módulos e testes visíveis para o cliente.
    """
    resultado = {}

    for nome_modulo, modulo in modules.items():
        meta = modulo.get("meta", {})
        sections = modulo.get("sections", {})

        if not _visivel_para(meta, client_id, client_versao):
            continue

        novas_secoes = {}

        for nome_secao, testes in sections.items():
            testes_filtrados = [
                teste for teste in testes
                if _visivel_para(teste, client_id, client_versao)
            ]

            if testes_filtrados:
                novas_secoes[nome_secao] = testes_filtrados

        # remove módulos vazios
        if novas_secoes:
            resultado[nome_modulo] = {
                "meta": meta,
                "sections": novas_secoes
            }

    return resultado
