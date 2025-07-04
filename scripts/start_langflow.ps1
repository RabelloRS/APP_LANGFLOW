# Script para iniciar Langflow no ambiente virtual
Write-Host "=== Iniciador do Langflow (Ambiente Virtual) ===" -ForegroundColor Green
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path ".venv")) {
    Write-Host "ERRO: Ambiente virtual .venv nao encontrado." -ForegroundColor Red
    Write-Host "Execute: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "Execute: python -m pip install --upgrade pip" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "OK: Ambiente virtual ativado" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Erro ao ativar ambiente virtual: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o Python está funcionando no ambiente virtual
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python no ambiente virtual: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python nao encontrado no ambiente virtual." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o Langflow está instalado no ambiente virtual
try {
    python -c "import langflow" 2>$null
    Write-Host "Langflow ja esta instalado no ambiente virtual." -ForegroundColor Green
} catch {
    Write-Host "Instalando Langflow no ambiente virtual..." -ForegroundColor Yellow
    try {
        pip install langflow
        Write-Host "Langflow instalado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "ERRO: Falha ao instalar Langflow." -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

Write-Host ""
Write-Host "Iniciando servidor Langflow..." -ForegroundColor Cyan
Write-Host "O Langflow sera aberto automaticamente no seu navegador." -ForegroundColor Cyan
Write-Host "Para parar o servidor, feche esta janela ou pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Função para verificar se o servidor está rodando
function Test-LangflowServer {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Função para monitorar o status do servidor
function Start-LangflowWithMonitoring {
    Write-Host "Iniciando Langflow..." -ForegroundColor Green
    
    # Iniciar Langflow em background usando o Python do ambiente virtual
    $pythonPath = ".\.venv\Scripts\python.exe"
    $langflowProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "3000" -PassThru -WindowStyle Hidden
    
    Write-Host "Aguardando inicializacao do servidor..." -ForegroundColor Yellow
    
    # Aguardar até 30 segundos para o servidor iniciar
    $timeout = 30
    $elapsed = 0
    $checkInterval = 2
    
    while ($elapsed -lt $timeout) {
        Start-Sleep -Seconds $checkInterval
        $elapsed += $checkInterval
        
        Write-Host "Verificando servidor... ($elapsed/$timeout segundos)" -ForegroundColor Cyan
        
        if (Test-LangflowServer) {
            Write-Host "OK: Langflow iniciado com sucesso!" -ForegroundColor Green
            Write-Host "Servidor rodando em: http://localhost:3000" -ForegroundColor Green
            Write-Host "Status: ONLINE" -ForegroundColor Green
            
            # Abrir navegador
            try {
                Start-Process "http://localhost:3000"
                Write-Host "Navegador aberto automaticamente" -ForegroundColor Green
            } catch {
                Write-Host "Aviso: Nao foi possivel abrir o navegador automaticamente" -ForegroundColor Yellow
                Write-Host "Abra manualmente: http://localhost:3000" -ForegroundColor Cyan
            }
            
            # Mostrar informações do processo
            Write-Host ""
            Write-Host "Informacoes do Servidor:" -ForegroundColor Cyan
            Write-Host "   PID: $($langflowProcess.Id)" -ForegroundColor White
            Write-Host "   Porta: 3000" -ForegroundColor White
            Write-Host "   Host: 0.0.0.0" -ForegroundColor White
            Write-Host "   Status: Ativo" -ForegroundColor Green
            Write-Host ""
            Write-Host "Monitoramento ativo - O servidor continuara rodando" -ForegroundColor Yellow
            Write-Host "Para parar: Feche esta janela ou pressione Ctrl+C" -ForegroundColor Red
            
            # Monitoramento contínuo
            $monitorCount = 0
            while ($true) {
                Start-Sleep -Seconds 10
                $monitorCount++
                
                if (Test-LangflowServer) {
                    Write-Host "OK: Servidor funcionando - Monitoramento #$monitorCount" -ForegroundColor Green
                } else {
                    Write-Host "ERRO: Servidor nao responde - Monitoramento #$monitorCount" -ForegroundColor Red
                    Write-Host "Tentando reconectar..." -ForegroundColor Yellow
                    
                    # Tentar reiniciar se necessário
                    if ($monitorCount -gt 3) {
                        Write-Host "Reiniciando servidor..." -ForegroundColor Yellow
                        Stop-Process -Id $langflowProcess.Id -Force -ErrorAction SilentlyContinue
                        Start-Sleep -Seconds 2
                        $langflowProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "3000" -PassThru -WindowStyle Hidden
                        $monitorCount = 0
                    }
                }
            }
            
            return
        }
    }
    
    # Se chegou aqui, o servidor não iniciou
    Write-Host "ERRO: Timeout - Langflow nao iniciou em $timeout segundos" -ForegroundColor Red
    Write-Host "Verificando possiveis problemas..." -ForegroundColor Yellow
    
    # Verificar se o processo ainda está rodando
    if (-not $langflowProcess.HasExited) {
        Write-Host "Aviso: Processo Langflow ainda esta rodando (PID: $($langflowProcess.Id))" -ForegroundColor Yellow
        Write-Host "Aguardando mais alguns segundos..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        if (Test-LangflowServer) {
            Write-Host "OK: Langflow iniciou apos delay!" -ForegroundColor Green
            Start-Process "http://localhost:3000"
        } else {
            Write-Host "ERRO: Servidor ainda nao esta respondendo" -ForegroundColor Red
            Stop-Process -Id $langflowProcess.Id -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "ERRO: Processo Langflow foi encerrado" -ForegroundColor Red
    }
    
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Iniciar Langflow com monitoramento
Start-LangflowWithMonitoring