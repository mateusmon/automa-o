import time

from multiprocessing import Process
from playwright.sync_api import sync_playwright, expect
from loguru import logger

from concorrencia.cadastrar_requisicao import cadastrar_requisicao
from concorrencia.atender_requisicao import atender_requisicao


TSE_CLIENTE = {
    "usuario": "50555065120",
    "senha": "2748838",
    "url": "http://jboss-aws.linkdata.com.br:8080/tse-qas/web"
}

TSE_DADOS = {
    "almoxarifados": {
        "almoxarifado_central": {
            "codigo": "0001",
            "nome": "ALMOXARIFADO CENTRAL"
        },
        "JUDICIAL": {
            "codigo": "0002",
            "nome": "SUBALMOXARIFADO MATERIAL DE LIMPEZA"
        }
    },

    "materiais": {
        "abacaxi_perola_natural": {
            "nome": "ABACAXI PÉROLA NATURAL",
            "codigo": "200002577",
            "quantidade": 1,
            "preco_unitario": 10.00,
            "codigo_endereco": "999999",
            "observacao": "ABATACEPTE"
        },
        "agua_sanitaria": {
            "nome": "ÁGUA SANITÁRIA EMBALAGEM 1 LITRO (CT PREST. SERVIÇO)",
            "codigo": "200007955",
            "quantidade": "",
            "preco_unitario": 3.99,
            "codigo_endereco": "LIMPEZA",
            "observacao": "ÁGUA SANITÁRIA"
        }
    },

    "urs": {
        "engenharia_clinica": {
            "nome": "ENGENHARIA CLINICA - HRG",
            "codigo": "006858"
        }
    }
}

SEADPB_CLIENTE = {
    "usuario": "07167706442",
    "senha": "2748838",
    "url": "http://seadpbqas.linkdata.com.br:8080/seadpb/web"
}

SEADPB_DADOS = {
    "almoxarifados": {
        "maternidade_peregrino": {
            "codigo": "00000232",
            "nome": "MATERNIDADE DR. PEREGRINO FILHO - ALMOXARIADO CENTRAL"
        },
    },

    "materiais": {
        "papel_sulfite": {
            "nome": "PAPEL SULFITE A4 210 X 297MM 75G BRANCO MULTIUSO PACOTE COM 500 FLS",
            "codigo": "200033068",
            "quantidade": 1
        },
    },

    "urs": {
        "gerencia_operacional": {
            "nome": "GERENCIA OPERACIONAL DE SISTEMA DE CUSTOS ADMINISTRATIVOS",
            "codigo": "006570"
        }
    }
}

SEADPB_DADOS_TESTE = {
    "almoxarifados": {
        "secretaria_administracao": {
            "codigo": "00019000",
            "nome": "SECRETARIA DE ESTADO DA ADMINISTRAÇÃO - CENTRAL"
        },
    },

    "materiais": {
        "acucar_cristal": {
            "nome": "AÇUCAR CRISTAL EMBALAGEM COM 1KG",
            "codigo": "200036361",
            "quantidade": 1,
            "preco_unitario": 3.64,
            "codigo_endereco": "000001",
            "observacao": "AÇUCAR CRISTAL"
        },
    },

    "urs": {
        "gerencia_operacional": {
            "nome": "GERENCIA OPERACIONAL DE SISTEMA DE CUSTOS ADMINISTRATIVOS",
            "codigo": "006570"
        }
    }
}


def login(page):
    url = SEADPB_CLIENTE["url"]
    usuario = SEADPB_CLIENTE["usuario"]
    senha = SEADPB_CLIENTE["senha"]

    logger.info("Iniciou login.")

    page.goto(
        url,
        wait_until="networkidle"
    )

    page.fill("#nmLogin", usuario)
    page.fill("#nmSenha", senha)
    page.get_by_role("button", name="Entrar").click()

    expect(
        page.get_by_role("button", name="Menu"), 
        "Falha no login. Verifique as credenciais no arquivo 'configs.yaml'"
    ).to_be_visible()
    
    logger.info("Login feito com sucesso!")


# -----------------------------
# Worker
# -----------------------------

def executar_fluxo(worker_id: int, fluxo):

    logger.info(f"[Worker {worker_id}] Iniciando")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        login(page)

        fluxo(page, SEADPB_DADOS_TESTE)

        browser.close()

    logger.info(f"[Worker {worker_id}] Finalizado")


# -----------------------------
# Runner
# -----------------------------

def rodar_concorrente(fluxo, quantidade):

    processos = []

    for i in range(quantidade):

        p = Process(
            target=executar_fluxo,
            args=(i + 1, fluxo)
        )

        p.start()
        time.sleep(1) # para todos os browsers não abrirem de uma vez
        processos.append(p)

    for p in processos:
        p.join()


# -----------------------------
# MAIN
# -----------------------------

def main():

    logger.info("=== CADASTROS ===")
    """
    rodar_concorrente(
        cadastrar_requisicao,
        1
    )
    
    
    #time.sleep(60)

    logger.info("=== ATENDIMENTOS ===")
    """
    rodar_concorrente(
        atender_requisicao,
        5
    )
    

if __name__ == "__main__":
    main()
    #print(list(DADOS["urs"].values())[0]["codigo"])
