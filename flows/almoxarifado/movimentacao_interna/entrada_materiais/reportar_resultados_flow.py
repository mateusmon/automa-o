from loguru import logger


def reportar_resultados(titulo: str, resultados: list[dict]) -> None:
    """
    Loga o relatório final de uma varredura de combinações. Nunca lança
    exceção — apenas expõe no log tudo que aconteceu, para revisão humana.

    Cada item de `resultados` deve ter as chaves:
        rotulo (str)          — descrição da combinação
        status (str)          — "SUCESSO", "FALHA_ESPERADA" ou "FALHA"
        etapa (str | None)    — sub-passo em que ocorreu a falha
        erro (str | None)     — repr da exceção, se houver

    A classificação de "falha esperada" é decidida por quem chama (o teste
    conhece as particularidades do seu módulo/cliente) — este flow só
    formata e conta o que já veio classificado.
    """
    logger.info("\nRESUMO — {}\n", titulo)

    if not resultados:
        logger.warning("Nenhuma combinação foi executada.")
        return

    log_por_status = {
        "SUCESSO": logger.success,
        "FALHA_ESPERADA": logger.warning,
        "FALHA": logger.error,
    }
    
    contagem = {"SUCESSO": 0, "FALHA_ESPERADA": 0, "FALHA": 0}

    for r in resultados:
        contagem[r["status"]] += 1
        detalhe = "" if r["status"] == "SUCESSO" else f"  << {r['etapa']}: {r['erro']}"
        log_por_status[r["status"]]("[{}] {}{}", r["status"], r["rotulo"], detalhe)

    logger.info(
        "\nTotal: {} | Sucesso: {} | Falhas esperadas: {} | Falhas inesperadas: {}",
        len(resultados), contagem["SUCESSO"], contagem["FALHA_ESPERADA"], contagem["FALHA"]
    )

    if contagem["FALHA"]:
        logger.error(
            "\nATENÇÃO: {} combinação(ões) falharam de forma inesperada. Revise o log acima.",
            contagem["FALHA"]
        )
