import re
import unicodedata

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    preencher_campo,
)

_SIGLAS_UF = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPA": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARA": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES",
    "GOIAS": "GO",
    "MARANHAO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARA": "PA",
    "PARAIBA": "PB",
    "PARANA": "PR",
    "PERNAMBUCO": "PE",
    "PIAUI": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDONIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SAO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO",
}


def _sigla_uf(nome_uf: str) -> str:
    """Extrai a sigla (ex: 'DF') a partir do nome do blueprint (ex: 'D01 DISTRITO FEDERAL')."""
    sem_prefixo = re.sub(r"^[A-Za-z]\d{1,2}\s+", "", nome_uf.strip()).upper()
    sem_acento = "".join(
        c
        for c in unicodedata.normalize("NFD", sem_prefixo)
        if unicodedata.category(c) != "Mn"
    )
    return _SIGLAS_UF.get(sem_acento, nome_uf)


def preencher_dados_gerais_cidade(page: Page, cidade: dict) -> bool:
    """
    Preenche a Cidade e confirma. Cenário A.
    Campos: Nome (`nmCidade`), U.F. (`uf`, lookup) e Região (`regiao`, lookup).
    O País é preenchido automaticamente pela U.F.; Código gerado.

    :param cidade: dict do blueprint (nome, uf, regiao).
    Retorna True se conseguiu concluir ou False se o botão de Confirmar estiver desabilitado.
    """
    logger.info("Iniciou preenchimento de dados gerais de Cidade '{}'.", cidade["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmCidade']").wait_for(state="visible")
    logger.info(
        "Preenchendo campos de Nome, U.F. e Região da Cidade: '{}', '{}', '{}'.",
        cidade["nome"],
        cidade["uf"],
        cidade["regiao"],
    )
    ctx.locator("input[name='nmCidade']").fill(cidade["nome"])
    try:
        preencher_campo(ctx, "input[name='uf']", _sigla_uf(cidade["uf"]), igual=True)
    except Exception:
        ctx.locator("input[name='model-1']").fill("DISTRITO FEDERAL")
        clicar_com_ajax(ctx, ctx.locator("button[name='submitSearch']"))
        clicar_com_ajax(ctx, ctx.locator("button[name='submitUse'] >> nth=0"))
    preencher_campo(ctx, "input[name='regiao']", cidade["regiao"])

    btn_submit = ctx.locator("button[name='submitFinish']")

    if btn_submit.is_disabled():
        logger.warning(
            "O botão de Confirmar está desabilitado. Não é possível prosseguir."
        )
        return False

    btn_submit.click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou preenchimento de dados gerais de Cidade '{}'.", cidade["nome"]
    )
    return True
