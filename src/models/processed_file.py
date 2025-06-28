"""
Modelo de dados para arquivos processados pelo sistema.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class FileStatus(str, Enum):
    """Status dos arquivos processados."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ProcessedFileBase(BaseModel):
    """Modelo base para arquivos processados."""
    file_path: str = Field(..., max_length=500, description="Caminho completo do arquivo")
    file_name: str = Field(..., max_length=255, description="Nome do arquivo")
    file_size: int = Field(..., ge=0, description="Tamanho do arquivo em bytes")

    @validator('file_path')
    def validate_file_path(cls, v):
        """Valida o caminho do arquivo."""
        if not v.strip():
            raise ValueError("Caminho do arquivo não pode estar vazio")
        return v.strip()

    @validator('file_name')
    def validate_file_name(cls, v):
        """Valida o nome do arquivo."""
        if not v.strip():
            raise ValueError("Nome do arquivo não pode estar vazio")
        return v.strip()

class ProcessedFileCreate(ProcessedFileBase):
    """Modelo para criação de registros de arquivos processados."""
    status: FileStatus = Field(default=FileStatus.PENDING, description="Status do processamento")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    services_count: int = Field(default=0, ge=0, description="Quantidade de serviços extraídos")

class ProcessedFileUpdate(BaseModel):
    """Modelo para atualização de registros de arquivos processados."""
    status: Optional[FileStatus] = Field(None, description="Status do processamento")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    services_count: Optional[int] = Field(None, ge=0, description="Quantidade de serviços")
    processed_at: Optional[datetime] = Field(None, description="Data/hora do processamento")

class ProcessedFile(ProcessedFileBase):
    """Modelo completo de arquivo processado com ID e timestamps."""
    id: int = Field(..., description="ID único do arquivo processado")
    status: FileStatus = Field(default=FileStatus.PENDING, description="Status do processamento")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    services_count: int = Field(default=0, ge=0, description="Quantidade de serviços extraídos")
    processed_at: datetime = Field(default_factory=datetime.now, description="Data/hora do processamento")

    class Config:
        """Configurações do modelo."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    @property
    def file_extension(self) -> str:
        """Retorna a extensão do arquivo."""
        return self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''

    @property
    def file_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB."""
        return self.file_size / (1024 * 1024)

    @property
    def file_size_formatted(self) -> str:
        """Retorna o tamanho do arquivo formatado."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size_mb:.1f} MB"

    @property
    def is_successful(self) -> bool:
        """Verifica se o processamento foi bem-sucedido."""
        return self.status == FileStatus.PROCESSED

    @property
    def is_failed(self) -> bool:
        """Verifica se o processamento falhou."""
        return self.status == FileStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """Verifica se o arquivo está pendente de processamento."""
        return self.status in [FileStatus.PENDING, FileStatus.PROCESSING]

    def to_dict(self) -> dict:
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "file_size_formatted": self.file_size_formatted,
            "status": self.status.value,
            "error_message": self.error_message,
            "services_count": self.services_count,
            "processed_at": self.processed_at.isoformat(),
            "is_successful": self.is_successful,
            "is_failed": self.is_failed,
            "is_pending": self.is_pending,
        }

    def __str__(self) -> str:
        """Representação string do arquivo processado."""
        status_emoji = {
            FileStatus.PENDING: "⏳",
            FileStatus.PROCESSING: "🔄",
            FileStatus.PROCESSED: "✅",
            FileStatus.FAILED: "❌",
            FileStatus.SKIPPED: "⏭️"
        }
        return f"{status_emoji.get(self.status, '❓')} {self.file_name} ({self.file_size_formatted}) - {self.services_count} serviços"

    def __repr__(self) -> str:
        """Representação detalhada do arquivo processado."""
        return f"ProcessedFile(id={self.id}, name='{self.file_name}', status='{self.status.value}', services={self.services_count})" 