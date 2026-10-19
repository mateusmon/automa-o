from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import yaml


def _load_config() -> dict:
    path = Path(__file__).parent / "db_config.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_session(client_name: str) -> Session:
    """
    Returns a SQLAlchemy Session for a given client and database.

    Usage:
        with get_session("tse", "almoxarifado") as session:
            results = session.execute(...)
    """
    config = _load_config()

    try:
        dsn = config["clients"][client_name]["dsn"]
    except KeyError:
        raise ValueError(
            f"No DSN configured for client='{client_name}'."
        )

    engine = create_engine(dsn, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
