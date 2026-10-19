# Corporativo — Mapa do Módulo e Localizadores

> Documento de referência para criação dos testes do módulo **Corporativo** do ASI.
> Reúne: mapa de seções/sub-páginas (confirmado via MCP no cliente `pcdfv4`),
> caminho de navegação (v3/v4), heading de cada página, e os `name=` reais dos
> campos de cada formulário de cadastro. Fonte dos localizadores: flows do
> Genesis (`genesis/flows/`) + inspeção ao vivo via MCP `asi-automacao`.
>
> **Cliente de referência:** `pcdfv4` (v4) — `http://pcdfqas.linkdata.com.br:8080/pcdf-40/web`
> **Chaves do blueprint:** entidades novas do Corporativo usam sufixo `_cr`
> (ver `genesis/blueprint/blueprint.yaml`).

---

## Mapa de seções e sub-páginas (confirmado via MCP)

| # | Seção | Sub-páginas |
| --- | ------- | ------------- |
| 1 | **Estrutura Organizacional** | Almoxarifado · CC - Centro de Custos · UA - Unidade Administrativa · UG - Unidade Gestora · UL - Unidade de Localização · UR - Unidade de Requisição |
| 2 | **Localidade** | País · Região · UF - Unidade da Federação · Cidade · Endereço · Instalação |
| 3 | **Entidade Externa** | Fornecedor · Portador · Órgão Externo |
| 4 | **Funcionário** | Cadastro · Funções |
| 5 | **Material** | Consumo · Permanente · Serviço · Supply · Unidade de Medida · Modelo de Importação |
| 6 | **Segurança** | Perfil · Usuário · Log – Auditoria |
| 7 | **Característica do Bem** | Definição · Manutenção |
| 8 | **Agenda/Notificações** | Envio de Comunicado · Grupo de Usuário · Visualização |
| 9 | **Auxiliares** | Assinaturas nos Relatórios |

> Navegação v4 (padrão): `ir_home()` → texto **"Corporativo"** → título
> **"Abrir menu"** → texto da **seção** → texto da **sub-página** →
> `page.locator("i").nth(2).click()` (abre o form) → heading confirma.
> Conteúdo do form fica em iframe → usar `escopo(page)` / `obter_frame_conteudo(page)`.
>
> Navegação v3 (padrão): `clicar_menu_com_retry` → link **"Corporativo"** →
> link da **seção** → texto da **sub-página** → heading confirma. Sem iframe.

---

## Localizadores por página

Legenda: **[CK]** = chave única do registro. Campos de lookup preenchidos com
`preencher_campo(ctx, seletor, valor)`. Confirmar = `button[name='submitFinish']`
ou `get_by_role("button", name="Confirmar")`. Sucesso/erro = `esperar_sucesso_ou_erro(ctx)`.

### Filtros de Consulta C/A/E (`model-N`) — confirmados ao vivo (Wave 1 + 2)

A Consulta filtra pelo `model-N` abaixo; a **seleção casa pelo Nome** (coluna sempre exibida
no grid — ver skill `/padroes-testes`). `submitSearch` abre a busca e a dispara.

| Página | Filtro | `model-N` | Observação |
|---|---|---|---|
| UA | Sigla | `model-4` | grid não mostra Sigla → casar por Nome (`model-3`) |
| UR | Nome | `model-5` | |
| Almoxarifado | Sigla | `model-4` | |
| UG | Nome | `model-2` | |
| CC | Nome | `model-2` | |
| País/Região/UF/Cidade | Nome | `model-1` | |
| Endereço | Nome | `model-3` | Órgão/Instalação antes |
| Instalação | Nome | `model-2` | CEP: máscara `XX.XXX-XXX` (`_formatar_cep`) |
| Função | Nome | `model-1` | |
| Órgão Externo | Nome | `model-4` | (CNPJ=`model-2`, Sigla=`model-12`) |
| Fornecedor | CNPJ (fmt `XX.XXX.XXX/XXXX-XX`) | `model-2` | casa por Nome/Razão |
| Portador | CPF (fmt `XXX.XXX.XXX-XX`) | `model-2` | casa por Nome |
| Funcionário | CPF (derivado da matrícula, fmt) | `model-4` | casa por Nome |
| Unidade de Medida | **Sigla** | `model-2` | `dsUm` (Descrição, `model-1`) é truncada por maxlength → filtrar/casar por Sigla |
| Definição (Característica) | Nome | `model-1` | (C/A/E ainda não feitos — cadastro hardcoda dado) |
| Modelo de Importação | Descrição | `model-1` | v4-only |

### 1. Estrutura Organizacional

#### UG - Unidade Gestora ✅ (teste já existe: `test_cadastro_ug`)

- **Heading v4:** `Estrutura Organizacional - UG - Unidade Gestora` · **v3:** `Estrutura Organizacional - U.G. (Unidade Gestora)`
- **Nav v4:** Corporativo → Estrutura Organizacional → "UG - Unidade Gestora"
- **Campos:**
  - `input[name='cdOrgao']` — Órgão (desabilitado, pré-preenchido)
  - `input[name='cdUg']` — Código **[CK]** (gerar, 6 díg.)
  - `input[name='nmUg']` — Nome
  - `input[name='cdCidade']` — Cidade (lookup; preenche UF automaticamente)
  - `input[name='sgUg']` — Sigla
  - `input[name='inAdmDireta'][value='S'|'N']` — Administração direta (radio)
- **Blueprint:** `unidade_gestora_cr` (nome, sigla, cidade, administracao_direta)

#### UA - Unidade Administrativa ✅ (teste já existe: `test_cadastro_ua`)

- **Heading (v3 e v4, no iframe/form):** `Estrutura Organizacional - U.A. (Unidade Administrativa)`
- **Breadcrumb externo v4 (usado no `expect` da navegação):** `Estrutura Organizacional - UA - Unidade Administrativa`
- **Nav v4:** Corporativo → Estrutura Organizacional → "UA - Unidade Administrativa"
  (o formulário abre direto ao clicar na sub-página — **não** usa `page.locator("i").nth(2)`)
- **Campos (aba Edição / Dados Gerais):**
  - `input[name='sgUa']` — Sigla **[CK]**
  - `input[name='nmUa']` — Nome
  - `input[name='ug']` — UG (lookup por sigla) — **obrigatório antes** de abrir Responsáveis
  - `input[name='uaSuperior']` — UA superior (opcional)
  - Aba **Responsáveis** (`button[name='submitTabResponsaveis']`):
    - `input[name='funcionario-1-2']` — Responsável (lookup por nome)
    - `input[name='tipoFuncao-1-3']` — Função (lookup)
    - `input[name='hierarquia-1-5']` — checkbox hierarquia (a linha 1 já vem pronta;
      não é necessário clicar "Adicionar linhas")
- **Consulta (filtros `model-N`):** Órgão=`model-0`, U.G.=`model-1`, Código=`model-2`,
  Nome=`model-3`, **Sigla=`model-4`**, U.A. superior=`model-5`, Data bloqueio=`model-6`,
  Responsável=`model-7`. Seleção via `submitUse` (Anexar); exclusão via `submitDelete`
  (diálogo "Confirma Exclusão?").
- **Blueprint:** `unidade_administrativa_cr` (sigla, ug, nome, responsavel{nome, funcao})

#### UL - Unidade de Localização ✅ (teste já existe: `test_cadastro_ul`)

- **Heading (form):** `Estrutura Organizacional - U.L. (Unidade de Localização)`
- **Breadcrumb externo v4 (usado no `expect`):** `Estrutura Organizacional - UL - Unidade de Localização`
- **Nav v4:** Corporativo → Estrutura Organizacional → "UL - Unidade de Localização"
  (form abre direto, sem `i.nth(2)`)
- **Campos (Dados Gerais + aba Responsáveis):**
  - `input[name='sgUl']` — Sigla **[CK]**
  - `input[name='ua']` — \*U.A. (lookup) · `input[name='centroCusto']` — \*C.C. (lookup)
  - `input[name='local']` — \*Endereço (lookup `lookup-local`; `preencher_campo` funciona)
  - Aba Responsáveis (`button[name='submitTabResponsaveis']`):
    - `input[name='hierarquia-1-2']` — Responsável (lookup por nome)
    - `input[name='tipoFuncao-1-3']` — Função (lookup)
    - `input[name='hierarquia-1-5']` — checkbox assinatura
- **Chave única = (Órgão, UG, UA, Endereço).** Todos os 5 endereços padrão já têm
  UL com a UA SGRTA (4 ULs + a UL de estoque), então o `unidade_localizacao_cr`
  usa um **endereço dedicado** ("REGIÃO CORPORATIVA DE MÓDULOS S9", 6º de
  `enderecos`) para não colidir. Erro se colidir: "Esta U.L. com este Orgão,
  U.G., U.A. e Local já foi cadastrada".
- **Consulta:** Sigla da U.L. = **model-8** (há duas "Sigla" na tela; a 1ª, após
  Endereço, é a da UL).
- **Exclusão:** exige remover o responsável antes (aba Responsáveis) — a exclusão
  direta não passa. Detalhar no card de Exclusão da UL.
- **Blueprint:** `unidade_localizacao_cr` (sigla, unidade_administrativa, endereco, centro_custo, responsavel{nome, funcao})

#### CC - Centro de Custos ✅ (teste já existe: `test_cadastro_cc`)

- **Heading (form):** `Estrutura Organizacional - Centro de Custo`
- **Breadcrumb externo v4 (usado no `expect`):** `Estrutura Organizacional - CC - Centro de Custos`
- **Nav v4:** Corporativo → Estrutura Organizacional → "CC - Centro de Custos" (form abre direto)
- **Campos:** `input[name='nmCentroCusto']` — Nome (único editável obrigatório;
  Órgão pré-preenchido — varia por cliente, Código gerado). Confirmar = `button[name='submitFinish']`.
- **Consulta:** Nome = **model-2**. Exclusão direta (Anexar → Excluir).
- **Blueprint:** `centro_custo_cr` (nome)

#### UR - Unidade de Requisição ✅ (teste já existe: `test_cadastro_ur`)

- **Cadastro mínimo (obrigatórios):** só `cdUa`, `cdCentroCusto`, `nmUr`, `cdLocal`
  e Confirmar. Abas Autorizador/Centro de Custo e sub-tabelas (catálogo, dias, UL,
  atividade) **não** são necessárias para o cadastro. Form abre direto (sem `i.nth(2)`).
- **Chave única = (U.A., Endereço).** O blueprint `unidade_requisicao_cr` usa o 5º
  endereço ("LOCALIDADE PATRIMONIAL DE ESTOQUE G3") porque os 4 primeiros já são
  usados pelas URs padrão com a mesma UA SGRTA (senão dá "UR já cadastrada para
  esta UA e Endereço").
- **Breadcrumb externo v4 (usado no `expect`):** `Estrutura Organizacional - UR - Unidade de Requisição`
- **Consulta (filtros `model-N`):** Órgão=0, UG=1, UA=2, C.Custo=3, Código=4,
  **Nome=5**, Sigla=6, Endereço=7, Responsável=8, Atividade=10.
- **Heading (form):** `Estrutura organizacional - U.R. (Unidade Requisita...)`
- **Nav v4:** Corporativo → Estrutura Organizacional → "UR - Unidade de Requisição"
- **Campos:**
  - `input[name='cdOrgao']` / `input[name='cdUg']` (desabilitados)
  - `input[name='cdUa']` — **\*U.A.** (lookup `lookup-cdUa`, obrigatório)
  - `input[name='cdCentroCusto']` — Centro de custo (lookup `lookup-cdCentroCusto`)
  - `input[name='cdUr']` (desabilitado — gerado)
  - `input[name='nmUr']` — Nome
  - `input[name='nrFuncionario']`, `input[name='nrTelefoneRamal']`
  - `input[name='cdLocal']` — **\*Endereço** (lookup `lookup-cdLocal`, obrigatório)
  - `input[name='cdResponsavel']` — Responsável (lookup)
  - checkboxes: `bloqueio`, `inAgendamento`
  - Abas: Autorizador (`submitTabAutorizador`), Centro de Custo (`submitTabCentroCustos`)
  - Sub-tabelas: catálogo (`cdCatalogo-1-2`), dias (`nrDia-1-2`), UL (`cdUl-1-2`), atividade (`cdAtividade-1-2`)
- **Blueprint:** `unidade_requisicao_cr` (sigla_ua/ua, nome, endereco, centro_custo) — ver `unidades_requisicao`

#### Almoxarifado ✅ (teste já existe: `test_cadastro_almoxarifado`)

- **Heading (form h1):** `Estrutura organizacional - Almoxarifado` (org. minúsculo)
- **Breadcrumb externo v4 (usado no `expect`):** `Estrutura Organizacional - Almoxarifado`
  (o `name` do `get_by_role` é substring case-insensitive → a mesma string serve v3/v4)
- **Nav v4:** Corporativo → Estrutura Organizacional → "Almoxarifado". ⚠️ O item do flyout
  tem duplicado **oculto** no DOM → clicar com `.filter(visible=True)`.
- **Nav v3:** Corporativo → Estrutura Organizacional → `.menu-link a[title='Almoxarifado']`.
  ⚠️ "Almoxarifado" casa **3 links** (o módulo homônimo + ícone + texto da sub-página);
  `get_by_role("link", name="Almoxarifado")` dá strict mode violation.
- **Campos (obrigatórios `*`):** Órgão (`orgao`, pré, varia por cliente), Código
  (`cdAlmoxarifado`, gerado), **Nome** (`dsAlmoxarifado`), **U.G.** (`cdUg`, lookup
  `lookup-cdUg`). Sigla (`sgAlmoxarifado`) **não** tem `*` mas é a chave de consulta.
  Controle financeiro = radio `inControleFin` (`S`/`N`, default `S`).
  Opcionais: `cdAlmoxSup` (Almoxarifado superior), `cdResponsavel`, `cdCoResponsavel`,
  checkboxes `virtual`(disabled)/`bloqueado`/`suspenso`. Confirmar = `submitFinish`.
- **Consulta:** Sigla = **model-4**. Exclusão direta (Anexar → Excluir), confirmada v3+v4.
- **Chave única = Sigla.** Sem chave composta (diferente de UR/UL).
- **Blueprint:** `almoxarifado_cr` (nome, sigla, unidade_gestora → CGTAD padrão) — ver `almoxarifados`

### 2. Localidade

> **Testes de Cadastro prontos:** País, Região, UF, Cidade, Endereço ✅ (validados v3+v4).
> **Instalação ⚠️ bloqueada por bug de aplicação:** o campo CEP (`nrCep`) rejeita
> qualquer valor bem-formado ("CEP inválido! Ex: 12345-678") — testado com `70000-000`,
> `70040-010` (real) e `70000000` (cru). Teste com `pytest.skip`; chamado a abrir.
>
> **Navegação (as 6):** form abre direto. **v4**: Corporativo → "Abrir menu" →
> "Localidade" → sub-página `.filter(visible=True).first` → `i.nth(2)` (recolhe menu).
> **v3**: Corporativo → "Localidade" → `.menu-link a[title='<nome exato>']` (os nomes
> v3 são os simples: País, Região, "UF - Unidade da Federação", Cidade, Instalação, Endereço).
> Heading = `Localidade - X` (igual v3/v4), exceto UF: v4 breadcrumb `Localidade - UF -
> Unidade da Federação`, v3 h1 `Localidade - U.F.`.
>
> **Consulta — filtro Nome (cleanup):** model-1 para País/Região/UF/Cidade; **model-3**
> para Endereço (Órgão e Instalação são lookups antes do Nome). Exclusão direta.

#### UF - Unidade da Federação

- **Heading v4:** `Localidade - UF - Unidade da` · **v3:** `Localidade - U.F.`
- **Nav v4:** Corporativo → Localidade → "UF - Unidade da Federação"
- **Campos:**
  - `input[name='nmUf']` — Nome
  - `input[name='pais']` — País (lookup)
  - `input[name='sgUf']` — Sigla
- **Blueprint:** `uf_cr` (nome, pais, sigla)

#### Cidade

- **Heading:** `Localidade - Cidade`
- **Nav v4:** Corporativo → Localidade → "Cidade"
- **Campos:**
  - `input[name='nmCidade']` — Nome
  - `input[name='uf']` — UF (lookup)
  - `input[name='regiao']` — Região (lookup)
- **Blueprint:** `cidade_cr` (nome, uf, regiao)

#### País ✅ inspecionado

- **Heading:** `Localidade - País`
- **Nav v4:** Corporativo → Localidade → "País"
- **Campos:** `input[name='cdPais']` (desab.) · `input[name='nmPais']` (Nome) · `input[name='sgPais']` (Sigla) · checkbox `indBloqueado`
- **Blueprint:** `pais_cr` (nome, sigla)

#### Região ✅ inspecionado

- **Heading:** `Localidade - Região`
- **Nav v4:** Corporativo → Localidade → "Região"
- **Campos:** `input[name='cdRegiao']` (Código **[CK]**, editável) · `input[name='nmRegiao']` (Nome) · `input[name='regiaoSuperior']` (lookup `lookup-regiaoSuperior`, opcional) · checkbox `indBloqueado`
- **Blueprint:** `regiao_cr` (codigo, nome)

#### Endereço ✅ inspecionado

- **Heading:** `Localidade - Endereço`
- **Nav v4:** Corporativo → Localidade → "Endereço"
- **Campos:** `input[name='orgao']` (desab., \*Órgão) · `input[name='cdLocal']` (desab.) · `input[name='nmLocal']` (Nome) · `input[name='instalacao']` (**\*Instalação**, lookup `lookup-instalacao`) · `input[name='localSup']` (Local superior, lookup, opcional)
- **Blueprint:** `endereco_cr` (nome, instalacao) — ver `enderecos`

#### Instalação ✅ inspecionado

- **Heading:** `Localidade - Instalação`
- **Nav v4:** Corporativo → Localidade → "Instalação"
- **Campos:** `input[name='orgao']` (desab.) · `input[name='cdInstalacao']` (desab.) · `input[name='nmInstalacao']` (Nome) · `input[name='dsEndereco']` (Endereço) · `input[name='cidade']` (lookup `lookup-cidade`) · `input[name='nmBairro']` (Bairro) · `input[name='nrCep']` (CEP)
- **Blueprint:** `instalacao_cr` (nome, endereco, cidade, bairro, cep) — ver `instalacao`

### 3. Entidade Externa

> **Navegação (as 3 sub-páginas):** form abre direto. Em **v4**: Corporativo →
> "Abrir menu" → "Entidade Externa" → sub-página → `page.locator("i").nth(2).click()`
> (recolhe o menu lateral). Em **v3**: Corporativo → "Entidade externa" →
> `a[id^='menuItemLink']` com texto "Cadastro de <Sub-página>" (o link visível tem
> prefixo "Cadastro de …"). Heading v4 = breadcrumb externo `Entidade Externa - X`;
> heading v3 = h1 do form (exato — ver cada uma).

#### Fornecedor ✅ (teste: `test_cadastro_fornecedor`)

- **Heading:** v4 breadcrumb `Entidade Externa - Fornecedor`; v3 h1 `Fornecedor`.
- **Campos (form com abas; só a aba Cadastro é necessária):**
  - `select situacaoJuridica` — Tipo (PESSOA JURIDICA/FISICA/ESTRANGEIRO) — via `select_tipo`
  - `select cdTpForPorte` — Porte (MICRO-EMPRESA/…) — via `select_tipo`
  - `input[name='inCartorio'][value='N']` — radio
  - `input[name='nrIdentAgente']` — CNPJ **formatado** XX.XXX.XXX/XXXX-XX **[CK]**
  - `input[name='nmRazaoSocialGeral']` — Razão social · `input[name='nmAgente']` — Nome Fantasia
  - `input[name='edAgente']` — Endereço · `input[name='nmBairro']` — Bairro
  - `input[name='cdCidade']` — Cidade (lookup, `preencher_campo`)
  - `input[name='nrDdd1']`("61") / `input[name='nrFone1']` — DDD/Telefone
  - País pré-preenchido; sub-tabela Contato ignorada. Confirmar = `submitFinish`.
- **Consulta:** CNPJ = **model-2** (formatado). Exclusão direta.
- **Blueprint:** `fornecedor_cr` (nome, tipo, porte, endereco, cnpj, cidade, bairro, fone)

#### Órgão Externo ✅ (teste: `test_cadastro_orgao_externo`)

- **Heading:** v4 breadcrumb `Entidade Externa - Órgão Externo`; v3 h1 `Órgão Externo`.
- **Campos:** `input[name='nrIdentAgente']` (Identificação/CNPJ **formatado** **[CK]**, checkbox `validaCNPJ` fica marcado) · `input[name='cdUasg']` (UASG) · `input[name='nmAgente']` (**\*Nome**) · `input[name='sgOrgaoExterno']` (Sigla) · `input[name='edAgente']` (**\*Endereço**) · `input[name='nmBairro']` (**\*Bairro**) · `input[name='cdCidade']` (**\*Cidade**, lookup) · `input[name='nrCep']` (formatado XXXXX-XXX) · `nrDdd1`("61")/`nrFone1` · `input[name='nmEmail']`. `cdAgente`(Código) gerado.
- **Consulta:** CNPJ = **model-2**, Nome = model-4, Sigla = **model-12**. Exclusão direta.
- **Blueprint:** `orgao_externo_cr` (nome, sigla, cnpj, uasg, endereco, bairro, cidade, cep, fone, email)

#### Portador ✅ (teste: `test_cadastro_portador`)

- **Heading:** v4 breadcrumb `Entidade Externa - Portador`; v3 h1 `Portador`.
- **Campos:** `input[name='nmRegistroCivil']` (**\*Nome/Registro Civil**) · `input[name='nrIdentAgente']` (**\*CPF** formatado XXX.XXX.XXX-XX **[CK]**) · `input[name='nrRG']` (**\*R.G.**) · `input[name='edAgente']` (**\*Endereço**) · `input[name='cdCidade']` (**\*Cidade**, lookup) · `input[name='nrCep']` · `nrDdd1`("61")/`nrFone1` (**\*Telefone**) · `input[name='agenteFornecedorOrgaoExterno']` (**\*Fornecedor/Órgão Externo**) · `input[name='nmEmail']`. Órgão pré-preenchido.
- ⚠️ **Lookup `agenteFornecedorOrgaoExterno` (caso especial):** o `preencher_campo` falha aqui — o clique no botão `lookup-agente` é interceptado pelo dropdown de autocomplete aberto (só nesta página). Usar `preencher_autocomplete(ctx, selector, valor)` (digita + ArrowDown+Enter). Os demais lookups (cidade) seguem `preencher_campo` normal.
- **Dependência:** exige um Fornecedor **ou** Órgão Externo já cadastrado → `_cr` usa fornecedor **padrão** (`fornecedores[0]`).
- **Consulta:** CPF = **model-2**. Exclusão direta.
- **Blueprint:** `portador_cr` (nome, cpf, rg, endereco, cidade, cep, fone, fornecedor, email)

### 4. Funcionário ✅ (inspecionado ao vivo v3+v4)

#### Cadastro (de Funcionário)

- **Heading:** v4 breadcrumb externo `Funcionário - Cadastro`; v3 h1 do form `Funcionário`.
- **Nav v4:** Corporativo → Abrir menu → "Funcionário" → "Cadastro" → `i.nth(2)` (recolhe menu).
- **Nav v3:** menu → Corporativo → `link ^Funcionári` → `a[id^='menuItemLink']` has_text `^Cadastro de Funcionári`.
- **Campos:**
  - `input[name='cdFuncionario']` — \*Matrícula (**maxlength 8**: a matrícula de 11 díg. do
    blueprint trunca p/ 8 — inofensivo; o identificador real é o CPF). Preencher com "Novo" já ativo.
  - `input[name='cdUa']` — U.A. (**opcional**, sem `*` em v3/v4); lookup é `lookup-ccdUa` (**cc duplo**,
    não `lookup-cdUa`). Referencia SGRTA (padrão) — exige o dado provisionado no ambiente.
  - `input[name='nmRegistroCivil']` — \*Nome (Registro Civil).
  - `input[name='nrCpf']` — CPF (opcional; derivado da matrícula, **formatado** `XXX.XXX.XXX-XX`).
  - `input[name='nmEmail']` — E-mail (opcional).
  - `* Órgão` (`orgao`) — desabilitado, pré-preenchido (varia por cliente).
  - Submit: `button[name='submitFinish']`. Consulta CPF=`model-4`.
- **Blueprint:** `funcionario_cr` (matricula, nome, email, sigla_ua).

#### Funções

- **Heading:** v4 breadcrumb externo `Funcionário - Funções`; v3 h1 do form `Função`.
- **Nav v4:** Corporativo → Abrir menu → "Funcionário" → "Funções" → `i.nth(2)`.
- **Nav v3:** menu → Corporativo → `link ^Funcionári` → `a[id^='menuItemLink']` has_text `Cadastro de Funções`.
- **Campos:** `input[name='nmTpFuncaoHier']` — Nome (Código gerado). Submit `submitFinish`. Consulta Nome=`model-1`.
- **Blueprint:** `funcao_cr` (nome)

### 5. Material

#### Unidade de Medida

- **Heading:** `Material - Unidade de Medida`
- **Nav v4:** Corporativo → Material → "Unidade de Medida"
- **Campos:**
  - `input[name='dsUm']` — Descrição
  - `input[name='sgUm']` — Sigla **[CK]**
- **Blueprint:** `unidade_medida_cr` (descricao, sigla)

#### Supply ✅ validado (pcdf v3 + pcdfv4 v4, ciclo rerunnável) — cadastra Grupo→Subgrupo→Material NOVOS (texto livre)

- **Heading:** v4 breadcrumb `Material - Supply`; v3 h1 `Supply`. É CRUD.
- **Nav v4:** Corporativo → Abrir menu → Material → "Supply". Flows em `cadastro_supply/`.
- **Cadastro (texto livre — NÃO usa o lookup do grupo):** `preencher_supply` faz tudo (é o único
  flow, então confirma):
  1. `input[name='grupoCdExemplo']`=código + `input[name='grupoDsExemplo']`=nome.
  2. `button[name='submitAddLine1']` (+Subgrupos) → `input[name='subgrupoCdExemplo']` + `subgrupoDsExemplo`.
  3. `button[name='submitAddLine2']` (+Materiais) → `input[name='materialDsExemplo']` (código do material é gerado).
  4. `button[name='submitFinish']`.
  - ⚠️ **Dados inventados**: grupo `100` (alto/livre, fora do intervalo SIASG 00–99) → não colide.
    "OUTROS" do SIASG é 7599 etc.; um subgrupo sob grupo existente daria "já foi incluído".
- **Exclusão (o teste orquestra — DOIS passos: subgrupo, depois grupo):** o grupo só pode ser excluído quando
  está vazio, então deleta-se o subgrupo primeiro.
  1. `consultar_subgrupo_supply` (abre `lookup-grupoDsExemplo` → `select[name='tpFil']`=SUBGRUPO → filtra
     `input[name='filtro']`=subgrupo_codigo → dblclick `img.x-tree-node-icon.icon-subgrupo-open`) →
     `selecionar_subgrupo_supply` (marca radio `input[name='sgSel']` do material → bool) →
     `excluir_movimento(esperar_sucesso=True)`.
  2. `consultar_grupo_supply` (abre lookup → `tpFil`=GRUPO → filtra grupo_codigo → dblclick o nó do grupo por texto
     `"{grupo_codigo} - {grupo_nome}"`) → `excluir_movimento(esperar_sucesso=True)`.
- **Blueprint:** `supply_cr` (grupo_codigo="100", grupo_nome, subgrupo_codigo="10099", subgrupo_nome, material_nome).
- 🐞 **BUG do app (documentado em card BUG):** se o cadastro digitar um grupo que JÁ existe, dá "ERRO JAVA!" no
  `submitAddLine2`. Por isso a exclusão precisa remover também o grupo (senão o órfão quebra o re-cadastro).

#### Consumo / Permanente / Serviço ✅ inspecionados (mesmo form `com.linkdata.corporativo.material.bemser`)

- **Headings:** `Tabelas - Material Consumo` · `Tabelas - Material Permanente` · `Tabelas - Serviços`
- **Nav v4:** Corporativo → Material → "Consumo" | "Permanente" | "Serviço"
- **Abas:** Cadastrar · Características · Imagens · Detalhes · Observações
- **Campos (Dados Gerais + Material):**
  - `select[name='tipoTela']` (NORMAL / MOVER MATERIAL / MOVER COMPLEMENTO)
  - `input[name='subgrupo']` — Subgrupo (lookup `lookup-subgrupo`)
  - `input[name='material_DsBemGenerico']` — Material genérico (lookup)
  - `textarea[name='complemento_NmBemServico']` — Complemento/nome (+ lookup)
  - `input[name='complemento_CdUmElementar']` — Unidade de medida (lookup)
  - `input[name='complemento_CdConta']` — Conta contábil (lookup)
  - `input[name='complemento_siasg']` — Código SIASG
  - `select[name='tdStatus']` (ANÁLISE / Ativo / INDISPONÍVEL)
  - `input[name='cdMatAntigo']`
  - **Permanente:** + checkbox `emplaquetavel`
  - **Consumo:** + checkbox `inControleUnitarioAtendimento` (desab.)
- **Blueprint:** `material_consumo_cr`, `material_permanente_cr`, `material_servico_cr`
  (nome, complemento, unidade_medida, subgrupo) — ver `materiais`/`bens`.
  A **conta contábil** é escolhida aleatoriamente em runtime pelo flow (exceto
  nomes com "HOSPITALAR"/"ODONTOLOGICO") — por isso **não** fica no blueprint.

- **Consumo ✅ Cadastro + Exclusão implementados (v3+v4).** Cenário A (um só
  `preencher`, escopo via `escopo(page)`). Fluxos quebrados em `selecionar_subgrupo_flow`
  e `selecionar_conta_flow`. Sequência: subgrupo (preenche + clica `img[title='Retornar']`
  no painel de classificação; fallback Federal Supply) → `submitAddLine1` →
  `material_DsBemGenerico` (nome genérico) → `complemento_NmBemServico` →
  **clicar no heading `Material` para disparar o ajax** → U.M. (`complemento_CdUmElementar`)
  → conta (lookup → linha aleatória não-HOSPITALAR → `submitUse`) → status
  (`select tdStatus=01` Ativo; erro se desabilitado/ANÁLISE = restrição de perfil) →
  Confirmar (`submitFinish`, timeout 90s).
- ⚠️ **APRENDIZADO CRÍTICO (v3):** após digitar o **complemento novo**, é obrigatório
  **clicar fora do campo** (no heading `Material`) para o ajax recarregar. Se pular esse
  passo, a v3 abre sozinha a busca do complemento (alerta "Nenhum COMPLEMENTO encontrado!")
  e a máscara `div.ext-el-mask` trava os cliques seguintes (ex.: lookup da conta). **Não
  é bug** — é o passo de blur que o Genesis já fazia. A v4 não exibe o alerta, mas também
  depende do mesmo clique.
- **Exclusão:** o form não tem "Consulta" padrão. Carrega-se o material pela busca do
  complemento (`selecionar_material_consumo_flow`): Novo → digita complemento → clica
  heading → `lookup-complemento_NmBemServico` (auto-filtra por COMPLEMENTO) → clica
  `img[title='Retornar']` da linha `.x-grid3-body .x-grid3-row` → habilita Excluir →
  shared `excluir_movimento(page, esperar_sucesso=True)`. O teste de Exclusão serve de
  limpeza do que o Cadastro criou.
- **Selecionar material — não encontrado:** quando o material NÃO existe, a busca do
  complemento retorna o alerta **"Nenhum COMPLEMENTO encontrado!"** (`.ext-mb-text`),
  não um grid vazio. O flow aguarda **alerta OU linha** (`expect(alerta.or_(linha))`); se
  for o alerta, dá OK, espera a máscara sumir, clica `submitCancel` e retorna `False`
  (teste faz `pytest.skip`). Se for a linha, clica `Retornar` e retorna `True`.
- **Flows compartilhados (Consumo/Permanente/Serviço):** por ser o mesmo form `bemser`, os
  flows genéricos ficam em `flows/corporativo/material/` (`selecionar_subgrupo`,
  `preencher_dados_gerais_material`, `selecionar_conta`, `confirmar_material`,
  `selecionar_material`), recebem o dict `material` e são **chamados pelo teste**. Só a
  **navegação** é por tipo (`cadastro_material_{consumo,permanente}/navegar_*`).

#### Permanente ✅ Cadastro + Exclusão implementados (v3+v4)

- Idêntico ao Consumo, reusando os flows compartilhados; só a navegação muda.
- **Nav v4:** Corporativo → Material → "Permanente" → `i.nth(2)`; heading breadcrumb
  `Material - Permanente`. **Nav v3:** Corporativo → "Material / Serviço" → "Permanente";
  h1 `Tabelas - Material Permanente`.
- **UM = "UN"** (`material_permanente_cr.unidade_medida`), **não "UMT"** — UMT é UM de
  consumo e não aparece no lookup do form de permanente (o `garantir_bens` usa "UN").
- **Não** marca `emplaquetavel` (opcional; o `garantir_bens` também não marca).
- Subgrupo `7195` (MOBILIARIOS DIVERSOS); nome `B99 BEM PERMANENTE CR`.

#### Modelo de Importação ✅ validado (pcdfv4) — É CRUD (corrige nota antiga) — v3 pendente

- **Heading:** v4 breadcrumb `Material - Modelo de Importação`; v3 h1 `Modelo de Importação`.
- **Nav v4:** Corporativo → Abrir menu → Material → "Modelo de Importação".
- **Campos:**
  - `input[name='dsModelo']` — \*Descrição (chave única).
  - `input[name='dsCompleta']` — \*Material (lookup `lookup-dsCompleta`). ⚠️ **Só aceita material
    PERMANENTE** (bem, elem. despesa 4490) — consumo (ex. "C01 CANETA") NÃO aparece. Usa o bem de
    `garantir_bens`: "M01 MESA DE ESCRITÓRIO EM MDF AUTOMATIZADO". `preencher_campo` resolve direto.
  - `input[name='cdModelo']` — Código (desabilitado, gerado).
  - `input[name='inNrPatrimonial']` — checkbox "Adicionar Número Patrimonial" (não marcado).
  - Grid Características (⚠️ **OBRIGATÓRIO ≥1**, apesar de sem asterisco — app rejeita com
    "É necessário informar pelo menos uma característica."): abrir `lookup-caracteristica-1-3` →
    `submitSearch` (sem filtro) → Anexar a 1ª linha
    (`table[name='paginationTable'] tbody tr:first-child button[name='submitUse']`; catálogo varia
    por cliente, não prender a nome). Usar `tr:first-child`, **não** `.first` (o grid ext replica
    linhas ocultas de medição → `.first` casaria um submitUse não-clicável → timeout 60s).
  - ⚠️ **O bem escolhido precisa ter ≥1 característica associada** — a consulta de característica
    lista as do bem; se o bem não tiver nenhuma, vem vazia e o cadastro falha. (M01 não tinha; foi
    preciso associar uma no cadastro do bem.)
  - Submit `button[name='submitFinish']`.
- **Só existe na v4** — não achamos cliente v3 com essa funcionalidade. No `modules_catalog`
  as entradas usam `"clients": CLIENTES_V4`.
- **Flows (uma ação por flow, `flows/corporativo/material/cadastro_modelo_importacao/`):**
  - Cadastro (o teste orquestra): `acessar_modelo_importacao` → `preencher_dados_gerais_modelo_importacao`
    (só Descrição + Material) → `consultar_caracteristicas` (abre lookup + `submitSearch`) →
    `selecionar_caracteristicas` (Anexar 1ª linha **e confirma**: `submitFinish` + `esperar_sucesso_ou_erro`,
    pois é o último flow da sequência — convenção do projeto).
  - Exclusão (o teste orquestra): `acessar_modelo_importacao` → `consultar_modelo_importacao`
    (`submitSearch` → `model-1`=descricao → `submitSearch`) → `selecionar_modelo_importacao` (Anexar 1ª
    linha; `submitCancel`+False se vazio) → `excluir_movimento(esperar_sucesso=True)`.
- **Exclusão — filtros da Consulta própria:** `model-0-from/to`=Código, **`model-1`=Descrição**,
  `model-2`=Bem/Serviço.
- **Blueprint:** `modelo_importacao_cr` (descricao, material). Característica é dinâmica (não no blueprint).

### 6. Segurança

#### Perfil

- **Heading:** `Segurança - Perfil`
- **Nav v4:** Corporativo → Segurança → "Perfil"
- **Fluxo:** cópia de perfil existente → renomear.
  - `button "Consulta"` → `input[name='model-2']` (perfil p/ copiar) → consultar
  - `table[name='paginationTable'] tbody tr` → `button[name='submitUse']`
  - `button "Copiar perfil"` → `input[name='nmPerfil']` (novo nome) → Confirmar
- **Blueprint:** `perfil_cr` (nome, perfil_p_copia)

#### Usuário

- **Heading:** `Segurança - Usuário`
- **Nav v4:** Corporativo → Segurança → "Usuário"
- **Campos:**
  - `input[name='funcionario']` — Funcionário (lookup por nome) **[CK]**
  - `input[name='senha']` / `input[name='confirmacaoSenha']`
  - Sistemas: `title "Adicionar Linhas"` → `input[name='sistemas-{i}-2']` (sistema) →
    `button[name='edit-sistemas-{i}-5']` → `input[name='perfis-1-2']` (perfil, lookup `lookup-perfil-1-2`) →
    `input[name='cdPerfilSelecionado']` (check) → `button "Retornar"`
  - `input[name='cdSistemaSelecionado']` (check)
- **Blueprint:** `funcionario_usuario_cr` — registro isolado com dados do
  funcionário **e** do usuário. O teste cria funcionário → usuário; a exclusão
  remove usuário → funcionário. Perfil referencia perfil PADRÃO (não `_cr`).

#### Log – Auditoria ⚠️ provavelmente consulta/relatório (não cadastro CRUD)

Pode ignorar Log - Auditoria.

### 7. Característica do Bem

#### Definição ✅ (teste já existe: `test_definicao_bem`)

- **Nav:** Corporativo → Característica do Bem → "Definição"
- **Campos:**
  - `button[name='submitCancel']` (limpa antes)
  - `input[name='nmCaracteristica']` — Nome
  - `input[name='nrTamanho']` — Tamanho
  - `input[name='inTabelado'][value='S'|'N']` — Tabelado (radio)
- **Blueprint:** `caracteristica_bem_cr` (nome, tamanho, tabelado)

#### Manutenção ✅ inspecionado

- **Heading:** `Características do Bem - Manutenção`
- **Nav v4:** Corporativo → Característica do Bem → "Manutenção"
- **Campos:** `input[name='cdCaracteristica']` (lookup `lookup-cdCaracteristica` — referencia uma característica já criada na "Definição") + tabela de itens
- **Dependência:** exige característica já cadastrada (ver `caracteristica_bem_cr`).
- **Blueprint:** reusa `caracteristica_bem_cr` (não precisa dado novo próprio).

### 8. Agenda/Notificações

#### Grupo de Usuário ✅ inspecionado

- **Heading:** `Grupo de Usuários`
- **Campos:** `input[name='tipoAviso']` (**\*Tipo de aviso**, lookup) + tabela de usuários (checkbox enviar email / mostrar-logar)
- **Dependência:** exige um "Tipo de aviso" (valor de sistema) + usuários.
- **Blueprint:** _(a definir — depende de tipo de aviso; provavelmente fora da 1ª onda)_

Se fizer o teste, não o rode para não correr o risco de enviar emails em massa.

#### Envio de Comunicado ⚠️ não inspecionado — provável ação (envio), não CRUD

Ignore este teste.

#### Visualização ⚠️ não inspecionado — provável consulta

Ignore este teste.

### 9. Auxiliares

#### Assinaturas nos Relatórios ✅ inspecionado

- **Heading:** `Cadastrar assinaturas`
- **Campos:** `input[name='relatorio']` (**\*Relatório**, lookup) · `input[name='contexto']` (**\*Contexto**) · `radio[name='tipo']` (orgao/ug) · aba Assinaturas
- **Dependência:** exige um relatório + contexto (valores de sistema) + funcionários (assinantes).
- **Blueprint:** _(config — provavelmente fora da 1ª onda de testes CRUD)_

---

## Páginas NÃO inspecionadas (periféricas / provavelmente não-CRUD)

- **Material → Modelo de Importação** — ferramenta de importação
- **Segurança → Log – Auditoria** — consulta/relatório de auditoria
- **Agenda/Notificações → Envio de Comunicado** — ação de envio
- **Agenda/Notificações → Visualização** — consulta

> Essas quatro não têm o padrão de cadastro CRUD e não precisam de
> dados `_cr` na primeira onda de testes. Confirmar prioridade com o time.
