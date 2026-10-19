# Genesis executado pela Sentinela

Esta suíte migra gradualmente o provisionamento do Genesis legado para a
infraestrutura comum de testes. Durante a transição, `genesis/` continua sendo
o executor oficial e não deve ser removido ou alterado por estes testes.

## Contrato dos testes

- Função e Unidade de Medida são idempotentes: se a massa-base já existir, o
  teste a encontra; se estiver ausente, cria e consulta novamente.
- Perfis usa os Perfis do usuário Link autenticado como origem, ignora a chave
  `perfis` do blueprint e deriva uma cópia integral por Sistema com `prefixo_perfil`.
- Usuários usa `usuarios` e redescobre os Perfis do Link para derivar os vínculos
  com `prefixo_perfil`; ignora `usuarios[].sistemas` e `codigo_funcionario`, como
  o legado. Funcionários e Perfis precisam existir antes desta etapa.
- Cidade é uma pré-condição comum: o piloto apenas confirma sua existência com
  ou sem acento e não a cria nem a corrige.
- A migração preserva o contrato do Genesis legado: não abre registros existentes
  para validar campos adicionais, nem cria regras de integridade novas.
- A massa criada é persistente e nunca é excluída ao final.
- Dados vêm de `ContextoCliente`; chaves `_cr` continuam exclusivas dos CRUDs.
- Credenciais são escolhidas explicitamente com `dados_usuario("link")` ou
  `dados_usuario("teste")`.
- Navegação, consulta, seleção e preenchimento reutilizam os flows canônicos de
  `flows/`; não se importam módulos internos de `genesis/`.
- Cada novo teste deve entrar no catálogo da GUI e no bloco `tests/genesis` de
  `sentinela/ordem.yaml`, respeitando as dependências da massa.

Cidade, Função e Unidade de Medida são os modelos básicos. Perfis é o modelo avançado
para listas, leitura de grids, derivação de dados e cópia integral de registros.

Antes de expandir para novas entidades, seguir a transposição comportamental definida
em `tests/genesis/PLANO_SPRINTS.md`.

## Transposição de Usuários

Modelo de referência: implementação de Perfis da revisão SVN 65994 (Roniel).
O loop fica em `test_garantir_usuarios.py`; operações de tela específicas ficam em
`flows/genesis/usuario/`. Reutiliza a consulta corporativa de Usuário, a leitura dos
Perfis do Link e a derivação de nomes introduzidas em Perfis.

| Etapa | Legado e destino novo | Diferença |
|---|---|---|
| Dados | `usuarios` + `prefixo_perfil`, agora pelo `ContextoCliente` | Somente acesso tipado; ausência encerra sem criar |
| Papel | Link, via `dados_usuario("link")` | Somente infraestrutura de login/logout |
| Navegação | Perfil e Usuário com retorno booleano e reconhecimento da página já aberta | Wrappers Genesis usam o navegador universal principal |
| Existência | Nome exato, caixa ignorada, removendo `código - ` de cada célula | Nenhuma; verifica e cancela, sem anexar |
| Criação | Funcionário → senha → Sistemas/Perfis → Sistema padrão → confirmação | Nenhuma; último preenchimento confirma |
| Pós-criação | Consulta novamente e exige a mesma identidade | Nenhuma |

Os wrappers de navegação preservam menus ausentes e o rótulo `Usuários` da v3;
os flows corporativos atuais não expõem esse contrato. Nenhum flow compartilhado
ou arquivo do Genesis legado foi alterado.

A identidade de Usuário difere do helper de seleção exata: não anexa, não acusa
duplicidade e não aceita apenas o total do grid (nomes mascarados não correspondem).
A derivação de vínculos preserva Sistemas repetidos; não usa a validação de
unicidade de `selecionar_perfis_origem`, exclusiva da cópia de Perfis.

O vínculo mantém duas tentativas por lookup, cancela consultas sem registros e
reaproveita a linha para o próximo Sistema. Nenhum vínculo possível é erro.
O fallback de senha ocorre somente quando o campo indica recusa por política;
outros erros são propagados. Registros existentes não são corrigidos.

Validação QAS em 22/09/2026: TRE-PE v3 passou em 19,7s e CJF v4 em 34,5s.
Os cinco usuários já existiam em ambos: validada a execução idempotente; criação,
vínculos e fallback de senha ainda não foram exercitados ao vivo. PCDF interrompida
no login por orientação do usuário. Catálogo permite TRE-PE somente para Usuários.
Relatórios: `sentinela/reports/2026-09-22_14h43_trepe/` e
`sentinela/reports/2026-09-22_14h43_cjf/`.

## Correções da revisão crítica

- Perfis aceita ausência de `prefixo_perfil` e encerra antes do login; menu ausente
  encerra sem consultar, com logout. Usa a navegação booleana Genesis já existente.
- Funcionário e Perfil no cadastro de Usuários usam o auxiliar
  `flows/genesis/shared/preencher_lookup_flow.py`, que preserva as variações de nome,
  tentativas e esperas de `genesis/utils/espera.py`. `utils/waits.py` não foi alterado.
- Verificações locais: algoritmos de lookup/variações comparados por AST com o legado,
  cenários de prefixo/menu ausentes simulados e cinco testes coletados pelo Pytest.
  As execuções QAS acima são anteriores a essas correções; criação continua pendente
  de validação ao vivo.
