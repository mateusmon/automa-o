from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def escolher_tipo(page: Page, select_name: str, texto: str) -> None:
    logger.info("Iniciou escolha de tipo '{}'.", texto)

    ctx = escopo(page)

    ctx.locator(f"select[name='{select_name}']").select_option(
        label=ctx.eval_on_selector(
            f"select[name='{select_name}']",
            """(select, texto) => {
                const option = Array.from(select.options).find(o =>
                    o.text.includes(texto)
                );
                if (!option) throw new Error(`Nenhuma opção encontrada com texto: ${texto}`);
                return option.text;
            }""",
            texto
        )
    )

    logger.info("Finalizou escolha de tipo '{}'.", texto)
