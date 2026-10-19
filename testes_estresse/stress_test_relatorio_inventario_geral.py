#!/usr/bin/env python3
"""
Stress test — Relatório Inventário Geral (Patrimônio)
=====================================================
Dispara N navegadores Chromium em paralelo com abertura escalonada.
Todos os parâmetros estão no bloco CONFIGURAÇÃO abaixo.

Uso:
    python stress_test_relatorio_inventario_geral.py
"""

# ================================================================
# CONFIGURAÇÃO — edite aqui, não precisa mexer no resto do arquivo
# ================================================================

# Quantidade de navegadores em paralelo
INSTANCIAS: int = 16

# False = com interface gráfica  |  True = sem interface gráfica
HEADLESS: bool = False

# Tempo de espera entre a abertura de cada browser (em segundos)
# Exemplo: 0.5 = meio segundo; use 0 para abrir todos de uma vez
DELAY_ENTRE_BROWSERS_S: float = 10

# Delay entre cada ação dentro do browser (em milissegundos)
# Aumentar se a página não responde a tempo; 0 = sem delay adicional
SLOW_MO_MS: int = 500

# ------------------------------------------------------------------
# Ambiente e credenciais
# Adicione quantos usuários quiser na lista — serão distribuídos
# em rodízio entre as instâncias.
# ------------------------------------------------------------------
CONFIGURACAO_AMBIENTE: dict = {
    "url": "http://appt-oci.asicompany.com.br/trepe-treinamento/web",
    "nome_cliente": "TSE",
    "usuarios": [
        {"nome": "teste", "usuario": "8230172", "senha": "17114323"},
        {"nome": "teste", "usuario": "7084502", "senha": "2748838"},
        {"nome": "teste", "usuario": "7984592", "senha": "2748838"},
        {"nome": "teste", "usuario": "9999999", "senha": "2748838"},
        {"nome": "teste", "usuario": "0214155", "senha": "2748838"},
        {"nome": "teste", "usuario": "0244071", "senha": "2748838"},
        {"nome": "teste", "usuario": "0744561", "senha": "2748838"},
        {"nome": "teste", "usuario": "5795232", "senha": "2748838"},
        {"nome": "teste", "usuario": "0271451", "senha": "2748838"},
        {"nome": "teste", "usuario": "6695664", "senha": "2748838"},
        {"nome": "teste", "usuario": "0401723", "senha": "2748838"},
        {"nome": "teste", "usuario": "8466784", "senha": "2748838"},
        {"nome": "teste", "usuario": "4169674", "senha": "2748838"},
        {"nome": "teste", "usuario": "0288788", "senha": "2748838"},
        {"nome": "teste", "usuario": "0484486", "senha": "2748838"},
        {"nome": "teste", "usuario": "5055506", "senha": "2748838"},
        {"nome": "teste", "usuario": "8644026", "senha": "2748838"},
    ],
}

# ------------------------------------------------------------------
# Dados do relatório
# Preencha com os valores do seu ambiente. Campos com None usam o
# valor padrão do sistema ou são deixados em branco.
# ------------------------------------------------------------------
DADOS_RELATORIO: dict = {
    # Sigla da Unidade Gestora — campo UG no formulário (obrigatório)
    "ug_sigla": "TSE",

    # Data de referência — formato YYYYMMDD
    # None = usa a data de hoje automaticamente
    "data_referencia": "01012024",
}

# ================================================================
# FIM DA CONFIGURAÇÃO
# ================================================================


import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger
from playwright.sync_api import sync_playwright, Page

from utils import evidencia
from utils.waits import preencher_autocomplete_select, esperar_pagina_carregar

from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.patrimonio.relatorios.relatorio_inventario_geral.navegar_para_relatorio_inventario_geral_flow import (
    acessar_relatorio_inventario_geral,
)


# --------------------------------------------------------------------------- #
# Modelo de resultado                                                           #
# --------------------------------------------------------------------------- #

@dataclass
class Resultado:
    id: int
    usuario: str
    status: str        # "OK" | "FALHA" | "SEM_DADOS"
    duracao_s: float
    erro: Optional[str] = None


# --------------------------------------------------------------------------- #
# Preenchimento do formulário                                                   #
# --------------------------------------------------------------------------- #

def _preencher_formulario(page: Page) -> None:
    """
    Preenche UG e data de referência com os valores definidos em DADOS_RELATORIO.
    Replica preencher_dados_gerais_flow.py com data configurável.
    """
    preencher_autocomplete_select(page, "input[name='ug']", DADOS_RELATORIO["ug_sigla"])

    data = DADOS_RELATORIO["data_referencia"] or datetime.today().strftime("%Y%m%d")
    page.type("input[name='dtReferencia']", data, delay=50)

    page.click("button[name='submitPrint']")
    esperar_pagina_carregar(page)


# --------------------------------------------------------------------------- #
# Impressão do relatório (thread-safe)                                          #
# --------------------------------------------------------------------------- #

def _imprimir_relatorio(page: Page, inst_id: int) -> str:
    """
    Replica imprimir_relatorio_flow.py com nome de PDF único por instância,
    evitando conflito de arquivo entre threads que gravam no mesmo _temp_dir.

    Retorna:
        "OK"        — PDF gerado e salvo
        "SEM_DADOS" — relatório retornou HTML indicando ausência de registros
    Lança:
        ValueError  — se o HTML contiver erro Java
        TimeoutError — se o link do relatório não aparecer em 50s
    """
    heading = page.get_by_role("heading", name="Relatórios disponíveis")
    try:
        heading.wait_for(state="visible", timeout=1_000)
    except Exception:
        botao = page.locator('button[name="submitPrint"]')
        if botao.is_visible() and botao.is_enabled():
            botao.click()
            esperar_pagina_carregar(page)

    page.locator("input[name='listaRelatorios-1-3']").click()
    esperar_pagina_carregar(page)

    page.locator("button[name='submitPrint']").click()
    esperar_pagina_carregar(page)

    page.locator(
        'td[name="name-1-2"] >> a[name="linkRelatFinalizado"]'
    ).wait_for(state="visible", timeout=50_000)

    tipo = page.locator('td[name="type-1-3"]').inner_text().strip()
    relatorio_e_html = "HTML" in tipo.upper()

    with page.expect_popup() as popup_info:
        page.locator('td[name="name-1-2"] >> a[name="linkRelatFinalizado"]').click()

    popup_page = popup_info.value
    page.wait_for_timeout(0)

    if relatorio_e_html:
        conteudo = popup_page.content()
        popup_page.close()

        if "Nenhum registro encontrado" in conteudo:
            logger.warning("[inst {:02d}] Nenhum registro encontrado.", inst_id)
            return "SEM_DADOS"
        if "Não há dados a serem impressos" in conteudo:
            logger.warning("[inst {:02d}] Sem dados para impressão.", inst_id)
            return "SEM_DADOS"

        raise ValueError(
            "Relatório em HTML com possível erro Java — verifique manualmente."
        )

    evidencia.registrar_pdf(popup_page, f"relatorio_inventario_inst{inst_id:02d}")
    return "OK"


# --------------------------------------------------------------------------- #
# Execução de uma instância                                                     #
# --------------------------------------------------------------------------- #

def _executar(inst_id: int, usuario: dict) -> Resultado:
    """Sobe um browser isolado e executa o fluxo completo do relatório."""
    inicio = time.monotonic()

    dados_cliente = {
        "url": CONFIGURACAO_AMBIENTE["url"],
        "nome": CONFIGURACAO_AMBIENTE["nome_cliente"],
        "usuario": usuario["usuario"],
        "senha": usuario["senha"],
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO_MS,
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
                acessar_relatorio_inventario_geral(page)
                _preencher_formulario(page)
                status = _imprimir_relatorio(page, inst_id)
                logout(page)
            finally:
                ctx.close()
                browser.close()

        return Resultado(inst_id, usuario["nome"], status, time.monotonic() - inicio)

    except Exception as exc:
        duracao = time.monotonic() - inicio
        erro = repr(exc)[:300]
        logger.error("[inst {:02d}] {}", inst_id, erro)
        return Resultado(inst_id, usuario["nome"], "FALHA", duracao, erro)


# --------------------------------------------------------------------------- #
# Ponto de entrada                                                              #
# --------------------------------------------------------------------------- #

def main() -> None:
    usuarios = CONFIGURACAO_AMBIENTE["usuarios"]
    url = CONFIGURACAO_AMBIENTE["url"]

    data_ref = DADOS_RELATORIO["data_referencia"] or datetime.today().strftime("%Y%m%d")

    path_ev = PROJECT_ROOT / "evidencia"
    path_ev.mkdir(parents=True, exist_ok=True)
    evidencia.iniciar(path_ev)

    SEP = "=" * 64
    print(f"\n{SEP}")
    print(f"  STRESS TEST — Relatório Inventário Geral (Patrimônio)")
    print(f"  Instâncias            : {INSTANCIAS}")
    print(f"  Headless              : {HEADLESS}")
    print(f"  Delay entre browsers  : {DELAY_ENTRE_BROWSERS_S}s")
    print(f"  Slow-mo por ação      : {SLOW_MO_MS}ms")
    print(f"  URL                   : {url}")
    print(f"  UG                    : {DADOS_RELATORIO['ug_sigla']}")
    print(f"  Data de referência    : {data_ref}")
    print(f"  Usuários disponíveis  : {len(usuarios)} (distribuídos por rodízio)")
    print(f"{SEP}")
    print()

    tarefas = [
        (i + 1, usuarios[i % len(usuarios)])
        for i in range(INSTANCIAS)
    ]

    resultados: list[Resultado] = []
    inicio_geral = time.monotonic()
    _lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=INSTANCIAS) as pool:
        futuros: dict = {}

        for i, tarefa in enumerate(tarefas):
            if i > 0 and DELAY_ENTRE_BROWSERS_S > 0:
                time.sleep(DELAY_ENTRE_BROWSERS_S)
            futuros[pool.submit(_executar, *tarefa)] = tarefa[0]

        for fut in as_completed(futuros):
            r = fut.result()
            resultados.append(r)

            icone = "✓" if r.status in ("OK", "SEM_DADOS") else "✗"
            linha = (
                f"  [{icone}] #{r.id:02d}"
                f"  {r.usuario:<14}"
                f"  {r.status:<10}"
                f"  {r.duracao_s:>6.1f}s"
            )
            if r.erro:
                linha += f"\n       => {r.erro}"

            with _lock:
                print(linha)

    total_s = time.monotonic() - inicio_geral
    n_ok = sum(1 for r in resultados if r.status == "OK")
    n_sem_dados = sum(1 for r in resultados if r.status == "SEM_DADOS")
    n_fail = sum(1 for r in resultados if r.status == "FALHA")
    duracoes_ok = [r.duracao_s for r in resultados if r.status in ("OK", "SEM_DADOS")]

    print()
    print(f"{SEP}")
    print(f"  RESUMO")
    print(f"  Total instâncias  : {INSTANCIAS}")
    print(f"  PDF gerado (OK)   : {n_ok}")
    print(f"  Sem registros     : {n_sem_dados}")
    print(f"  Falha             : {n_fail}")
    print(f"  Taxa sem falha    : {(n_ok + n_sem_dados) / INSTANCIAS * 100:.0f}%")
    print(f"  Tempo real        : {total_s:.1f}s")
    if duracoes_ok:
        media = sum(duracoes_ok) / len(duracoes_ok)
        print(f"  Média por inst.   : {media:.1f}s")
        print(f"  Mínimo            : {min(duracoes_ok):.1f}s")
        print(f"  Máximo            : {max(duracoes_ok):.1f}s")
    print(f"{SEP}")
    print()


if __name__ == "__main__":
    main()
