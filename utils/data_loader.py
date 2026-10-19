import json
import yaml

from pathlib import Path


def load_data(path: Path) -> dict:
    """
    Carrega dados de um arquivo JSON ou YAML e retorna como dicionário.

    - JSON: usa json.loads sobre o conteúdo bruto do arquivo
    - YAML: usa yaml.safe_load (evita execução de código arbitrário)

    :param path: Caminho do arquivo a ser carregado
    :type path: Path
    :return: Dados estruturados em formato dict
    :rtype: dict
    :raises ValueError: Caso o formato do arquivo não seja suportado
    """
    # Identifica o formato pelo sufixo do arquivo (.json, .yaml, .yml)
    if path.suffix == ".json":
        # Lê todo o conteúdo do arquivo como string (UTF-8)
        # e converte de JSON para dict Python
        return json.loads(path.read_text(encoding="utf-8"))
    
    if path.suffix in (".yaml", ".yml"):
        # Lê o conteúdo como string e faz parse com safe_load
        # safe_load evita riscos de segurança presentes no load padrão
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    
    # Caso o formato não seja reconhecido, falha explicitamente
    # (importante para evitar comportamentos silenciosos)
    raise ValueError(f"Formato não suportado: {path}")
