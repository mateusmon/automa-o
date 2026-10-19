from loguru import logger

from utils.waits import preencher_autocomplete

def preencher_dados_gerais(page, almoxarifado, ur, material, quantidade="1"):

    logger.info("Preenchendo dados gerais da solicitação de materiais no almoxarifado '{}'.", almoxarifado["nome"])

    nome_completo_material = f"{material["nome"]} {material["complemento"]}"

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_autocomplete(page, "input[name='almoxarifado']", almoxarifado["sigla"])
    logger.info("Preenchendo nome da UR: '{}'.", ur["nome"])
    preencher_autocomplete(page, "input[name='ur']", ur["nome"])
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_autocomplete(page, "input[name='CatalogoMat-1-3']", nome_completo_material)

    logger.info("Preenchendo quantidade solicitada: '{}'.", quantidade)
    field_quantidade = page.locator("input[name='qtSolicitacao2-5']")
    field_quantidade.dblclick()
    field_quantidade.type(quantidade, delay=50)

    logger.info("Finalizou preenchimento de dados gerais da solicitação de materiais no almoxarifado '{}'.", almoxarifado["nome"])