"""
Modelo de dados para serviços de planilhas de preços de referência.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class ServiceSource(str, Enum):
    """Fontes de dados de serviços."""
    SINAPI = "sinapi"
    SICRO = "sicro"
    CPOS = "cpos"
    EMOP = "emop"
    CRIADA = "criada"
    OUTROS = "outros"

class ServiceType(str, Enum):
    """Tipos de serviços."""
    ONERADO = "onerado"
    DESONERADO = "desonerado"

class ServiceBase(BaseModel):
    """Modelo base para serviços."""
    source: ServiceSource = Field(..., description="Fonte do serviço (SINAPI, SICRO, CPOS, EMOP, CRIADA)")
    origin_file: str = Field(..., max_length=500, description="Arquivo de origem do dado")
    service_code: str = Field(..., max_length=100, description="Código do serviço")
    base_date: date = Field(..., description="Data base do preço")
    description: str = Field(..., min_length=10, max_length=1000, description="Descrição do serviço")
    is_loaded: bool = Field(..., description="Se é onerado (True) ou desonerado (False)")
    value: Decimal = Field(..., ge=Decimal("0.01"), le=Decimal("999999999.99"), description="Valor em R$")

    @validator('description')
    def validate_description(cls, v):
        """Valida a descrição do serviço."""
        if not v.strip():
            raise ValueError("Descrição não pode estar vazia")
        return v.strip()

    @validator('service_code')
    def validate_service_code(cls, v):
        """Valida o código do serviço."""
        if not v.strip():
            raise ValueError("Código do serviço não pode estar vazio")
        return v.strip().upper()

    @validator('origin_file')
    def validate_origin_file(cls, v):
        """Valida o arquivo de origem."""
        if not v.strip():
            raise ValueError("Arquivo de origem não pode estar vazio")
        return v.strip()

class ServiceCreate(ServiceBase):
    """Modelo para criação de serviços."""
    pass

class ServiceUpdate(BaseModel):
    """Modelo para atualização de serviços."""
    source: Optional[ServiceSource] = Field(None, description="Fonte do serviço")
    origin_file: Optional[str] = Field(None, max_length=500, description="Arquivo de origem")
    service_code: Optional[str] = Field(None, max_length=100, description="Código do serviço")
    base_date: Optional[date] = Field(None, description="Data base do preço")
    description: Optional[str] = Field(None, min_length=10, max_length=1000, description="Descrição")
    is_loaded: Optional[bool] = Field(None, description="Se é onerado")
    value: Optional[Decimal] = Field(None, ge=Decimal("0.01"), le=Decimal("999999999.99"), description="Valor")

class Service(ServiceBase):
    """Modelo completo de serviço com ID e timestamps."""
    id: int = Field(..., description="ID único do serviço")
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação")
    updated_at: datetime = Field(default_factory=datetime.now, description="Data de atualização")

    class Config:
        """Configurações do modelo."""
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }

    @property
    def service_type(self) -> ServiceType:
        """Retorna o tipo do serviço baseado no campo is_loaded."""
        return ServiceType.ONERADO if self.is_loaded else ServiceType.DESONERADO

    @property
    def formatted_value(self) -> str:
        """Retorna o valor formatado em reais."""
        return f"R$ {self.value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def to_dict(self) -> dict:
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "source": self.source.value,
            "origin_file": self.origin_file,
            "service_code": self.service_code,
            "base_date": self.base_date.isoformat(),
            "description": self.description,
            "is_loaded": self.is_loaded,
            "service_type": self.service_type.value,
            "value": float(self.value),
            "formatted_value": self.formatted_value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __str__(self) -> str:
        """Representação string do serviço."""
        return f"Serviço {self.service_code} - {self.description[:50]}... - {self.formatted_value}"

    def __repr__(self) -> str:
        """Representação detalhada do serviço."""
        return f"Service(id={self.id}, code='{self.service_code}', source='{self.source.value}', value={self.value})" 