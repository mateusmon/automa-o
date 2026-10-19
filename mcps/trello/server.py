"""
Servidor MCP do Trello — gerencia o board do projeto (listas, cards, comentários,
membros e etiquetas) via API REST do Trello.

Credenciais vêm de variáveis de ambiente (definidas no `.mcp.json`, campo `env`):
  TRELLO_API_KEY, TRELLO_TOKEN
— nunca hardcoded aqui.

Fluxo de trabalho típico:
  1. O agente executa uma tarefa (ex.: criar testes do Corporativo).
  2. Ao finalizar, usa `adicionar_comentario` para relatar tudo no card.
  3. Usa `mover_card` para levar o card à lista "Análise".
  4. O revisor lê o comentário e, se precisar, escreve um novo comentário.
  5. O agente usa `listar_comentarios` para ler a resposta e retomar.
  6. Aprovado → o revisor move para "Feito" manualmente.

Registro no Claude Code: ver mcps/trello/README.md (ou o `.mcp.json` na raiz).
"""
from __future__ import annotations

import os
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP, Image

API_KEY = os.environ["TRELLO_API_KEY"]
TOKEN = os.environ["TRELLO_TOKEN"]
BASE = "https://api.trello.com/1"
MAX_ATTACHMENT_BYTES = 12 * 1024 * 1024

mcp = FastMCP("trello")


# ---------------------------------------------------------------------------
# Helper — todas as chamadas à API REST do Trello passam por aqui.
# A autenticação (key/token) segue no cabeçalho OAuth, nunca na URL/log.
# ---------------------------------------------------------------------------
def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": (
            f'OAuth oauth_consumer_key="{API_KEY}", oauth_token="{TOKEN}"'
        )
    }


def _req(method: str, path: str, params: dict | None = None):
    p: dict = {}
    if params:
        p.update({k: v for k, v in params.items() if v is not None})
    resp = httpx.request(
        method,
        f"{BASE}{path}",
        params=p,
        headers=_auth_headers(),
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json() if resp.text.strip() else None


# ---------------------------------------------------------------------------
# Ferramentas MCP
# ---------------------------------------------------------------------------
@mcp.tool()
def listar_boards() -> str:
    """Lista os boards acessíveis ao membro autenticado, com ID e nome."""
    boards = _req("GET", "/members/me/boards", {"fields": "id,name"})
    if not boards:
        return "(nenhum board encontrado)"
    return "\n".join(f"{board['id']}  {board['name']}" for board in boards)


@mcp.tool()
def listar_listas(board_id: str) -> str:
    """Lista todas as listas de um board com seus IDs e nomes."""
    listas = _req("GET", f"/boards/{board_id}/lists", {"fields": "id,name"})
    if not listas:
        return "(nenhuma lista encontrada)"
    return "\n".join(f"{l['id']}  {l['name']}" for l in listas)


@mcp.tool()
def listar_cards(lista_id: str) -> str:
    """
    Lista os cards de uma lista com ID, nome, etiquetas e descrição.

    As etiquetas saem por NOME, entre colchetes, logo após o nome do card —
    cards sem etiqueta aparecem como `[sem etiqueta]`. Para agir sobre uma
    etiqueta (adicionar/remover) é preciso o ID dela: use `listar_etiquetas_board`.
    """
    cards = _req("GET", f"/lists/{lista_id}/cards", {"fields": "id,name,desc,labels"})
    if not cards:
        return "(nenhum card encontrado)"
    partes = []
    for c in cards:
        nomes = [l.get("name") or "(sem nome)" for l in (c.get("labels") or [])]
        etiquetas = ", ".join(nomes) if nomes else "sem etiqueta"
        desc = (c.get("desc") or "").strip()
        linha = f"{c['id']}  {c['name']}  [{etiquetas}]"
        if desc:
            linha += f"\n    {desc}"
        partes.append(linha)
    return "\n".join(partes)


@mcp.tool()
def buscar_card_por_numero(board_nome: str, numero: str) -> str:
    """Busca um card pelo número curto nativo do Trello (`idShort`) no board."""
    numero = numero.strip()
    if not numero.isdecimal() or int(numero) < 1:
        return "Informe um número de card inteiro positivo."
    numero = str(int(numero))

    boards = _req("GET", "/members/me/boards", {"fields": "id,name"}) or []
    correspondentes = [
        board for board in boards
        if board.get("name", "").casefold() == board_nome.strip().casefold()
    ]
    if not correspondentes:
        nomes = ", ".join(sorted(board.get("name", "") for board in boards))
        return f'Board "{board_nome}" não encontrado. Boards disponíveis: {nomes or "(nenhum)"}'
    if len(correspondentes) > 1:
        ids = ", ".join(board["id"] for board in correspondentes)
        return f'Nome de board ambíguo para "{board_nome}" (IDs: {ids}).'

    board = correspondentes[0]
    cards = _req(
        "GET",
        f"/boards/{board['id']}/cards/all",
        {"fields": "id,name,idShort,idList,shortUrl", "filter": "all"},
    ) or []
    card = next((card for card in cards if str(card.get("idShort")) == numero), None)
    if card is None:
        return f'Nenhum card com número "{numero}" encontrado no board "{board_nome}".'

    listas = _req("GET", f"/boards/{board['id']}/lists", {"fields": "id,name"}) or []
    nomes_listas = {lista["id"]: lista.get("name", "?") for lista in listas}
    return (
        f"{card.get('name', '(sem título)')} | numero={numero} "
        f"| idShort={card['idShort']} "
        f"| lista={nomes_listas.get(card.get('idList'), '?')} "
        f"| id={card['id']} | {card.get('shortUrl', '')}"
    )


@mcp.tool()
def obter_detalhes_card(card_id: str) -> str:
    """Lê um card pelo ID, incluindo descrição, anexos e itens das checklists."""
    card = _req(
        "GET",
        f"/cards/{card_id}",
        {
            "fields": "id,name,desc,idList",
            "attachments": "true",
            "checklists": "all",
        },
    )
    if not card:
        return f"Card {card_id} não encontrado."

    linhas = [f"{card.get('name', '(sem título)')} — {card.get('id', card_id)}"]
    descricao = (card.get("desc") or "").strip()
    linhas.append("Descrição:\n" + (descricao or "(vazia)"))

    anexos = card.get("attachments") or []
    linhas.append("Anexos:")
    if anexos:
        for anexo in anexos:
            linhas.append(
                "- {name} | id={id} | tipo={mime} | bytes={bytes}".format(
                    name=anexo.get("name") or "(sem nome)",
                    id=anexo.get("id", "?"),
                    mime=anexo.get("mimeType") or "desconhecido",
                    bytes=anexo.get("bytes", "?"),
                )
            )
    else:
        linhas.append("(nenhum)")

    checklists = card.get("checklists") or []
    linhas.append("Checklists:")
    if checklists:
        for checklist in checklists:
            linhas.append(f"- {checklist.get('name', '(sem título)')} | id={checklist.get('id', '?')}")
            for item in checklist.get("checkItems") or []:
                estado = "feito" if item.get("state") == "complete" else "pendente"
                linhas.append(
                    f"  - [{estado}] {item.get('name', '(sem texto)')} | id={item.get('id', '?')}"
                )
    else:
        linhas.append("(nenhuma)")
    return "\n".join(linhas)


@mcp.tool()
def obter_imagem_anexo(card_id: str, anexo_id: str) -> Image:
    """Retorna a imagem anexada ao card como imagem visível; aceita somente anexos de imagem."""
    anexo = _req("GET", f"/cards/{card_id}/attachments/{anexo_id}")
    if not anexo:
        raise ValueError(f"Anexo {anexo_id} não encontrado no card {card_id}.")

    mime_type = (anexo.get("mimeType") or "").lower()
    nome = anexo.get("name") or ""
    if not mime_type.startswith("image/"):
        raise ValueError(
            f"O anexo {anexo_id} não é identificado como imagem "
            f"(tipo: {mime_type or 'desconhecido'})."
        )

    nome_url = quote(nome, safe="") or "attachment"
    url = f"{BASE}/cards/{card_id}/attachments/{anexo_id}/download/{nome_url}"
    with httpx.stream(
        "GET",
        url,
        headers=_auth_headers(),
        follow_redirects=True,
        timeout=30.0,
    ) as resposta:
        if resposta.is_error:
            raise RuntimeError(
                f"Falha ao baixar anexo do Trello (HTTP {resposta.status_code})."
            )
        tamanho = resposta.headers.get("content-length")
        if tamanho and int(tamanho) > MAX_ATTACHMENT_BYTES:
            raise ValueError(
                f"A imagem excede o limite de {MAX_ATTACHMENT_BYTES // (1024 * 1024)} MB "
                "para retorno pelo MCP."
            )
        dados = bytearray()
        for bloco in resposta.iter_bytes():
            dados.extend(bloco)
            if len(dados) > MAX_ATTACHMENT_BYTES:
                raise ValueError(
                    f"A imagem excede o limite de {MAX_ATTACHMENT_BYTES // (1024 * 1024)} MB "
                    "para retorno pelo MCP."
                )
        conteudo = bytes(dados)
    if not conteudo:
        raise ValueError(f"O anexo {anexo_id} não retornou conteúdo.")

    formato = mime_type.split("/", 1)[1]
    return Image(data=conteudo, format=formato)


@mcp.tool()
def definir_item_checklist(
    card_id: str,
    item_id: str,
    concluido: bool,
) -> str:
    """Marca ou desmarca um item de checklist do card pelo ID do item."""
    estado = "complete" if concluido else "incomplete"
    _req("PUT", f"/cards/{card_id}/checkItem/{item_id}", {"state": estado})
    verbo = "marcado como concluído" if concluido else "marcado como pendente"
    return f"Item {item_id} {verbo} no card {card_id}."


@mcp.tool()
def criar_card(
    lista_id: str,
    nome: str,
    descricao: str = "",
    etiquetas: list[str] | None = None,
    membros: list[str] | None = None,
) -> str:
    """
    Cria um card na lista especificada.

    `etiquetas` e `membros` são listas de IDs (do board) — opcionais.
    """
    params: dict = {"idList": lista_id, "name": nome, "desc": descricao}
    if etiquetas:
        params["idLabels"] = ",".join(etiquetas)
    if membros:
        params["idMembers"] = ",".join(membros)
    card = _req("POST", "/cards", params)
    if not card:
        return "Falha ao criar card (resposta vazia da API)."
    return f"Card criado: {card['id']}  {card['name']}"


@mcp.tool()
def mover_card(card_id: str, lista_id: str) -> str:
    """Move um card para outra lista."""
    _req("PUT", f"/cards/{card_id}", {"idList": lista_id})
    return f"Card {card_id} movido para a lista {lista_id}."


@mcp.tool()
def listar_comentarios(card_id: str) -> str:
    """Lista os comentários do card em ordem cronológica (autor + data + texto)."""
    acoes = _req(
        "GET",
        f"/cards/{card_id}/actions",
        {"filter": "commentCard", "limit": "1000"},
    )
    if not acoes:
        return "(nenhum comentário)"
    acoes = list(reversed(acoes))  # a API devolve do mais novo para o mais antigo
    partes = []
    for a in acoes:
        autor_obj = a.get("memberCreator") or {}
        autor = autor_obj.get("fullName") or autor_obj.get("username") or "?"
        data = a.get("date", "")
        texto = (a.get("data") or {}).get("text", "")
        partes.append(f"[{data}] {autor}:\n{texto}")
    return "\n\n".join(partes)


@mcp.tool()
def adicionar_comentario(card_id: str, texto: str) -> str:
    """Adiciona um comentário ao card."""
    _req("POST", f"/cards/{card_id}/actions/comments", {"text": texto})
    return f"Comentário adicionado ao card {card_id}."


@mcp.tool()
def atualizar_descricao(card_id: str, descricao: str) -> str:
    """Atualiza (sobrescreve) a descrição do card."""
    _req("PUT", f"/cards/{card_id}", {"desc": descricao})
    return f"Descrição do card {card_id} atualizada."


@mcp.tool()
def adicionar_membro(card_id: str, membro_id: str) -> str:
    """Adiciona um membro ao card pelo ID do membro no Trello."""
    _req("POST", f"/cards/{card_id}/idMembers", {"value": membro_id})
    return f"Membro {membro_id} adicionado ao card {card_id}."


@mcp.tool()
def adicionar_etiqueta(card_id: str, etiqueta_id: str) -> str:
    """Adiciona uma etiqueta ao card pelo ID da etiqueta."""
    _req("POST", f"/cards/{card_id}/idLabels", {"value": etiqueta_id})
    return f"Etiqueta {etiqueta_id} adicionada ao card {card_id}."


@mcp.tool()
def remover_etiqueta(card_id: str, etiqueta_id: str) -> str:
    """
    Remove uma etiqueta do card pelo ID da etiqueta.

    Remove apenas o vínculo card↔etiqueta — a etiqueta continua existindo no board.
    Remover uma etiqueta que o card não tem é no-op (a API não reclama).
    """
    _req("DELETE", f"/cards/{card_id}/idLabels/{etiqueta_id}")
    return f"Etiqueta {etiqueta_id} removida do card {card_id}."


@mcp.tool()
def listar_membros_board(board_id: str) -> str:
    """Lista membros do board com ID e nome de usuário."""
    membros = _req("GET", f"/boards/{board_id}/members", {"fields": "id,username,fullName"})
    if not membros:
        return "(nenhum membro encontrado)"
    return "\n".join(
        f"{m['id']}  {m.get('username', '')}  ({m.get('fullName', '')})" for m in membros
    )


@mcp.tool()
def listar_etiquetas_board(board_id: str) -> str:
    """Lista etiquetas do board com ID, nome e cor."""
    etiquetas = _req("GET", f"/boards/{board_id}/labels", {"fields": "id,name,color"})
    if not etiquetas:
        return "(nenhuma etiqueta encontrada)"
    return "\n".join(
        f"{e['id']}  {e.get('name') or '(sem nome)'}  [{e.get('color') or '-'}]"
        for e in etiquetas
    )


if __name__ == "__main__":
    mcp.run()
