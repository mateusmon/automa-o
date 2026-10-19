import random
import string
import tempfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def gerar_numero_nota_fiscal():
    """
    Gera um número simples de nota fiscal (9 dígitos).
    Exemplo: 000123456
    """
    return f"{random.randint(0, 999_999_999):09d}"


def gerar_chave_nfe_fake():
    """
    Gera uma chave NF-e fictícia de 44 dígitos (não validada).
    """
    uf = random.choice([
        "11","12","13","14","15","16","17","21","22","23","24","25",
        "26","27","28","29","31","32","33","35","41","42","43","50",
        "51","52","53"
    ])

    data = f"{random.randint(20, 30):02d}{random.randint(1, 12):02d}"  # AAMM fake
    cnpj = f"{random.randint(0, 99999999999999):014d}"
    modelo = "55"
    serie = f"{random.randint(0, 999):03d}"
    numero_nf = f"{random.randint(0, 999999999):09d}"
    tipo_emissao = "1"
    codigo_numerico = f"{random.randint(0, 99999999):08d}"
    dv = str(random.randint(0, 9))

    return (
        uf + data + cnpj + modelo + serie +
        numero_nf + tipo_emissao + codigo_numerico + dv
    )


def gerar_numero_empenho():
    """
    Gera número de empenho no padrão:
    xxxxNExxxxxx
    Exemplo: 2024NE000123
    """
    ano = random.randint(2000, 2099)
    sequencial = f"{random.randint(0, 999999):06d}"
    # As letras NE são inseridas automaticamente
    return f"{ano}{sequencial}"


def gerar_processo_sei():
    """
    Gera número de processo SEI no padrão:
    xxxx.xx.xxxxxxxxx-x
    Exemplo: 2304.12.000123456-7
    """
    bloco1 = random.randint(1000, 9999)
    bloco2 = random.randint(10, 99)
    bloco3 = f"{random.randint(0, 999999999):09d}"
    dv = random.randint(0, 9)

    # Os pontos e o traço é inserido automaticamente
    return f"{bloco1}{bloco2}{bloco3}{dv}"


def gerar_numero_com_digitos(digitos=10) -> str:
    """Gera um número com um certo número de dígitos."""
    return "".join(str(random.randint(0, 9)) for _ in range(digitos))

def gerar_nf_por_data():
    """
    Gera um número no formato de ano - mês - dia - hora - minuto - segundo
    Ex: 260323142955
    """

    agora = datetime.now()

    formato = agora.strftime("%y%m%d%H%M%S")

    return formato

def gerar_imagem_temporaria(nome_arquivo: str = "imagem_teste.png") -> Path:
    """Gera uma imagem PNG simples na pasta temporária do sistema operacional."""
    temp_dir = Path(tempfile.gettempdir())
    caminho_imagem = temp_dir / nome_arquivo

    # Cria uma imagem simples de 200x200 pixels
    img = Image.new("RGB", (200, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((20, 90), "TESTE AUTOMATIZADO", fill=(255, 255, 0))

    img.save(caminho_imagem)
    return caminho_imagem

def gerar_pdf_temporario(nome_arquivo: str = "documento_teste.pdf") -> Path:
    """Gera um PDF sintético simples no diretório temporário do sistema operacional."""
    temp_dir = Path(tempfile.gettempdir())
    caminho_pdf = temp_dir / nome_arquivo

    c = canvas.Canvas(str(caminho_pdf), pagesize=letter)
    c.drawString(100, 750, "DOCUMENTO DE TESTE AUTOMATIZADO - PLAYWRIGHT")
    c.drawString(100, 730, "Este arquivo foi gerado dinamicamente durante o fluxo.")
    c.save()

    return caminho_pdf

def gerar_email() -> str:
    """Gera um endereço de e-mail aleatório."""
    caracteres = string.ascii_lowercase + string.digits
    usuario = "".join(random.choices(caracteres, k=10))

    return f"{usuario}@teste.com"
