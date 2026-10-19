_versao: int = 3


def set_versao(v: int) -> None:
    global _versao
    _versao = int(v)


def get_versao() -> int:
    return _versao


def escopo(page):
    """
    Retorna o contexto de interação com a DOM para a versão ativa.

    - v4+: retorna o frame de conteúdo (a UI é renderizada dentro de um iframe)
    - v3 e anteriores: retorna a própria page

    Uso nos flows:
        ctx = escopo(page)
        ctx.locator("...").click()
        aguardar_ajax_global(page)  # page continua acessível diretamente
    """
    if _versao >= 4:
        from utils.waits import obter_frame_conteudo
        return obter_frame_conteudo(page)
    return page
