"""
Monitor de Arquivos para o Sistema RAG de Planilhas.
Monitora a pasta D:\\docs_baixados e processa novos arquivos automaticamente.
"""

import os
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from datetime import datetime

from src.database.db_manager import db_manager
from src.utils.logger import get_logger
from src.processors.government_spreadsheet_processor import government_processor

class FileMonitor:
    """Monitor de arquivos para processamento automático."""
    
    def __init__(self, watch_path="D:\\docs_baixados", processed_path=None, discard_path=None):
        self.logger = get_logger("file_monitor")
        self.watch_path = Path(watch_path)
        self.processed_path = Path(processed_path) if processed_path else Path("data/processed")
        self.discard_path = Path(discard_path) if discard_path else Path("data/discard")
        
        # Criar diretórios se não existirem
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.discard_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar observer
        self.observer = Observer()
        self.event_handler = FileEventHandler(self)
        
        # Status do monitor
        self.is_running = False
        self.monitor_thread = None
        
        self.logger.info(f"File Monitor inicializado - Monitorando: {self.watch_path}")
    
    def start_monitoring(self):
        """Inicia o monitoramento de arquivos."""
        if self.is_running:
            self.logger.warning("Monitor já está rodando")
            return
        
        if not self.watch_path.exists():
            self.logger.error(f"Diretório de monitoramento não existe: {self.watch_path}")
            return
        
        try:
            # Configurar observer
            self.observer.schedule(self.event_handler, str(self.watch_path), recursive=True)
            self.observer.start()
            
            self.is_running = True
            self.logger.info("Monitor de arquivos iniciado com sucesso")
            
            # Processar arquivos existentes
            self.process_existing_files()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar monitor: {e}")
            self.is_running = False
    
    def stop_monitoring(self):
        """Para o monitoramento de arquivos."""
        if not self.is_running:
            return
        
        try:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            self.logger.info("Monitor de arquivos parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar monitor: {e}")
    
    def process_existing_files(self):
        """Processa arquivos que já existem no diretório monitorado."""
        self.logger.info("Processando arquivos existentes...")
        
        for file_path in self.watch_path.rglob("*"):
            if file_path.is_file():
                self.process_file(file_path)
    
    def process_file(self, file_path):
        """Processa um arquivo específico."""
        try:
            self.logger.info(f"Processando arquivo: {file_path}")
            
            # Verificar se é um arquivo suportado
            if not self.is_supported_file(file_path):
                self.logger.info(f"Arquivo não suportado: {file_path}")
                self.move_to_discard(file_path, "Tipo de arquivo não suportado")
                return
            
            # Tentar processar como planilha governamental
            try:
                system, services = government_processor.process_government_spreadsheet(str(file_path))
                
                if services:
                    # Arquivo processado com sucesso
                    self.logger.info(f"Arquivo processado com sucesso: {file_path} - {len(services)} serviços")
                    self.move_to_processed(file_path, system, len(services))
                else:
                    # Nenhum serviço encontrado
                    self.logger.info(f"Nenhum serviço encontrado: {file_path}")
                    self.move_to_discard(file_path, "Nenhum serviço encontrado")
            
            except Exception as e:
                self.logger.error(f"Erro ao processar arquivo {file_path}: {e}")
                self.move_to_discard(file_path, f"Erro de processamento: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Erro geral ao processar {file_path}: {e}")
    
    def is_supported_file(self, file_path):
        """Verifica se o arquivo é de um tipo suportado."""
        supported_extensions = {
            '.xlsx', '.xls', '.csv', '.pdf', '.doc', '.docx', 
            '.txt', '.json', '.zip', '.7z', '.rar'
        }
        return file_path.suffix.lower() in supported_extensions
    
    def move_to_processed(self, file_path, system, services_count):
        """Move arquivo para pasta de processados."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{timestamp}_{file_path.name}"
            new_path = self.processed_path / new_name
            
            shutil.move(str(file_path), str(new_path))
            
            # Registrar no banco de dados
            self.record_processed_file(str(new_path), system, services_count)
            
            self.logger.info(f"Arquivo movido para processados: {new_path}")
        
        except Exception as e:
            self.logger.error(f"Erro ao mover arquivo para processados: {e}")
    
    def move_to_discard(self, file_path, reason):
        """Move arquivo para pasta de descarte."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{timestamp}_{file_path.name}"
            new_path = self.discard_path / new_name
            
            shutil.move(str(file_path), str(new_path))
            
            # Registrar no banco de dados
            self.record_discarded_file(str(new_path), reason)
            
            self.logger.info(f"Arquivo movido para descarte: {new_path} - Motivo: {reason}")
        
        except Exception as e:
            self.logger.error(f"Erro ao mover arquivo para descarte: {e}")
    
    def record_processed_file(self, file_path, system, services_count):
        """Registra arquivo processado no banco de dados."""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processed_files (file_path, status, system, services_count, processed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (file_path, 'processed', system, services_count, datetime.now()))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao registrar arquivo processado: {e}")
    
    def record_discarded_file(self, file_path, reason):
        """Registra arquivo descartado no banco de dados."""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO processed_files (file_path, status, reason, processed_at)
                    VALUES (?, ?, ?, ?)
                """, (file_path, 'discarded', reason, datetime.now()))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao registrar arquivo descartado: {e}")
    
    def get_status(self):
        """Retorna o status do monitor."""
        return {
            "is_running": self.is_running,
            "watch_path": str(self.watch_path),
            "processed_path": str(self.processed_path),
            "discard_path": str(self.discard_path)
        }

class FileEventHandler(FileSystemEventHandler):
    """Handler para eventos de arquivo."""
    
    def __init__(self, file_monitor):
        self.file_monitor = file_monitor
        self.logger = get_logger("file_event_handler")
    
    def on_created(self, event):
        """Chamado quando um arquivo é criado."""
        if not event.is_directory:
            self.logger.info(f"Novo arquivo detectado: {event.src_path}")
            # Aguardar um pouco para garantir que o arquivo foi completamente escrito
            time.sleep(2)
            self.file_monitor.process_file(Path(str(event.src_path)))
    
    def on_moved(self, event):
        """Chamado quando um arquivo é movido."""
        if not event.is_directory:
            self.logger.info(f"Arquivo movido detectado: {event.dest_path}")
            time.sleep(2)
            self.file_monitor.process_file(Path(str(event.dest_path)))

# Instância global do monitor
file_monitor = FileMonitor() 