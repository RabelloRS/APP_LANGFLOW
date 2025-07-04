@echo off
echo Iniciando interface web do Sistema RAG...
cd /d %~dp0..

echo Verificando ambiente virtual...

if exist ".venv\Scripts\Activate.ps1" (
    echo Ativando ambiente virtual (.venv)...
    powershell -ExecutionPolicy Bypass -File ".venv\Scripts\Activate.ps1"
    echo Ambiente virtual (.venv) ativado.
) else (
    echo Ambiente virtual NAO encontrado. Sera usado o Python global.
)

echo.
echo Iniciando interface web...
echo Acesse: http://localhost:5000
echo.

python src\web\app.py

echo.
echo Interface web encerrada.
pause  