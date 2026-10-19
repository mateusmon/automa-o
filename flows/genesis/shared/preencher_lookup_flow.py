"""Lookup Genesis com as variações e tentativas do provisionamento legado.

Auxiliar restrito ao Genesis: preserva o contrato de genesis/utils/espera.py,
sem importar o executor legado nem alterar utils/waits.py.
"""

import re
import unicodedata

from loguru import logger
from playwright.sync_api import Frame, Locator, Page, TimeoutError, expect

from utils.waits import aguardar_ajax_global


def preencher_campo(
    ctx: Page | Frame,
    locator: str | Locator,
    texto: str,
    lookup_name: str | None = None,
) -> None:
    """
    Preenche um campo de lookup (busca por código/nome) e confirma a seleção.

    Funciona tanto com `Page` (v3) quanto com `Frame` (v4). O alerta de erro
    é buscado no mesmo escopo recebido, que é onde ele é renderizado em ambas
    as versões.

    Args:
        ctx: Instância de `Page` ou `Frame` onde o campo está localizado.
        locator: Seletor CSS (str) ou `Locator` já resolvido do campo de input.
        texto: Texto a preencher. Use `"   "` ou `"%"` para abrir a listagem
            completa e selecionar automaticamente o primeiro resultado.
        lookup_name: Nome do botão de lookup. Se omitido, deriva de
            `"lookup-{name}"` onde `name` é o atributo do input.
        page: `Page` raiz, necessário para `aguardar_ajax_global` em contextos
            onde `ctx` é um `Frame` (v4). Se omitido, usa `ctx`.
    """
    if isinstance(locator, Locator):
        field = locator
    else:
        field = ctx.locator(locator)

    # Obtendo o page a partir do frame para o aguardar_ajax_global
    _page = ctx if isinstance(ctx, Page) else ctx.page

    # aguardar_ajax_global(_page)
    field.wait_for(state="visible")

    # Caso especial: texto vago abre listagem completa — o lookup é acionado
    # diretamente sem fill, e o primeiro resultado é selecionado na tabela
    if texto in ("   ", "%"):
        input_name = field.get_attribute("name")
        button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"
        ctx.locator(f"button[name='{button_name}']").click()
        aguardar_ajax_global(_page)

        ctx.get_by_title("Consultar novo registro").last.click(no_wait_after=True)
        aguardar_ajax_global(_page)

        tbody = ctx.locator("table[name='paginationTable'] tbody")
        tbody.wait_for(state="visible")
        tbody.locator("tr").first.locator("button[name='submitUse']").click(no_wait_after=True)
        aguardar_ajax_global(_page)
        return

    variacoes = gerar_variacoes_nome(texto)
    input_name = field.get_attribute("name")
    button_name = lookup_name if lookup_name is not None else f"lookup-{input_name}"

    for tentativa, var_texto in enumerate(variacoes, start=1):
        is_ultima = (tentativa == len(variacoes))
        field.fill(var_texto)
        ctx.locator(f"button[name='{button_name}']").click()
        aguardar_ajax_global(_page)

        # Aguarda um tempo até que o valor correto (no formato código - nome) seja puxado
        try:
            expect(field).to_have_value(re.compile(r"^\d+"), timeout=1_000)
        except Exception:
            pass  # Casos sem código numérico — segue normalmente

        # Verifica se surgiu um alerta
        alerta_erro = False
        msg_alerta = ""
        try:
            alerta = ctx.locator(".alert-danger, .alert-warning")
            alerta.wait_for(state="visible", timeout=200)
            alerta_erro = True
            msg_alerta = alerta.inner_text()
        except TimeoutError:
            pass

        if alerta_erro:
            if not is_ultima:
                logger.debug("Lookup com '{}' retornou alerta ('{}'). Tentando próxima variação...", var_texto, msg_alerta)
                continue
            raise RuntimeError(
                f"Autocomplete falhou para '{texto}' (última tentativa '{var_texto}'): {msg_alerta}"
            )

        # Escolhe o primeiro resultado, caso encontre mais do que um resultado
        esta_na_consulta = ctx.get_by_text("Total de itens consultados:").is_visible()
        if esta_na_consulta:
            span_size = ctx.locator("span[name='searchResultSize']")
            try:
                if span_size.is_visible() and int(span_size.inner_text()) == 0:
                    if not is_ultima:
                        logger.debug("Lookup com '{}' retornou 0 resultados. Tentando próxima variação...", var_texto)
                        continue
            except Exception:
                pass
            primeira_linha = ctx.locator("table[name='paginationTable'] tbody tr").first
            primeira_linha.wait_for(state="visible")
            primeira_linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(_page)

        if var_texto != texto:
            logger.info("Lookup selecionado com sucesso usando a variação '{}' para '{}'", var_texto, texto)
        return


def gerar_variacoes_nome(texto: str) -> list[str]:
    """
    Gera variações para busca (com e sem acento),
    testando sem prefixos de blueprint (ex: 'B01 BRASÍLIA' -> 'BRASÍLIA' e 'BRASILIA').
    """
    if not texto:
        return [texto]

    # Remove qualquer prefixo de blueprint como 'B01 ', 'T01 ', 'A1 ', etc.
    texto_sem_prefixo = re.sub(r"^[A-Za-z]\d{1,2}\s+", "", texto.strip()).upper()

    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto_sem_prefixo)
        if unicodedata.category(c) != "Mn"
    )

    mapa_conhecido = {
        "BRASILIA": "BRASÍLIA",
        "GOIANIA": "GOIÂNIA",
        "SAO PAULO": "SÃO PAULO",
        "BELEM": "BELÉM",
        "MACEIO": "MACEIÓ",
        "CUIABA": "CUIABÁ",
        "FLORIANOPOLIS": "FLORIANÓPOLIS",
        "VITORIA": "VITÓRIA",
        "SAO LUIS": "SÃO LUÍS",
        "JOAO PESSOA": "JOÃO PESSOA",
        "MACAPA": "MACAPÁ",
        "AMAPA": "AMAPÁ",
    }

    candidatos = [texto_sem_prefixo, sem_acento]

    # Se o texto de entrada estiver sem acento, tenta aplicar a acentuação conhecida
    for sem_ac, com_ac in mapa_conhecido.items():
        if sem_ac in sem_acento and com_ac not in texto_sem_prefixo:
            candidatos.append(sem_acento.replace(sem_ac, com_ac))
        
    resultado = []
    for c in candidatos:
        if c and c not in resultado:
            resultado.append(c)
    return resultado
