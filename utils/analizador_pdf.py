import pdfplumber
import unicodedata
import re

from loguru import logger
from pathlib import Path


def normalize(text: str | None) -> str:
    if not text:
        return ""
    
    # Remove accents
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.upper().strip()


def validar_pdf(pdf_path: Path, dados_cliente: dict, material: dict) -> bool:
    logger.info("Iniciou validação de PDF.")
    
    textos = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                texto = page.extract_text()
                if texto:
                    textos.append(texto)
            except Exception as e:
                logger.warning("Erro ao extrair texto da página: {}", e)
    
    if not textos:
        logger.error("Nenhum texto encontrado no PDF.")
        return False
    
    texto_completo = normalize("\n".join(textos))

    # --- Cliente ---
    cliente_nomes = dados_cliente.get("nomes", [])

    if not cliente_nomes:
        logger.warning("Nenhum nome de cliente fornecido no arquivo yaml.")
    else:
        cliente_encontrado = any(normalize(nome) in texto_completo for nome in cliente_nomes)
        if not cliente_encontrado:
            logger.warning("Nome do cliente '{}' não encontrado no PDF.", cliente_nomes[0])

    # --- Material ---
    material_nome = normalize(material.get("nome", ""))
    material_complemento = normalize(material.get("complemento", ""))
    material_nome_completo = f"{material_nome} {material_complemento}".strip()

    if not material_nome_completo:
        logger.error("Nenhum nome de material fornecido no arquivo yaml.")
        return False

    # Match perfeita
    if material_nome_completo in texto_completo:
        material_ok = True

    else:
        # Regex ordenada (preserva ordem, tolera quebra de linha)
        tokens = material_nome_completo.split()
        pattern = ".*".join(map(re.escape, tokens))

        if re.search(pattern, texto_completo):
            logger.warning(
                "Material encontrado via regex ordenado (possível quebra de leiaute no PDF)."
            )
            material_ok = True
        
        else: 
            # Token fallback (último recurso)
            missing = [t for t in tokens if t not in texto_completo]

            if not missing:
                logger.warning(
                    "Material encontrado via fallback por tokens (leiaute possivelmente inconsistente)."
                )
                material_ok = True
            else:
                logger.error(
                    "Material '{}' não encontrado no PDF. Tokens ausentes: {}.",
                    material_nome_completo,
                    missing
                )
                material_ok = False

    logger.info("Finalizou validação de PDF.")
    return material_ok


def assert_relatorio_pdf_valido(pdf_path: Path, dados_cliente: dict, material: dict) -> None:

    if not isinstance(pdf_path, Path):
        raise TypeError(
            f"Tipo de relatório inesperado ({pdf_path}). "
            "Verifique o resultado manualmente."
        )

    if not validar_pdf(pdf_path, dados_cliente, material):
        raise ValueError(
            "Erro ao validar PDF. "
            "Dados não encontrados no PDF. Analise-o manualmente."
        )
