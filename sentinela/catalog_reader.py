"""
Lê o MODULES do modules_catalog.py e retorna quais testes estão disponíveis
para um cliente específico, considerando as regras de inclusão, exclusão e
versão do GRP (mesma lógica usada pela GUI em gui/core/module_filter.py).
"""

import importlib.util
import sys
from pathlib import Path

import yaml

_raiz = Path(__file__).resolve().parent.parent
if str(_raiz / "gui") not in sys.path:
    sys.path.insert(0, str(_raiz / "gui"))


def _carregar_modulo(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {nome} em {caminho}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MODULES = _carregar_modulo("modules_catalog", _raiz / "gui" / "catalog" / "modules_catalog.py").MODULES
_visivel_para = _carregar_modulo("module_filter", _raiz / "gui" / "core" / "module_filter.py")._visivel_para


def _versao_do_cliente(cliente_id: str) -> int | None:
    """Lê clientes[cliente_id]['versao'] em configs/configs.yaml. None se ausente."""
    configs_path = _raiz / "configs" / "configs.yaml"
    with open(configs_path, encoding="utf-8") as f:
        configs = yaml.safe_load(f)
    return configs.get("clientes", {}).get(cliente_id, {}).get("versao")


def testes_disponiveis_para(cliente_id: str) -> set[str]:
    """Retorna set de paths de testes disponíveis para o cliente."""
    disponiveis = set()
    client_versao = _versao_do_cliente(cliente_id)

    for _, modulo in MODULES.items():
        meta = modulo.get("meta", {})
        if not _visivel_para(meta, cliente_id, client_versao):
            continue

        for secao in modulo.get("sections", {}).values():
            for teste in secao:
                if "clientes" in teste:
                    raise ValueError(
                        f"Chave inválida 'clientes' encontrada em '{teste.get('path', '?')}. "
                        "Use 'clients'."
                    )
                path = teste.get("path")
                if not path:
                    continue

                if _visivel_para(teste, cliente_id, client_versao):
                    disponiveis.add(path)

    return disponiveis


def todos_os_testes_do_catalogo() -> set[str]:
    """Retorna set com todos os paths únicos do catálogo, sem filtragem."""
    todos = set()
    for modulo in MODULES.values():
        for secao in modulo.get("sections", {}).values():
            for teste in secao:
                path = teste.get("path")
                if path:
                    todos.add(path)
    return todos


def razao_ignorado(path: str, cliente_id: str) -> str:
    client_versao = _versao_do_cliente(cliente_id)

    for modulo in MODULES.values():
        meta = modulo.get("meta", {})
        for secao in modulo.get("sections", {}).values():
            for teste in secao:
                if teste.get("path") != path:
                    continue
                if not _visivel_para(meta, cliente_id, client_versao):
                    return "clients/versao (módulo)"
                if teste.get("clients"):
                    return "clients"
                if teste.get("exclude_clients"):
                    return "exclude_clients"
                if teste.get("versao_minima") is not None or teste.get("versao_maxima") is not None:
                    return "versao_minima/versao_maxima"
    return "desconhecido"
