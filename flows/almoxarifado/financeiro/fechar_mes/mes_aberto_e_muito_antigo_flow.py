from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from utils.competencia_financeira import obter_data_almoxarifado


def mes_aberto_e_muito_antigo(page):

    page.locator("#centralHeaderUserName").click()
    ano_mes_aberto = obter_data_almoxarifado(page, "YYYY/MM")
    ano_mes_atual = datetime.today().strftime("%Y/%m")
    
    dt_aberto = datetime.strptime(ano_mes_aberto, "%Y/%m")
    dt_atual = datetime.strptime(ano_mes_atual, "%Y/%m")
    mes_anterior = dt_atual - relativedelta(months=1)

    # Se o mês aberto NÃO for anterior ao mês atual, isto é, se for mais velho dois meses que o mês atual
    if dt_aberto != mes_anterior:
        pytest.fail(
            f"Mês aberto ({ano_mes_aberto}) é mais de um mês anterior ao mês atual ({ano_mes_atual})."
            "Faça o fechamento do mês de forma manual para prosseguir com os testes."
        )
