"""
Catálogo de testes do módulo Corporativo (ASI Automação 2.0).

Dado estrutural puro (ver GUIA_GUI.md secao 4) — sem lógica de UI.
Editado manualmente; nao gerar/reescrever programaticamente.
"""

MODULE = {
    "meta": {},
    "sections": {
        "Estrutura Organizacional": [
            {
                "name": "Cadastro de UG - Unidade Gestora",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_ug.py",
            },
            {
                "name": "Consulta de UG - Unidade Gestora",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_ug.py",
            },
            {
                "name": "Alteração de UG - Unidade Gestora",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_ug.py",
            },
            {
                "name": "Exclusão de UG - Unidade Gestora",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_ug.py",
            },
            {
                "name": "Cadastro de UA - Unidade Administrativa",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_ua.py",
            },
            {
                "name": "Consulta de UA - Unidade Administrativa",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_ua.py",
            },
            {
                "name": "Alteração de UA - Unidade Administrativa",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_ua.py",
            },
            {
                "name": "Exclusão de UA - Unidade Administrativa",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_ua.py",
            },
            {
                "name": "Cadastro de UR - Unidade de Requisição",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_ur.py",
            },
            {
                "name": "Consulta de UR - Unidade de Requisição",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_ur.py",
            },
            {
                "name": "Alteração de UR - Unidade de Requisição",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_ur.py",
            },
            {
                "name": "Exclusão de UR - Unidade de Requisição",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_ur.py",
            },
            {
                "name": "Cadastro de UL - Unidade de Localização",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_ul.py",
            },
            {
                "name": "Consulta de UL - Unidade de Localização",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_ul.py",
            },
            {
                "name": "Alteração de UL - Unidade de Localização",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_ul.py",
            },
            {
                "name": "Exclusão de UL - Unidade de Localização",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_ul.py",
            },
            {
                "name": "Cadastro de CC - Centro de Custos",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_cc.py",
                "exclude_clients": ["jfrj"],
            },
            {
                "name": "Consulta de CC - Centro de Custos",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_cc.py",
            },
            {
                "name": "Alteração de CC - Centro de Custos",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_cc.py",
            },
            {
                "name": "Exclusão de CC - Centro de Custos",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_cc.py",
                "exclude_clients": ["jfrj"],
            },
            {
                "name": "Cadastro de Almoxarifado",
                "path": "tests/corporativo/estrutura_organizacional/test_cadastro_almoxarifado.py",
            },
            {
                "name": "Consulta de Almoxarifado",
                "path": "tests/corporativo/estrutura_organizacional/test_consulta_almoxarifado.py",
            },
            {
                "name": "Alteração de Almoxarifado",
                "path": "tests/corporativo/estrutura_organizacional/test_alteracao_almoxarifado.py",
            },
            {
                "name": "Exclusão de Almoxarifado",
                "path": "tests/corporativo/estrutura_organizacional/test_exclusao_almoxarifado.py",
            },
        ],
        "Entidade Externa": [
            {
                "name": "Cadastro de Fornecedor",
                "path": "tests/corporativo/entidade_externa/test_cadastro_fornecedor.py",
            },
            {
                "name": "Consulta de Fornecedor",
                "path": "tests/corporativo/entidade_externa/test_consulta_fornecedor.py",
            },
            {
                "name": "Alteração de Fornecedor",
                "path": "tests/corporativo/entidade_externa/test_alteracao_fornecedor.py",
            },
            {
                "name": "Exclusão de Fornecedor",
                "path": "tests/corporativo/entidade_externa/test_exclusao_fornecedor.py",
            },
            {
                "name": "Cadastro de Órgão Externo",
                "path": "tests/corporativo/entidade_externa/test_cadastro_orgao_externo.py",
            },
            {
                "name": "Consulta de Órgão Externo",
                "path": "tests/corporativo/entidade_externa/test_consulta_orgao_externo.py",
            },
            {
                "name": "Alteração de Órgão Externo",
                "path": "tests/corporativo/entidade_externa/test_alteracao_orgao_externo.py",
            },
            {
                "name": "Exclusão de Órgão Externo",
                "path": "tests/corporativo/entidade_externa/test_exclusao_orgao_externo.py",
            },
            {
                "name": "Cadastro de Portador",
                "path": "tests/corporativo/entidade_externa/test_cadastro_portador.py",
            },
            {
                "name": "Consulta de Portador",
                "path": "tests/corporativo/entidade_externa/test_consulta_portador.py",
            },
            {
                "name": "Alteração de Portador",
                "path": "tests/corporativo/entidade_externa/test_alteracao_portador.py",
            },
            {
                "name": "Exclusão de Portador",
                "path": "tests/corporativo/entidade_externa/test_exclusao_portador.py",
            },
        ],
        "Localidade": [
            {
                "name": "Cadastro de País",
                "path": "tests/corporativo/localidade/test_cadastro_pais.py",
            },
            {
                "name": "Consulta de País",
                "path": "tests/corporativo/localidade/test_consulta_pais.py",
            },
            {
                "name": "Alteração de País",
                "path": "tests/corporativo/localidade/test_alteracao_pais.py",
            },
            {
                "name": "Exclusão de País",
                "path": "tests/corporativo/localidade/test_exclusao_pais.py",
            },
            {
                "name": "Cadastro de Região",
                "path": "tests/corporativo/localidade/test_cadastro_regiao.py",
            },
            {
                "name": "Consulta de Região",
                "path": "tests/corporativo/localidade/test_consulta_regiao.py",
            },
            {
                "name": "Alteração de Região",
                "path": "tests/corporativo/localidade/test_alteracao_regiao.py",
            },
            {
                "name": "Exclusão de Região",
                "path": "tests/corporativo/localidade/test_exclusao_regiao.py",
            },
            {
                "name": "Cadastro de UF - Unidade da Federação",
                "path": "tests/corporativo/localidade/test_cadastro_uf.py",
            },
            {
                "name": "Consulta de UF - Unidade da Federação",
                "path": "tests/corporativo/localidade/test_consulta_uf.py",
            },
            {
                "name": "Alteração de UF - Unidade da Federação",
                "path": "tests/corporativo/localidade/test_alteracao_uf.py",
            },
            {
                "name": "Exclusão de UF - Unidade da Federação",
                "path": "tests/corporativo/localidade/test_exclusao_uf.py",
            },
            {
                "name": "Cadastro de Cidade",
                "path": "tests/corporativo/localidade/test_cadastro_cidade.py",
            },
            {
                "name": "Consulta de Cidade",
                "path": "tests/corporativo/localidade/test_consulta_cidade.py",
            },
            {
                "name": "Alteração de Cidade",
                "path": "tests/corporativo/localidade/test_alteracao_cidade.py",
            },
            {
                "name": "Exclusão de Cidade",
                "path": "tests/corporativo/localidade/test_exclusao_cidade.py",
            },
            {
                "name": "Cadastro de Instalação",
                "path": "tests/corporativo/localidade/test_cadastro_instalacao.py",
            },
            {
                "name": "Consulta de Instalação",
                "path": "tests/corporativo/localidade/test_consulta_instalacao.py",
            },
            {
                "name": "Alteração de Instalação",
                "path": "tests/corporativo/localidade/test_alteracao_instalacao.py",
            },
            {
                "name": "Exclusão de Instalação",
                "path": "tests/corporativo/localidade/test_exclusao_instalacao.py",
            },
            {
                "name": "Cadastro de Endereço",
                "path": "tests/corporativo/localidade/test_cadastro_endereco.py",
            },
            {
                "name": "Consulta de Endereço",
                "path": "tests/corporativo/localidade/test_consulta_endereco.py",
            },
            {
                "name": "Alteração de Endereço",
                "path": "tests/corporativo/localidade/test_alteracao_endereco.py",
            },
            {
                "name": "Exclusão de Endereço",
                "path": "tests/corporativo/localidade/test_exclusao_endereco.py",
            },
        ],
        "Funcionário": [
            {
                "name": "Cadastro de Função",
                "path": "tests/corporativo/funcionario/test_cadastro_funcao.py",
            },
            {
                "name": "Consulta de Função",
                "path": "tests/corporativo/funcionario/test_consulta_funcao.py",
            },
            {
                "name": "Alteração de Função",
                "path": "tests/corporativo/funcionario/test_alteracao_funcao.py",
            },
            {
                "name": "Exclusão de Função",
                "path": "tests/corporativo/funcionario/test_exclusao_funcao.py",
            },
            {
                "name": "Cadastro de Funcionário",
                "path": "tests/corporativo/funcionario/test_cadastro_funcionario.py",
            },
            {
                "name": "Consulta de Funcionário",
                "path": "tests/corporativo/funcionario/test_consulta_funcionario.py",
            },
            {
                "name": "Alteração de Funcionário",
                "path": "tests/corporativo/funcionario/test_alteracao_funcionario.py",
            },
            {
                "name": "Exclusão de Funcionário",
                "path": "tests/corporativo/funcionario/test_exclusao_funcionario.py",
            },
        ],
        "Material": [
            {
                "name": "Cadastro de Unidade de Medida",
                "path": "tests/corporativo/material/test_cadastro_unidade_medida.py",
            },
            {
                "name": "Consulta de Unidade de Medida",
                "path": "tests/corporativo/material/test_consulta_unidade_medida.py",
            },
            {
                "name": "Alteração de Unidade de Medida",
                "path": "tests/corporativo/material/test_alteracao_unidade_medida.py",
            },
            {
                "name": "Exclusão de Unidade de Medida",
                "path": "tests/corporativo/material/test_exclusao_unidade_medida.py",
            },
            {
                "name": "Cadastro de Material de Consumo",
                "path": "tests/corporativo/material/test_cadastro_material_consumo.py",
            },
            {
                "name": "Consulta de Material de Consumo",
                "path": "tests/corporativo/material/test_consulta_material_consumo.py",
            },
            {
                "name": "Alteração de Material de Consumo",
                "path": "tests/corporativo/material/test_alteracao_material_consumo.py",
            },
            {
                "name": "Exclusão de Material de Consumo",
                "path": "tests/corporativo/material/test_exclusao_material_consumo.py",
            },
            {
                "name": "Cadastro de Material Permanente",
                "path": "tests/corporativo/material/test_cadastro_material_permanente.py",
            },
            {
                "name": "Consulta de Material Permanente",
                "path": "tests/corporativo/material/test_consulta_material_permanente.py",
            },
            {
                "name": "Alteração de Material Permanente",
                "path": "tests/corporativo/material/test_alteracao_material_permanente.py",
            },
            {
                "name": "Exclusão de Material Permanente",
                "path": "tests/corporativo/material/test_exclusao_material_permanente.py",
            },
            {
                "name": "Cadastro de Material Serviço",
                "path": "tests/corporativo/material/test_cadastro_material_servico.py",
            },
            {
                "name": "Consulta de Material Serviço",
                "path": "tests/corporativo/material/test_consulta_material_servico.py",
            },
            {
                "name": "Alteração de Material Serviço",
                "path": "tests/corporativo/material/test_alteracao_material_servico.py",
            },
            {
                "name": "Exclusão de Material Serviço",
                "path": "tests/corporativo/material/test_exclusao_material_servico.py",
            },
            {
                "name": "Cadastro de Modelo de Importação",
                "path": "tests/corporativo/material/test_cadastro_modelo_importacao.py",
                "versao_minima": 4,
            },
            {
                "name": "Consulta de Modelo de Importação",
                "path": "tests/corporativo/material/test_consulta_modelo_importacao.py",
                "versao_minima": 4,
            },
            {
                "name": "Alteração de Modelo de Importação",
                "path": "tests/corporativo/material/test_alteracao_modelo_importacao.py",
                "versao_minima": 4,
            },
            {
                "name": "Exclusão de Modelo de Importação",
                "path": "tests/corporativo/material/test_exclusao_modelo_importacao.py",
                "versao_minima": 4,
            },
            {
                "name": "Cadastro de Supply",
                "path": "tests/corporativo/material/test_cadastro_supply.py",
                "exclude_clients": ["tse"],
            },
            {
                "name": "Consulta de Supply",
                "path": "tests/corporativo/material/test_consulta_supply.py",
                "exclude_clients": ["tse"],
            },
            {
                "name": "Alteração de Supply",
                "path": "tests/corporativo/material/test_alteracao_supply.py",
                "exclude_clients": ["tse"],
            },
            {
                "name": "Exclusão de Supply",
                "path": "tests/corporativo/material/test_exclusao_supply.py",
                "exclude_clients": ["tse"],
            },
        ],
        "Característica do bem": [
            {
                "name": "Cadastro de Definição da Característica",
                "path": "tests/corporativo/caracteristica_bem/test_cadastro_definicao_caracteristica.py",
            },
            {
                "name": "Consulta de Definição da Característica",
                "path": "tests/corporativo/caracteristica_bem/test_corporativo_consulta_definicao_caracteristica.py",
            },
            {
                "name": "Alteração de Definição da Característica",
                "path": "tests/corporativo/caracteristica_bem/test_corporativo_alteracao_definicao_caracteristica.py",
            },
            {
                "name": "Exclusão de Definição da Característica",
                "path": "tests/corporativo/caracteristica_bem/test_corporativo_exclusao_definicao_caracteristica.py",
            },
        ],
        "Segurança": [
            {
                "name": "Cadastro de Perfil",
                "path": "tests/corporativo/seguranca/test_cadastro_perfil.py",
            },
            {
                "name": "Consulta de Perfil",
                "path": "tests/corporativo/seguranca/test_consulta_perfil.py",
            },
            {
                "name": "Alteração de Perfil",
                "path": "tests/corporativo/seguranca/test_alteracao_perfil.py",
            },
            {
                "name": "Exclusão de Perfil",
                "path": "tests/corporativo/seguranca/test_exclusao_perfil.py",
            },
            {
                "name": "Cadastro de Usuário",
                "path": "tests/corporativo/seguranca/test_cadastro_usuario.py",
            },
            {
                "name": "Consulta de Usuário",
                "path": "tests/corporativo/seguranca/test_consulta_usuario.py",
            },
            {
                "name": "Alteração de Usuário",
                "path": "tests/corporativo/seguranca/test_alteracao_usuario.py",
            },
            {
                "name": "Exclusão de Usuário",
                "path": "tests/corporativo/seguranca/test_exclusao_usuario.py",
            },
        ],
    },
}
