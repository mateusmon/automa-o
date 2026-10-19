from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.engine import RowMapping
from collections.abc import Sequence

from models import Material


# --- ORM-based queries (database-agnostic) ---

def buscar_material_por_nome(session: Session, nome: str) -> list:
    return (
        session.query(Material)
        .filter(Material.nome_completo.ilike(f"%{nome}%"))
        .all()
    )


# --- Raw SQL for complex queries that don't translate well to ORM ---

def relatorio_estoque_completo(session: Session, almoxarifado_id: int) -> Sequence[RowMapping]:
    sql = text("""
        SELECT m.nome, m.complemento, e.quantidade, e.data_ultima_movimentacao
        FROM material m
        JOIN estoque e ON e.material_id = m.id
        JOIN almoxarifado a ON a.id = e.almoxarifado_id
        WHERE a.id = :almo_id
        ORDER BY m.nome
    """)
    result = session.execute(sql, {"almo_id": almoxarifado_id})
    return result.mappings().all()
