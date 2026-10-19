from playwright.sync_api import Page
from domain.contexto_cliente import ContextoCliente
def test_dados(page: Page, contexto_cliente: ContextoCliente) -> None:
    material_padrao = contexto_cliente.material_padrao()
    print(material_padrao["nome"])
    print(material_padrao["codigo"])