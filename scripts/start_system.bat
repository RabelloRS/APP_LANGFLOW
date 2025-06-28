@echo off
chcp 65001 >nul
title Sistema RAG para Planilhas de Obras Públicas

echo.
echo ========================================
echo   Sistema RAG para Planilhas v1.0.0
echo ========================================
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado no PATH
    echo Instale o Python 3.8+ e tente novamente
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "..\venv" (
    echo Criando ambiente virtual...
    python -m venv ..\venv
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call ..\venv\Scripts\activate.bat

REM Instalar dependências se necessário
if not exist "..\venv\Lib\site-packages\rich" (
    echo Instalando dependências...
    pip install -r ..\requirements.txt
)

REM Executar o sistema
echo.
echo Iniciando sistema...
python start_system.py

REM Manter janela aberta em caso de erro
if errorlevel 1 (
    echo.
    echo Sistema encerrado com erro.
    pause
)

deactivate 