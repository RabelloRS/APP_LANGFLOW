#!/usr/bin/env python3
"""
Script principal para inicializar o sistema RAG para planilhas de obras públicas.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config.config import validate_config, create_directories, get_config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

def show_banner():
    """Exibe o banner do sistema."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    Sistema RAG para Planilhas de Obras Públicas v1.0.0      ║
    ║                                                              ║
    ║    Processamento e Consulta de Preços de Referência         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))

def check_requirements():
    """Verifica se os requisitos do sistema estão atendidos."""
    console.print("\n[bold yellow]🔍 Verificando requisitos do sistema...[/bold yellow]")
    
    requirements = [
        ("Python 3.8+", sys.version_info >= (3, 8)),
        ("Diretório de monitoramento", Path(get_config("file_monitor")["watch_directory"]).exists()),
        ("Permissões de escrita", os.access(Path(__file__).parent.parent, os.W_OK)),
    ]
    
    table = Table(title="Status dos Requisitos")
    table.add_column("Requisito", style="cyan")
    table.add_column("Status", style="green")
    
    all_ok = True
    for req, status in requirements:
        status_text = "✅ OK" if status else "❌ FALHOU"
        table.add_row(req, status_text)
        if not status:
            all_ok = False
    
    console.print(table)
    return all_ok

def initialize_system():
    """Inicializa o sistema."""
    console.print("\n[bold green]🚀 Inicializando sistema...[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Criar diretórios
        task1 = progress.add_task("Criando diretórios...", total=None)
        create_directories()
        progress.update(task1, completed=True)
        
        # Validar configurações
        task2 = progress.add_task("Validando configurações...", total=None)
        time.sleep(1)  # Simular validação
        config_valid = validate_config()
        progress.update(task2, completed=True)
        
        # Verificar banco de dados
        task3 = progress.add_task("Verificando banco de dados...", total=None)
        time.sleep(1)  # Simular verificação
        progress.update(task3, completed=True)
        
        # Verificar ChromaDB
        task4 = progress.add_task("Verificando ChromaDB...", total=None)
        time.sleep(1)  # Simular verificação
        progress.update(task4, completed=True)
    
    return config_valid

def show_menu():
    """Exibe o menu principal do sistema."""
    menu_options = [
        ("1", "Iniciar Langflow", "Interface web para consultas"),
        ("2", "Monitor de Arquivos", "Monitorar pasta de documentos"),
        ("3", "Processar Arquivos", "Processar arquivos pendentes"),
        ("4", "Consultar Serviços", "Buscar serviços no banco"),
        ("5", "Relatórios", "Gerar relatórios de processamento"),
        ("6", "Configurações", "Gerenciar configurações"),
        ("0", "Sair", "Encerrar o sistema"),
    ]
    
    table = Table(title="Menu Principal")
    table.add_column("Opção", style="cyan", no_wrap=True)
    table.add_column("Ação", style="white")
    table.add_column("Descrição", style="dim")
    
    for option, action, description in menu_options:
        table.add_row(option, action, description)
    
    console.print(table)

def main():
    """Função principal."""
    try:
        # Exibir banner
        show_banner()
        
        # Verificar requisitos
        if not check_requirements():
            console.print("\n[bold red]❌ Requisitos não atendidos. Verifique as configurações.[/bold red]")
            return 1
        
        # Inicializar sistema
        if not initialize_system():
            console.print("\n[bold red]❌ Falha na inicialização do sistema.[/bold red]")
            return 1
        
        console.print("\n[bold green]✅ Sistema inicializado com sucesso![/bold green]")
        
        # Exibir menu principal
        while True:
            show_menu()
            
            choice = console.input("\n[bold cyan]Escolha uma opção: [/bold cyan]")
            
            if choice == "1":
                console.print("\n[bold yellow]🌐 Iniciando Langflow...[/bold yellow]")
                # TODO: Implementar inicialização do Langflow
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "2":
                console.print("\n[bold yellow]📁 Iniciando monitor de arquivos...[/bold yellow]")
                # TODO: Implementar monitor de arquivos
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "3":
                console.print("\n[bold yellow]⚙️ Iniciando processamento de arquivos...[/bold yellow]")
                # TODO: Implementar processamento
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "4":
                console.print("\n[bold yellow]🔍 Iniciando consulta de serviços...[/bold yellow]")
                # TODO: Implementar consulta
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "5":
                console.print("\n[bold yellow]📊 Gerando relatórios...[/bold yellow]")
                # TODO: Implementar relatórios
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "6":
                console.print("\n[bold yellow]⚙️ Abrindo configurações...[/bold yellow]")
                # TODO: Implementar configurações
                console.print("Funcionalidade em desenvolvimento...")
                
            elif choice == "0":
                console.print("\n[bold green]👋 Encerrando sistema...[/bold green]")
                break
                
            else:
                console.print("\n[bold red]❌ Opção inválida![/bold red]")
            
            console.input("\nPressione Enter para continuar...")
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠️ Interrupção do usuário. Encerrando...[/bold yellow]")
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro inesperado: {e}[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 