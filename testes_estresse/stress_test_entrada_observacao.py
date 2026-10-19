#!/usr/bin/env python3
"""
Stress test — Entrada Simples com Observação
=============================================
Dispara N navegadores Chromium em paralelo, cada um executando o fluxo
completo de entrada com observação no almoxarifado do cliente ativo.

Uso:
    python stress_test_entrada_observacao.py           # 15 instâncias (padrão)
    python stress_test_entrada_observacao.py -n 30     # 30 instâncias
    python stress_test_entrada_observacao.py --headless
    python stress_test_entrada_observacao.py -n 10 --sem-pdf
"""

import argparse
import copy
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger
from playwright.sync_api import sync_playwright, Page

from domain.contexto_cliente import ContextoCliente
from utils.data_loader import load_data
from utils import evidencia
from utils.analizador_pdf import assert_relatorio_pdf_valido
from utils.waits import esperar_pagina_carregar

from flows.shared.login_flow import login
from flows.almoxarifado.movimentacao_interna.entrada_materiais.navegar_para_entrada_materiais_flow import (
    acessar_entrada_materiais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_dados_gerais_flow import (
    preencher_dados_gerais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_documentos_flow import (
    preencher_documentos,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.preencher_materiais_flow import (
    preencher_materiais,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.entrada_observacao.preencher_observacoes_flow import (
    preencher_observacoes,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.acoes_escolher_endereco_flow import (
    acoes_escolher_endereco,
)
from flows.almoxarifado.movimentacao_interna.entrada_materiais.finalizar_entrada_flow import (
    finalizar_entrada,
)


# --------------------------------------------------------------------------- #
# Modelo de resultado                                                           #
# --------------------------------------------------------------------------- #

@dataclass
class Resultado:
    id: int
    usuario: str
    status: str        # "OK" | "FALHA"
    duracao_s: float
    erro: Optional[str] = None


# --------------------------------------------------------------------------- #
# Carregamento de configuração                                                  #
# --------------------------------------------------------------------------- #

def _carregar_ambiente() -> tuple[list[dict], dict]:
    """
    Lê configs/configs.yaml e o blueprint do cliente ativo.

    Retorna:
        usuarios  — lista de dicts {nome, usuario, senha} vindos do configs.yaml
        blueprint — dados completos do cliente (blueprint YAML com URL já injetada)
    """
    config = load_data(PROJECT_ROOT / "configs" / "configs.yaml")
    cliente = config["cliente_ativo"]
    ambiente = config["ambiente"]
    cfg_cliente = config["clientes"][cliente]
    cfg_ambiente = cfg_cliente["ambientes"][ambiente]

    url = cfg_ambiente["url"]
    usuarios = [
        {"nome": nome, "usuario": creds["usuario"], "senha": creds["senha"]}
        for nome, creds in cfg_ambiente["usuarios"].items()
    ]

    blueprint = load_data(PROJECT_ROOT / cfg_cliente["arquivo_dados"])
    blueprint.setdefault("dados_cliente", {})
    blueprint["dados_cliente"]["url"] = url

    return usuarios, blueprint


# --------------------------------------------------------------------------- #
# PDF com nome único por instância (thread-safe)                               #
# --------------------------------------------------------------------------- #

def _imprimir_e_validar(
    page: Page,
    dados_cliente: dict,
    material: dict,
    inst_id: int,
) -> None:
    """
    Replica a lógica de imprimir_relatorio_observacoes_flow, mas usa um nome
    de arquivo único por instância para evitar conflito de escrita paralela.

    O flow original hardcoda o nome "relatorio_material"; com múltiplos threads
    escrevendo simultaneamente no mesmo _temp_dir do evidencia.py, haveria
    sobrescrita de arquivo. Aqui cada instância grava "relatorio_material_inst01",
    "relatorio_material_inst02" etc., garantindo isolamento.
    """
    page.locator('input[name="listaRelatorios-2-3"]').click()
    page.locator('button[name="submitPrint"]').click()
    esperar_pagina_carregar(page)

    page.locator(
        'td[name="name-1-2"] >> a[name="linkRelatFinalizado"]'
    ).wait_for(state="visible", timeout=30_000)

    tipo = page.locator('td[name="type-1-3"]').inner_text().strip()
    if "HTML" in tipo.upper():
        raise ValueError(
            "Relatório gerado em HTML — verifique se há dados e se o mês está aberto."
        )

    with page.expect_popup() as popup_info:
        page.locator('td[name="name-1-2"] >> a[name="linkRelatFinalizado"]').click()

    page.wait_for_timeout(5_000)

    pdf_path = evidencia.registrar_pdf(
        popup_info.value,
        f"relatorio_material_inst{inst_id:02d}",
    )
    assert_relatorio_pdf_valido(pdf_path, dados_cliente, material)


# --------------------------------------------------------------------------- #
# Execução de uma instância                                                     #
# --------------------------------------------------------------------------- #

def _executar(
    inst_id: int,
    blueprint: dict,
    usuario: dict,
    headless: bool = True,
    com_pdf: bool = False,
) -> Resultado:
    """Sobe um browser isolado e executa o fluxo completo."""
    inicio = time.monotonic()

    # Cópia isolada dos dados do cliente com as credenciais desta instância
    dados_cliente = copy.deepcopy(blueprint["dados_cliente"])
    dados_cliente["usuario"] = usuario["usuario"]
    dados_cliente["senha"] = usuario["senha"]

    # ContextoCliente lê blueprint de forma read-only — seguro compartilhar
    contexto = ContextoCliente(blueprint)
    almoxarifado = contexto.almoxarifado_padrao()
    fornecedor = contexto.fornecedor_padrao()
    material = contexto.material_padrao()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--start-maximized",
                    "--disable-pdfium",
                    "--disable-features=PdfViewer",
                    "--disable-extensions",
                ],
            )
            ctx = browser.new_context(no_viewport=True, accept_downloads=True)
            page = ctx.new_page()
            page.set_default_timeout(60_000)
            page.set_default_navigation_timeout(60_000)

            try:
                login(page, dados_cliente)
                acessar_entrada_materiais(page)
                preencher_dados_gerais(page, almoxarifado, fornecedor)
                preencher_documentos(page)
                preencher_materiais(page, material)
                preencher_observacoes(page, material)
                acoes_escolher_endereco(page, material)
                finalizar_entrada(page)

                if com_pdf:
                    _imprimir_e_validar(page, dados_cliente, material, inst_id)

            finally:
                ctx.close()
                browser.close()

        return Resultado(inst_id, usuario["nome"], "OK", time.monotonic() - inicio)

    except Exception as exc:
        duracao = time.monotonic() - inicio
        erro = repr(exc)[:300]
        logger.error("[inst {:02d}] {}", inst_id, erro)
        return Resultado(inst_id, usuario["nome"], "FALHA", duracao, erro)


# --------------------------------------------------------------------------- #
# Ponto de entrada                                                              #
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stress test — Entrada Simples com Observação (almoxarifado)"
    )
    parser.add_argument(
        "-n", "--instancias",
        type=int,
        default=20,
        metavar="N",
        help="Número de navegadores em paralelo (padrão: 15)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa os navegadores sem interface gráfica",
    )
    parser.add_argument(
        "--sem-pdf",
        action="store_true",
        help="Pula impressão e validação do PDF — mais rápido, menos assertivo",
    )
    args = parser.parse_args()

    com_pdf = not args.sem_pdf
    usuarios, blueprint = _carregar_ambiente()
    url = blueprint["dados_cliente"]["url"]

    if com_pdf:
        path_ev = PROJECT_ROOT / "evidencia"
        path_ev.mkdir(parents=True, exist_ok=True)
        evidencia.iniciar(path_ev)

    SEP = "=" * 62
    print(f"\n{SEP}")
    print(f"  STRESS TEST — Entrada Simples com Observação")
    print(f"  Instâncias : {args.instancias}")
    print(f"  Headless   : {args.headless}")
    print(f"  Com PDF    : {com_pdf}")
    print(f"  URL        : {url}")
    print(f"  Usuários   : {len(usuarios)} disponível(is), distribuídos por rodízio")
    print(f"{SEP}")
    print()

    tarefas = [
        (i + 1, blueprint, usuarios[i % len(usuarios)], args.headless, com_pdf)
        for i in range(args.instancias)
    ]

    resultados: list[Resultado] = []
    inicio_geral = time.monotonic()
    _lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.instancias) as pool:
        futuros = {pool.submit(_executar, *t): t[0] for t in tarefas}

        for fut in as_completed(futuros):
            r = fut.result()
            resultados.append(r)

            icone = "✓" if r.status == "OK" else "✗"
            linha = (
                f"  [{icone}] #{r.id:02d}"
                f"  {r.usuario:<14}"
                f"  {r.status:<5}"
                f"  {r.duracao_s:>6.1f}s"
            )
            if r.erro:
                linha += f"\n       => {r.erro}"

            with _lock:
                print(linha)

    total_s = time.monotonic() - inicio_geral
    n_ok = sum(1 for r in resultados if r.status == "OK")
    n_fail = len(resultados) - n_ok
    duracoes_ok = [r.duracao_s for r in resultados if r.status == "OK"]

    print()
    print(f"{SEP}")
    print(f"  RESUMO")
    print(f"  Total instâncias : {args.instancias}")
    print(f"  Sucesso          : {n_ok}")
    print(f"  Falha            : {n_fail}")
    print(f"  Taxa de sucesso  : {n_ok / args.instancias * 100:.0f}%")
    print(f"  Tempo real       : {total_s:.1f}s")
    if duracoes_ok:
        media = sum(duracoes_ok) / len(duracoes_ok)
        print(f"  Média por inst.  : {media:.1f}s")
        print(f"  Mínimo           : {min(duracoes_ok):.1f}s")
        print(f"  Máximo           : {max(duracoes_ok):.1f}s")
    print(f"{SEP}")
    print()


if __name__ == "__main__":
    main()
