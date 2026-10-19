from flows.genesis.garantir_uls.criar_ul_flow import criar_ul
from flows.genesis.garantir_uls.verificar_ul_existente_flow import (
    verificar_ul_existente,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_uls(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante a existência das Unidades de Localização (UL) informadas na massa."""
    logger.info("Iniciou teste Genesis para garantir Unidades de Localização.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    uls_data = contexto_cliente.unidades_localizacao()

    if not uls_data:
        logger.info("Nenhuma UL definida no arquivo yaml. Ignorando fluxo.")
        return

    if isinstance(uls_data, dict):
        uls_data = [uls_data]

    login(page, dados_usuario)

    uls_faltantes = verificar_ul_existente(page, uls_data)

    if not uls_faltantes:
        logger.info(
            "Todas as Unidades de Localização solicitadas já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir ULs com sucesso.")
        logout(page)
        return

    criar_ul(page=page, uls_faltantes=uls_faltantes)

    # Pós-validação apenas dos itens cadastrados
    verificacao_pos = verificar_ul_existente(page, uls_faltantes)

    fmt_faltantes = [
        f"Sigla: {item['sigla']} (Endereço: {item['endereco']})"
        for item in verificacao_pos
    ]

    assert len(verificacao_pos) == 0, (
        f"Os seguintes endereços de UL não foram encontrados após o cadastro: {fmt_faltantes}"
    )

    logger.success("Finalizou teste Genesis para garantir ULs com sucesso.")
    logout(page)
