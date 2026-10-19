"""
Este arquivo foi feito para servir como uma camada de segurança para o app.py.

Se houver algum erro ao fazer a importação ou um erro durante a execução de 
app.py, o este código vai pegá-lo e escrevê-lo em no arquivo erro_inicializacao.log
"""
import traceback

from pathlib import Path
from tkinter import messagebox

try:
    from app import App
except Exception:
    error_file = Path("erro_inicializacao.log")
    with open(error_file, "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())

    messagebox.showerror(
        "Erro ao iniciar",
        "Falha na importação de módulos.\n"
        "Veja 'erro_inicializacao.log'."
    )
    raise

if __name__ == "__main__":
    try:
        App().mainloop()
    except Exception:
        error_file = Path("erro_inicializacao.log")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

        messagebox.showerror(
            "Erro em tempo de execução",
            "Erro inesperado.\n"
            "Veja 'erro_inicializacao.log'."
        )