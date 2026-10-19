import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from filelock import FileLock

TZ_BR = timezone(timedelta(hours=-3))
BASE_DIR = Path(__file__).parent.parent / "historico_testes" / "estado_atual"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def _arquivo(cliente: str) -> Path:
    return BASE_DIR / f"{cliente}.json"


def _ler(cliente: str) -> dict:
    arq = _arquivo(cliente)
    if not arq.exists():
        return {}
    conteudo = arq.read_text(encoding="utf-8").strip()
    return json.loads(conteudo) if conteudo else {}


def _escrever_atomico(cliente: str, dados: dict) -> None:
    arq = _arquivo(cliente)
    tmp = arq.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, arq)  # rename atômico — nunca deixa o arquivo pela metade


def atualizar_lote(cliente: str, resultados: dict) -> None:
    """
    resultados: {nome_teste: {"modulo": str, "resultado": "pass"|"fail"|"skip"}}
    Mescla com o estado existente; sobrescreve apenas os testes informados,
    preservando os demais. Protegido por lock contra execuções concorrentes
    no mesmo cliente.
    """
    lock = FileLock(str(_arquivo(cliente)) + ".lock")
    with lock:
        dados = _ler(cliente)
        agora = datetime.now(TZ_BR).isoformat()
        for teste, info in resultados.items():
            dados[teste] = {
                "modulo": info["modulo"],
                "data": agora,
                "resultado": info["resultado"],
            }
        _escrever_atomico(cliente, dados)


def estado(cliente: str) -> dict:
    return _ler(cliente)


def resumo(cliente: str, filtro_resultado: str | None = None) -> None:
    dados = estado(cliente)
    if not dados:
        print(f"Nenhum teste registrado para {cliente}.")
        return
    for teste, info in sorted(dados.items()):
        if filtro_resultado and info["resultado"] != filtro_resultado:
            continue
        print(f"{teste:50} {info['resultado']:5} {info['data']}  [{info['modulo']}]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consulta o histórico de testes de um cliente.")
    parser.add_argument("cliente")
    parser.add_argument("--resultado", choices=["pass", "fail", "skip"], default=None)
    args = parser.parse_args()
    resumo(args.cliente, args.resultado)