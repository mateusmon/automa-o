"""Leitura da configuração do ASI e persistência da seleção local da GUI v2."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "configs.yaml"
# O loader em C (libyaml) é ~10× mais rápido; cai no Python puro se indisponível.
YAML_SAFE_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


@dataclass(frozen=True, slots=True)
class ClientConfiguration:
    """Dados de apresentação e execução de um cliente, carregados do YAML."""

    key: str
    label: str
    version: int | None
    url: str


@dataclass(frozen=True, slots=True)
class ConfigurationSnapshot:
    """Visão somente leitura das configurações para a nova interface."""

    clients: tuple[ClientConfiguration, ...]
    active_client_key: str | None

    def client(self, key: str) -> ClientConfiguration:
        """Obtém um cliente pela chave configurada."""
        for client in self.clients:
            if client.key == key:
                return client
        raise KeyError(f"Cliente não encontrado: {key}")


class ConfigurationService:
    """Carrega a configuração e persiste a seleção local de cliente."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self._config_path = config_path
        self._local_config_path = config_path.parent / "configs.local.yaml"

    def load(self) -> ConfigurationSnapshot:
        """Lê a configuração atual, aplicando apenas os seletores locais permitidos."""
        data = self._load_yaml(self._config_path)
        local_data = self._load_yaml(self._local_config_path, required=False)
        clients_data = data.get("clientes", {})
        if not isinstance(clients_data, Mapping):
            raise TypeError("configs.yaml deve conter clientes como um mapeamento.")

        clients = tuple(
            self._to_client_configuration(key, value)
            for key, value in clients_data.items()
        )
        active_client_key = local_data.get("cliente_ativo") or data.get("cliente_ativo")
        return ConfigurationSnapshot(
            clients=clients,
            active_client_key=active_client_key if isinstance(active_client_key, str) else None,
        )

    def set_active_client(self, client_key: str) -> bool:
        """Salva somente o cliente ativo em ``configs.local.yaml``."""
        snapshot = self.load()
        snapshot.client(client_key)
        local_data = dict(self._load_yaml(self._local_config_path, required=False))
        if local_data.get("cliente_ativo") == client_key:
            return False

        local_data["cliente_ativo"] = client_key
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._local_config_path.parent,
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                yaml.safe_dump(local_data, stream, allow_unicode=True, sort_keys=False)
            os.replace(temporary_path, self._local_config_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        return True

    @staticmethod
    def _to_client_configuration(key: object, value: object) -> ClientConfiguration:
        if not isinstance(key, str) or not isinstance(value, Mapping):
            raise TypeError("Cada cliente configurado deve possuir chave e dados válidos.")
        label = value.get("label", key)
        if not isinstance(label, str):
            raise TypeError(f"Label inválido para o cliente '{key}'.")
        version = value.get("versao")
        if version is not None and not isinstance(version, int):
            raise TypeError(f"Versão inválida para o cliente '{key}'.")
        direct_url = value.get("url")
        if direct_url is not None and not isinstance(direct_url, str):
            raise TypeError(f"URL inválida para o cliente '{key}'.")
        if isinstance(direct_url, str) and direct_url.strip():
            url = direct_url.strip()
        else:
            url = ConfigurationService._legacy_client_url(key, value.get("ambientes", {}))
        return ClientConfiguration(key, label, version, url)

    @staticmethod
    def _legacy_client_url(key: str, environments_data: object) -> str:
        """Resolve configs antigos por ambiente até a URL ser movida para o cliente."""
        if not isinstance(environments_data, Mapping):
            raise TypeError(f"Ambientes inválidos para o cliente '{key}'.")

        available_urls = {
            environment_data["url"].strip()
            for environment_data in environments_data.values()
            if isinstance(environment_data, Mapping)
            and isinstance(environment_data.get("url"), str)
            and environment_data["url"].strip()
        }
        if len(available_urls) == 1:
            return next(iter(available_urls))
        if not available_urls:
            return ""

        raise ValueError(
            f"Cliente '{key}' possui mais de uma URL em ambientes; configure uma URL única "
            "no cliente antes de remover os ambientes."
        )

    @staticmethod
    def _load_yaml(path: Path, required: bool = True) -> Mapping[str, object]:
        if not path.exists():
            if required:
                raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")
            return {}
        with path.open(encoding="utf-8") as stream:
            data = yaml.load(stream, Loader=YAML_SAFE_LOADER) or {}
        if not isinstance(data, Mapping):
            raise TypeError(f"Configuração inválida em {path}.")
        return data
