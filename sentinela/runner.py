"""
Orquestra a execução de todos os testes para um cliente.
"""

import sys
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

import storage
import yaml
from catalog_reader import testes_disponiveis_para, todos_os_testes_do_catalogo
from executor import executar_teste
from models import ResultadoTeste
from ordem_reader import (
    achatar_modulos,
    entradas_globais,
    ler_modulos,
    modulos_disponiveis,
    paths_invalidos,
    selecionar_modulos,
)
from reporter import gerar_relatorio

_sentinela_dir = Path(__file__).resolve().parent
_raiz = _sentinela_dir.parent

_SIMBOLO = {
    "passou": "✓",
    "retentou_passou": "✓~",
    "falhou": "✗",
    "retentou_falhou": "✗~",
    "skip": "⚠",
}

_PADROES_TRANSIENTES = [
    ("TimeoutError", "page.goto"),
    ("TimeoutError", "wait_for_load_state"),
    ("net::ERR_", None),
    ("browser has been closed", None),
]
_CONTROL_EVENT_PREFIX = "ASI_GUI_STATE:"


def _publicar_estado(execution_id: str, state: str) -> None:
    """Emite um marcador curto que a GUI associa ao registro proprietário."""
    print(f"{_CONTROL_EVENT_PREFIX}{execution_id}:{state}", flush=True)


def _aguardar_pausa(run_dir: Path, execution_id: str | None) -> None:
    """Consome pausa somente na fronteira entre itens da jornada/repetição."""
    if execution_id is None:
        return
    command = storage.ler_comando_controle(run_dir, execution_id)
    if command == "stop":
        raise KeyboardInterrupt
    if command != "pause":
        return

    _publicar_estado(execution_id, "PAUSED_BETWEEN_TESTS")
    while True:
        command = storage.ler_comando_controle(run_dir, execution_id)
        if command == "stop":
            raise KeyboardInterrupt
        if command == "resume":
            _publicar_estado(execution_id, "RUNNING")
            return
        time.sleep(0.2)


def _eh_erro_transiente(erro_resumo: str) -> bool:
    """Classifica somente a exceção final, sem ler código-fonte impresso no traceback."""
    texto = erro_resumo.casefold()
    for primario, secundario in _PADROES_TRANSIENTES:
        if primario.casefold() in texto:
            if secundario is None or secundario.casefold() in texto:
                return True
    return False


def _fmt_duracao(segundos_totais: float) -> str:
    minutos = int(segundos_totais // 60)
    segundos = int(segundos_totais % 60)
    return f"{minutos}m {segundos}s" if minutos else f"{segundos}s"


def _nome_run_para_ocorrencia(path_teste: str, ocorrencia: int, total: int) -> str:
    """Gera nome único de artefato quando o mesmo path aparece mais de uma vez na ordem."""
    nome_base = Path(path_teste).stem
    return f"{nome_base}_r{ocorrencia}" if total > 1 else nome_base


_OCORRENCIAS = ("falhou", "retentou_falhou", "skip")
_FALHAS = ("falhou", "retentou_falhou")


def _imprimir_ocorrencias(resultados: list[ResultadoTeste]) -> None:
    total = len(resultados)
    ocorrencias = [
        (i, r) for i, r in enumerate(resultados, 1) if r.status in _OCORRENCIAS
    ]
    if not ocorrencias:
        return

    print()
    print("  Falhas e skips " + "-" * 40)
    for i, r in ocorrencias:
        simbolo = _SIMBOLO.get(r.status, "?")
        print(f"  [{i}/{total}] {simbolo:<2}  {r.nome}")

        if r.status == "skip":
            print("      não executado (skip)")
        else:
            rotulo = "tentativa" if r.tentativa == 1 else "tentativas"
            acumulada = r.duracao_acumulada or r.duracao
            print(
                f"      {r.tentativa} {rotulo} — {_fmt_duracao(acumulada)} (última: {r.duracao:.1f}s)"
            )

        if r.erro_resumo:
            print(f"      {r.erro_resumo}")
        print(f"      {r.path}")
    print()


def _imprimir_contagens(resultados: list[ResultadoTeste]) -> None:
    """Linhas de contagem por status do resumo — compartilhado pelos dois modos."""
    passaram = sum(1 for r in resultados if r.status == "passou")
    retentou_passou = sum(1 for r in resultados if r.status == "retentou_passou")
    falharam = sum(1 for r in resultados if r.status == "falhou")
    retentou_falhou = sum(1 for r in resultados if r.status == "retentou_falhou")
    skips = sum(1 for r in resultados if r.status == "skip")

    print(f"  ✓   {passaram} passaram")
    print(f"  ✓~  {retentou_passou} retentaram e passaram")
    print(f"  ✗   {falharam} falharam")
    print(f"  ✗~  {retentou_falhou} retentaram e falharam")
    print(f"  ⚠   {skips} skip")


def _executar_com_tentativas(
    path_teste: str,
    cliente_id: str,
    max_tentativas: int,
    headless: bool,
    run_dir: Path,
    nome_run: str,
    prefixo: str,
    nome_exibicao: str | None = None,
    pausa: bool = False,
    ocorrencia: int = 1,
    execution_id: str | None = None,
) -> ResultadoTeste:
    """
    Executa um teste com retry de erro transiente, salvando log e artefatos.

    `nome_run` nomeia os arquivos do run (log, trace, screenshot), no modo
    teste único vem com sufixo _rN. `nome_exibicao` é o que aparece no
    terminal; por padrão, o mesmo que `nome_run`. `prefixo` é o rótulo de
    progresso já formatado, ex: "[3/40]" ou "[47/100]".
    """
    nome_exibicao = nome_exibicao or nome_run

    print(f"  {prefixo} Executando: {nome_exibicao} ...", flush=True)

    resultado = None
    tentativas_executadas: list[ResultadoTeste] = []
    houve_transiente = False
    duracao_acumulada = 0.0

    for tentativa in range(1, max_tentativas + 1):
        resultado = executar_teste(
            path_teste=path_teste,
            cliente_id=cliente_id,
            tentativa=tentativa,
            max_tentativas=max_tentativas,
            headless=headless,
            pausa=pausa,
            ocorrencia=ocorrencia,
            execution_id=execution_id,
        )
        duracao_acumulada += resultado.duracao

        storage.salvar_log(run_dir, nome_run, tentativa, resultado.saida)
        tentativas_executadas.append(resultado)

        if resultado.trace_paths:
            resultado.trace_paths = [
                destino
                for origem in resultado.trace_paths
                if (destino := storage.mover_trace(run_dir, nome_run, origem, tentativa))
            ]
        if resultado.status == "falhou":
            if resultado.screenshot_path:
                resultado.screenshot_path = storage.mover_screenshot(
                    run_dir, nome_run, resultado.screenshot_path, tentativa
                )

        if resultado.status in ("passou", "skip"):
            break

        if _eh_erro_transiente(resultado.erro_resumo) and tentativa < max_tentativas:
            houve_transiente = True
            print(
                f"  {prefixo} ↻ Tentativa {tentativa}/{max_tentativas} — erro transiente, retentando em 10s...",
                flush=True,
            )
            time.sleep(10)
        else:
            break

    assert resultado is not None
    resultado_consolidado = replace(resultado)
    resultado_consolidado.duracao_acumulada = duracao_acumulada
    resultado_consolidado.tentativas = tentativas_executadas

    falhas_anteriores = [
        item for item in tentativas_executadas if item.status == "falhou"
    ]

    if resultado.status == "skip" and falhas_anteriores:
        resultado_consolidado = replace(falhas_anteriores[-1])
        resultado_consolidado.status = "retentou_falhou"
        resultado_consolidado.tentativa = resultado.tentativa
        resultado_consolidado.duracao_acumulada = duracao_acumulada
        resultado_consolidado.tentativas = tentativas_executadas
    elif resultado.status == "passou" and houve_transiente:
        resultado_consolidado.status = "retentou_passou"
    elif resultado.status == "falhou" and houve_transiente:
        resultado_consolidado.status = "retentou_falhou"

    resultado = resultado_consolidado

    simbolo = _SIMBOLO.get(resultado.status, "?")
    duracao_fmt = f"{resultado.duracao:.1f}s"
    if resultado.status == "skip":
        print(f"  {prefixo} {simbolo} {nome_exibicao}  (skip)")
    elif resultado.status in _FALHAS and resultado.erro_resumo:
        print(
            f"  {prefixo} {simbolo} {nome_exibicao}  ({duracao_fmt}) — {resultado.erro_resumo}"
        )
    else:
        print(f"  {prefixo} {simbolo} {nome_exibicao}  ({duracao_fmt})")

    return resultado


def executar_para_cliente(
    cliente_id: str,
    max_tentativas: int,
    ttl_dias: int,
    modulo: str | None = None,
    headless: bool = False,
    pausa: bool = False,
    execution_id: str | None = None,
) -> list[ResultadoTeste]:
    storage.limpar_runs_antigos(ttl_dias)

    execution_id = storage.validar_execution_id(execution_id) if execution_id else None
    run_dir = storage.criar_diretorio_run(cliente_id, execution_id, modulo=modulo)
    if execution_id:
        print(f"Execution ID: {execution_id}", flush=True)
        print(f"Run salvo em [{execution_id}]: {run_dir.relative_to(_raiz)}/", flush=True)

    configs_path = _raiz / "configs" / "configs.yaml"
    with open(configs_path, encoding="utf-8") as f:
        configs = yaml.safe_load(f)
    clientes = configs.get("clientes", {})
    if cliente_id not in clientes:
        print(
            f"[Sentinela] Erro: cliente '{cliente_id}' não encontrado em configs/configs.yaml."
        )
        sys.exit(1)
    label = clientes[cliente_id].get("label", cliente_id.upper())

    modulos = ler_modulos()
    blocos_selecionados = selecionar_modulos(modulos, modulo)
    if modulo is not None and not blocos_selecionados:
        print(f"\n[Sentinela] Erro: nenhum módulo encontrado para '{modulo}'.")
        print("  Módulos disponíveis na ordem.yaml:")
        for modulo_disponivel in modulos_disponiveis(modulos):
            print(f"    {modulo_disponivel}")
        sys.exit(1)

    ordem = achatar_modulos(modulos)
    invalidos = paths_invalidos(ordem)
    disponiveis = testes_disponiveis_para(cliente_id)

    entradas = entradas_globais(modulos)
    modulos_do_escopo = {bloco.modulo for bloco in blocos_selecionados}
    entradas_do_escopo = [
        entrada for entrada in entradas if entrada[0] in modulos_do_escopo
    ]
    testes_com_posicao = [
        (path, posicao)
        for _, path, posicao in entradas_do_escopo
        if path in disponiveis
    ]
    testes = [path for path, _ in testes_com_posicao]

    if modulo is not None and not testes:
        print(
            f"\n[Sentinela] Aviso: o módulo '{modulo}' existe na ordem.yaml, mas nenhum teste está disponível para o cliente '{cliente_id}'."
        )
        sys.exit(0)

    todos_catalogo = todos_os_testes_do_catalogo()
    ausentes = sorted(todos_catalogo - set(ordem))

    print()
    print("=" * 48)
    print("  Sentinela — Execução")
    print("=" * 48)
    print()
    print(f"  Cliente : {label}")
    if modulo is not None:
        print(f"  Módulo  : {modulo}")
    print(f"  Testes  : {len(testes)}")
    if ausentes:
        print(f"  ⚠  {len(ausentes)} teste(s) do catálogo ausentes da ordem.yaml")
    if invalidos:
        print(f"  ⚠  {len(invalidos)} path(s) inválido(s) na ordem.yaml:")
        for p in invalidos:
            print(f"     ✗ {p}")
    print()

    resultados: list[ResultadoTeste] = []
    total = len(testes)
    contagem_paths = Counter(testes)
    ocorrencias_paths: Counter = Counter()
    inicio_total = time.perf_counter()
    active_marker: Path | None = None

    try:
        active_marker = storage.marcar_run_ativo(run_dir)
        for i, (path_teste, posicao_global) in enumerate(testes_com_posicao, 1):
            _aguardar_pausa(run_dir, execution_id)
            ocorrencias_paths[path_teste] += 1
            nome_run = _nome_run_para_ocorrencia(
                path_teste,
                ocorrencias_paths[path_teste],
                contagem_paths[path_teste],
            )
            resultado = _executar_com_tentativas(
                path_teste=path_teste,
                cliente_id=cliente_id,
                max_tentativas=max_tentativas,
                headless=headless,
                run_dir=run_dir,
                nome_run=nome_run,
                prefixo=f"[{i}/{total}]",
                pausa=pausa,
                ocorrencia=posicao_global,
                execution_id=execution_id,
            )
            resultados.append(resultado)

    except KeyboardInterrupt:
        print()
        print("  [interrompido pelo usuário]")

    finally:
        try:
            if resultados:
                duracao_total = time.perf_counter() - inicio_total

                duracao_str = _fmt_duracao(duracao_total)

                print()
                print("  Resumo " + "-" * 40)
                _imprimir_contagens(resultados)
                print(f"  Duração total: {duracao_str}")
                _imprimir_ocorrencias(resultados)
                if execution_id is None:
                    print(f"  Run salvo em: {run_dir.relative_to(_raiz)}/")

                relatorio = gerar_relatorio(
                    run_dir, resultados, cliente_id, label, duracao_total
                )
                print(f"  Relatório  : {relatorio.relative_to(_raiz)}")
                print()
        finally:
            if active_marker is not None:
                try:
                    active_marker.unlink(missing_ok=True)
                except OSError:
                    pass

    return resultados


def executar_teste_unico(
    path_teste: str,
    cliente_id: str,
    max_tentativas: int,
    ttl_dias: int,
    headless: bool = False,
    count: int = 1,
    pausa: bool = False,
    execution_id: str | None = None,
) -> list[ResultadoTeste]:
    storage.limpar_runs_antigos(ttl_dias)

    execution_id = storage.validar_execution_id(execution_id) if execution_id else None
    run_dir = storage.criar_diretorio_run(cliente_id, execution_id, path_teste=path_teste)
    if execution_id:
        print(f"Execution ID: {execution_id}", flush=True)
        print(f"Run salvo em [{execution_id}]: {run_dir.relative_to(_raiz)}/", flush=True)

    configs_path = _raiz / "configs" / "configs.yaml"
    with open(configs_path, encoding="utf-8") as f:
        configs = yaml.safe_load(f)
    clientes = configs.get("clientes", {})
    if cliente_id not in clientes:
        print(
            f"[Sentinela] Erro: cliente '{cliente_id}' não encontrado em configs/configs.yaml."
        )
        sys.exit(1)
    label = clientes[cliente_id].get("label", cliente_id.upper())

    print()
    print("=" * 48)
    print("  Sentinela — Teste único")
    print("=" * 48)
    print()
    print(f"  Cliente : {label}")
    print(f"  Teste   : {Path(path_teste).stem}")
    if count > 1:
        print(f"  Count   : {count} repetições")
    print()

    resultados: list[ResultadoTeste] = []
    inicio_total = time.perf_counter()
    active_marker: Path | None = None

    nome_teste = Path(path_teste).stem

    try:
        active_marker = storage.marcar_run_ativo(run_dir)
        for repeticao in range(1, count + 1):
            _aguardar_pausa(run_dir, execution_id)
            resultado = _executar_com_tentativas(
                path_teste=path_teste,
                cliente_id=cliente_id,
                max_tentativas=max_tentativas,
                headless=headless,
                run_dir=run_dir,
                nome_run=nome_teste if count == 1 else f"{nome_teste}_r{repeticao}",
                prefixo=f"[{repeticao}/{count}]",
                nome_exibicao=nome_teste,
                pausa=pausa,
                execution_id=execution_id,
            )
            resultados.append(resultado)

    except KeyboardInterrupt:
        print()
        print("  [interrompido pelo usuário]")

    finally:
        try:
            if resultados:
                duracao_total = time.perf_counter() - inicio_total

                duracao_str = _fmt_duracao(duracao_total)

                print()
                print("  Resumo " + "-" * 40)
                if count == 1:
                    resultado_final = resultados[0]
                    print(
                        f"  {_SIMBOLO.get(resultado_final.status, '?')}  {resultado_final.status}"
                    )
                else:
                    _imprimir_contagens(resultados)
                    indices = [
                        i for i, r in enumerate(resultados, 1) if r.status in _OCORRENCIAS
                    ]
                    if indices:
                        print(
                            f"  Repetições com ocorrência: {', '.join(str(i) for i in indices)}"
                        )
                    print(f"  Repetições executadas: {len(resultados)}/{count}")
                print(f"  Duração total: {duracao_str}")
                _imprimir_ocorrencias(resultados)
                if execution_id is None:
                    print(f"  Run salvo em: {run_dir.relative_to(_raiz)}/")

                relatorio = gerar_relatorio(
                    run_dir, resultados, cliente_id, label, duracao_total
                )
                print(f"  Relatório  : {relatorio.relative_to(_raiz)}")
                print()
        finally:
            if active_marker is not None:
                try:
                    active_marker.unlink(missing_ok=True)
                except OSError:
                    pass

    return resultados
