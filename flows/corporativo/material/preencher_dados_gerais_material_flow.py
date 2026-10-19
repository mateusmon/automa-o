from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais_material(page: Page, material: dict) -> None:
    """
    Preenche os dados gerais do material (nome genérico, complemento e unidade de
    medida) no form `bemser`, compartilhado por Consumo/Permanente/Serviço. Cenário A
    (escopo via `escopo(page)`). **Não** faz o submit e **não** seleciona subgrupo/conta
    — isso é orquestrado pelo teste (`selecionar_subgrupo`, `selecionar_conta`,
    `confirmar_material`).

    Pressupõe que o subgrupo já foi selecionado. Adiciona a linha de material,
    preenche nome e complemento, clica fora do campo (heading) para disparar o ajax e
    preenche a unidade de medida.

    :param material: dict do blueprint (nome, complemento, unidade_medida).
    """
    logger.info("Iniciou preenchimento de dados gerais de material '{}'.", material["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)
    logger.info("Preenchendo campo de Nome do material com '{}'.", material["nome"])
    ctx.locator("input[name='material_DsBemGenerico']").fill(material["nome"])
    logger.info("Preenchendo campo de Complemento do material com '{}'.", material["complemento"])
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(material["complemento"])

    # Clicar fora do campo (no heading "Material") dispara o ajax que valida o
    # complemento. Sem esse passo, a v3 abre automaticamente a busca do complemento
    # (alerta "Nenhum COMPLEMENTO encontrado!") cuja máscara trava o restante do fluxo.
    ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='complemento_CdUmElementar']", material["unidade_medida"])

    logger.info("Finalizou preenchimento de dados gerais de material '{}'.", material["nome"])
