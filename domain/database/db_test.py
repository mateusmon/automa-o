"""
This file tests connection with dbs inside db_config.yaml
"""

from connections import get_session
from queries import buscar_material_por_nome

with get_session("pcdf") as session:
    materiais = buscar_material_por_nome(session, "CANETA ESFEROGRÁFICA AZUL AUTOMATIZADO")
    for m in materiais:
        print(f"Nome completo: {m.nome_completo}, Código: {m.codigo}")
