from loguru import logger

# Formas de operação com falha conhecida e esperada para a SEADPB
# (ver GUIA_TESTES.md, seção "Entrada de Materiais — SEADPB").
FORMAS_COM_FALHA_ESPERADA = ("COMPRA",)


def reportar_resultados_entrada(resultados: list[dict]) -> None:
    """
    Loga o relatório final da varredura de tipos e finalidades de Entrada de
    Bens (ver tests/casos/patrimonio/test_entrada_bens_todos_tipos.py).

    Nunca lança exceção — apenas expõe no log tudo que aconteceu, para
    revisão humana, distinguindo falhas esperadas (ex.: COMPRA na SEADPB)
    de falhas inesperadas.
    """
    logger.info("=" * 90)
    logger.info("RESUMO — Entrada de Bens (todos os tipos e finalidades) — SEADPB")
    logger.info("=" * 90)

    if not resultados:
        logger.warning("Nenhuma combinação de Tipo de Bem/Forma de Operação foi executada.")
        logger.info("=" * 90)
        return

    sucessos = []
    falhas_esperadas = []
    falhas_inesperadas = []

    for r in resultados:
        descricao = f"{r['tipo_bem']} + {r['forma_operacao']}"

        if r["status"] == "OK":
            sucessos.append(r)
            logger.success("[OK] {}", descricao)
            continue

        e_esperada = str(r["forma_operacao"]).strip().upper() in FORMAS_COM_FALHA_ESPERADA

        if e_esperada:
            falhas_esperadas.append(r)
            logger.warning("[FALHOU - ESPERADO] {} -> {}", descricao, r["erro"])
        else:
            falhas_inesperadas.append(r)
            logger.error("[FALHOU - INESPERADO] {} -> {}", descricao, r["erro"])

    logger.info("-" * 90)
    logger.info(
        "Total de combinações: {} | Sucesso: {} | Falhas esperadas: {} | Falhas inesperadas: {}",
        len(resultados), len(sucessos), len(falhas_esperadas), len(falhas_inesperadas)
    )

    if falhas_inesperadas:
        logger.error(
            "ATENÇÃO: {} combinação(ões) falharam de forma inesperada. Revise o log acima.",
            len(falhas_inesperadas)
        )

    logger.info("=" * 90)
