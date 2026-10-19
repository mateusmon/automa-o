# MCP Trello — gerenciamento de cards do board

Servidor MCP que expõe o board do Trello do projeto ao agente: listar/criar/mover
cards, ler e adicionar comentários, atualizar descrição, e gerenciar membros e
etiquetas — tudo via API REST do Trello.

## Por que existe

Automatiza o ciclo de trabalho por card do projeto:

1. O agente executa uma tarefa (ex.: criar testes do Corporativo).
2. Ao finalizar, usa `adicionar_comentario` para relatar tudo o que foi feito no card.
3. Usa `mover_card` para mover o card para a lista **"Análise"**.
4. Você lê o comentário e, se houver correções, escreve um novo comentário no card.
5. O agente usa `listar_comentarios` para ler sua resposta e retomar o trabalho.
6. Se aprovar, você move o card para **"Feito"** manualmente.

## Instalação

```bash
.venv\Scripts\python.exe -m pip install -r mcps/trello/requirements.txt
```

## Credenciais

As credenciais **não** ficam no código. São lidas de variáveis de ambiente
definidas no [`.mcp.json`](../../.mcp.json) da raiz (campo `env` do servidor
`trello`):

```json
"trello": {
  "command": ".venv/Scripts/python.exe",
  "args": ["mcps/trello/server.py"],
  "env": {
    "TRELLO_API_KEY": "<sua_chave>",
    "TRELLO_TOKEN": "<seu_token>"
  }
}
```

> O `.mcp.json` **não é versionado** (está no `svn:ignore`) porque contém
> credenciais. Cada máquina mantém o seu.

## Ferramentas

| Ferramenta | O que faz |
| --- | --- |
| `listar_boards()` | Lista boards acessíveis ao membro autenticado (ID + nome). |
| `listar_listas(board_id)` | Lista as listas do board (ID + nome). |
| `listar_cards(lista_id)` | Lista os cards de uma lista (ID, nome, etiquetas por nome, descrição). |
| `obter_detalhes_card(card_id)` | Lê descrição, anexos e checklists de um card, incluindo IDs e estados dos itens. |
| `obter_imagem_anexo(card_id, anexo_id)` | Baixa e retorna visualmente um anexo de imagem do card. |
| `definir_item_checklist(card_id, item_id, concluido)` | Marca ou desmarca um item de checklist. |
| `criar_card(lista_id, nome, descricao, etiquetas, membros)` | Cria um card (etiquetas/membros são listas de IDs, opcionais). |
| `mover_card(card_id, lista_id)` | Move um card para outra lista. |
| `listar_comentarios(card_id)` | Comentários do card em ordem cronológica (autor + data + texto). |
| `adicionar_comentario(card_id, texto)` | Adiciona um comentário. |
| `atualizar_descricao(card_id, descricao)` | Sobrescreve a descrição do card. |
| `adicionar_membro(card_id, membro_id)` | Adiciona um membro pelo ID. |
| `adicionar_etiqueta(card_id, etiqueta_id)` | Adiciona uma etiqueta pelo ID. |
| `remover_etiqueta(card_id, etiqueta_id)` | Remove a etiqueta do card (a etiqueta continua no board). |
| `listar_membros_board(board_id)` | Membros do board (ID + username + nome). |
| `listar_etiquetas_board(board_id)` | Etiquetas do board (ID + nome + cor). |

Para inspecionar um card sem listar a lista inteira, use `obter_detalhes_card` com o ID do
card. A saída inclui os IDs necessários para abrir uma imagem com `obter_imagem_anexo` ou
alterar um item com `definir_item_checklist`. A leitura de comentários continua disponível
em `listar_comentarios(card_id)`.

## Arquitetura

`httpx` (síncrono) chama a API REST (`https://api.trello.com/1/`). A autenticação
OAuth usa cabeçalho HTTP, para que `key`/`token` não apareçam na URL nem nos logs
de requisição. O servidor usa `FastMCP` do pacote `mcp`, no mesmo padrão do
`mcps/asi/server.py`.
