# Guia de migração do Genesis

Este arquivo é o roteiro de trabalho para os membros do projeto de automação que darão
continuidade à migração do Genesis legado para `tests/genesis/` e para a árvore principal
de `flows/`.

## Estado da preparação

A base inicial está pronta:

- o módulo Genesis é opt-in na Sentinela e aparece por último no catálogo;
- o catálogo separa `Rotina do usuário Link` e `Rotina do usuário Teste`;
- Cidade, Função e Unidade de Medida foram transpostas e certificadas em duas rodadas de
  PCDF e CJF;
- as 25 etapas do Genesis foram inventariadas na ordem real;
- Perfis foi transposto (referência avançada da revisão 65994); Usuários também
  foi transposto, com certificação em QAS ainda pendente. Ver `README.md`.

A partir daqui, a equipe deve transpor **uma entidade por vez**, seguindo a fila deste
documento. O Genesis legado deve permanecer operacional e inalterado durante a migração.

## Modelos obrigatórios

Antes de começar qualquer entidade, leia integralmente estes três testes e os flows que
eles importam:

1. `tests/genesis/test_garantir_cidade.py` — modelo de **pré-condição**: consulta e
   verifica, mas nunca cria.
2. `tests/genesis/test_garantir_funcao.py` — modelo de **garantia com usuário Link**:
   consulta, retorna se existir, cria se faltar e consulta novamente.
3. `tests/genesis/test_garantir_unidade_medida.py` — mesmo modelo de garantia usando o
   **usuário Teste**.

Esses testes definem a estrutura esperada. Uma nova transposição deve manter o mesmo
formato sempre que o comportamento legado permitir:

1. obter dados pelo `ContextoCliente`;
2. obter o usuário com `dados_usuario("link")` ou `dados_usuario("teste")`;
3. fazer login;
4. acessar a página pelo flow canônico;
5. consultar;
6. usar a mesma regra de existência do service legado;
7. retornar sem alterar o registro quando ele já existir;
8. preencher e confirmar somente quando estiver ausente;
9. acessar e consultar novamente para comprovar a criação;
10. fazer logout;
11. nunca excluir a massa criada.

Não copie seletores ou detalhes específicos dos pilotos para outra entidade. Copie a
**arquitetura e a sequência comportamental**.

## Contrato que deve ser preservado

O objetivo é transpor, não modernizar. Para cada entidade, preserve exatamente:

- chave e dados do blueprint;
- papel de usuário;
- posição na rotina;
- regra usada para decidir se o registro existe;
- campos, ordem e decisões da criação;
- confirmação de sucesso;
- consulta pós-criação;
- comportamento quando dados, menus ou resultados estiverem ausentes.

Não introduza validações adicionais, auto-reparo, limpeza de massa, regras novas,
tratamentos de erro novos ou refatorações oportunistas. Não altere arquivos em `genesis/`.

## Fontes de verdade

Leia nesta ordem antes de editar uma entidade:

1. `AGENTS.md`;
2. `.agents/skills/padroes-testes/SKILL.md`;
3. este guia;
4. a rotina em `genesis/routines/link_user.py` ou `genesis/routines/teste_user.py`;
5. `genesis/flows/garantir_<entidade>_flow.py`;
6. o service e a navegação legados usados pelo flow;
7. os flows canônicos correspondentes em `flows/`;
8. o getter do `ContextoCliente` e os dados do blueprint.

O Genesis legado define **o comportamento**. Os três pilotos e as convenções atuais
definem **a estrutura do código novo**.

## Seleção exata compartilhada

Existe um único helper Genesis para grids cuja identidade é a igualdade exata de uma
célula:

`flows/genesis/shared/selecionar_registro_exato_flow.py`

Reutilize `selecionar_registro_exato()` em toda entidade compatível. Não crie uma cópia
ou um helper de seleção exata por teste.

Cidade é uma exceção já implementada no mesmo módulo: ela apenas verifica a pré-condição,
aceita `BRASÍLIA`/`BRASILIA`, remove o código visual e nunca anexa uma linha. Identidades
compostas, colunas específicas ou grids diferentes devem preservar a regra do service
legado. Se for necessário estender o helper, a extensão deve ser mínima e reutilizável.

## Como tratar flows complexos e listas

Um `for` não é, por si só, um problema. URs, Funcionários, Perfis, Usuários, Materiais e
outras entidades representam listas reais do blueprint ou da interface. Esses loops fazem
parte do comportamento que deve ser preservado.

Ao migrar uma entidade com vários registros:

- o teste pode iterar os dados e orquestrar `consultar → selecionar → criar → consultar`;
- cada flow continua responsável por uma operação de UI;
- algoritmos internos refinados de uma tela podem permanecer juntos quando dependem do
  mesmo estado, índice, linha dinâmica ou diálogo;
- extraia um auxiliar somente quando houver uma fronteira estável e já comprovada;
- não reescreva retries, waits, condições ou ordem de cliques apenas para reduzir linhas;
- compare o resultado novo com o legado registro por registro.

Flows complexos não devem ser copiados cegamente para um único flow monolítico, mas também
não devem ser fragmentados artificialmente. A prioridade é preservar o comportamento
refinado; a divisão segue operações reais da interface.

### Exceção controlada: loops de varredura dinâmica no teste

Embora os testes comuns não devam conter lógica, testes de varredura dinâmica podem manter
`for` no próprio teste quando a quantidade de registros só é conhecida em execução e cada
iteração orquestra uma sequência completa de flows. Essa exceção mantém o algoritmo visível
nos fluxogramas gerados a partir da AST do teste; mover toda a varredura para um flow único
reduziria a documentação a uma caixa opaca.

A exceção autoriza somente a iteração e as decisões de orquestração. Seletores, interações de
UI, waits e algoritmos internos da tela permanecem nos flows. `garantir_perfis` é o modelo
Genesis dessa situação, assim como os testes especiais que percorrem todos os tipos e
finalidades de Entrada e Baixa.

## Papéis e ordem de execução

O `ProvisionEngine` executa primeiro a rotina Link, redefine a sessão e depois executa a
rotina Teste. Preserve essa fronteira:

- testes da ordem 1–12 usam `contexto_cliente.dados_usuario("link")` e ficam na seção
  `Rotina do usuário Link` do catálogo;
- testes da ordem 13–25 usam `contexto_cliente.dados_usuario("teste")` e ficam na seção
  `Rotina do usuário Teste`;
- registre cada teste também em `sentinela/ordem.yaml`, na posição correspondente;
- não misture entidades dos dois papéis numa mesma sessão.

## Procedimento por entidade

1. Escolha a primeira entidade pendente da fila.
2. Leia todas as fontes de verdade.
3. Registre antes de codar uma comparação curta:

| Etapa | Genesis legado | Destino novo | Diferença autorizada |
|---|---|---|---|
| Dados | chave/getter | `ContextoCliente` | nenhuma |
| Papel | `link` ou `teste` | mesmo papel | nenhuma |
| Navegação | navegação legada | flow canônico | somente infraestrutura |
| Existência | regra do service | consulta + seleção | nenhuma |
| Criação | campos e sequência | flows de preenchimento | nenhuma |
| Pós-criação | nova consulta | nova consulta | nenhuma |

4. Reutilize flows canônicos somente quando forem equivalentes.
5. Crie apenas flows que correspondam diretamente a ações do legado.
6. Crie `tests/genesis/test_garantir_<entidade>.py` conforme os três modelos.
7. Registre o teste na seção correta do catálogo e na ordem correta da Sentinela.
8. Faça validações estáticas e dry-run. QAS exige autorização expressa.
9. Compare dados, papel, existência, criação e pós-criação com o legado.
10. Marque a entidade como transposta; certifique-a separadamente nos clientes definidos.

## Quando parar e pedir decisão

Pare antes de editar se:

- o legado estiver errado, incompleto ou contraditório;
- o comportamento não puder ser reproduzido com os flows existentes;
- for necessário alterar `flows/shared/`;
- faltarem dados no blueprint ou getter no `ContextoCliente`;
- houver dúvida sobre o papel de usuário;
- v3 e v4 exigirem mudança de comportamento, não apenas de infraestrutura;
- a validação exigir criar, alterar ou excluir dados não autorizados;
- a solução pretendida introduzir comportamento que o legado não possui.

## Decisões já aprovadas

- Cidade é somente pré-condição; verificar `BRASÍLIA`/`BRASILIA` e nunca criá-la.
- `B01 BRASÍLIA` não é dado de massa; o código visual não integra o nome da Cidade.
- Genesis permanece opt-in e por último no catálogo durante a migração.
- O catálogo piloto permanece limitado a `pcdf` e `cjf` até nova decisão.
- Não criar suíte unitária auxiliar para esta transposição.
- Não adicionar `obrigatoria` aos flows de navegação.
- Reutilizar o helper de seleção exata em todas as transposições compatíveis.

## Fila de migração

**FAVOR IGNORAR ESTA PARTE**

| Ordem | Entidade | Blueprint | Papel | Depende de | Flow legado | Service legado | Flows principais | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | Cidade | `cidade` | `link` | — | `genesis/flows/garantir_cidade_flow.py` | `genesis/services/cidade_service.py` | `flows/corporativo/localidade/cadastro_cidade/` | certificado |
| 2 | Funcionários | `funcionarios` | `link` | — | `genesis/flows/garantir_funcionarios_flow.py` | `genesis/services/funcionario_service.py` | `flows/corporativo/funcionario/cadastro_funcionario/` | pendente |
| 3 | Função | `funcao` | `link` | — | `genesis/flows/garantir_funcao_flow.py` | `genesis/services/funcao_service.py` | `flows/corporativo/funcionario/cadastro_funcao/` | certificado |
| 4 | Centro de Custo | `centro_custo` | `link` | — | `genesis/flows/garantir_centro_custo_flow.py` | `genesis/services/centro_custo_service.py` | `flows/corporativo/estrutura_organizacional/cadastro_cc/` | pendente |
| 5 | Unidade Administrativa | `unidade_administrativa` + UG da configuração | `link` | Funcionários; Função | `genesis/flows/garantir_ua_flow.py` | `genesis/services/ua_service.py` | `flows/corporativo/estrutura_organizacional/cadastro_ua/` | pendente |
| 6 | Associação Funcionário/UA | `funcionarios` + `unidade_administrativa` | `link` | Funcionários; UA | `genesis/flows/garantir_associacao_funcionarios_ua_flow.py` | `genesis/services/associacao_funcionario_ua_service.py` | `flows/corporativo/funcionario/cadastro_funcionario/` (parcial) | pendente |
| 7 | Instalação | `instalacao` | `link` | Cidade | `genesis/flows/garantir_instalacao_flow.py` | `genesis/services/instalacao_service.py` | `flows/corporativo/localidade/cadastro_instalacao/` | pendente |
| 8 | Endereços | `enderecos` | `link` | Instalação | `genesis/flows/garantir_enderecos_flow.py` | `genesis/services/endereco_service.py` | `flows/corporativo/localidade/cadastro_endereco/` | pendente |
| 9 | Unidades de Requisição | `unidades_requisicao` | `link` | UA; Endereços; Centro de Custo | `genesis/flows/garantir_urs_flow.py` | `genesis/services/ur_service.py` | `flows/corporativo/estrutura_organizacional/cadastro_ur/` | pendente |
| 10 | Perfis | `prefixo_perfil` | `link` | Perfis do usuário Link | `genesis/flows/garantir_perfis_flow.py` | `genesis/services/perfil_service.py` | `flows/corporativo/seguranca/cadastro_perfil/` | transposto; validado TRE-PE v3 e CJF v4 |
| 11 | Usuários | `usuarios` + `prefixo_perfil` | `link` | Funcionários; Perfis | `genesis/flows/garantir_usuarios_flow.py` | `genesis/services/usuario_service.py` | `flows/corporativo/seguranca/cadastro_usuario/` + `flows/genesis/usuario/` | transposto; existência validada TRE-PE v3/CJF v4; criação pendente |
| 12 | Remoção de restrições dos perfis | `usuarios` | `link` | Usuários; Perfis | `genesis/flows/remover_restricoes_perfis_flow.py` | — | sem equivalente direto | pendente |
| 13 | Almoxarifados | `almoxarifados` + UG da configuração | `teste` | — | `genesis/flows/garantir_almoxarifados_flow.py` | `genesis/services/almoxarifado_service.py` | `flows/corporativo/estrutura_organizacional/cadastro_almoxarifado/` | pendente |
| 14 | Fornecedores | `fornecedores` | `teste` | Cidade | `genesis/flows/garantir_fornecedores_flow.py` | `genesis/services/fornecedor_service.py` | `flows/corporativo/entidade_externa/cadastro_fornecedor/` | pendente |
| 15 | Órgão Externo | `orgao_externo` | `teste` | Cidade | `genesis/flows/garantir_orgao_externo_flow.py` | `genesis/services/orgao_externo_service.py` | `flows/corporativo/entidade_externa/cadastro_orgao_externo/` | pendente |
| 16 | Unidade de Medida | `unidade_medida` | `teste` | — | `genesis/flows/garantir_um_flow.py` | `genesis/services/um_service.py` | `flows/corporativo/material/cadastro_unidade_medida/` | certificado |
| 17 | Subgrupos (Supply) | `grupos` | `teste` | Grupos Supply existentes | `genesis/flows/garantir_grupos_subgrupos_flow.py` | `genesis/services/subgrupo_service.py` | `flows/corporativo/material/cadastro_supply/` | pendente |
| 18 | Materiais de Consumo | `materiais` | `teste` | Subgrupos; U.M.; permissões | `genesis/flows/garantir_materiais_flow.py` | `genesis/services/material_service.py` | `flows/corporativo/material/` + `cadastro_material_consumo/` | pendente |
| 19 | Endereços de Estoque | `almoxarifados` + `enderecos_material` | `teste` | Almoxarifados | `genesis/flows/garantir_endereco_material_flow.py` | `genesis/services/endereco_material_service.py` | `flows/almoxarifado/auxiliares/endereco_estoque/` | pendente |
| 20 | Endereçamentos de Material | `almoxarifados` + `materiais` + `enderecos_material` + `unidade_medida` | `teste` | Almoxarifados; Materiais; Endereços; U.M. | `genesis/flows/garantir_enderecamentos_flow.py` | `genesis/services/enderecamento_material_service.py` | `flows/almoxarifado/auxiliares/enderecamento_de_material/` | pendente |
| 21 | Unidades de Localização | `unidades_localizacao` | `teste` | UA; Endereços; Centro de Custo; Funcionários; Função | `genesis/flows/garantir_uls_flow.py` | `genesis/services/ul_service.py` | `flows/corporativo/estrutura_organizacional/cadastro_ul/` | pendente |
| 22 | Catálogos | `catalogo` + `almoxarifados` + `unidades_requisicao` | `teste` | Almoxarifados; URs; Materiais | `genesis/flows/garantir_catalogos_flow.py` | `genesis/services/catalogo_service.py` | `flows/patrimonio/auxiliares/catalogo_materiais/` | pendente |
| 23 | Bens Permanentes | `bens` | `teste` | Subgrupos; permissões | `genesis/flows/garantir_bens_flow.py` | `genesis/services/bem_service.py` | `flows/corporativo/material/` + `cadastro_material_permanente/` | pendente |
| 24 | Associação de Característica ao Bem | — (usa o Bem aberto) | `teste` | Bens; característica disponível | `genesis/flows/garantir_caracteristica_flow.py` | `genesis/services/caracteristica_service.py` | sem equivalente direto | pendente |
| 25 | Evento | `evento` | `teste` | Competência do Almoxarifado | `genesis/flows/garantir_evento_flow.py` | `genesis/services/evento_service.py` | `flows/almoxarifado/gestao_de_compras/evento/` | pendente |

Observações do inventário:

- a ordem 1–12 vem de `link_user.py`; a ordem 13–25 vem de `teste_user.py`;
- o reset de sessão entre as duas rotinas é obrigatório;
- a chave `perfis` do blueprint não é consumida pelo flow atual de Perfis. Os Perfis de
  origem são descobertos a partir do usuário Link autenticado, e os novos nomes são
  derivados de `prefixo_perfil`. Preserve esse comportamento até decisão explícita.

**FAVOR IGNORAR ESTA PARTE**

## Critério de conclusão por entidade

Uma entidade só está transposta quando:

- usa a mesma chave, o mesmo papel e a mesma regra de existência do legado;
- cria os mesmos campos na mesma sequência;
- observa o alerta real de sucesso quando houver criação;
- consulta novamente e encontra o registro;
- não exclui nem corrige registros existentes;
- não importa código da árvore `genesis/`;
- está no catálogo e na Sentinela, na seção e ordem corretas;
- passa no dry-run e nas execuções autorizadas dos clientes definidos.

## Encerramento futuro

Somente depois das 25 entidades estarem certificadas será possível avaliar a retirada do
Genesis legado. Essa retirada é uma tarefa separada e exige autorização explícita.
