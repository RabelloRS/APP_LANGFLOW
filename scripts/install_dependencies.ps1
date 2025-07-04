# Script PowerShell para instalar dependências do Sistema RAG
Write-Host "Instalando dependencias do Sistema RAG..." -ForegroundColor Green

# Navegar para o diretório do projeto
Set-Location $PSScriptRoot\..

Write-Host "Verificando ambiente virtual..." -ForegroundColor Yellow

# Ativar ambiente virtual se existir
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual (.venv)..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
    Write-Host "Ambiente virtual (.venv) ativado." -ForegroundColor Green
} else {
    Write-Host "Ambiente virtual NAO encontrado. Sera usado o Python global." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Instalando dependencias do requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Instalando dependencias especificas da interface web..." -ForegroundColor Yellow
pip install flask flask-socketio python-socketio python-engineio

Write-Host ""
Write-Host "Dependencias instaladas com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar a interface web, execute:" -ForegroundColor Cyan
Write-Host "scripts\start_web_interface.ps1" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para continuar" 