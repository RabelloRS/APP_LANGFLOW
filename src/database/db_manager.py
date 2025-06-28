"""
Gerenciador de banco de dados para o sistema RAG de planilhas.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

from config.config import get_config
from src.utils.logger import get_logger

logger = get_logger("database")

class DatabaseManager:
    """Gerenciador principal do banco de dados."""
    
    def __init__(self):
        self.config = get_config("database")
        self.db_path = self.config["path"]
        self._ensure_db_directory()
        self._create_tables()
    
    def _ensure_db_directory(self):
        """Garante que o diretório do banco existe."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório do banco verificado: {db_dir}")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexões com o banco."""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.config.get("timeout", 30),
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            yield conn
        except Exception as e:
            logger.error(f"Erro na conexão com banco: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self):
        """Cria as tabelas do banco de dados."""
        logger.info("Criando tabelas do banco de dados...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela Services
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source VARCHAR(50) NOT NULL,
                    origin_file VARCHAR(500) NOT NULL,
                    service_code VARCHAR(100) NOT NULL,
                    base_date DATE NOT NULL,
                    description TEXT NOT NULL,
                    is_loaded BOOLEAN NOT NULL,
                    value DECIMAL(15,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela ProcessedFiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path VARCHAR(500) UNIQUE NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    original_archive VARCHAR(500),
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'pending',
                    error_message TEXT,
                    services_count INTEGER DEFAULT 0,
                    has_spreadsheets BOOLEAN DEFAULT FALSE,
                    ai_classification VARCHAR(100),
                    ai_confidence DECIMAL(3,2),
                    ai_relevant BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Tabela FileOperations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type VARCHAR(50) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    target_path VARCHAR(500),
                    operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Tabela AIModels
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name VARCHAR(100) NOT NULL,
                    model_type VARCHAR(50) NOT NULL,
                    model_version VARCHAR(20) NOT NULL,
                    training_data_path VARCHAR(500),
                    accuracy DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabela TrainingData
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path VARCHAR(500) NOT NULL,
                    classification VARCHAR(100) NOT NULL,
                    is_relevant BOOLEAN NOT NULL,
                    confidence_score DECIMAL(3,2),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Criar índices para melhor performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_source ON services(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_code ON services(service_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_services_date ON services(base_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed_files_path ON processed_files(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed_files_status ON processed_files(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_operations_type ON file_operations(operation_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_operations_date ON file_operations(operation_date)")
            
            conn.commit()
            logger.info("Tabelas criadas com sucesso")
    
    def insert_service(self, service_data: Dict[str, Any]) -> int:
        """Insere um novo serviço no banco."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO services (source, origin_file, service_code, base_date, 
                                    description, is_loaded, value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                service_data["source"],
                service_data["origin_file"],
                service_data["service_code"],
                service_data["base_date"],
                service_data["description"],
                service_data["is_loaded"],
                service_data["value"]
            ))
            conn.commit()
            return cursor.lastrowid or 0
    
    def insert_processed_file(self, file_data: Dict[str, Any]) -> int:
        """Insere um novo arquivo processado no banco."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processed_files (file_path, file_name, file_size, file_type,
                                           original_archive, status, services_count,
                                           has_spreadsheets, ai_classification, 
                                           ai_confidence, ai_relevant)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_data["file_path"],
                file_data["file_name"],
                file_data["file_size"],
                file_data["file_type"],
                file_data.get("original_archive"),
                file_data.get("status", "pending"),
                file_data.get("services_count", 0),
                file_data.get("has_spreadsheets", False),
                file_data.get("ai_classification"),
                file_data.get("ai_confidence"),
                file_data.get("ai_relevant", False)
            ))
            conn.commit()
            return cursor.lastrowid or 0
    
    def update_processed_file(self, file_id: int, update_data: Dict[str, Any]):
        """Atualiza um arquivo processado."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query de atualização dinamicamente
            set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [file_id]
            
            cursor.execute(f"""
                UPDATE processed_files 
                SET {set_clause}, processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
    
    def insert_file_operation(self, operation_data: Dict[str, Any]) -> int:
        """Insere uma nova operação de arquivo no banco."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_operations (operation_type, file_path, target_path,
                                           success, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (
                operation_data["operation_type"],
                operation_data["file_path"],
                operation_data.get("target_path"),
                operation_data["success"],
                operation_data.get("error_message")
            ))
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_processed_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Busca um arquivo processado pelo caminho."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processed_files WHERE file_path = ?
            """, (file_path,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_pending_files(self) -> List[Dict[str, Any]]:
        """Busca arquivos pendentes de processamento."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processed_files 
                WHERE status IN ('pending', 'processing')
                ORDER BY processed_at ASC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_services_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Busca serviços de um arquivo específico."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM services WHERE origin_file = ?
                ORDER BY service_code
            """, (file_path,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de serviços
            cursor.execute("SELECT COUNT(*) FROM services")
            total_services = cursor.fetchone()[0]
            
            # Total de arquivos processados
            cursor.execute("SELECT COUNT(*) FROM processed_files")
            total_files = cursor.fetchone()[0]
            
            # Arquivos por status
            cursor.execute("""
                SELECT status, COUNT(*) FROM processed_files 
                GROUP BY status
            """)
            files_by_status = dict(cursor.fetchall())
            
            # Serviços por fonte
            cursor.execute("""
                SELECT source, COUNT(*) FROM services 
                GROUP BY source
            """)
            services_by_source = dict(cursor.fetchall())
            
            # Arquivos com planilhas
            cursor.execute("""
                SELECT COUNT(*) FROM processed_files 
                WHERE has_spreadsheets = TRUE
            """)
            files_with_spreadsheets = cursor.fetchone()[0]
            
            return {
                "total_services": total_services,
                "total_files": total_files,
                "files_by_status": files_by_status,
                "services_by_source": services_by_source,
                "files_with_spreadsheets": files_with_spreadsheets
            }
    
    def backup_database(self) -> str:
        """Cria backup do banco de dados."""
        if not self.config.get("backup_enabled", True):
            logger.warning("Backup desabilitado nas configurações")
            return ""
        
        backup_dir = Path(self.db_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"services_backup_{timestamp}.db"
        
        with self.get_connection() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"Backup criado: {backup_path}")
        return str(backup_path)
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """Remove backups antigos."""
        backup_dir = Path(self.db_path).parent / "backups"
        if not backup_dir.exists():
            return
        
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup_file in backup_dir.glob("services_backup_*.db"):
            if backup_file.stat().st_mtime < cutoff_date:
                backup_file.unlink()
                logger.info(f"Backup removido: {backup_file}")

# Instância global do gerenciador de banco
db_manager = DatabaseManager() 