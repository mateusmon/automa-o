@echo off
chcp 65001 > nul

cd /d "%~dp0"

if not exist .venv\Scripts\pythonw.exe (
    echo ERROR: venv do Python não foi encontrado em venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist gui\main.py (
    echo ERROR: Arquivo main.py não encontrado.
    pause
    exit /b 1
)

.venv\Scripts\pythonw.exe gui\main.py