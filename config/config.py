"""
Configurações principais do sistema RAG para planilhas de obras públicas.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
for directory in [DATA_DIR, DATABASE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações do sistema
SYSTEM_CONFIG = {
    "name": "Sistema RAG para Planilhas de Obras Públicas",
    "version": "1.0.0",
    "description": "Sistema de processamento e consulta de planilhas de preços de referência",
    "author": "Equipe de Desenvolvimento",
}

# Configurações de monitoramento de arquivos
FILE_MONITOR_CONFIG = {
    "watch_directory": "D:\\docs_baixados",  # Pasta a ser monitorada
    "supported_extensions": [
        # Documentos
        ".pdf", ".doc", ".docx", ".rtf",
        # Planilhas
        ".xls", ".xlsx", ".csv", ".tsv",
        # Arquivos de texto
        ".txt", ".json", ".xml", ".html",
        # Arquivos compactados
        ".zip", ".7z", ".rar", ".tar.gz", ".tar.bz2"
    ],
    "scan_interval": 30,                    # Intervalo de verificação (segundos)
    "max_file_size": 500 * 1024 * 1024,    # Tamanho máximo de arquivo (500MB)
    "backup_processed": True,               # Fazer backup de arquivos processados
    "backup_directory": str(DATA_DIR / "processed"),
    "discard_directory": str(DATA_DIR / "discard"),  # Pasta para arquivos sem planilhas
    "recursive_scan": True,                 # Verificar subpastas
    "max_depth": 10,                        # Profundidade máxima de subpastas
}

# Configurações de descompactação
ARCHIVE_EXTRACTOR_CONFIG = {
    "supported_formats": [".zip", ".7z", ".rar", ".tar.gz", ".tar.bz2"],
    "extract_to_subfolder": True,           # Extrair para subpasta com nome do arquivo
    "delete_after_extract": True,           # Remover arquivo compactado após extração
    "max_extract_size": 1024 * 1024 * 1024, # Tamanho máximo para extração (1GB)
    "password_file": str(DATA_DIR / "passwords.txt"),  # Arquivo com senhas comuns
    "temp_directory": str(DATA_DIR / "temp"),
}

# Configurações de IA para classificação
AI_CLASSIFIER_CONFIG = {
    "model_type": "sentence_transformer",   # Tipo de modelo (sentence_transformer, sklearn, custom)
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "confidence_threshold": 0.7,            # Threshold mínimo de confiança
    "batch_size": 10,                       # Tamanho do lote para processamento
    "max_text_length": 10000,               # Comprimento máximo do texto para análise
    "training_data_path": str(DATA_DIR / "training_data"),
    "models_path": str(DATA_DIR / "ai_models"),
    "keywords_weight": 0.3,                 # Peso das palavras-chave na classificação
    "structure_weight": 0.4,                # Peso da estrutura do documento
    "content_weight": 0.3,                  # Peso do conteúdo textual
}

# Palavras-chave para classificação de planilhas de engenharia
ENGINEERING_KEYWORDS = {
    "sinapi": [
        "sinapi", "sistema nacional de pesquisa de custos e índices da construção civil",
        "composição de preços", "custo unitário", "insumo", "serviço",
        "código", "descrição", "unidade", "preço unitário"
    ],
    "sicro": [
        "sicro", "sistema de custos rodoviários", "rodovia", "pavimentação",
        "terraplenagem", "drenagem", "ponte", "viaduto", "túnel"
    ],
    "cpos": [
        "cpos", "composição de preços", "orçamento", "preço de referência",
        "composição", "insumo", "serviço", "custo"
    ],
    "emop": [
        "emop", "empresa", "municipal", "estadual", "federal",
        "prefeitura", "governo", "administração pública"
    ],
    "criada": [
        "criada", "customizada", "específica", "particular",
        "proprietária", "interna", "exclusiva"
    ],
    "geral": [
        "engenharia", "construção", "obra", "projeto", "orçamento",
        "preço", "custo", "serviço", "material", "equipamento",
        "mão de obra", "composição", "tabela de preços"
    ]
}

# Configurações do banco de dados
DATABASE_CONFIG = {
    "type": "sqlite",
    "path": str(DATABASE_DIR / "services.db"),
    "backup_enabled": True,
    "backup_interval": 24,  # horas
    "max_connections": 10,
    "timeout": 30,
}

# Configurações do ChromaDB (RAG)
CHROMA_CONFIG = {
    "path": str(DATABASE_DIR / "chroma_db"),
    "collection_name": "services_collection",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200,
}

# Configurações de processamento de PDF
PDF_PROCESSOR_CONFIG = {
    "extract_tables": True,
    "extract_text": True,
    "extract_images": False,
    "ocr_enabled": False,
    "max_pages": 1000,
    "timeout": 300,  # segundos
    "temp_directory": str(DATA_DIR / "temp"),
}

# Configurações de processamento de Word
WORD_PROCESSOR_CONFIG = {
    "extract_tables": True,
    "extract_text": True,
    "extract_images": False,
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "timeout": 180,  # segundos
    "temp_directory": str(DATA_DIR / "temp"),
}

# Configurações de processamento de planilhas
SPREADSHEET_PROCESSOR_CONFIG = {
    "supported_formats": [".xls", ".xlsx", ".csv", ".tsv"],
    "max_sheet_size": 10000,  # Máximo de linhas por planilha
    "detect_headers": True,
    "auto_clean": True,  # Limpeza automática de dados
    "encoding_detection": True,
    "timeout": 120,  # segundos
}

# Configurações de classificação de planilhas
SPREADSHEET_CLASSIFIER_CONFIG = {
    "price_reference_keywords": [
        "sinapi", "sicro", "cpos", "emop", "criada",
        "preço de referência", "composição de preços",
        "tabela de preços", "orçamento de referência",
        "custo unitário", "preço unitário"
    ],
    "excluded_keywords": [
        "contrato", "licitação", "edital", "proposta",
        "relatório", "memorial", "projeto", "apresentação",
        "manual", "instrução", "norma", "regulamento"
    ],
    "confidence_threshold": 0.7,
    "max_services_per_file": 10000,
    "min_services_for_valid": 5,  # Mínimo de serviços para considerar válido
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(LOGS_DIR / "system.log"),
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "console_output": True,
    "ai_log_file": str(LOGS_DIR / "ai_classifier.log"),
    "file_operations_log": str(LOGS_DIR / "file_operations.log"),
}

# Configurações do Langflow
LANGFLOW_CONFIG = {
    "host": "localhost",
    "port": 7860,
    "api_key": os.getenv("LANGFLOW_API_KEY", ""),
    "timeout": 30,
    "retry_attempts": 3,
}

# Configurações do Ollama (LLM local)
OLLAMA_CONFIG = {
    "host": "localhost",
    "port": 11434,
    "model": "llama2:7b",
    "temperature": 0.1,
    "max_tokens": 2048,
    "timeout": 60,
}

# Configurações de validação de dados
VALIDATION_CONFIG = {
    "min_description_length": 10,
    "max_description_length": 1000,
    "min_value": 0.01,
    "max_value": 999999999.99,
    "required_fields": ["source", "service_code", "description", "value"],
    "date_format": "%Y-%m-%d",
    "currency_symbols": ["R$", "$", "€", "£"],
    "decimal_separators": [",", "."],
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "batch_size": 100,
    "max_workers": 4,
    "memory_limit": 1024 * 1024 * 1024,  # 1GB
    "cache_enabled": True,
    "cache_ttl": 3600,  # 1 hora
    "ai_processing_timeout": 30,  # segundos
    "file_processing_timeout": 300,  # segundos
}

# Configurações de segurança
SECURITY_CONFIG = {
    "encrypt_sensitive_data": False,
    "hash_file_paths": True,
    "sanitize_inputs": True,
    "max_file_path_length": 500,
    "allowed_file_extensions": [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt",
        ".zip", ".7z", ".rar", ".json", ".xml", ".html"
    ],
}

def get_config(section: str) -> Dict[str, Any]:
    """
    Retorna a configuração de uma seção específica.
    
    Args:
        section: Nome da seção de configuração
        
    Returns:
        Dicionário com as configurações da seção
    """
    configs = {
        "system": SYSTEM_CONFIG,
        "file_monitor": FILE_MONITOR_CONFIG,
        "archive_extractor": ARCHIVE_EXTRACTOR_CONFIG,
        "ai_classifier": AI_CLASSIFIER_CONFIG,
        "engineering_keywords": ENGINEERING_KEYWORDS,
        "database": DATABASE_CONFIG,
        "chroma": CHROMA_CONFIG,
        "pdf_processor": PDF_PROCESSOR_CONFIG,
        "word_processor": WORD_PROCESSOR_CONFIG,
        "spreadsheet_processor": SPREADSHEET_PROCESSOR_CONFIG,
        "spreadsheet_classifier": SPREADSHEET_CLASSIFIER_CONFIG,
        "logging": LOGGING_CONFIG,
        "langflow": LANGFLOW_CONFIG,
        "ollama": OLLAMA_CONFIG,
        "validation": VALIDATION_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "security": SECURITY_CONFIG,
    }
    
    return configs.get(section, {})

def validate_config() -> bool:
    """
    Valida as configurações do sistema.
    
    Returns:
        True se todas as configurações são válidas
    """
    try:
        # Verificar se a pasta de monitoramento existe
        watch_dir = Path(FILE_MONITOR_CONFIG["watch_directory"])
        if not watch_dir.exists():
            print(f"AVISO: Pasta de monitoramento não existe: {watch_dir}")
            return False
            
        # Verificar se o modelo Ollama está disponível
        # (implementar verificação se necessário)
        
        # Verificar permissões de escrita nos diretórios
        for directory in [DATA_DIR, DATABASE_DIR, LOGS_DIR]:
            if not os.access(directory, os.W_OK):
                print(f"ERRO: Sem permissão de escrita em: {directory}")
                return False
                
        return True
        
    except Exception as e:
        print(f"ERRO na validação de configuração: {e}")
        return False

def create_directories():
    """Cria os diretórios necessários para o sistema."""
    directories = [
        DATA_DIR / "processed",
        DATA_DIR / "temp",
        DATA_DIR / "raw",
        DATA_DIR / "discard",
        DATA_DIR / "training_data",
        DATA_DIR / "ai_models",
        LOGS_DIR,
        DATABASE_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Diretório criado/verificado: {directory}")

if __name__ == "__main__":
    # Teste das configurações
    print("=== Teste de Configurações ===")
    create_directories()
    
    if validate_config():
        print("✅ Configurações válidas")
    else:
        print("❌ Configurações inválidas")
        
    print(f"Diretório base: {BASE_DIR}")
    print(f"Diretório de dados: {DATA_DIR}")
    print(f"Diretório de banco: {DATABASE_DIR}")
    
    # Mostrar configurações de IA
    ai_config = get_config("ai_classifier")
    print(f"\nConfigurações de IA:")
    print(f"- Modelo: {ai_config.get('model_name', 'N/A')}")
    print(f"- Threshold de confiança: {ai_config.get('confidence_threshold', 'N/A')}")
    print(f"- Tamanho do lote: {ai_config.get('batch_size', 'N/A')}") 