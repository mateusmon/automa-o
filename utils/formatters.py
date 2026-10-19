def decimal_br(valor: float) -> str:
    """Converte decimal para formato brasileiro 0,00"""
    return f"{valor:.2f}".replace(".", ",")

def inteiro_str(valor: int) -> str:
    """Converte inteiro para string"""
    return str(valor)
