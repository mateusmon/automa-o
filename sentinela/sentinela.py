"""
Sentinela — executor inteligente de testes ASI.
Entrypoint CLI.
"""

import argparse
import io
import sys
from pathlib import Path

import yaml

_sentinela_dir = Path(__file__).resolve().parent
_raiz = _sentinela_dir.parent

sys.path.insert(0, str(_sentinela_dir))

from catalog_reader import testes_disponiveis_para, todos_os_testes_do_catalogo, razao_ignorado
import ordem_reader
from ordem_reader import (
    achatar_modulos,
    filtrar_para_cliente,
    ler_modulos,
    modulos_disponiveis,
    normalizar_modulo,
    selecionar_modulos,
)
from reporter import imprimir_relatorio_consolidado
from runner import executar_para_cliente, executar_teste_unico
from storage import limpar_todos_runs, validar_execution_id

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

AJUDA_DETALHADA = """
Sentinela — Ajuda
=================

Uso:
  python sentinela/sentinela.py --cliente NOME [opções]

Argumentos disponíveis:

  --cliente NOME
      Cliente a executar (ex: tcerj, pcdf, tse).
      Obrigatório, exceto quando usado com --todos ou --limpar.

  --todos
      Roda para todos os clientes definidos em configs/configs.yaml.

  --teste PATH
      Roda um único teste específico (ignora ordem.yaml).
      Pode ser combinado com --todos para rodar em todos os clientes.
      Exemplo: --teste tests/almoxarifado/consulta/test_consulta_simples.py --todos

  --modulo PREFIXO
      Seleciona jornadas lógicas da ordem.yaml pelo prefixo informado.
      Cada jornada pode conter pré-condições em outras pastas físicas.
      Pode ser usado nos três níveis de granularidade:
        --modulo tests/patrimonio
        --modulo tests/almoxarifado
        --modulo tests/almoxarifado/movimentacao_interna
      Compatível com --dry-run.

  --dry-run
      Simula a execução sem abrir browser nem rodar testes.
      Mostra quais testes seriam executados, ignorados e ausentes da ordem.

  --tentativas N
      Número de tentativas por teste em caso de falha.
      Sobrescreve o valor de tentativas em sentinela/config.yaml.

  --ttl N
      Tempo de vida dos runs salvos em dias.
      Sobrescreve ttl_dias em sentinela/config.yaml.

  --ambiente NOME
      Ambiente a usar (padrão: qas).
      Sobrescreve o ambiente configurado em configs/configs.yaml.
    
  --headless
      Executa os testes em modo headless (sem abrir o navegador).
      Útil ao rodar a Sentinela em segundo plano ou em CI/CD.

  --pausa
      Ao falhar um teste comum, abre a pausa do Playwright para investigação
      e aguarda Resume no Inspector. Os testes do Genesis novo sempre usam
      essa pausa em modo visual, mesmo sem a flag. Sem a flag, os demais testes
      só coletam evidências e fecham o navegador.
      Não tem efeito junto com --headless.

  --relatorio
      Ao final da execução (depois do resumo), imprime no terminal um
      relatório consolidado: média de duração das conclusões bem-sucedidas e
      percentual de sucesso, por cliente/teste e por teste agregando todos os
      clientes rodados no comando (útil com --todos).

  --limpar
      Apaga todos os runs salvos pelo Sentinela.

  --ajuda
      Exibe esta mensagem de ajuda e sai.

  --count N
      Repete o mesmo teste N vezes seguidas (requer --teste).
      Todas as repetições entram na mesma lista de resultados, então o resumo
      mostra quantas falharam e em quais repetições — útil para identificar
      teste intermitente.
      Exemplo: --teste tests/almoxarifado/consulta/test_consulta_simples.py --count 100

Exemplos:
  python sentinela/sentinela.py --cliente tcerj --dry-run
  python sentinela/sentinela.py --cliente pcdf --tentativas 2
  python sentinela/sentinela.py --todos --dry-run
  python sentinela/sentinela.py --todos --relatorio
  python sentinela/sentinela.py --ajuda
  python sentinela/sentinela.py --cliente tcerj --teste tests/almoxarifado/movimentacao_interna/test_consulta_material.py --count 100
"""


def _carregar_config_sentinela() -> dict:
    caminho = _sentinela_dir / "config.yaml"
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _carregar_configs_projeto() -> dict:
    caminho = _raiz / "configs" / "configs.yaml"
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _executar_dry_run(cliente_id: str, modulo: str | None = None) -> None:
    configs = _carregar_configs_projeto()
    clientes = configs.get("clientes", {})
    if cliente_id not in clientes:
        print(f"[Sentinela] Erro: cliente '{cliente_id}' não encontrado em configs/configs.yaml.")
        print(f"  Clientes disponíveis: {', '.join(clientes.keys())}")
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
    ordem_selecionada = achatar_modulos(blocos_selecionados)
    disponiveis = testes_disponiveis_para(cliente_id)
    para_executar = filtrar_para_cliente(ordem_selecionada, disponiveis)
    ignorados = [path for path in ordem_selecionada if path not in disponiveis]

    todos_catalogo = todos_os_testes_do_catalogo()
    ausentes = sorted(todos_catalogo - set(ordem))

    print()
    print("  Sentinela — Dry Run")
    print("  " + "=" * 44)
    print()
    print(f"  Cliente : {label}")
    print()

    print(f"  Testes que seriam executados ({len(para_executar)})")
    print("  " + "-" * 44)
    for i, path in enumerate(para_executar, 1):
        print(f"  {i}. {path}")
    print()

    print(f"  Ignorados por incompatibilidade com o cliente ({len(ignorados)})")
    print("  " + "-" * 44)
    for path in ignorados:
        razao = razao_ignorado(path, cliente_id)
        print(f"  - {path}  [{razao}]")
    print()

    print(f"  Testes no catálogo ausentes da ordem.yaml ({len(ausentes)})")
    print("  " + "-" * 44)
    for path in ausentes:
        print(f"  ⚠  {path}")
    print()

    invalidos = ordem_reader.paths_invalidos(ordem)
    print(f"  Paths inválidos na ordem.yaml ({len(invalidos)})")
    print("  " + "-" * 44)
    for path in invalidos:
        print(f"  ✗  {path}")
    print()


def _executar_teste_unico(path_teste: str, cliente_id: str, max_tentativas: int, ttl_dias: int, headless: bool = False, count: int = 1, pausa: bool = False, execution_id: str | None = None) -> list:
    path_teste = path_teste.replace("\\", "/")
    if not (_raiz / path_teste).exists():
        print(f"[Sentinela] Erro: arquivo não encontrado: {path_teste}")
        sys.exit(1)

    disponiveis = testes_disponiveis_para(cliente_id)
    if path_teste not in disponiveis:
        razao = razao_ignorado(path_teste, cliente_id)
        print(f"[Sentinela] Aviso: teste não disponível para o cliente '{cliente_id}'. Razão: {razao}")
        return []

    return executar_teste_unico(path_teste, cliente_id, max_tentativas, ttl_dias, headless=headless, count=count, pausa=pausa, execution_id=execution_id)


def _label_cliente(configs: dict, cliente_id: str) -> str:
    return configs.get("clientes", {}).get(cliente_id, {}).get("label", cliente_id.upper())


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--cliente", default=None)
    parser.add_argument("--todos", action="store_true")
    parser.add_argument("--teste", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tentativas", type=int, default=None)
    parser.add_argument("--ttl", type=int, default=None)
    parser.add_argument("--ambiente", default="qas")
    parser.add_argument("--limpar", action="store_true")
    parser.add_argument("--modulo", default=None)
    parser.add_argument("--ajuda", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--pausa", action="store_true")
    parser.add_argument("--relatorio", action="store_true")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--execution-id", default=None)

    args = parser.parse_args()

    if args.modulo:
        args.modulo = normalizar_modulo(args.modulo)

    if args.ajuda:
        print(AJUDA_DETALHADA)
        sys.exit(0)

    if args.limpar:
        limpar_todos_runs()
        print("[Sentinela] Runs sem processo ativo foram apagados; execuções ativas foram preservadas.")
        sys.exit(0)

    if args.dry_run:
        if not args.cliente:
            print("[Sentinela] --dry-run requer --cliente.")
            sys.exit(1)
        _executar_dry_run(args.cliente, modulo=args.modulo)
        return

    if args.count < 1:
        print("[Sentinela] --count deve ser no mínimo 1.")
        sys.exit(1)

    if args.count > 1 and not args.teste:
        print("[Sentinela] --count requer --teste.")
        sys.exit(1)

    config = _carregar_config_sentinela()
    try:
        execution_id = (
            validar_execution_id(args.execution_id)
            if args.execution_id
            else None
        )
    except ValueError as error:
        print(f"[Sentinela] {error}")
        sys.exit(1)
    tentativas = args.tentativas if args.tentativas is not None else config["tentativas"]
    ttl = args.ttl if args.ttl is not None else config["ttl_dias"]

    if args.teste:
        if args.todos:
            configs = _carregar_configs_projeto()
            resultados_por_cliente = {}
            for cliente_id in configs.get("clientes", {}).keys():
                print(f"\n{'=' * 50}")
                print(f"  Cliente: {cliente_id}")
                print(f"{'=' * 50}")
                resultados = _executar_teste_unico(args.teste, cliente_id, tentativas, ttl, headless=args.headless, count=args.count, pausa=args.pausa, execution_id=execution_id)
                if args.relatorio and resultados:
                    resultados_por_cliente[cliente_id] = resultados
            if args.relatorio:
                labels = {cid: _label_cliente(configs, cid) for cid in resultados_por_cliente}
                imprimir_relatorio_consolidado(resultados_por_cliente, labels)
            return
        if not args.cliente:
            print("[Sentinela] --teste requer --cliente.")
            sys.exit(1)
        resultados = _executar_teste_unico(args.teste, args.cliente, tentativas, ttl, headless=args.headless, count=args.count, pausa=args.pausa, execution_id=execution_id)
        if args.relatorio and resultados:
            configs = _carregar_configs_projeto()
            label = _label_cliente(configs, args.cliente)
            imprimir_relatorio_consolidado({args.cliente: resultados}, {args.cliente: label})
        return

    if args.cliente:
        resultados = executar_para_cliente(args.cliente, tentativas, ttl, modulo=args.modulo, headless=args.headless, pausa=args.pausa, execution_id=execution_id)
        if args.relatorio and resultados:
            configs = _carregar_configs_projeto()
            label = _label_cliente(configs, args.cliente)
            imprimir_relatorio_consolidado({args.cliente: resultados}, {args.cliente: label})
        return

    if args.todos:
        configs = _carregar_configs_projeto()
        resultados_por_cliente = {}
        for cliente_id in configs.get("clientes", {}).keys():
            print(f"\n{'=' * 50}")
            print(f"  Iniciando cliente: {cliente_id}")
            print(f"{'=' * 50}")
            resultados = executar_para_cliente(cliente_id, tentativas, ttl, modulo=args.modulo, headless=args.headless, pausa=args.pausa, execution_id=execution_id)
            if args.relatorio and resultados:
                resultados_por_cliente[cliente_id] = resultados
        if args.relatorio:
            labels = {cid: _label_cliente(configs, cid) for cid in resultados_por_cliente}
            imprimir_relatorio_consolidado(resultados_por_cliente, labels)
        return

    print("[Sentinela] Nenhuma ação especificada. Use --ajuda para ver os comandos.")
    sys.exit(1)


if __name__ == "__main__":
    main()
