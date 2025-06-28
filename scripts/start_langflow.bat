@echo off
echo Iniciando Langflow no ambiente virtual...
echo.

REM Executar tudo no PowerShell para manter o ambiente virtual ativado
powershell.exe -ExecutionPolicy Bypass -File "start_langflow.ps1"

pause 