# ASI Automação 2.0

## Escopo do Projeto de Teste Automatizado

| | |
| --- | --- |
| **Versão** | 2.0 |
| **Data de última atualização do documento** | 17/09/2026 |
| **Responsável** | Equipe de Automação de Testes |
| **Status** | Em andamento |

---

## 1. Visão Geral

Este documento registra o escopo da automação end-to-end do ASI. A solução usa Playwright e Pytest para simular o uso real da interface web e Tkinter para permitir execução por pessoas não técnicas.

Os testes são data-driven: configuração e massa são carregadas dinamicamente por cliente, permitindo reutilizar a mesma suíte em diferentes ambientes sem alterar o código.

---

## 2. Organização e Cobertura

### 2.1 Massa de Dados — Genesis

O Genesis prepara o ambiente antes da suíte, criando e verificando entidades necessárias como almoxarifados, materiais, fornecedores e unidades requisitantes. É idempotente, resiliente a falhas e disponível na GUI pela ação **Preparar Ambiente**.

### 2.2 Testes de Operações Básicas (CRUD)

Os módulos Almoxarifado, Patrimônio e Corporativo foram mapeados e possuem cobertura automatizada. As tabelas consolidam a árvore de testes; os arquivos em `tests/` e o catálogo da GUI são a fonte operacional de cada cenário.

#### 1 Almoxarifado

| Área | Cobertura automatizada | Pendências conhecidas |
| --- | --- | --- |
| Movimentação Interna | Entradas, requisição, atendimento, recebimento, devolução, baixa, estorno e transferência entre contas, incluindo consultas e manutenções aplicáveis. | — |
| Movimentação Externa | Cadastro, atendimento e recebimento de transferências entre almoxarifados, com consulta, alteração e exclusão aplicáveis. | — |
| Gestão de Estoque | Políticas de compras, inventário, classificações e transferência entre endereços. | — |
| Gestão de Compras | Ressuprimento, pedido de compra, autorizações, baixa, eventos, previsões de consumo, nível de estoque e relatórios de empenho. | Autorização e manutenção de previsão de consumo da UR permanecem em evolução. |
| Financeiro | Prévia RMMA, relatórios RMMA/RMAA e fechamento de mês. | — |
| Consulta | Consulta de material. | — |

#### 2 Patrimônio

| Área | Cobertura automatizada | Pendências conhecidas |
| --- | --- | --- |
| Movimentação | Entradas, transferências, recebimentos, devoluções, baixas, estornos, contratos de manutenção, requisições, atendimentos e adição a bem principal. | Alteração de transferência interna; baixa por erro de inclusão. |
| Inventário | Formação de comissão. | Exportação/importação de coletor, manutenção, críticas e inventário parcial. |
| Financeiro | Resumo Mensal de Bens e Ano/Mês de referência da UG. | — |
| Modificação | Responsável do local, detentor, situação física, número patrimonial, conta contábil, alteração individual, valor de mercado, status do bem e modificação de material. | Alteração de responsável, consulta de detentor por recebimento e alteração de conta contábil. |
| Termos de Responsabilidade | Emissão e recebimento, incluindo consultas. | — |
| Auxiliares | Situação física, catálogo de materiais, intervalo patrimonial, roteiros, definições e motivos de saída. | Alteração de conta contábil. |
| Relatórios | Gráficos, inventário geral, relatórios financeiros, entradas, baixas, movimentações, etiquetas e relatórios solicitados. | — |
| Consulta Geral | Consulta e impressão de material. | — |

#### 3 Corporativo

O módulo Corporativo foi mapeado integralmente e está coberto por **104 testes** em `tests/corporativo/`. Para cada entidade abaixo há cobertura de **Cadastro, Consulta, Alteração e Exclusão**.

| Área | Entidades cobertas |
| --- | --- |
| Estrutura Organizacional | Unidade Gestora, Centro de Custos, Unidade Administrativa, Unidade de Localização, Unidade de Requisição e Almoxarifado |
| Localidade | País, Região, Unidade da Federação, Cidade, Instalação e Endereço |
| Entidade Externa | Fornecedor, Órgão Externo e Portador |
| Funcionário | Função e Funcionário |
| Material | Unidade de Medida, Consumo, Permanente, Serviço, Supply e Modelo de Importação |
| Segurança | Perfil e Usuário |
| Característica do Bem | Definição de Característica |

### 2.3 Testes de Fluxo Completo (End-to-End)

Além de operações isoladas, os testes completos encadeiam etapas de negócio e exercitam praticamente todos os botões e ações críticos. O fluxo completo de requisição já possui implementação inicial; a evolução de longo prazo adicionará massa exclusiva e validação de saldo e preço médio após cada movimentação.

| Área crítica | Status | Observação |
| --- | --- | --- |
| Entrada do almoxarifado | Implementado | — |
| Cadastro de requisição | Implementado | — |
| Atendimento de requisição | Implementado | — |
| Recebimento de requisição | Implementado | — |
| Devolução de requisição | Implementado | — |
| Transferência entre almoxarifados | Implementado | — |
| Recebimento de transferência entre almoxarifados | Em desenvolvimento | — |
| Baixa do almoxarifado | Implementado | — |
| Entrada do patrimônio | Implementado | — |
| Transferência interna | Em desenvolvimento | — |
| Recebimento de transferência interna | Em desenvolvimento | — |
| Transferência externa | Em desenvolvimento | — |
| Recebimento de transferência externa | Em desenvolvimento | — |
| Baixa do patrimônio | Em desenvolvimento | — |

### 2.4 Plataforma Web

Hoje a solução é executada localmente pela GUI. A evolução planejada busca permitir disparo remoto autorizado e centralizar logs, evidências e histórico. A nova GUI unificada é a etapa atual; a migração completa para web será decidida separadamente. A GUI Tkinter permanece como fallback até a validação da substituta.

### 2.5 Escopo de Longo Prazo — Próximo Ciclo

| Frente | Status | Resultado esperado |
| --- | --- | --- |
| Finalização da nova GUI | Planejado | Interface modernizada que reúna Testes Gerais, Genesis e Sentinela, com a GUI atual como fallback até a homologação. |
| Confecção dos testes completos | Em desenvolvimento | Jornadas amplas para áreas críticas, exercitando praticamente todos os botões e ações disponíveis em cada fluxo. |
| Validação de dados e regras de negócio | Planejado | Jornadas E2E longas, autocontidas e rerunnáveis, com massa exclusiva e validação pela UI dos códigos, saldos e preços médios esperados. |
| Cobertura de novos módulos | Planejado | Priorização por criticidade e presença nos clientes; histórias por regra, testes no padrão flows + testes e registro na GUI/Sentinela. |
| Pesquisa de testes HTTP, concorrência e estresse | Pesquisa | Prova de conceito limitada, com critérios de segurança, isolamento e sustentabilidade antes de compromisso de produto. |

#### Critérios de conclusão

- **Nova GUI:** sprints concluídas, execução de Testes Gerais, Genesis e Sentinela validada e fallback documentado.
- **Testes completos:** botões e ações críticos mapeados, resultado validado e execução rerunnável em estado conhecido.
- **Regras de negócio:** valores esperados preservados durante a execução e consultados pela UI após cada movimentação.
- **Novos módulos:** revisão técnica, validação em clientes representativos, dados provisionados e registro no catálogo/ordem do Sentinela.
- **HTTP, concorrência e estresse:** decisão “seguir” ou “não seguir” baseada em POC com autenticação, isolamento, observabilidade, limites de carga e compatibilidade com o ASI.

---

## 3. Arquitetura Técnica

| Camada | Responsabilidade |
| --- | --- |
| **Testes** (`tests/`) | Orquestram os casos de teste; cada arquivo encadeia os flows necessários. |
| **Flows** (`flows/`) | Ações reutilizáveis de automação, com um propósito por arquivo. |
| **Utilitários** (`utils/`) | Esperas, evidências, logging e apoio a validações. |
| **Domínio** (`domain/`) | Contexto tipado do cliente e acesso a dados de configuração. |
| **GUI** (`gui/`) | Seleção de cliente/ambiente, execução e logs em tempo real. |
| **Genesis** (`genesis/`) | Provisão idempotente e resiliente da massa de dados. |
| **Sentinela** (`sentinela/`) | Execução ordenada de jornadas e auditoria de regressão. |

## 4. Stack Tecnológica

| Tecnologia | Finalidade |
| --- | --- |
| **Python 3.14** | Linguagem principal |
| **Playwright (sync)** | Automação de browser |
| **Pytest** | Execução e fixtures |
| **pytest-repeat** | Detecção de falhas intermitentes |
| **Loguru** | Logging estruturado |
| **Tkinter** | GUI local |
| **PyYAML** | Configuração e massa de testes |
| **pdfplumber** | Extração e validação de PDFs |

## 5. Legenda de Status

| Status | Significado |
| --- | --- |
| **Implementado** | Teste implementado e validado |
| **Em desenvolvimento** | Teste em construção |
| **Planejado** | Previsto no escopo, ainda não iniciado |
| **Pesquisa** | Investigação sem compromisso inicial de produto |
