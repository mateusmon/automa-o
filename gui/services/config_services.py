import yaml
import tempfile
import shutil

from pathlib import Path


class _SafeDumperQuoted(yaml.SafeDumper):
    """SafeDumper that always single-quotes strings,
    preventing numeric-looking values like '02714517181'
    from being written without quotes and read back as ints."""
    pass


def _str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


_SafeDumperQuoted.add_representer(str, _str_representer)


class ConfigService:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.local_config_path = config_path.parent / "configs.local.yaml"

        self._data = self._load(self.config_path)
        self._local_data = self._load_local()

    # ---------- Public API ----------

    def get_data(self) -> dict:
        """
        Returns the base configuration dictionary (configs.yaml).
        Should be treated as read-only outside this class.
        """
        return self._data

    def get_cliente_ativo(self) -> str | None:
        return self._local_data.get("cliente_ativo") or self._data.get("cliente_ativo")

    def get_ambiente(self) -> str | None:
        return self._local_data.get("ambiente") or self._data.get("ambiente")

    def get_clientes(self) -> dict:
        return self._data.get("clientes", {})

    def update_client_url(self, client_id: str | None, ambiente: str | None, new_url: str | None):
        """
        Updates the URL of a client for a given environment
        and persists the configuration safely to configs.yaml.
        """
        clientes = self._data.get("clientes", {})

        if client_id not in clientes:
            raise KeyError(f"Cliente '{client_id}' não encontrado na configuração.")

        ambientes = clientes[client_id].get("ambientes", {})

        if ambiente not in ambientes:
            raise KeyError(
                f"Ambiente '{ambiente}' não encontrado para o cliente '{client_id}'."
            )

        old_url = ambientes[ambiente].get("url")

        try:
            ambientes[ambiente]["url"] = new_url
            self._persist(self.config_path, self._data)
        except Exception:
            ambientes[ambiente]["url"] = old_url
            raise


    def set_cliente_ativo(self, client_id: str) -> bool:
        clientes = self._data.get("clientes", {})

        if client_id not in clientes:
            raise KeyError(f"Cliente '{client_id}' não encontrado.")

        current = self.get_cliente_ativo()

        if current == client_id:
            return False  # nothing changed

        old_value = self._local_data.get("cliente_ativo")

        try:
            self._local_data["cliente_ativo"] = client_id
            self._persist(self.local_config_path, self._local_data)
        except Exception:
            self._local_data["cliente_ativo"] = old_value
            raise

        return True  # changed


    def set_ambiente(self, ambiente: str | None) -> bool:
        current = self.get_ambiente()

        if current == ambiente:
            return False

        old_value = self._local_data.get("ambiente")

        try:
            self._local_data["ambiente"] = ambiente
            self._persist(self.local_config_path, self._local_data)
        except Exception:
            self._local_data["ambiente"] = old_value
            raise

        return True

    # ---------- Internal ----------

    def _load(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {path}"
            )

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}


    def _load_local(self) -> dict:
        """
        Loads configs.local.yaml if it exists.
        Returns an empty dict if the file doesn't exist yet —
        the first call to set_cliente_ativo or set_ambiente will create it.
        """
        if not self.local_config_path.exists():
            return {}

        with open(self.local_config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return data


    def _persist(self, path: Path, data: dict):
        """
        Persists a configuration dict to the given path using atomic write.
        """
        temp_file = None

        try:
            with tempfile.NamedTemporaryFile(
                "w",
                delete=False,
                encoding="utf-8"
            ) as tmp:
                yaml.dump(
                    data,
                    tmp,
                    Dumper=_SafeDumperQuoted,
                    allow_unicode=True,
                    sort_keys=False
                )
                temp_file = Path(tmp.name)

            shutil.move(temp_file, path)

        finally:
            if temp_file and temp_file.exists():
                temp_file.unlink(missing_ok=True)
