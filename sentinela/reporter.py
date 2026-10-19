"""
Gera o relatório HTML de um run da Sentinela.
"""
from pathlib import Path
from collections import Counter
from html import escape

from models import ResultadoTeste

_AMBIENTE = "QAS"

_COR = {
    "passou":          "#2d8a4e",
    "retentou_passou": "#7ab648",
    "falhou":          "#c0392b",
    "retentou_falhou": "#e07060",
    "skip":            "#888888",
}

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; background: #f5f5f5; color: #222; }
.header { background: #1a2535; color: #fff; padding: 24px 32px; }
.header h1 { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
.header .meta { color: #aab; font-size: 13px; margin-bottom: 12px; }
.badges { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 10px; }
.badge { padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: 600; background: #2a3a50; }
.badge.passou          { color: #2d8a4e; }
.badge.retentou_passou { color: #7ab648; }
.badge.falhou          { color: #e05545; }
.badge.retentou_falhou { color: #e07060; }
.badge.skip            { color: #aaa; }
.container { max-width: 1200px; margin: 24px auto; padding: 0 16px; }
.toolbar { margin-bottom: 14px; display: flex; gap: 8px; }
.btn-toggle { background: #dfe7f0; border: 1px solid #cdd6e2; color: #222; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; cursor: pointer; }
.btn-toggle:hover { background: #d4dfeb; }
table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 4px #0001; }
thead th { background: #e8edf3; padding: 10px 12px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: #555; border-bottom: 1px solid #d0d8e4; }
tbody tr.row-main { border-bottom: 1px solid #eee; }
tbody tr.row-main:hover { background: #f9fafb; }
td { padding: 9px 12px; vertical-align: middle; }
td.num { color: #888; width: 40px; }
td.status { width: 130px; font-weight: 600; white-space: nowrap; }
td.dur, td.tent { width: 90px; color: #555; }
td.acoes { width: 120px; }
td.acoes a { color: #3a7bd5; text-decoration: none; margin-right: 6px; font-size: 12px; }
td.acoes a:hover { text-decoration: underline; }
.nome-artefato { display: block; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #777; font-size: 10px; }
tr.row-detail td { padding: 0; background: #fafafa; border-bottom: 1px solid #eee; }
.detail-box { padding: 8px 16px 8px 48px; }
.erro-resumo { font-size: 13px; color: #c0392b; margin-bottom: 4px; }
details summary { cursor: pointer; color: #666; font-size: 12px; user-select: none; margin-top: 2px; }
details summary:hover { color: #333; }
pre.traceback { background: #1e1e1e; color: #d4d4d4; padding: 10px 14px; border-radius: 4px; font-size: 11px; overflow-x: auto; margin-top: 6px; white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto; }
img.screenshot { display: block; max-width: 100%; margin-top: 6px; border: 1px solid #444; border-radius: 4px; }
.log-inline { background: #f0f4f8; border: 1px solid #d0d8e4; border-radius: 4px; padding: 8px 12px; font-size: 11px; font-family: monospace; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; margin-top: 6px; color: #333; }
.grupo { background: #fff; border-radius: 6px; box-shadow: 0 1px 4px #0001; overflow: hidden; margin-bottom: 14px; }
.grupo > summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; margin: 0; padding: 11px 16px; background: #dfe7f0; font-size: 13px; color: #222; }
.grupo > summary::-webkit-details-marker { display: none; }
.grupo > summary::before { content: "▸"; color: #8894a5; font-size: 11px; }
.grupo[open] > summary::before { content: "▾"; }
.grupo[open] > summary { border-bottom: 1px solid #cdd6e2; }
.grupo > summary:hover { background: #d4dfeb; }
.grupo-rotulo { font-weight: 600; }
.grupo-contagem { color: #667; font-size: 12px; }
.grupo table { border-radius: 0; box-shadow: none; }
"""

_LABEL_STATUS = {
    "passou":          "✓ Passou",
    "retentou_passou": "✓~ Retentou/Passou",
    "falhou":          "✗ Falhou",
    "retentou_falhou": "✗~ Retentou/Falhou",
    "skip":            "⚠ Skip",
}

# Ordem dos blocos e se cada um abre por padrão.
_GRUPOS = (
    (("falhou", "retentou_falhou", "skip"), False),
    ("retentou_passou", False),
    ("passou",          False),
)


def _parsear_datetime(run_dir: Path) -> str:
    """Extrai e formata data/hora do nome do diretório (YYYY-MM-DD_HHhMM_cliente)."""
    nome = run_dir.name
    partes = nome.split("_")
    try:
        data = partes[0]          # YYYY-MM-DD
        hora = partes[1]          # HHhMM
        ano, mes, dia = data.split("-")
        hh, mm = hora.split("h")
        return f"{dia}/{mes}/{ano} {hh}:{mm}"
    except Exception:
        return nome


def _duracao_fmt(r: ResultadoTeste) -> str:
    acumulada = r.duracao_acumulada or r.duracao
    if acumulada > r.duracao:
        return f"{r.duracao:.1f}s <span style='color:#999'>(total {acumulada:.1f}s)</span>"
    return f"{r.duracao:.1f}s"


def _tentativas_fmt(r: ResultadoTeste) -> str:
    if r.status == "skip":
        return "—"
    return f"{r.tentativa}/{r.max_tentativas}"


def _renderizar_acoes(r: ResultadoTeste) -> str:
    if r.status == "skip":
        return "—"
    traces = [
        (item.tentativa, path)
        for item in (r.tentativas or [r])
        for path in item.trace_paths
    ]
    if not traces:
        return "—"

    links = []
    for tentativa, path in traces:
        nome = escape(path.name)
        links.append(
            f'<a href="https://trace.playwright.dev" target="_blank" '
            f'title="Arraste {nome} para o visualizador">[trace T{tentativa}]</a>'
            f'<span class="nome-artefato">{nome}</span>'
        )
    return " ".join(links)


def _renderizar_screenshot(r: ResultadoTeste) -> str:
    """
    Renderiza o screenshot da falha dentro de um <details>, carregado sob clique.

    A imagem fica no mesmo diretório do HTML, então basta um src relativo — nada
    de base64, que incharia o relatório. O <details> fechado somado ao
    loading="lazy" evita que um run com dezenas de falhas baixe megabytes de PNG
    de uma vez só na abertura.
    """
    if r.screenshot_path is None:
        return ""

    nome = escape(r.screenshot_path.name)

    return (
        '<details>'
        '<summary>Exibir screenshot da falha</summary>'
        f'<a href="{nome}" target="_blank">'
        f'<img class="screenshot" src="{nome}" loading="lazy" alt="Screenshot da falha">'
        '</a>'
        '</details>'
    )


def _renderizar_historico_tentativas(r: ResultadoTeste) -> str:
    """Exibe status, erro e artefatos de cada tentativa executada."""
    if len(r.tentativas) <= 1:
        return ""

    itens = []
    for tentativa in r.tentativas:
        resumo = f" — {escape(tentativa.erro_resumo)}" if tentativa.erro_resumo else ""
        artefatos = []
        for trace_path in tentativa.trace_paths:
            artefatos.append(f"trace: {escape(trace_path.name)}")
        if tentativa.screenshot_path is not None:
            artefatos.append(f"screenshot: {escape(tentativa.screenshot_path.name)}")
        sufixo = f" ({'; '.join(artefatos)})" if artefatos else ""
        itens.append(
            f"<li>Tentativa {tentativa.tentativa}: "
            f"{escape(_LABEL_STATUS.get(tentativa.status, tentativa.status))}{resumo}{sufixo}</li>"
        )

    return (
        '<details class="tentativas-detalhe">'
        '<summary>Exibir histórico das tentativas</summary>'
        f'<ul>{"".join(itens)}</ul>'
        '</details>'
    )


def _renderizar_screenshots_tentativas(r: ResultadoTeste) -> str:
    """Renderiza todos os screenshots preservados, sem repetir o resultado principal."""
    tentativas = r.tentativas or [r]
    return "".join(_renderizar_screenshot(item) for item in tentativas)


def _renderizar_linhas(resultados: list[ResultadoTeste], status_grupo: tuple | str = None) -> str:
    """
    Linhas de um único status ou grupo de status.

    O índice e o rótulo de duplicata são contados sobre a lista completa, não
    sobre o grupo, é o que mantém "#47" sendo a repetição 47 e apontando para
    os arquivos `_r47` do run.
    """
    contagem_nomes: Counter = Counter(r.nome for r in resultados)
    ocorrencias: Counter = Counter()
    linhas = []

    status_set = None
    if status_grupo is not None:
        status_set = {status_grupo} if isinstance(status_grupo, str) else set(status_grupo)

    for idx, r in enumerate(resultados):
        ocorrencias[r.nome] += 1
        if status_set is not None and r.status not in status_set:
            continue

        duplicata = contagem_nomes[r.nome] > 1
        label_nome = f"{r.nome} [{ocorrencias[r.nome]}/{contagem_nomes[r.nome]}]" if duplicata else r.nome

        cor = _COR.get(r.status, "#888")
        status_label = _LABEL_STATUS.get(r.status, r.status)
        acoes_html = _renderizar_acoes(r)

        linhas.append(f"""
  <tr class="row-main">
    <td class="num">{idx + 1}</td>
    <td>{escape(label_nome)}</td>
    <td class="status" style="color:{cor}">{escape(status_label)}</td>
    <td class="dur">{_duracao_fmt(r)}</td>
    <td class="tent">{_tentativas_fmt(r)}</td>
    <td class="acoes">{acoes_html}</td>
  </tr>""")

        saida_escaped = escape(r.saida or "")
        if saida_escaped.strip():
            erro_html = f'<div class="erro-resumo">{escape(r.erro_resumo)}</div>' if r.erro_resumo else ""
            linhas.append(f"""
  <tr class="row-detail">
    <td colspan="6">
      <div class="detail-box">
        {erro_html}
        {_renderizar_historico_tentativas(r)}
        {_renderizar_screenshots_tentativas(r)}
        <details>
          <summary>Exibir saída completa</summary>
          <pre class="traceback">{saida_escaped}</pre>
        </details>
      </div>
    </td>
  </tr>""")

    return "\n".join(linhas)


def _renderizar_grupos(resultados: list[ResultadoTeste]) -> str:
    """Um bloco recolhível por status; fechado, o browser não renderiza o conteúdo."""
    blocos = []

    for status, aberto in _GRUPOS:
        status_set = {status} if isinstance(status, str) else set(status)
        qtd = sum(1 for r in resultados if r.status in status_set)
        if not qtd:
            continue

        if isinstance(status, tuple):
            cor = "#c0392b"
            rotulo = "Falhas / Skips"
        else:
            cor = _COR.get(status, "#888")
            rotulo = escape(_LABEL_STATUS.get(status, status))

        substantivo = "teste" if qtd == 1 else "testes"

        blocos.append(f"""
<details class="grupo"{" open" if aberto else ""}>
  <summary>
    <span class="grupo-rotulo" style="color:{cor}">{rotulo}</span>
    <span class="grupo-contagem">{qtd} {substantivo}</span>
  </summary>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Teste</th>
        <th>Status</th>
        <th>Duração</th>
        <th>Tentativas</th>
        <th>Ações</th>
      </tr>
    </thead>
    <tbody>
{_renderizar_linhas(resultados, status)}
    </tbody>
  </table>
</details>""")

    qtd_total = len(resultados)
    substantivo_total = "teste" if qtd_total == 1 else "testes"
    blocos.append(f"""
<details class="grupo">
  <summary>
    <span class="grupo-rotulo" style="color:#222">Todos os testes (Ordem de Execução)</span>
    <span class="grupo-contagem">{qtd_total} {substantivo_total}</span>
  </summary>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Teste</th>
        <th>Status</th>
        <th>Duração</th>
        <th>Tentativas</th>
        <th>Ações</th>
      </tr>
    </thead>
    <tbody>
{_renderizar_linhas(resultados)}
    </tbody>
  </table>
</details>""")

    return "\n".join(blocos)


_SUCESSO = ("passou", "retentou_passou")


def _media_e_pct(execucoes: list[ResultadoTeste]) -> tuple[float | None, float]:
    """Média de duração das execuções bem-sucedidas e % de sucesso sobre o total."""
    sucessos = [r for r in execucoes if r.status in _SUCESSO]
    pct = (len(sucessos) / len(execucoes) * 100) if execucoes else 0.0
    media = (sum(r.duracao for r in sucessos) / len(sucessos)) if sucessos else None
    return media, pct


def _fmt_media(media: float | None) -> str:
    return f"{media:.1f}s" if media is not None else "—"


def imprimir_relatorio_consolidado(
    resultados_por_cliente: dict[str, list[ResultadoTeste]],
    labels: dict[str, str],
) -> None:
    """
    Imprime no terminal um relatório consolidado por cliente/teste e por teste
    (agregado entre todos os clientes). Chamado ao final da execução quando
    `--relatorio` é passado à Sentinela.
    """
    if not any(resultados_por_cliente.values()):
        return

    print()
    print("  " + "=" * 56)
    print("  Sentinela — Relatório Consolidado")
    print("  " + "=" * 56)
    print()

    print("  Por cliente / teste")
    print("  " + "-" * 56)
    for cliente_id, execucoes in resultados_por_cliente.items():
        if not execucoes:
            continue
        label = labels.get(cliente_id, cliente_id.upper())
        por_teste: dict[str, list[ResultadoTeste]] = {}
        for r in execucoes:
            por_teste.setdefault(r.nome, []).append(r)
        for nome, execs in por_teste.items():
            media, pct = _media_e_pct(execs)
            sucessos = sum(1 for r in execs if r.status in _SUCESSO)
            print(f"  {label}/{nome}: média {_fmt_media(media)} | {pct:.1f}% sucesso ({sucessos}/{len(execs)})")
    print()

    por_teste_global: dict[str, list[ResultadoTeste]] = {}
    for execucoes in resultados_por_cliente.values():
        for r in execucoes:
            por_teste_global.setdefault(r.nome, []).append(r)

    print("  Por teste (todos os clientes)")
    print("  " + "-" * 56)
    for nome, execs in por_teste_global.items():
        media, pct = _media_e_pct(execs)
        sucessos = sum(1 for r in execs if r.status in _SUCESSO)
        print(f"  {nome}: média {_fmt_media(media)} | {pct:.1f}% sucesso ({sucessos}/{len(execs)})")
    print()


def gerar_relatorio(
    run_dir: Path,
    resultados: list[ResultadoTeste],
    cliente_id: str,
    label: str,
    duracao_total: float,
) -> Path:
    datetime_str = _parsear_datetime(run_dir)
    ambiente = _AMBIENTE

    minutos = int(duracao_total // 60)
    segundos = int(duracao_total % 60)
    duracao_str = f"{minutos}m {segundos}s" if minutos else f"{segundos}s"

    passaram        = sum(1 for r in resultados if r.status == "passou")
    ret_passou      = sum(1 for r in resultados if r.status == "retentou_passou")
    falharam        = sum(1 for r in resultados if r.status == "falhou")
    ret_falhou      = sum(1 for r in resultados if r.status == "retentou_falhou")
    skips           = sum(1 for r in resultados if r.status == "skip")

    grupos_html = _renderizar_grupos(resultados)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sentinela — {escape(label)} — {escape(datetime_str)}</title>
<style>
{_CSS}
</style>
</head>
<body>

<div class="header">
  <h1>Sentinela — Run de {escape(datetime_str)}</h1>
  <div class="meta">Cliente: <strong>{escape(label)}</strong> &nbsp;|&nbsp; Ambiente: <strong>{escape(ambiente)}</strong> &nbsp;|&nbsp; Duração total: <strong>{escape(duracao_str)}</strong></div>
  <div class="badges">
    <span class="badge passou">✓ {passaram} passaram</span>
    <span class="badge retentou_passou">✓~ {ret_passou} retentaram e passaram</span>
    <span class="badge falhou">✗ {falharam} falharam</span>
    <span class="badge retentou_falhou">✗~ {ret_falhou} retentaram e falharam</span>
    <span class="badge skip">⚠ {skips} skip</span>
  </div>
</div>

<div class="container">
{grupos_html}
</div>
</body>
</html>
"""

    report_path = run_dir / "report.html"
    report_path.write_text(html, encoding="utf-8", errors="replace")
    return report_path
