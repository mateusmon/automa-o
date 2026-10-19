import os
from pathlib import Path

import yaml


class ConfigService:
    """
    Read-only configuration loader for Genesis.

    Responsibilities:
        - Load configs.yaml
        - Overlay cliente_ativo and ambiente from configs.local.yaml if present
        - Extract active client and environment
        - Build deterministic runtime_config dict
        - Fail fast on missing or invalid data

    Does NOT:
        - Modify configs.yaml
        - Persist changes
        - Manage client switching
    """

    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._data = self._load()

    # --- Public API ---
    def get_runtime_config(self) -> dict:
        """
        Extracts and validates runtime configuration required by Genesis.

        Returns:
            dict: flattened runtime configuration.

        Raises:
            RuntimeError: if required configuration is missing.
        """
        client_id = self._data.get("cliente_ativo")
        ambiente = self._data.get("ambiente")
        clientes = self._data.get("clientes", {})

        if not client_id:
            raise RuntimeError("configs.yaml: 'cliente_ativo' is not defined.")

        if not isinstance(clientes, dict):
            raise RuntimeError("configs.yaml: 'clientes' section is missing or invalid.")

        if client_id not in clientes:
            raise RuntimeError(
                f"configs.yaml: cliente_ativo '{client_id}' not found in 'clientes'."
            )

        if not ambiente:
            raise RuntimeError("configs.yaml: 'ambiente' is not defined.")

        cliente_config = clientes[client_id]

        ambientes = cliente_config.get("ambientes", {})

        if not isinstance(ambientes, dict):
            raise RuntimeError(
                f"configs.yaml: 'ambientes' section missing or invalid for client '{client_id}'"
            )

        if ambiente not in ambientes:
            raise RuntimeError(
                f"configs.yaml: ambiente '{ambiente}' not found for cliente '{client_id}'."
            )

        ambiente_config = ambientes[ambiente]

        # Required runtime fields
        client_version = cliente_config.get("versao")
        url = ambiente_config.get("url")
        users = ambiente_config.get("usuarios")

        if not url:
            raise RuntimeError(
                f"configs.yaml: 'url' not defined for client '{client_id}' and ambiente '{ambiente}'."
            )

        if not isinstance(client_version, int):
            raise RuntimeError(
                f"configs.yaml: 'versao' must be an integer for client '{client_id}'."
            )

        if not isinstance(users, dict):
            raise RuntimeError(f"configs.yaml: 'usuarios' not defined for ambiente '{ambiente}'")

        arquivo_dados = cliente_config.get("arquivo_dados")

        if not arquivo_dados:
            raise RuntimeError(
                f"configs.yaml: 'arquivo_dados' not defined for client '{client_id}'"
            )

        unidade_gestora = cliente_config.get("unidade_gestora")

        if not isinstance(unidade_gestora, dict) or not all(
            unidade_gestora.get(campo) for campo in ("nome", "sigla")
        ):
            raise RuntimeError(
                f"configs.yaml: 'unidade_gestora' incompleta ou não definida para cliente "
                f"'{client_id}'. Preencha 'nome' e 'sigla' com a UG real do cliente."
            )

        return {
            "cliente": client_id,
            "label": cliente_config.get("label"),
            "ambiente": ambiente,
            "url": url,
            "versao": client_version,
            "usuarios": users,
            "arquivo_dados": arquivo_dados,
            "unidade_gestora": unidade_gestora,
            "usuario_execucao": self._data.get("usuario_execucao"),
            "usuario_local": self._data.get("usuario_local", []),
            "funcionario_local": self._data.get("funcionario_local", []),
        }

    # --- Internal ---
    def _load(self) -> dict:
        if not self._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self._config_path}.")

        with open(self._config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self._apply_local_overlay(data)

        return data

    def _apply_local_overlay(self, data: dict) -> None:
        """
        Overlays cliente_ativo and ambiente from configs.local.yaml if present.
        Mutates data in place.
        """
        local_path = self._config_path.parent / "configs.local.yaml"

        if local_path.exists():
            with open(local_path, "r", encoding="utf-8") as f:
                local = yaml.safe_load(f) or {}

            for chave in ("cliente_ativo", "ambiente", "usuario_local", "funcionario_local"):
                if chave in local:
                    data[chave] = local[chave]

        cliente_por_execucao = os.environ.get("ASI_CLIENTE_ATIVO")

        if cliente_por_execucao:
            data["cliente_ativo"] = cliente_por_execucao
