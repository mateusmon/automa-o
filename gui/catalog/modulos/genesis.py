"""Catálogo dos testes de preparação de massa do Genesis."""

MODULE = {
    "meta": {},
    "sections": {
        "Rotina do usuário Link": [
            {
                "name": "Garantir Cidade",
                "path": "tests/genesis/test_garantir_cidade.py",
            },
            {
                "name": "Garantir Funcionário",
                "path": "tests/genesis/test_garantir_funcionario.py",
            },
            {
                "name": "Garantir Função",
                "path": "tests/genesis/test_garantir_funcao.py",
            },
            {
                "name": "Garantir Centro de Custo",
                "path": "tests/genesis/test_garantir_centro_custo.py",
                "exclude_clients": ["jfrj"],
            },
            {
                "name": "Garantir Unidade Administrativa",
                "path": "tests/genesis/test_garantir_ua.py",
            },
            {
                "name": "Garantir Associacao entre Funcionarios e UA",
                "path": "tests/genesis/test_garantir_associacao_funcionarios_ua.py",
            },
            {
                "name": "Garantir Instalação",
                "path": "tests/genesis/test_garantir_instalacao.py",
            },
            {
                "name": "Garantir Endereços",
                "path": "tests/genesis/test_garantir_enderecos.py",
            },
            {
                "name": "Garantir URs",
                "path": "tests/genesis/test_garantir_urs.py",
            },
            {
                "name": "Garantir Perfis",
                "path": "tests/genesis/test_garantir_perfis.py",
            },
            {
                "name": "Garantir Usuários",
                "path": "tests/genesis/test_garantir_usuarios.py",
            },
            {
                "name": "Garantir Remoção das Restrições do Perfil",
                "path": "tests/genesis/test_remover_restricoes_perfis.py",
            },
        ],
        "Rotina do usuário Teste": [
            {
                "name": "Garantir Almoxarifados",
                "path": "tests/genesis/test_garantir_almoxarifados.py",
            },
            {
                "name": "Garantir Fornecedores",
                "path": "tests/genesis/test_garantir_fornecedores.py",
            },
            {
                "name": "Garantir Orgãos Externos",
                "path": "tests/genesis/test_garantir_orgao_externo.py",
            },
            {
                "name": "Garantir Unidade de Medida",
                "path": "tests/genesis/test_garantir_unidade_medida.py",
            },
            {
                "name": "Garantir Subgrupos",
                "path": "tests/genesis/test_garantir_subgrupos.py",
            },
            {
                "name": "Garantir Materiais",
                "path": "tests/genesis/test_garantir_materiais.py",
            },
            {
                "name": "Garantir Endereços de Materiais",
                "path": "tests/genesis/test_garantir_enderecos_material.py",
            },
            {
                "name": "Garantir Endereçamento",
                "path": "tests/genesis/test_garantir_enderecamentos.py",
            },
            {
                "name": "Garantir ULs",
                "path": "tests/genesis/test_garantir_uls.py",
            },
            {
                "name": "Garantir Catálogos",
                "path": "tests/genesis/test_garantir_catalogos.py",
            },
            {
                "name": "Garantir Bens",
                "path": "tests/genesis/test_garantir_bens.py",
            },
            {
                "name": "Garantir Características",
                "path": "tests/genesis/test_garantir_caracteristica.py",
            },
            {
                "name": "Garantir Eventos",
                "path": "tests/genesis/test_garantir_eventos.py",
            },
        ],
    },
}
