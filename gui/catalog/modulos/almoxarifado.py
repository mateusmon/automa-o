"""
Catálogo de testes do módulo Almoxarifado (ASI Automação 2.0).

Dado estrutural puro (ver GUIA_GUI.md secao 4) — sem lógica de UI.
Editado manualmente; nao gerar/reescrever programaticamente.
"""

MODULE = {
        "meta": {},
        "sections": {
            "Movimentação Interna": [
                {
                    "name": "Consulta de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_material.py"
                },
                {
                    "name": "Entrada Compra", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_simples.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada Compra com Observação", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_simples_observacao.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada Extra-Orçamentária", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_extra_orcamentaria.py"
                },
                {
                    "name": "Entrada de Materiais — Todos os Tipos e Finalidades",
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_materiais_todos_tipos.py",
                    # "clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Materiais (20 Itens)",
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_20_materiais.py",
                },
                {
                    "name": "Entrada Doação", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_almoxarifado_entrada_doacao.py"
                },
                {
                    "name": "Entrada Consumo Imediato", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_consumo_imediato.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Consulta de Última Entrada",
                    "path": "tests/almoxarifado/movimentacao_interna/test_almoxarifado_consulta_entrada.py"
                },
                {
                    "name": "Alteração de Entrada Compra", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_almoxarifado_alteracao_entrada.py"
                },
                {
                    "name": "Exclusão de Entrada Compra", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_ultima_entrada.py"
                },
                {
                    "name": "Solicitação de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_solicitacao_materiais.py"
                },
                {
                    "name": "Consulta de Solicitação de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_solicitacao_materiais.py"
                },
                {
                    "name": "Alteração de Solicitação de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_alteracao_solicitacao_materiais.py"
                },
                {
                    "name": "Exclusão de Solicitação de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_solicitacao_materiais.py"
                },
                {
                    "name": "Cadastro de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_cadastro_requisicao.py"
                },
                {
                    "name": "Cadastro de Requisição (20 Itens)",
                    "path": "tests/almoxarifado/movimentacao_interna/test_cadastro_requisicao_20_itens.py",
                },
                {
                    "name": "Consulta de Cadastro de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_cadastro_requisicao.py"
                },
                {
                    "name": "Alteração de Cadastro de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_alteracao_cadastro_requisicao.py"
                },
                {
                    "name": "Exclusão de Cadastro de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_cadastro_requisicao.py",
                },
                {
                    "name": "Autorização de Requisição",
                    "path": "tests/almoxarifado/movimentacao_interna/test_autorizacao_requisicao.py"
                },
                {
                    "name": "Atendimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_atendimento_requisicao.py"
                },
                {
                    "name": "Consulta de Atendimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_atendimento_requisicao.py"
                },
                {
                    "name": "Alteração de Atendimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_alteracao_atendimento_requisicao.py"
                },
                {
                    "name": "Exclusão de Atendimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_atendimento_requisicao.py"
                },
                {
                    "name": "Atendimento Automático de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_atendimento_requisicao_automatico.py"
                },
                {
                    "name": "Atendimento de Requisição (20 Itens)",
                    "path": "tests/almoxarifado/movimentacao_interna/test_atendimento_requisicao_automatica_20_itens.py",
                },
                {
                    "name": "Recebimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_recebimento_requisicao.py"
                },
                {
                    "name": "Consulta de Recebimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_recebimento_requisicao.py"
                },
                {
                    "name": "Exclusão de Recebimento de Requisição", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_recebimento_requisicao.py"
                },
                {
                    "name": "Devolução de Materiais", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_devolucao.py"
                },
                {
                    "name": "Consulta de Devolução de Materiais", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_devolucao_materiais.py"
                },
                {
                    "name": "Alteração de Devolução de Materiais", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_alteracao_devolucao_materiais.py"
                },
                {
                    "name": "Exclusão de Devolução de Materiais", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_devolucao_materiais.py"
                },
                {
                    "name": "Recebimento de Devolução de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_recebimento_devolucao.py"
                },
                {
                    "name": "Consulta de Recebimento de Devolução de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_recebimento_devolucao.py"
                },
                {
                    "name": "Exclusão de Recebimento de Devolução de Materiais",
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_recebimento_devolucao.py"
                },
                {
                    "name": "Baixa de Material por Extravio", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_baixa.py"
                },
                {
                    "name": "Baixa de Material por Doação", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_baixa_por_doacao.py"
                },
                {
                    "name": "Baixa de Material por Cadastro Indevido", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_baixa_por_cadastro_indevido.py"
                },
                {
                    "name": "Baixa de Material Completa", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_baixa_completa.py"
                },
                {
                    "name": "Consulta de Baixa de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_baixa_material.py"
                },
                {
                    "name": "Alteração de Baixa de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_alteracao_baixa_material.py"
                },
                {
                    "name": "Exclusão de Baixa de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_baixa_material.py"
                },
                {
                    "name": "Estorno de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_estorno.py"
                },
                {
                    "name": "Consulta de Estorno de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_estorno_materiais.py"
                },
                {
                    "name": "Exclusão de Estorno de Material", 
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_estorno_materiais.py"
                },
                {
                    "name": "Transferência entre Contas",
                    "path": "tests/almoxarifado/movimentacao_interna/test_transferencia_entre_contas.py"
                },
                {
                    "name": "Consulta de Transferência entre Contas",
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_transferencia_entre_contas.py"
                },
                {
                    "name": "Exclusão de Transferência entre Contas",
                    "path": "tests/almoxarifado/movimentacao_interna/test_exclusao_transferencia_entre_contas.py"
                }
            ],

            "Movimentação Externa": [
                {
                    "name": "Cadastro da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_cadastro_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Consulta de Cadastro da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_consulta_cadastro_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Alteração de Cadastro da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_alteracao_cadastro_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Exclusão de Cadastro da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_exclusao_cadastro_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Atendimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_atendimento_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Consulta de Atendimento de Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_consulta_atendimento_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Alteração do Atendimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_alteracao_atendimento_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Exclusão do Atendimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_exclusao_atendimento_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Recebimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_recebimento_transferencia_entre_almoxarifado.py"
                },
                {
                    "name": "Consulta de Recebimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_consulta_recebimento_transferencia_entre_almoxarifados.py"
                },
                {
                    "name": "Exclusão de Recebimento da Transferência entre Almoxarifados",
                    "path": "tests/almoxarifado/movimentacao_externa/test_exclusao_recebimento_transferencia_entre_almoxarifados.py"
                },
            ],

            "Gestão de Estoque": [
                {
                    "name": "Política de Compras - Parâmetros Baixa Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_parametros_baixa_frequencia.py"
                },
                {
                    "name": "Consulta de Parâmetros Baixa Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_consulta_parametros_baixa_frequencia.py"
                },
                {
                    "name": "Alteração de Parâmetros Baixa Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_alteracao_parametros_baixa_frequencia.py"
                },
                {
                    "name": "Política de Compras - Parâmetros Alta Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_parametros_alta_frequencia.py"
                },
                {
                    "name": "Consulta de Parâmetros de Alta Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_consulta_parametros_alta_frequencia.py"
                },
                {
                    "name": "Alteração de Parâmetros de Alta Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_alteracao_parametros_alta_frequencia.py"
                },
                {
                    "name": "Exclusão de Parâmetros de Alta Frequência",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_exclusao_parametros_alta_frequencia.py"
                },
                {
                    "name": "Inventário",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_inventario.py"
                },
                {
                    "name": "Inventário por Levantamento",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_inventario_por_levantamento.py"
                },
                {
                    "name": "Inventário por Auditoria",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_inventario_por_auditoria.py"
                },
                {
                    "name": "Consulta de Inventário",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_consulta_inventario.py"
                },
                {
                    "name": "Alteração de Inventário",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_alteracao_inventario.py"
                },
                {
                    "name": "Exclusão de Inventário",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_exclusao_inventario.py"
                },
                {
                    "name": "Transferência entre Endereços",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_transferencia_entre_enderecos.py"
                },
                {
                    "name": "Consulta de Transferência entre Endereços",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_consulta_transferencia_entre_enderecos.py"
                },
                {
                    "name": "Exclusão de Transferência entre Endereços",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_exclusao_transferencia_entre_enderecos.py"
                },
                {
                    "name": "Classificação de Material Quanto à Natureza",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_natureza.py"
                },
                {
                    "name": "Classificação de Material Quanto ao Consumo",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_consumo.py"
                },
                {
                    "name": "Classificação de Material Quanto à Criticidade",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_criticidade.py"
                },
                {
                    "name": "Classificação de Material Quanto ao Valor",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_valor.py"
                },
                {
                    "name": "Classificação de Material por Almoxarifado",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_almoxarifado.py"
                },
                {
                    "name": "Classificação de Material por Material",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_por_material.py"
                },
                {
                    "name": "Classificação de Material por Conta",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_conta.py"
                },
                {
                    "name": "Classificação de Material por Endereço",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_endereco.py"
                },
                {
                    "name": "Classificação de Material por Natureza de Estoque",
                    "path": "tests/almoxarifado/gestao_de_estoque/test_classificacao_material_natureza_estoque.py"
                },
            ],

            "Gestão de Compras": [
                {
                    "name": "Pedido de Ressuprimento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_pedido_ressuprimento.py"
                },
                {
                    "name": "Consulta de Pedido de Ressuprimento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_pedido_ressuprimento.py"
                },
                {
                    "name": "Alteração de Pedido de Ressuprimento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_alteracao_pedido_ressuprimento.py"
                },
                {
                    "name": "Exclusão de Pedido de Ressuprimento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_exclusao_pedido_ressuprimento.py"
                },
                {
                    "name": "Pedido de Compra",
                    "path": "tests/almoxarifado/gestao_de_compras/test_pedido_compra.py"
                },
                {
                    "name": "Consulta de Pedido de Compra",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_pedido_compra.py"
                },
                {
                    "name": "Alteração de Pedido de Compra",
                    "path": "tests/almoxarifado/gestao_de_compras/test_alteracao_pedido_compra.py"
                },
                {
                    "name": "Exclusão de Pedido de Compra",
                    "path": "tests/almoxarifado/gestao_de_compras/test_exclusao_pedido_compra.py"
                },
                {
                    "name": "Autorização de Pedido de Compra",
                    "path": "tests/almoxarifado/gestao_de_compras/test_autorizacao_pedido_compra.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Baixa de Pedido",
                    "path": "tests/almoxarifado/gestao_de_compras/test_baixa_pedido.py"
                },
                {
                    "name": "Consulta de Baixa de Pedido",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_baixa_pedido.py"
                },
                {
                    "name": "Alteração de Baixa de Pedido",
                    "path": "tests/almoxarifado/gestao_de_compras/test_alteracao_baixa_pedido.py"
                },
                {
                    "name": "Cadastro de Evento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_evento.py"
                },
                {
                    "name": "Consulta de Cadastro de Evento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_evento.py"
                },
                {
                    "name": "Alteração de Cadastro de Evento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_alteracao_evento.py"
                },
                {
                    "name": "Exclusão de Cadastro de Evento",
                    "path": "tests/almoxarifado/gestao_de_compras/test_exclusao_evento.py"
                },
                {
                    "name": "Cadastro de Previsão de Consumo da UR",
                    "path": "tests/almoxarifado/gestao_de_compras/test_cadastro_previsao_consumo.py"
                },
                {
                    "name": "Consulta de Cadastro de Previsão de Consumo da UR",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_previsao_consumo.py"
                },
                {
                    "name": "Alteração de Cadastro de Previsão de Consumo da UR",
                    "path": "tests/almoxarifado/gestao_de_compras/test_alteracao_previsao_consumo.py"
                },
                {
                    "name": "Exclusão de Cadastro de Previsão de Consumo da UR",
                    "path": "tests/almoxarifado/gestao_de_compras/test_exclusao_previsao_consumo.py"
                },
                {
                    "name": "Nível de Estoque",
                    "path": "tests/almoxarifado/gestao_de_compras/test_nivel_estoque.py"
                },
                {
                    "name": "Consulta de Relatórios de Empenho",
                    "path": "tests/almoxarifado/gestao_de_compras/test_consulta_relatorios_empenho.py",
                    # Na v4 o equivalente fica em Almoxarifado → Relatórios (ver GUIA_TESTES.md)
                    "versao_maxima": 3
                },
                {
                    "name": "Impressão de Relatórios de Empenho",
                    "path": "tests/almoxarifado/gestao_de_compras/test_impressao_relatorios_empenho.py",
                    # Na v4 o equivalente fica em Almoxarifado → Relatórios (ver GUIA_TESTES.md)
                    "versao_maxima": 3
                }
            ],

            "Financeiro": [
                {
                    "name": "Prévia RMMA", 
                    "path": "tests/almoxarifado/financeiro/test_gerar_previa_rmma.py"
                },
                {
                    "name": "Relatório RMMA",
                    "path": "tests/almoxarifado/financeiro/test_rmma.py"
                },
                {
                    "name": "Fechar Mês", 
                    "path": "tests/almoxarifado/financeiro/test_almoxarifado_fechar_mes.py"
                },
                {
                    "name": "Abrir Mês", 
                    "path": "tests/almoxarifado/financeiro/test_almoxarifado_abrir_mes.py"
                },
                {
                    "name": "Ativar UG", 
                    "path": "tests/almoxarifado/financeiro/test_ativar_ug.py"
                },
                {
                    "name": "Suspender UG", 
                    "path": "tests/almoxarifado/financeiro/test_suspender_ug.py"
                },
                {
                    "name": "Verificar Pendências da UG", 
                    "path": "tests/almoxarifado/financeiro/test_verificar_pendencias.py"
                },
            ],

            "Auxiliares": [
                {
                    "name": "Definição das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_definicao_caracteristica.py"
                },
                {
                    "name": "Consulta de Definição das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_almoxarifado_consulta_definicao_caracteristica.py"
                },
                {
                    "name": "Alteração de Definição das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_almoxarifado_alteracao_definicao_caracteristica.py"
                },
                {
                    "name": "Exclusão de Definição das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_almoxarifado_exclusao_definicao_caracteristica.py"
                },
                {
                    "name": "Manutenção das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_manutencao_caracteristicas.py"
                },
                {
                    "name": "Consulta de Manutenção das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_consulta_manutencao_caracteristicas.py"
                },
                {
                    "name": "Alteração de Manutenção das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_manutencao_caracteristicas.py"
                },
                {
                    "name": "Exclusão de Manutenção das Características", 
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_manutencao_caracteristicas.py"
                },
                {
                    "name": "Endereçamento de Material", 
                    "path": "tests/almoxarifado/auxiliares/test_enderecamento_material.py"
                },
                {
                    "name": "Consulta do Endereçamento de Material", 
                    "path": "tests/almoxarifado/auxiliares/test_consulta_enderecamento_material.py"
                },
                {
                    "name": "Alteração do Endereçamento de Material", 
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_enderecamento_material.py"
                },
                {
                    "name": "Exclusão do Endereçamento de Material", 
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_enderecamento_material.py"
                },
                {
                    "name": "Endereço de Estoque",
                    "path": "tests/almoxarifado/auxiliares/test_endereco_estoque.py"
                },
                {
                    "name": "Consulta de Endereço de Estoque",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_endereco_estoque.py"
                },
                {
                    "name": "Alteração de Endereço de Estoque",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_endereco_estoque.py"
                },
                {
                    "name": "Exclusão de Endereço de Estoque",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_endereco_estoque.py"
                },
                {
                    "name": "Calendário de Requisição",
                    "path": "tests/almoxarifado/auxiliares/test_calendario_requisicao.py"
                },
                {
                    "name": "Consulta de Calendário de Requisição",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_calendario_requisicao.py"
                },
                {
                    "name": "Alteração de Calendário de Requisição",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_calendario_requisicao.py"
                },
                {
                    "name": "Exclusão de Calendário de Requisição",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_calendario_requisicao.py"
                },
                {
                    "name": "Catálogo Restrito",
                    "path": "tests/almoxarifado/auxiliares/test_catalogo_restrito.py"
                },
                {
                    "name": "Consulta do Catálogo Restrito",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_catalogo_restrito.py"
                },
                {
                    "name": "Alteração do Catálogo Restrito",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_catalogo_restrito.py"
                },
                {
                    "name": "Exclusão do Catálogo Restrito",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_catalogo_restrito.py"
                },
                {
                    "name": "Consulta de Conta Contábil",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_conta_contabil_almox.py"
                },
                {
                    "name": "Configuração Lançamentos - Operações",
                    "path": "tests/almoxarifado/auxiliares/test_configuracao_lancamentos_operacoes.py"
                },
                {
                    "name": "Consulta de Configuração Lançamentos - Operações",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_configuracao_lancamentos_operacoes.py"
                },
                {
                    "name": "Alteração de Configuração Lançamentos - Operações",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_configuracao_lancamentos_operacoes.py"
                },
                {
                    "name": "Exclusão de Configuração Lançamentos - Operações",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_configuracao_lancamentos_operacoes.py"
                },
                {
                    "name": "Configuração Lançamentos - Documentação",
                    "path": "tests/almoxarifado/auxiliares/test_configuracao_lancamentos_documentacao.py"
                },
                {
                    "name": "Consulta de Configuração Lançamentos - Documentação",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_configuracao_lancamentos_documentacao.py"
                },
                {
                    "name": "Alteração de Configuração Lançamentos - Documentação",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_configuracao_lancamentos_documentacao.py"
                },
                {
                    "name": "Exclusão de Configuração Lançamentos - Documentação",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_configuracao_lancamentos_documentacao.py"
                },
                {
                    "name": "Configuração Lançamentos - Tipo de Observação",
                    "path": "tests/almoxarifado/auxiliares/test_configuracao_lancamentos_observacao.py"
                },
                {
                    "name": "Consulta de Configuração Lançamentos - Tipo de Observação",
                    "path": "tests/almoxarifado/auxiliares/test_consulta_configuracao_lancamentos_observacao.py"
                },
                {
                    "name": "Alteração de Configuração Lançamentos - Tipo de Observação",
                    "path": "tests/almoxarifado/auxiliares/test_alteracao_configuracao_lancamentos_observacao.py"
                },
                {
                    "name": "Exclusão de Configuração Lançamentos - Tipo de Observação",
                    "path": "tests/almoxarifado/auxiliares/test_exclusao_configuracao_lancamentos_observacao.py"
                },
            ],

            "Relatórios": [
                {
                    "name": "Relatórios Gerenciais - Não Movimentado", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_nao_movimentado.py"
                },
                {
                    "name": "Relatórios Gerenciais - Material - Etiquetas",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_material_etiquetas.py"
                },
                {
                    "name": "Relatórios Gerenciais - Movimentação",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_movimentacao.py"
                },
                {
                    "name": "Relatórios Gerenciais - Entradas",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_entradas.py"
                },
                {
                    "name": "Relatórios Gerenciais - Saídas",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_saidas.py"
                },
                {
                    "name": "Relatórios Gerenciais - Estoque de Almoxarifado",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_estoque_almoxarifado.py"
                },
                {
                    "name": "Relatórios Gerenciais - Materiais a Vencer",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_materias_vencer.py"
                },
                {
                    "name": "Relatórios Gerenciais - Gráficos das Aquisições", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_graficos_aquisicoes.py"
                },
                {
                    "name": "Relatórios Gerenciais - Gráficos do Consumo", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_graficos_consumo.py"
                },
                {
                    "name": "Relatórios Gerenciais - Atendimentos", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_atendimentos.py"
                },
                {
                    "name": "Relatórios Gerenciais - Saldo de Previsão de Consumo",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_saldo_previsao_consumo.py",
                    "exclude_clients": ["mpf", "mpfv4"]
                },
                {
                    "name": "Relatórios Gerenciais - Fornecedor / Materiais Vendidos", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_fornecedor_materiais_vendidos.py"
                },
                {
                    "name": "Relatórios Gerenciais - Materiais Vendidos / Fornecedores", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_materiais_vendidos_fornecedores.py"
                },
                {
                    "name": "Relatórios Gerenciais - Empenho",
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_empenho.py",
                    # Na v3 o equivalente fica em Almoxarifado → Gestão de Compras (ver GUIA_TESTES.md)
                    "versao_minima": 4
                },
                {
                    "name": "Relatórios Gerenciais - Solicitados", 
                    "path": "tests/almoxarifado/relatorios/test_relatorios_gerenciais_solicitados.py"
                },
            ],

            "Casos de Teste": [
                {
                    "name": "Ciclo Completo de Requisição de Material",
                    "path": "tests/casos/almoxarifado/test_ciclo_requisicao.py",
                    "description": ( # Esse descrição não funciona ainda. ajuste no modules_builder
                            "Executa o ciclo completo de requisição de material:\n"
                            "1. Entrada de material\n"
                            "2. Cadastro de requisição\n"
                            "3. Autorização de requisição (se aplicável)\n"
                            "4. Atendimento de requisição\n"
                            "5. Recebimento de requisição\n"
                            "6. Devolução de material\n"
                            "7. Recebimento de devolução"
                        ),
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                }
            ]
        },
    }
