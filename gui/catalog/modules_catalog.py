"""
Catálogo de módulos e testes disponíveis no ASI Automação 2.0.

Este arquivo agrega o dict MODULES a partir dos arquivos individuais
em catalog/modulos/, na ordem de exibição esperada pela GUI.

"""

from catalog.modulos.almoxarifado import MODULE as ALMOXARIFADO
from catalog.modulos.corporativo import MODULE as CORPORATIVO
from catalog.modulos.especificos import MODULE as TESTES_ESPECIFICOS
from catalog.modulos.genesis import MODULE as GENESIS
from catalog.modulos.patrimonio import MODULE as PATRIMONIO

# from catalog.modulos.compras import MODULE as COMPRAS  # módulo desativado

# A ordem das chaves aqui é a ordem de exibição dos módulos na GUI.
MODULES = {
    "Almoxarifado": ALMOXARIFADO,
    "Patrimônio": PATRIMONIO,
    "Corporativo": CORPORATIVO,
    "Testes Específicos": TESTES_ESPECIFICOS,
    "Genesis": GENESIS,
    # "Compras": COMPRAS,
}
