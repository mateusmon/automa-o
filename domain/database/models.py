from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, quoted_name


class Base(DeclarativeBase):
    pass


class Material(Base):
    __tablename__ = quoted_name("cr_bem_servico", quote=True)

    codigo = Column(Integer, primary_key=True, name=quoted_name("cd_bem_servico", quote=True))
    complemento = Column(String(200), name=quoted_name("nm_bem_servico", quote=True))
    nome_completo = Column(String(200), name=quoted_name("ds_completa", quote=True))
    conta = Column(String(100), name=quoted_name("cd_conta", quote=True))


# class Almoxarifado(Base):
#     __tablename__ = "CR_ALMOXARIFADO"

#     codigo = Column(Integer, primary_key=True)
#     nome = Column(String(200))
#     codigo = Column(String(50))
