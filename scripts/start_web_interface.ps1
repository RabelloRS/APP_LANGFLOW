# Script PowerShell para iniciar a interface web do Sistema RAG
Write-Host "Iniciando interface web do Sistema RAG..." -ForegroundColor Green

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
Write-Host "Iniciando interface web..." -ForegroundColor Yellow
Write-Host "Acesse: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

# Executar a aplicação Flask
python src\web\app.py

Write-Host ""
Write-Host "Interface web encerrada." -ForegroundColor Yellow
Read-Host "Pressione Enter para continuar" 