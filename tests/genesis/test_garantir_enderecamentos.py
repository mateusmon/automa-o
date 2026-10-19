from flows.genesis.garantir_enderecamentos.criar_enderecamento_flow import (
    criar_enderecamento,
)
from flows.genesis.garantir_enderecamentos.verificar_enderecamento_existente_flow import (
    verificar_enderecamento_existente,
)
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout


def test_garantir_enderecamentos(page: Page, contexto_cliente: ContextoCliente) -> None:
    """Garante o endereçamento dos materiais para os almoxarifados conforme a massa."""
    logger.info("Iniciou teste Genesis para garantir Endereçamentos de Material.")

    dados_usuario = contexto_cliente.dados_usuario("teste")
    almoxarifados_data = contexto_cliente.almoxarifados()
    materiais_data = contexto_cliente.materiais()
    enderecos_data = contexto_cliente.enderecos_material()
    unidade_medida_data = contexto_cliente.unidade_medida()

    if (
        not almoxarifados_data
        or not materiais_data
        or not enderecos_data
        or not unidade_medida_data
    ):
        logger.info(
            "Massa de dados incompleta no YAML para endereçamento. Ignorando fluxo."
        )
        return

    # Normaliza para lista se vierem como dicionários únicos
    if isinstance(almoxarifados_data, dict):
        almoxarifados_data = [almoxarifados_data]
    if isinstance(materiais_data, dict):
        materiais_data = [materiais_data]
    if isinstance(enderecos_data, dict):
        enderecos_data = [enderecos_data]

    login(page, dados_usuario)

    enderecamentos_faltantes = verificar_enderecamento_existente(
        page, almoxarifados_data, materiais_data, enderecos_data
    )

    if not enderecamentos_faltantes:
        logger.info(
            "Todos os endereçamentos solicitados já existem. Nenhuma criação necessária."
        )
        logger.success("Finalizou teste Genesis para garantir Endereçamentos.")
        logout(page)
        return

    criar_enderecamento(
        page=page,
        enderecamentos_faltantes=enderecamentos_faltantes,
        unidade_medida_data=unidade_medida_data,
    )

    # Pós-validação apenas dos que precisavam ser criados
    verificacao_pos = []
    for item in enderecamentos_faltantes:
        res = verificar_enderecamento_existente(
            page,
            [item["almoxarifado"]],
            [item["material"]],
            [item["endereco"]],
        )
        verificacao_pos.extend(res)

    fmt_faltantes = [
        f"{it['material']['nome']} no almoxarifado {it['almoxarifado']['sigla']} (Endereço: {it['endereco']['descricao']})"
        for it in verificacao_pos
    ]

    assert len(verificacao_pos) == 0, (
        f"Os seguintes endereçamentos não foram validados após o cadastro: {fmt_faltantes}"
    )

    logger.success("Finalizou teste Genesis para garantir Endereçamentos com sucesso.")
    logout(page)
