"""
Sistema de logging centralizado para o sistema RAG de planilhas.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger
from config.config import get_config

class InterceptHandler(logging.Handler):
    """Handler para interceptar logs do logging padrão e redirecionar para loguru."""
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

class SystemLogger:
    """Sistema de logging centralizado."""
    
    def __init__(self):
        self.config = get_config("logging")
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o sistema de logging."""
        # Remover handlers padrão
        logger.remove()
        
        # Configurar formato
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para console
        if self.config.get("console_output", True):
            logger.add(
                sys.stdout,
                format=log_format,
                level=self.config.get("level", "INFO"),
                colorize=True
            )
        
        # Handler para arquivo principal
        main_log_file = self.config.get("file")
        if main_log_file:
            logger.add(
                main_log_file,
                format=log_format,
                level=self.config.get("level", "INFO"),
                rotation=self.config.get("max_size", 10 * 1024 * 1024),
                retention=self.config.get("backup_count", 5),
                compression="zip"
            )
        
        # Handler para logs de IA
        ai_log_file = self.config.get("ai_log_file")
        if ai_log_file:
            logger.add(
                ai_log_file,
                format=log_format,
                level="DEBUG",
                rotation=self.config.get("max_size", 10 * 1024 * 1024),
                retention=self.config.get("backup_count", 5),
                compression="zip"
            )
        
        # Handler para logs de operações de arquivo
        file_ops_log_file = self.config.get("file_operations_log")
        if file_ops_log_file:
            logger.add(
                file_ops_log_file,
                format=log_format,
                level="INFO",
                rotation=self.config.get("max_size", 10 * 1024 * 1024),
                retention=self.config.get("backup_count", 5),
                compression="zip"
            )
        
        # Interceptar logs do logging padrão
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        
        # Configurar loguru para bibliotecas externas
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True
    
    def get_logger(self, name: str):
        """Retorna um logger configurado para um módulo específico."""
        return logger.bind(name=name)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, 
                          error_message: Optional[str] = None, **kwargs):
        """Log específico para operações de arquivo."""
        file_logger = self.get_logger("file_operations")
        
        if success:
            file_logger.info(
                f"Operação '{operation}' realizada com sucesso para: {file_path}",
                extra=kwargs
            )
        else:
            file_logger.error(
                f"Falha na operação '{operation}' para: {file_path} - {error_message}",
                extra=kwargs
            )
    
    def log_ai_operation(self, operation: str, file_path: str, classification: str,
                        confidence: float, **kwargs):
        """Log específico para operações de IA."""
        ai_logger = self.get_logger("ai_classifier")
        
        ai_logger.info(
            f"Classificação IA: {classification} (confiança: {confidence:.2f}) "
            f"para arquivo: {file_path}",
            extra=kwargs
        )
    
    def log_system_event(self, event: str, details: str, level: str = "INFO", **kwargs):
        """Log para eventos do sistema."""
        system_logger = self.get_logger("system")
        
        if level.upper() == "DEBUG":
            system_logger.debug(f"Evento: {event} - {details}", extra=kwargs)
        elif level.upper() == "INFO":
            system_logger.info(f"Evento: {event} - {details}", extra=kwargs)
        elif level.upper() == "WARNING":
            system_logger.warning(f"Evento: {event} - {details}", extra=kwargs)
        elif level.upper() == "ERROR":
            system_logger.error(f"Evento: {event} - {details}", extra=kwargs)
        elif level.upper() == "CRITICAL":
            system_logger.critical(f"Evento: {event} - {details}", extra=kwargs)

# Instância global do logger
system_logger = SystemLogger()

def get_logger(name: str):
    """Função conveniente para obter um logger."""
    return system_logger.get_logger(name)

def log_file_operation(operation: str, file_path: str, success: bool, 
                      error_message: Optional[str] = None, **kwargs):
    """Função conveniente para log de operações de arquivo."""
    system_logger.log_file_operation(operation, file_path, success, error_message, **kwargs)

def log_ai_operation(operation: str, file_path: str, classification: str,
                    confidence: float, **kwargs):
    """Função conveniente para log de operações de IA."""
    system_logger.log_ai_operation(operation, file_path, classification, confidence, **kwargs)

def log_system_event(event: str, details: str, level: str = "INFO", **kwargs):
    """Função conveniente para log de eventos do sistema."""
    system_logger.log_system_event(event, details, level, **kwargs) 