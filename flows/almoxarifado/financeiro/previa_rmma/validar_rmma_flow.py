import pdfplumber
import unicodedata

from loguru import logger
from pathlib import Path


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode()
    return text.upper()


def validar_rmma(pdf_path: Path, dados_cliente: dict) -> bool:
    logger.info("Iniciou validação de PDF.")

    textos = []

    with pdfplumber.open(pdf_path) as pdf:
        for pdf_page in pdf.pages:
            texto = pdf_page.extract_text()
            if texto:
                textos.append(texto)

    if not textos:
        logger.error("Nenhum texto encontrado no PDF.")
        return False

    texto_completo = _normalize("\n".join(textos))
    cliente_nome = _normalize(dados_cliente.get("nome", ""))

    cliente_ok = bool(cliente_nome) and cliente_nome in texto_completo

    if not cliente_ok:
        logger.error("Cliente '{}' não encontrado no PDF.", cliente_nome)

    logger.info("Finalizou validação de PDF.")
    return cliente_ok
