"""
Catálogo de testes do módulo Patrimônio (ASI Automação 2.0).

Dado estrutural puro (ver GUIA_GUI.md secao 4) — sem lógica de UI.
Editado manualmente; nao gerar/reescrever programaticamente.
"""

MODULE = {
    "meta": {},
    "sections": {
        "Movimentação": [
                {
                    "name": "Consulta Geral", 
                    "path": "tests/patrimonio/movimentacao/test_consulta_geral.py"
                },
                {
                    "name": "Entrada de Bens",
                    "path": "tests/patrimonio/movimentacao/test_entrada_patrimonio.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bens (20 Materiais)",
                    "path": "tests/patrimonio/movimentacao/test_entrada_20_materiais.py",
                },
                {
                    "name": "Entrada de Bens com Observação",
                    "path": "tests/patrimonio/movimentacao/test_entrada_observacao.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bem Próprio Controlado",
                    "path": "tests/patrimonio/movimentacao/test_entrada_proprio_controlado.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bem de Terceiros",
                    "path": "tests/patrimonio/movimentacao/test_entrada_terceiros.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bem tipo Extra-orçamentária",
                    "path": "tests/patrimonio/movimentacao/test_entrada_extraorcamentaria.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bem tipo Importação (N/ORÇ)",
                    "path": "tests/patrimonio/movimentacao/test_entrada_importacao.py",
                    "clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bem tipo Doação",
                    "path": "tests/patrimonio/movimentacao/test_patrimonio_entrada_doacao.py",
                    "exclude_clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Entrada de Bens — Todos os Tipos e Finalidades",
                    "path": "tests/casos/patrimonio/test_entrada_bens_todos_tipos.py",
                    # "clients": ["seadpb", "seadpbadapt"]
                },
                {
                    "name": "Consulta de Entrada",
                    "path": "tests/patrimonio/movimentacao/test_patrimonio_consulta_entrada.py"
                },
                {
                    "name": "Alteração de Entrada",
                    "path": "tests/patrimonio/movimentacao/test_patrimonio_alteracao_entrada.py"
                },
                {
                    "name": "Exclusão de Entrada",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_entrada.py"
                },
                {
                    "name": "Transferência Interna Completa", 
                    "path": "tests/patrimonio/movimentacao/test_transferencia_interna_completa.py"
                },
                {
                    "name": "Transferência Interna", 
                    "path": "tests/patrimonio/movimentacao/test_transferencia_interna.py"
                },
                {
                    "name": "Transferência Interna (20 Materiais)",
                    "path": "tests/patrimonio/movimentacao/test_transferencia_interna_20_materiais.py",
                },
                {
                    "name": "Transferência Interna Sem Assinatura Eletrônica", 
                    "path": "tests/patrimonio/movimentacao/test_transferencia_interna_sem_assinatura.py"
                },
                {
                    "name": "Autorização da Transferência Interna", 
                    "path": "tests/patrimonio/movimentacao/test_autorizacao_transferencia_interna.py"
                },
                {
                    "name": "Transferência Interna Temporária", 
                    "path": "tests/patrimonio/movimentacao/test_transferencia_interna_temporaria.py"
                },
                {
                    "name": "Consulta de Transferência Interna",
                    "path": "tests/patrimonio/movimentacao/test_consulta_transferencia_interna.py"
                },
                {
                    "name": "Exclusão de Transferência Interna",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_transferencia_interna.py"
                },
                {
                    "name": "Recebimento da Transferência Interna", 
                    "path": "tests/patrimonio/movimentacao/test_recebimento_transferencia_interna.py"
                },
                {
                    "name": "Recebimento da Transferência Interna Temporária", 
                    "path": "tests/patrimonio/movimentacao/test_recebimento_transferencia_interna_temporaria.py"
                },
                {
                    "name": "Recebimento da Transferência Interna Completa", 
                    "path": "tests/patrimonio/movimentacao/test_recebimento_transferencia_interna_completa.py"
                },
                {
                    "name": "Devolução da Transferência Interna", 
                    "path": "tests/patrimonio/movimentacao/test_devolucao_transferencia_interna.py"
                },
                {
                    "name": "Transferência Externa Completa",
                    "path": "tests/patrimonio/movimentacao/test_transferencia_externa_completa.py"
                },
                {
                    "name": "Devolução de Transferência Externa Completa",
                    "path": "tests/patrimonio/movimentacao/test_devolucao_transferencia_externa_completa.py"
                },
                {
                    "name": "Transferência Externa",
                    "path": "tests/patrimonio/movimentacao/test_transferencia_externa.py"
                },
                {
                    "name": "Consulta de Transferência Externa",
                    "path": "tests/patrimonio/movimentacao/test_consulta_transferencia_externa.py"
                },
                {
                    "name": "Alteração de Transferência Externa",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_transferencia_externa.py"
                },
                {
                    "name": "Exclusão de Transferência Externa",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_transferencia_externa.py"
                },
                {
                    "name": "Devolução de Transferência Externa",
                    "path": "tests/patrimonio/movimentacao/test_devolucao_transferencia_externa.py"
                },
                {
                    "name": "Seleção de Bens",
                    "path": "tests/patrimonio/movimentacao/test_selecao_bens.py"
                },
                {
                    "name": "Consulta de Seleção de Bens",
                    "path": "tests/patrimonio/movimentacao/test_consulta_selecao_bens.py"
                },
                {
                    "name": "Alteração de Seleção de Bens",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_selecao_bens.py"
                },
                {
                    "name": "Exclusão de Seleção de Bens",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_selecao_bens.py"
                },
                {
                    "name": "Baixa de Bens Doação",
                    "path": "tests/patrimonio/movimentacao/test_baixa_bens_doacao.py"
                },
                {
                    "name": "Baixa de Bens Cadastramento Indevido",
                    "path": "tests/patrimonio/movimentacao/test_baixa_bens_cadastramento_indevido.py"
                },
                {
                    "name": "Baixa de Bens Extravio ou Sinistro",
                    "path": "tests/patrimonio/movimentacao/test_baixa_bens_extravio_sinistro.py"
                },
                {
                    "name": "Consulta de Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_consulta_baixa_bens.py"
                },
                {
                    "name": "Alteração de Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_baixa_bens.py"
                },
                {
                    "name": "Exclusão de Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_baixa_bens.py"
                },
                {
                    "name": "Estorno da Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_estorno_baixa_bens.py"
                },
                {
                    "name": "Consulta do Estorno da Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_consulta_estorno_baixa_bens_flow.py"
                },
                {
                    "name": "Alteração do Estorno da Baixa de Bens",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_estorno_baixa_bens.py"
                },
                {
                    "name": "Contrato de Manutenção - Fora da Garantia",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_fora_garantia.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Contrato de Manutenção - Na Garantia",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_na_garantia.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Contrato de Manutenção - Outros ou Diversos",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_outros.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Consulta de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_consulta_contrato_manutencao.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Alteração de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_contrato_manutencao.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Exclusão de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_contrato_manutencao.py",
                    # Na v4 o equivalente fica em Patrimônio → Auxiliares → Contrato de Manutenção
                    "versao_maxima": 3
                },
                {
                    "name": "Cadastro de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_requisicao_bens.py"
                },
                {
                    "name": "Consulta de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_consulta_requisicao_bens.py"
                },
                {
                    "name": "Alteração de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_requisicao_bens.py"
                },
                {
                    "name": "Exclusão de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_requisicao_bens.py"
                },
                {
                    "name": "Atendimento de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_atendimento_requisicao_bens.py"
                },
                {
                    "name": "Consulta de Atendimento de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_consulta_atendimento_requisicao_bens.py"
                },
                {
                    "name": "Exclusão de Atendimento de Requisição de Bens",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_atendimento_requisicao_bens.py"
                },
                {
                    "name": "Adição a Bem Principal",
                    "path": "tests/patrimonio/movimentacao/test_adicao_bem_principal.py"
                },
                {
                    "name": "Consulta de Adição a Bem Principal",
                    "path": "tests/patrimonio/movimentacao/test_consulta_adicao_bem_principal.py"
                },
                {
                    "name": "Alteração de Adição a Bem Principal",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_adicao_bem_principal.py"
                },
                {
                    "name": "Exclusão de Adição a Bem Principal",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_adicao_bem_principal.py"
                },
                # Este teste está disponível para clientes v4 em Patrimônio → Movimentação → Baixa → Roteiro Padrão.
                {
                    "name": "Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_roteiro_padrao_baixa.py",
                    "versao_minima": 4
                },
                # Este teste está disponível para clientes v4 em Patrimônio → Movimentação → Baixa → Roteiro Padrão.
                {
                    "name": "Consulta de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_consulta_roteiro_padrao_baixa.py",
                    "versao_minima": 4
                },
                # Este teste está disponível para clientes v4 em Patrimônio → Movimentação → Baixa → Roteiro Padrão.
                {
                    "name": "Alteração de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_roteiro_padrao_baixa.py",
                    "versao_minima": 4
                },
                # Este teste está disponível para clientes v4 em Patrimônio → Movimentação → Baixa → Roteiro Padrão.
                {
                    "name": "Exclusão de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_roteiro_padrao_baixa.py",
                    "versao_minima": 4
                },
            ],

            "Inventário": [
                {
                    "name": "Formação de Comissão de Inventário",
                    "path": "tests/patrimonio/inventario/test_formacao_comissao_inventario.py"
                },
                {
                    "name": "Consulta de Formação de Comissão de Inventário",
                    "path": "tests/patrimonio/inventario/test_consulta_formacao_comissao_inventario.py"
                },
                {
                    "name": "Alteração de Formação de Comissão de Inventário",
                    "path": "tests/patrimonio/inventario/test_alteracao_formacao_comissao_inventario.py"
                },
                {
                    "name": "Exclusão de Formação de Comissão de Inventário",
                    "path": "tests/patrimonio/inventario/test_exclusao_formacao_comissao_inventario.py"
                },
            ],

            "Financeiro": [
                {
                    "name": "Resumo Mensal de Bens (RMB)",
                    "path": "tests/patrimonio/financeiro/test_resumo_mensal_bens_rmb.py"
                },
                {
                    "name": "Fechar Mês",
                    "path": "tests/patrimonio/financeiro/test_fechar_mes_pcdf.py",
                    "clients": ["pcdf", "pcdfv4"]
                },
                {
                    "name": "Abrir Mês",
                    "path": "tests/patrimonio/financeiro/test_abrir_mes_pcdf.py",
                    "clients": ["pcdf", "pcdfv4"]
                },
                {
                    "name": "Fechar Mês",
                    "path": "tests/patrimonio/financeiro/test_patrimonio_fechar_mes.py",
                    "exclude_clients": ["pcdf", "pcdfv4"]
                },
                {
                    "name": "Abrir Mês",
                    "path": "tests/patrimonio/financeiro/test_patrimonio_abrir_mes.py",
                    "exclude_clients": ["pcdf", "pcdfv4"]
                },
            ],
            
            "Modificação": [
                {
                    "name": "Modificação de Responsável do Local",
                    "path": "tests/patrimonio/modificacao/test_modificacao_responsavel_local.py"
                },
                {
                    "name": "Consulta Modificação de Responsável do Local",
                    "path": "tests/patrimonio/modificacao/test_consulta_modificacao_responsavel_local.py"
                },
                {
                    "name": "Exclusão Modificação de Responsável do Local",
                    "path": "tests/patrimonio/modificacao/test_exclusao_modificacao_responsavel_local.py"
                },
                {
                    "name": "Detentor do Bem - Cadastro",
                    "path": "tests/patrimonio/modificacao/test_detentor_bem_cadastro.py"
                },
                {
                    "name": "Consulta de Detentor do Bem - Cadastro",
                    "path": "tests/patrimonio/modificacao/test_consulta_detentor_bem_cadastro.py"
                },
                {
                    "name": "Exclusão de Detentor do Bem - Cadastro",
                    "path": "tests/patrimonio/modificacao/test_exclusao_detentor_bem_cadastro.py"
                },
                {
                    "name": "Detentor do Bem - Recebimento",
                    "path": "tests/patrimonio/modificacao/test_detentor_bem_recebimento.py"
                },
                {
                    "name": "Situação Física",
                    "path": "tests/patrimonio/modificacao/test_situacao_fisica.py"
                },
                {
                    "name": "Número Patrimonial",
                    "path": "tests/patrimonio/modificacao/test_numero_patrimonial.py"
                },
                {
                    "name": "Consulta de Número Patrimonial",
                    "path": "tests/patrimonio/modificacao/test_consulta_numero_patrimonial.py"
                },
                {
                    "name": "Exclusão de Número Patrimonial",
                    "path": "tests/patrimonio/modificacao/test_exclusao_numero_patrimonial.py"
                },
                {
                    "name": "Conta Contábil",
                    "path": "tests/patrimonio/modificacao/test_conta_contabil.py"
                },
                {
                    "name": "Consulta de Conta Contábil",
                    "path": "tests/patrimonio/modificacao/test_consulta_conta_contabil.py"
                },
                {
                    "name": "Exclusão de Modificação de Conta Contábil",
                    "path": "tests/patrimonio/modificacao/test_exclusao_conta_contabil.py"
                },
                {
                    "name": "Alteração Individual do Bem",
                    "path": "tests/patrimonio/modificacao/test_alteracao_individual_bem.py"
                },
                {
                    "name": "Consulta da Alteração Individual do Bem",
                    "path": "tests/patrimonio/modificacao/test_consulta_alteracao_individual_bem.py"
                },
                {
                    "name": "Alteração da Alteração Individual do Bem",
                    "path": "tests/patrimonio/modificacao/test_alteracao_alteracao_individual_bem.py"
                },
                {
                    "name": "Exclusão da Alteração Individual do Bem",
                    "path": "tests/patrimonio/modificacao/test_exclusao_alteracao_individual_bem.py"
                },
                {
                    "name": "Valor do Mercado",
                    "path": "tests/patrimonio/modificacao/test_valor_mercado.py"
                },
                {
                    "name": "Consulta de Valor do Mercado",
                    "path": "tests/patrimonio/modificacao/test_consulta_valor_mercado.py"
                },
                {
                    "name": "Alteração de Valor do Mercado",
                    "path": "tests/patrimonio/modificacao/test_alteracao_valor_mercado.py"
                },
                {
                    "name": "Exclusão de Valor do Mercado",
                    "path": "tests/patrimonio/modificacao/test_exclusao_valor_mercado.py"
                },
                {
                    "name": "Status do Bem",
                    "path": "tests/patrimonio/modificacao/test_status_bem.py"
                },
                {
                    "name": "Consulta de Status do Bem",
                    "path": "tests/patrimonio/modificacao/test_consulta_status_bem.py"
                },
                {
                    "name": "Alteração de Status do Bem",
                    "path": "tests/patrimonio/modificacao/test_alteracao_status_bem.py"
                },
                {
                    "name": "Exclusão de Status do Bem",
                    "path": "tests/patrimonio/modificacao/test_exclusao_status_bem.py"
                },
                {
                    "name": "Modificação de Material",
                    "path": "tests/patrimonio/modificacao/test_modificacao_material.py"
                },
                {
                    "name": "Consulta de Modificação de Material",
                    "path": "tests/patrimonio/modificacao/test_consulta_modificacao_material.py"
                },
                {
                    "name": "Exclusão de Modificação de Material",
                    "path": "tests/patrimonio/modificacao/test_exclusao_modificacao_material.py"
                },
            ],

            "Termo de Responsabilidade": [
                {
                    "name": "Emissão do Termo de Responsabilidade",
                    "path": "tests/patrimonio/termo_responsabilidade/test_emissao_termo_responsabilidade.py"
                },
                {
                    "name": "Consulta da Emissão do Termo de Responsabilidade",
                    "path": "tests/patrimonio/termo_responsabilidade/test_consulta_emissao_termo_responsabilidade.py",
                },
                {
                    "name": "Exclusão da Emissão do Termo de Responsabilidade",
                    "path": "tests/patrimonio/termo_responsabilidade/test_exclusao_emissao_termo_responsabilidade.py",
                },
                {
                    "name": "Recebimento do Termo de Responsabilidade",
                    "path": "tests/patrimonio/termo_responsabilidade/test_recebimento_termo_responsabilidade.py",
                },
                {
                    "name": "Consulta do Recebimento do Termo de Responsabilidade",
                    "path": "tests/patrimonio/termo_responsabilidade/test_consulta_recebimento_termo_responsabilidade.py",
                },
            ],

            "Auxiliares": [
                {
                    "name": "Situação Física",
                    "path": "tests/patrimonio/auxiliares/test_situacao_fisica.py"
                },
                {
                    "name": "Consulta de Situação Física",
                    "path": "tests/patrimonio/auxiliares/test_consulta_situacao_fisica.py"
                },
                {
                    "name": "Alteração de Situação Física",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_situacao_fisica.py"
                },
                {
                    "name": "Exclusão de Situação Física",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_situacao_fisica.py"
                },
                {
                    "name": "Catálogo de Materiais",
                    "path": "tests/patrimonio/auxiliares/test_catalogo_materiais.py"
                },
                {
                    "name": "Consulta de Catálogo de Materiais",
                    "path": "tests/patrimonio/auxiliares/test_consulta_catalogo_materiais.py"
                },
                {
                    "name": "Alteração de Catálogo de Materiais",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_catalogo_materiais.py"
                },
                {
                    "name": "Exclusão de Catálogo de Materiais",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_catalogo_materiais.py"
                },
                {
                    "name": "Consulta de Intervalo de Nº Patrimoniais",
                    "path": "tests/patrimonio/auxiliares/test_consulta_intervalo_n_patrimoniais.py"
                },
                {
                    "name": "Alteração de Intervalo de Nº Patrimoniais",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_intervalo_n_patrimoniais.py"
                },
                {
                    "name": "Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_roteiro_padrao_baixa.py",
                    "versao_maxima": 3
                },
                {
                    "name": "Consulta de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_consulta_roteiro_padrao_baixa.py",
                    "versao_maxima": 3
                },
                {
                    "name": "Alteração de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_roteiro_padrao_baixa.py",
                    "versao_maxima": 3
                },
                {
                    "name": "Exclusão de Roteiro Padrão para Baixa",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_roteiro_padrao_baixa.py",
                    "versao_maxima": 3
                },
                {
                    "name": "Definição de Operações Entrada de Bem Próprio",
                    "path": "tests/patrimonio/auxiliares/test_definicao_operacoes_entrada_bem_proprio.py"
                },
                {
                    "name": "Definição de Operações Entrada de Bem de Terceiros",
                    "path": "tests/patrimonio/auxiliares/test_definicao_operacoes_entrada_bem_terceiros.py"
                },
                {
                    "name": "Definição de Operações Baixa",
                    "path": "tests/patrimonio/auxiliares/test_definicao_operacoes_baixa.py"
                },
                {
                    "name": "Definição de Operações Reavaliação de Bem",
                    "path": "tests/patrimonio/auxiliares/test_definicao_operacoes_reavaliacao_bem.py"
                },
                {
                    "name": "Consulta de Definição de Operações",
                    "path": "tests/patrimonio/auxiliares/test_consulta_definicao_operacoes.py"
                },
                {
                    "name": "Alteração de Definição de Operações",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_definicao_operacoes.py"
                },
                {
                    "name": "Exclusão de Definição de Operações",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_definicao_operacoes.py"
                },
                {
                    "name": "Definição de Documentos",
                    "path": "tests/patrimonio/auxiliares/test_definicao_documentos.py"
                },
                {
                    "name": "Consulta de Definição de Documentos",
                    "path": "tests/patrimonio/auxiliares/test_consulta_definicao_documentos.py"
                },
                {
                    "name": "Alteração de Definição de Documentos",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_definicao_documentos.py"
                },
                {
                    "name": "Exclusão de Definição de Documentos",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_definicao_documento.py"
                },
                {
                    "name": "Definição dos Tipos de Observações",
                    "path": "tests/patrimonio/auxiliares/test_definicao_tipos_observacoes.py"
                },
                {
                    "name": "Consulta da Definição dos Tipos de Observações",
                    "path": "tests/patrimonio/auxiliares/test_consulta_definicao_tipos_observacoes.py"
                },
                {
                    "name": "Alteração da Definição dos Tipos de Observações",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_definicao_tipos_observacao.py"
                },
                {
                    "name": "Exclusão da Definição dos Tipos de Observações",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_definicao_tipos_observacao.py"
                },
                {
                    "name": "Definição dos Motivos de Saída Temporária Interna",
                    "path": "tests/patrimonio/auxiliares/test_definicao_motivos_saida_temporaria.py"
                },
                {
                    "name": "Definição dos Motivos de Saída Temporária Externa",
                    "path": "tests/patrimonio/auxiliares/test_definicao_motivos_saida_temporaria_externa.py"
                },
                {
                    "name": "Consulta de Definição dos Motivos de Saída Temporária",
                    "path": "tests/patrimonio/auxiliares/test_consulta_definicao_motivos_saida_temporaria.py"
                },
                {
                    "name": "Alteração de Definição dos Motivos de Saída Temporária",
                    "path": "tests/patrimonio/auxiliares/test_alteracao_definicao_motivos_saida_temporaria.py"
                },
                {
                    "name": "Exclusão de Definição dos Motivos de Saída Temporária",
                    "path": "tests/patrimonio/auxiliares/test_exclusao_definicao_motivos_saida_temporaria.py"
                },
                {
                    "name": "Consulta de Conta Contábil",
                    "path": "tests/patrimonio/auxiliares/test_consulta_conta_contabil.py"
                },
                {
                    "name": "Contrato de Manutenção - Fora da Garantia",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_fora_garantia.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
                {
                    "name": "Contrato de Manutenção - Na Garantia",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_na_garantia.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
                {
                    "name": "Contrato de Manutenção - Outros ou Diversos",
                    "path": "tests/patrimonio/movimentacao/test_contrato_manutencao_outros.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
                {
                    "name": "Consulta de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_consulta_contrato_manutencao.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
                {
                    "name": "Alteração de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_alteracao_contrato_manutencao.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
                {
                    "name": "Exclusão de Contrato de Manutenção",
                    "path": "tests/patrimonio/movimentacao/test_exclusao_contrato_manutencao.py",
                    # Na v3 o equivalente fica em Patrimônio → Movimentação
                    "versao_minima": 4
                },
            ],

            "Relatórios": [
                {
                    "name": "Gráfico de Distribuição das Aquisições",
                    "path": "tests/patrimonio/relatorios/test_grafico_distribuicao_aquisicoes.py"
                },
                {
                    "name": "Gráfico de Distribuição das Baixas",
                    "path": "tests/patrimonio/relatorios/test_grafico_distribuicao_baixas.py"
                },
                {
                    "name": "Relatório de Inventário Geral",
                    "path": "tests/patrimonio/relatorios/test_relatorio_inventario_geral.py"
                },
                {
                    "name": "Outros Relatórios",
                    "path": "tests/patrimonio/relatorios/test_outros_relatorios.py"
                },
                {
                    "name": "Relatórios Financeiros",
                    "path": "tests/patrimonio/relatorios/test_relatorios_financeiros.py"
                },
                {
                    "name": "Relatório de Entradas",
                    "path": "tests/patrimonio/relatorios/test_relatorio_entradas.py"
                },
                {
                    "name": "Relatório de Baixas",
                    "path": "tests/patrimonio/relatorios/test_relatorio_baixas.py"
                },
                {
                    "name": "Relatório de Movimentações",
                    "path": "tests/patrimonio/relatorios/test_relatorio_movimentacoes.py"
                },
                {
                    "name": "Etiquetas Patrimoniais",
                    "path": "tests/patrimonio/relatorios/test_etiquetas_patrimoniais.py"
                },
                {
                    "name": "Relatório Solicitados Patrimônio",
                    "path": "tests/patrimonio/relatorios/test_relatorio_solicitados_patrimonio.py"
                },
            ],
        },
    }