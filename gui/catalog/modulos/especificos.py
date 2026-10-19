"""
Catálogo de testes do módulo Testes Específicos (ASI Automação 2.0).

Dado estrutural puro (ver GUIA_GUI.md secao 4) — sem lógica de UI.
Editado manualmente; nao gerar/reescrever programaticamente.
"""

MODULE = {
    "meta": {},
    "sections": {
        "Específicos": [{"name": "Login", "path": "tests/especificos/test_login.py"}],
        "Almoxarifado": [
            {
                "name": "Entrada de Material Completa",
                "path": "tests/almoxarifado/movimentacao_interna/test_entrada_completa.py",
            },
            {
                "name": "Todos os Tipos de Entrada de Material",
                "path": "tests/almoxarifado/movimentacao_interna/test_entrada_materiais_todos_tipos.py",
            },
            {
                "name": "Cadastro de Requisição Completa",
                "path": "tests/almoxarifado/movimentacao_interna/test_cadastro_requisicao_completa.py",
            },
            {
                "name": "Recebimento de Requisição Completa",
                "path": "tests/almoxarifado/movimentacao_interna/test_recebimento_requisicao_completa.py",
            },
            {
                "name": "Devolução de Requisição Completa",
                "path": "tests/almoxarifado/movimentacao_interna/test_devolucao_completa.py",
            },
            {
                "name": "Baixa de Material Completa",
                "path": "tests/almoxarifado/movimentacao_interna/test_baixa_completa.py",
            },
            {
                "name": "Baixa de Material Todas as Modalidades e Situações",
                "path": "tests/especificos/test_baixa_todas_modalidades_situacao_almoxarifado.py",
            },
            {
                "name": "Cadastro da Transferência entre Almoxarifados Completa",
                "path": "tests/especificos/test_cadastro_transferencia_entre_almoxarifados_completa.py",
            },
            {
                "name": "Recebimento da Transferência entre Almoxarifados Completa",
                "path": "tests/especificos/test_recebimento_transferencia_entre_almoxarifados_completa.py",
            },
        ],
        "Patrimônio": [
            {
                "name": "Entrada de Bem Completa",
                "path": "tests/patrimonio/movimentacao/test_entrada_patrimonio_completa.py",
            },
            {
                "name": "Baixa de Bens Doação Completa",
                "path": "tests/patrimonio/movimentacao/test_baixa_bens_doacao_completa.py",
            },
            {
                "name": "Entrada de Bens — Todos os Tipos",
                "path": "tests/casos/patrimonio/test_entrada_bens_todos_tipos.py",
            },
            {
                "name": "Baixa de Bens — Todos os Tipos",
                "path": "tests/especificos/test_baixa_todos_tipos_patrimonio.py",
            },
        ],
    },
}
