@echo off
echo Instalando dependencias do Sistema RAG...
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
echo Instalando dependencias do requirements.txt...
pip install -r requirements.txt

echo.
echo Instalando dependencias especificas da interface web...
pip install flask flask-socketio python-socketio python-engineio

echo.
echo Dependencias instaladas com sucesso!
echo.
echo Para iniciar a interface web, execute:
echo scripts\start_web_interface.bat
echo.
pause 