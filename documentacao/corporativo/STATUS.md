# Status — Testes do Módulo Corporativo

> Destino: `documentacao/corporativo/STATUS.md`
> Atualizar a cada card fechado: marcar ✅ na operação concluída e preencher
> o campo `Arquivo` com o caminho do teste.
>
> Legenda: ✅ aprovado · 🔄 em progresso · ⏳ pendente · ⚠️ bloqueado · — não aplicável

---

## Princípio de isolamento dos dados `_cr`

Cada entidade `_cr` do blueprint foi projetada para **não depender de nenhuma
outra entidade `_cr`**. Quando um campo de lookup é obrigatório, ele referencia
sempre um dado **padrão** já provisionado pelo Genesis (ex.: `unidade_gestora`
CGTAD, `unidade_administrativa` SGRTA, `funcionarios[0]`, `enderecos[0]`).

Consequência direta: **a ordem dos cards no Trello não importa para corretude**
— qualquer teste de Cadastro `_cr` pode ser executado independentemente, sem
que outro `_cr` precise existir primeiro. A exclusão também não tem impedimento
de vínculo entre `_cr`s, pois nenhum outro `_cr` referencia o que foi criado.

O único cuidado de sequência é dentro do **próprio CRUD de uma sub-página**:
Cadastro → Consulta → Alteração → Exclusão, nessa ordem, porque Consulta,
Alteração e Exclusão pressupõem que o registro já existe.

---

## Padrão dos testes Consulta / Alteração / Exclusão (Wave 1 concluída)

Para as páginas de **formulário genérico** (Consulta → Anexar → editar/Excluir), os
três testes reaproveitam a navegação do Cadastro e adicionam apenas dois flows novos,
uniformes e provados (referência: `test_*_cc.py`, `test_*_pais.py`):

- **`consultar_{slug}`**: `submitSearch` (abre a consulta) → `input[name='model-N'].fill(chave)` → `submitSearch`.
  O `model-N` de cada página está no `MAPA_E_LOCALIZADORES.md`.
- **`selecionar_{slug}` → bool**: delega ao auxiliar compartilhado `selecionar_movimentacao(ctx, <nome>)`,
  que aguarda o total vindo do banco (`span[name='searchResultSize']`) — robusto contra o falso-negativo
  de contar linhas antes de a busca retornar. ⚠️ **Casar pelo Nome** (coluna sempre exibida no grid), não
  pela Sigla: alguns grids não têm coluna Sigla (ex.: UA mostra Órgão/UG/Código/Nome/Responsável). Se
  `False`, `submitCancel` para limpar a tela.
- **`alterar_{slug}`**: altera um campo editável e **restaura** o valor original (2 confirmações),
  mantendo o registro localizável e o teste re-executável. ⚠️ Se o form tem **lookup obrigatório
  que não repopula** ao Anexar (ex.: Almoxarifado → U.G. `cdUg`), re-selecionar o lookup com
  `preencher_campo` (ou `preencher_autocomplete` se o botão do lookup for interceptado) antes de
  cada `submitFinish`.
- **Testes**: Consulta acrescenta `page.wait_for_timeout(5_000)`; Alteração chama `alterar_{slug}`;
  Exclusão chama `excluir_movimento(page, esperar_sucesso=True)`.

**Wave 1 validada em pcdf (v3) + pcdfv4 (v4), ciclo completo:** CC, UA, UR, Almoxarifado,
País, Região, UF, Cidade, Endereço, Função, Órgão Externo.
(Alteração de Almoxarifado ficou pendente na Wave 1 e foi corrigida manualmente pelo Roniel.)

### Wave 2 (validada em pcdfv4; padrões idênticos aos da Wave 1)

**C/A/E completos:** Instalação (CEP desbloqueado, máscara `XX.XXX-XXX`), Unidade de Medida
(consulta/casa pela **Sigla** — a Descrição `dsUm` é truncada por maxlength no banco),
Fornecedor, Funcionário.
**Consulta + Alteração** (Exclusão já existia): Material de Consumo, Permanente, Serviço
(altera o `cdMatAntigo`, campo livre; o form `bemser` repopula os obrigatórios ao Anexar).
**Só Consulta** (reuso puro): Modelo de Importação (v4).
**Consulta + Exclusão OK, Alteração PENDENTE (ajuste manual):** UG, Portador (lookups
obrigatórios não repopulam ao Anexar) e Modelo (validação do grid de característica:
"A ordem não pode ser 1"). Flows marcados com `# NOTA`.

**Chave formatada nas consultas:** Fornecedor CNPJ=`model-2` (`XX.XXX.XXX/XXXX-XX`),
Portador CPF=`model-2`, Funcionário CPF=`model-4` (derivado da matrícula); casam pelo Nome.
`model-N` do Nome: UG=2, Instalação=2, Unidade de Medida (Sigla)=2, Definição=1.

**Wave 2 NÃO feita (pendências para retomar):** UL (Sigla=model-8; exclusão exige remover
responsável antes), Supply (CRUD de árvore — atípico), Definição de Característica (o cadastro
atual hardcoda "MARCA AUTOMATIZADA" e não usa `caracteristica_bem_cr` — refatorar o cadastro
para o `_cr` antes de fazer C/A/E, senão a exclusão apagaria dado compartilhado).

---

## 1. Estrutura Organizacional

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| UG - Unidade Gestora | `unidade_gestora_cr` | ✅ | ⏳ | ⏳ | ⏳ | `tests/corporativo/estrutura_organizacional/test_cadastro_ug.py` |
| CC - Centro de Custos | `centro_custo_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/estrutura_organizacional/test_cadastro_cc.py` |
| UA - Unidade Administrativa | `unidade_administrativa_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/estrutura_organizacional/test_cadastro_ua.py` |
| UL - Unidade de Localização | `unidade_localizacao_cr` | ✅ | ✅ | ✅ | 🔄 | `tests/corporativo/estrutura_organizacional/test_cadastro_ul.py` |
| UR - Unidade de Requisição | `unidade_requisicao_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/estrutura_organizacional/test_cadastro_ur.py` |
| Almoxarifado | `almoxarifado_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/estrutura_organizacional/test_cadastro_almoxarifado.py` |

> **UG_cr**: código gerado em runtime (campo `codigo: ""`). Lookups referenciam
> cidade padrão (B01 BRASÍLIA). Não há outros `_cr` dependendo dela.
>
> **UA_cr**: lookup `ug` → CGTAD (padrão); responsável → `funcionarios[0]` (padrão).
>
> **UL_cr**: lookup `unidade_administrativa` → SGRTA (padrão); `centro_custo` →
> `centro_custo` padrão; `responsavel` → funcionário/função padrão. A chave única
> da UL é **(UA, Endereço)** e os 5 endereços padrão já têm UL com a UA SGRTA
> (4 ULs + a UL de estoque), então o `endereco` do `_cr` usa um **endereço
> dedicado** ("REGIÃO CORPORATIVA DE MÓDULOS S9", 6º de `enderecos`, provisionado
> em pcdf e pcdfv4). **A exclusão da UL NÃO exige remover o responsável antes** —
> é só clicar em Excluir (confirmado na GUI pelo Roniel; a nota anterior era falsa).
> ⚠️ **O grid de resultado da UL não tem coluna Sigla nem Nome** (Órgão / Responsável /
> Corresponsável / U.G. / U.A. / Código / Endereço) — a seleção casa pelo **Endereço**
> (dedicado, exclusivo da `_cr`). Consulta filtra pela **Sigla = `model-8`**; a Alteração
> mexe na Sigla (`sgUl`), único campo tipo-nome (a chave única é U.A.+Endereço).
>
> **UR_cr**: lookup `sigla_ua` → SGRTA (padrão); `endereco` → `enderecos[4]`
> ("LOCALIDADE PATRIMONIAL DE ESTOQUE G3", 5º/último, padrão). A chave única da
> UR é **(UA, Endereço)**; os endereços 1..4 já são usados pelas URs padrão com a
> mesma UA SGRTA, então o `_cr` usa o 5º endereço (livre) para não colidir.
> Autorizador não é obrigatório.
>
> **CC_cr**: único campo editável é o Nome (`nmCentroCusto`); Órgão pré-preenchido
> e Código gerado. Exclusão pela UI confirmada (Consulta Nome=`model-2` →
> Anexar → Excluir). Nome distinto do padrão ("C02 …" vs "C01 …"), sem colisão.
>
> **Almoxarifado_cr**: chave única = Sigla (`sgAlmoxarifado`). Campos preenchidos:
> Nome (`dsAlmoxarifado`), Sigla, Controle financeiro (`inControleFin=S`, já default)
> e U.G. (`cdUg`, lookup → CGTAD padrão). Órgão pré-preenchido (varia por cliente) e
> Código gerado. Nome/sigla distintos dos almoxarifados padrão (AIAOT/ASAST). Exclusão
> pela UI confirmada nos dois clientes (Consulta Sigla=`model-4` → Anexar → Excluir).
> Só depende da UG padrão; nenhum outro `_cr` o referencia.

---

## 2. Localidade

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| País | `pais_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/localidade/test_cadastro_pais.py` |
| Região | `regiao_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/localidade/test_cadastro_regiao.py` |
| UF - Unidade da Federação | `uf_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/localidade/test_cadastro_uf.py` |
| Cidade | `cidade_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/localidade/test_cadastro_cidade.py` |
| Instalação | `instalacao_cr` | ⚠️ | ⏳ | ⏳ | ⏳ | `tests/corporativo/localidade/test_cadastro_instalacao.py` (skip) |
| Endereço | `endereco_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/localidade/test_cadastro_endereco.py` |

> **Filtro Nome na consulta (cleanup):** model-1 para País/Região/UF/Cidade; **model-3**
> para Endereço (a consulta de Endereço tem Órgão e Instalação como lookups antes do Nome).
> Todas com Código gerado (exceto Região, cujo `cdRegiao` é editável = chave). Lookups:
> UF→país, Cidade→uf+regiao, Endereço→instalacao. Nav v3 = `.menu-link a[title='<nome>']`.
>
> **⚠️ Instalação BLOQUEADA por bug de aplicação:** o campo CEP (`nrCep`) rejeita
> qualquer valor bem-formado ("CEP inválido! Ex: 12345-678") — testado ao vivo com
> CEP formatado (`70000-000`), CEP real (`70040-010`) e cru (`70000000`). Cidade
> resolve normal; só o CEP falha. Flow e navegação prontos; teste com `pytest.skip`.
> Chamado a ser aberto pelo Roniel. Remover o skip quando corrigido.

> **Sem dependência entre `_cr`s**: `uf_cr` usa país padrão (BRASIL);
> `cidade_cr` usa UF padrão (D01 DISTRITO FEDERAL) e região padrão (CENTRO);
> `endereco_cr` usa instalação padrão (ÁREA AUTOMATIZADA); `instalacao_cr`
> usa cidade padrão (B01 BRASÍLIA). Nenhum `_cr` depende de outro `_cr`.
>
> País, Região, Instalação e Endereço já foram inspecionados ao vivo
> (marcados com ✅ no `MAPA_E_LOCALIZADORES.md`).

---

## 3. Entidade Externa

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Fornecedor | `fornecedor_cr` | ✅ | ⏳ | ⏳ | ⏳ | `tests/corporativo/entidade_externa/test_cadastro_fornecedor.py` |
| Órgão Externo | `orgao_externo_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/entidade_externa/test_cadastro_orgao_externo.py` |
| Portador | `portador_cr` | ✅ | ⏳ | ⏳ | ⏳ | `tests/corporativo/entidade_externa/test_cadastro_portador.py` |

> **Fornecedor_cr**: chave única = CNPJ (`nrIdentAgente`, formatado). Selects
> `situacaoJuridica` (tipo) e `cdTpForPorte` (porte) via `select_tipo`; radio
> `inCartorio=N`; cidade lookup. DDD "61". Consulta CNPJ=`model-2`.
>
> **Órgão Externo_cr**: chave única = CNPJ/Identificação (`nrIdentAgente`,
> formatado). Campos: `nmAgente`(Nome), `sgOrgaoExterno`(Sigla), `cdUasg`,
> endereço/bairro/cidade(lookup)/CEP/telefone/email. Consulta CNPJ=`model-2`,
> Sigla=`model-12`.
>
> **Portador_cr**: chave única = CPF (`nrIdentAgente`, formatado). lookup
> `agenteFornecedorOrgaoExterno` → `fornecedores[0]` padrão (AUTOMATIZADO SOLUÇÕES
> COMERCIAIS LTDA); **não** depende de `fornecedor_cr`. ⚠️ Esse lookup é um caso
> especial: usa `preencher_autocomplete` (teclado) porque o `preencher_campo`
> (botão lookup) é interceptado pelo dropdown só nesta página. Consulta CPF=`model-2`.
>
> Os três: form abre direto; exclusão direta pela UI (Consulta → Anexar → Excluir),
> confirmada nos dois clientes. Órgão vem pré-preenchido (varia por cliente).

---

## 4. Funcionário

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Funções | `funcao_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/funcionario/test_cadastro_funcao.py` |
| Cadastro | `funcionario_cr` | ✅ | ⏳ | ⏳ | ⏳ | `tests/corporativo/funcionario/test_cadastro_funcionario.py` |

> **Funções antes de Cadastro** apenas por conveniência: `funcionario_cr` usa
> UA padrão (SGRTA), não `funcao_cr`. São independentes entre si.
>
> **Funções_cr**: campo único Nome (`nmTpFuncaoHier`); Código gerado. Heading v4
> (breadcrumb) `Funcionário - Funções`, h1 do form `Função`. Consulta Nome=`model-1`.
>
> **Funcionário_cr**: obrigatórios Matrícula (`cdFuncionario`, **maxlength 8** — a
> matrícula de 11 díg. do blueprint é truncada, inofensivo) e Nome (`nmRegistroCivil`).
> O identificador real é o **CPF** (`nrCpf`, derivado da matrícula formatada) — a
> consulta é por CPF=`model-4`. U.A. (`cdUa`) é **opcional**, preenchida via lookup
> `lookup-ccdUa` → SGRTA (padrão). Heading v4 (breadcrumb) `Funcionário - Cadastro`,
> h1 do form `Funcionário`.
>
> **Validação:** v4 (pcdfv4) ✅ ambos com `.alert-success`. v3: Função ✅ (tse);
> Cadastro de Funcionário — nav v3 + form + submit confirmados (exclusão pela UI
> achou/removeu o registro criado), **mas** o lookup da U.A. (SGRTA) exige o dado
> padrão provisionado — pendente rodar num cliente v3 logável e com Genesis
> provisionado (pcdf estava fora; tse/seadpb sem dados/login na ocasião). Registros
> de teste excluídos em pcdfv4 e tse.

---

## 5. Material

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Unidade de Medida | `unidade_medida_cr` | ✅ | ⏳ | ⏳ | ⏳ | `tests/corporativo/material/test_cadastro_unidade_medida.py` |
| Consumo | `material_consumo_cr` | ✅ | ⏳ | ⏳ | ✅ | `tests/corporativo/material/test_cadastro_material_consumo.py` · `test_exclusao_material_consumo.py` |
| Permanente | `material_permanente_cr` | ✅ | ⏳ | ⏳ | ✅ | `tests/corporativo/material/test_cadastro_material_permanente.py` · `test_exclusao_material_permanente.py` |
| Serviço | `material_servico_cr` | ✅ | ⏳ | ⏳ | ✅ | `tests/corporativo/material/test_cadastro_material_servico.py` · `test_exclusao_material_servico.py` |
| Supply | `supply_cr` | ✅ | ✅ | ✅ | ✅ | `test_cadastro_supply.py` · `test_consulta_supply.py` · `test_alteracao_supply.py` · `test_exclusao_supply.py` (ciclo rerunnável; exclusão em 2 passos: subgrupo depois grupo) |
| Modelo de Importação | `modelo_importacao_cr` | ✅ | ⏳ | ⏳ | ✅ | `test_cadastro_modelo_importacao.py` · `test_exclusao_modelo_importacao.py` (validado pcdfv4; v3 pendente) |

> Os três materiais `_cr` usam `unidade_medida` padrão (UMT) e `subgrupo`
> padrão — não dependem de `unidade_medida_cr`.
>
> **Supply — C/A/E concluído** (validado em MPF v4, ciclo completo). A **Consulta** é reuso puro
> (`consultar_subgrupo_supply` + `selecionar_subgrupo_supply`); não há consulta padrão — o
> `submitSearch` do form fica desabilitado e a busca é só pela árvore do lookup.
> ⚠️ **Alteração — o campo é o `grupoDsExemplo`, não o `subgrupoDsExemplo`**: os campos `grupo*`
> são genéricos e recebem **o nó carregado da árvore**. Ao carregar o subgrupo 10099,
> `grupoCdExemplo`='10099' e `grupoDsExemplo`='SUBGRUPO CR' (único habilitado, sem maxlength),
> enquanto `subgrupo*`/`material*` ficam vazios e desabilitados. Renomear é seguro: a Consulta
> filtra pelo **código** e a Exclusão acha o grupo pelo texto "100 - GRUPO CR" (não tocado).
>
> **Supply** ✅ concluído (ciclo rerunnável). Cadastra Grupo→Subgrupo→Material
> **novos e inventados** por **texto livre** (grupo 100, alto/livre) via +Subgrupos/+Materiais.
> **Exclusão em 2 passos** (subgrupo, depois grupo — o grupo só some vazio). 🐞 Card de BUG
> aberto: cadastrar um grupo que já existe dá "ERRO JAVA" (por isso a exclusão remove o grupo).
> **Modelo de Importação** ✅ (só v4): Descrição (chave) + Material (lookup, só bem PERMANENTE)
> + 1 Característica obrigatória. (A nota antiga de que Modelo "podia ser ignorado" estava
> errada — é cadastro real.)
>
> ✅ **Modelo de Importação — validado em pcdfv4** (v3 pendente). Duas descobertas ao vivo
> (v4) que corrigem o card: (1) o lookup de Material só aceita **bem PERMANENTE** — consumo
> não aparece; usa-se "M01 MESA DE ESCRITÓRIO EM MDF AUTOMATIZADO" (garantir_bens). (2) O
> grid de Características é **OBRIGATÓRIO ≥1** (sem asterisco, mas o app exige) — o flow anexa
> a 1ª característica disponível. ⚠️ **O bem usado precisa ter ao menos uma característica
> associada** (o M01 não tinha; após associar, a consulta retornou e o teste passou).
> Detalhes no MAPA §5.
>
> Conta contábil de material é escolhida em runtime pelo flow (não vem do
> blueprint), conforme comentário no próprio `blueprint.yaml`.

---

## 6. Segurança

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Perfil | `perfil_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/seguranca/test_cadastro_perfil.py` (+ consulta/alteracao/exclusao) |
| Usuário | `funcionario_usuario_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/seguranca/test_cadastro_usuario.py` (+ consulta/alteracao/exclusao) |
| Log – Auditoria | — | — | ⛔ | — | — | fora de escopo (só-leitura, dispensado pelo Roniel) |

> **Perfil — validado em MPF (v4).** Perfil MÍNIMO (uma funcionalidade), não cópia: Nome +
> Sistema (CORPORATIVO) + 1 módulo (BAIRRO) → Confirmar (não precisa conceder permissão).
> `perfil_cr` = {nome, sistema, modulo}. Sistema (`sistema`) e Módulo (`contexto-1-3`) são
> lookups do tipo DIÁLOGO (Consulta model-0/model-1 → Anexar), não autocomplete. Consulta
> Nome=`model-2`, grid com coluna Nome. Alteração renomeia `nmPerfil` (sufixo). Getter
> `perfil_cr()`. (O botão "Copiar perfil" existe e é o que o Genesis `garantir_perfis` usa,
> mas traz TODAS as funcionalidades — por isso o teste monta o mínimo.)
>
> **Usuário — validado em MPF (v4).** Fluxo de 2 entidades: o Cadastro cria primeiro o
> funcionário (reusa o flow de Funcionário com `funcionario_usuario_cr`) e depois o usuário
> sobre ele; a Exclusão remove o usuário e depois o funcionário (2 passos, guardados). Perfil
> associado é PADRÃO (`ADM AUTOMATIZADO CR`), não `perfil_cr`. Recipe do Genesis
> (`garantir_usuarios/v4.py`). Consulta especial: `model-1` = funcionário via lookup
> (`lookup-model-1`, `divWarningMsg` se não existe); grid mascara o nome (`matrícula - *****`),
> então a seleção pega a 1ª linha. **Alteração**: o Usuário não tem campo Nome → altera SÓ o
> **E-mail** (`nmEmail`, toggle entre dois válidos); **não** re-preencher a senha (a mesma
> senha faz o Confirmar dar erro; senha em branco mantém a atual). Getter
> `funcionario_usuario_cr()`.
>
> Log – Auditoria é somente consulta → fora de escopo (Roniel dispensou as só-leitura).

---

## 7. Característica do Bem

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Definição | `caracteristica_bem_cr` | ✅ | ✅ | ✅ | ✅ | `tests/corporativo/caracteristica_bem/test_cadastro_definicao_caracteristica.py` (+ consulta/alteracao/exclusao) |
| Manutenção | — | ⏳ | ⏳ | ⏳ | ⏳ | — |

> Manutenção não tem chave `_cr` no blueprint — confirmar via `inspecionar()`
> antes de criar a chave e o card.

---

## 8. Agenda/Notificações

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Grupo de Usuário | — | ⏳ | ⏳ | ⏳ | ⏳ | — |
| Envio de Comunicado | — | ⏳ | ⏳ | ⏳ | ⏳ | — |
| Visualização | — | — | ⏳ | — | — | — |

> Nenhuma chave `_cr` definida ainda — confirmar via `inspecionar()` antes de
> criar as chaves e os cards. Visualização provavelmente é somente leitura.

---

## 9. Auxiliares

| Sub-página | Blueprint `_cr` | Cadastro | Consulta | Alteração | Exclusão | Arquivo(s) |
|---|---|:---:|:---:|:---:|:---:|---|
| Assinaturas nos Relatórios | — | ⏳ | ⏳ | ⏳ | ⏳ | — |

> Sem chave `_cr` definida — confirmar via `inspecionar()` antes de criar.

---

## Resumo de progresso (fase: Cadastros)

| Seção | Total | Concluídos | % |
| --- | :---: | :---: | :---: |
| Estrutura Organizacional | 6 | 6 | 100% |
| Localidade | 6 | 5 | 83% |
| Entidade Externa | 3 | 3 | 100% |
| Funcionário | 2 | 2 | 100% |
| Material | 6 | 6 | 100% |
| Segurança | 2 | 0 | 0% |
| Característica do Bem | 2 | 1 | 50% |
| Agenda/Notificações | 2 | 0 | 0% |
| Auxiliares | 1 | 0 | 0% |
| **Total** | **30** | **23** | **77%** |

> **Consumo, Permanente e Serviço compartilham o form `bemser`** → os flows genéricos ficam em
> `flows/corporativo/material/` (`selecionar_subgrupo`, `preencher_dados_gerais_material`,
> `selecionar_conta`, `confirmar_material`, `selecionar_material`), reutilizados pelos três
> (recebem o dict `material`). Só a **navegação** é própria de cada tipo. **Serviço** reusou
> 100% dos flows compartilhados — só a nav é nova (headings: v4 `Material - Serviço`, v3
> `Tabelas - Serviços`; usa `material_servico_cr`, subgrupo 7510, UM "UMT" padrão).
> **UM do permanente = "UN"** (não "UMT", que é UM de consumo e não aparece
> no lookup do form de permanente). Permanente **não** precisa marcar `emplaquetavel`.

> **Material de Consumo** foi o 1º card com teste de **Exclusão** feito junto do
> Cadastro (o de Exclusão limpa o registro que o Cadastro criou, dispensando script
> descartável). Aprendizados no MAPA §5.