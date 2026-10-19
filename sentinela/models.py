from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ResultadoTeste:
    path: str
    nome: str
    status: str
    duracao: float
    tentativa: int
    max_tentativas: int
    saida: str
    trace_paths: list[Path] = field(default_factory=list)
    screenshot_path: Path | None = None
    erro_resumo: str = ""
    duracao_acumulada: float = 0.0
    tentativas: list["ResultadoTeste"] = field(default_factory=list, repr=False)
