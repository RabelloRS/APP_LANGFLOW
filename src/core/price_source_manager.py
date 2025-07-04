"""
Gerenciador de fontes de dados de preços baseado nas práticas do priceAPI.
Adaptado do projeto: https://github.com/yorikvanhavre/priceAPI
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

from config.config import get_config
from src.utils.logger import get_logger
from src.database.db_manager import db_manager

logger = get_logger("price_source_manager")

@dataclass
class PriceSource:
    """Fonte de dados de preços baseada no priceAPI."""
    name: str
    month: int
    year: int
    currency: str
    download_url: Optional[str] = None
    check_url: Optional[str] = None
    data_file: Optional[str] = None
    cub_value: Optional[float] = None
    location: Optional[str] = None
    description: Optional[str] = None

class BasePriceSource(ABC):
    """Classe base para fontes de dados de preços."""
    
    def __init__(self, source_config: PriceSource):
        self.config = source_config
        self.data = []
        self.logger = get_logger(f"source_{source_config.name.lower()}")
    
    @abstractmethod
    def build(self) -> bool:
        """Constrói/atualiza os dados da fonte."""
        pass
    
    @abstractmethod
    def parse_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse dos dados do arquivo."""
        pass
    
    def save_to_database(self, services: List[Dict[str, Any]]) -> int:
        """Salva serviços no banco de dados."""
        saved_count = 0
        for service in services:
            try:
                service_id = db_manager.insert_service(service)
                if service_id:
                    saved_count += 1
            except Exception as e:
                self.logger.error(f"Erro ao salvar serviço: {e}")
        
        self.logger.info(f"Salvos {saved_count} serviços da fonte {self.config.name}")
        return saved_count

class SINAPISource(BasePriceSource):
    """Fonte de dados SINAPI."""
    
    def build(self) -> bool:
        """Constrói dados SINAPI."""
        try:
            if not self.config.data_file or not Path(self.config.data_file).exists():
                self.logger.error(f"Arquivo de dados não encontrado: {self.config.data_file}")
                return False
            
            services = self.parse_data(self.config.data_file)
            saved_count = self.save_to_database(services)
            
            self.logger.info(f"Fonte SINAPI construída com {saved_count} serviços")
            return saved_count > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao construir fonte SINAPI: {e}")
            return False
    
    def parse_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse de dados SINAPI."""
        services = []
        
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        service = self._parse_sinapi_row(row)
                        if service:
                            services.append(service)
            
            elif file_path.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    service = self._parse_sinapi_row(row.to_dict())
                    if service:
                        services.append(service)
        
        except Exception as e:
            self.logger.error(f"Erro ao fazer parse dos dados: {e}")
        
        return services
    
    def _parse_sinapi_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse de uma linha de dados SINAPI."""
        try:
            # Mapeamento de colunas SINAPI
            code = str(row.get('CODIGO', row.get('CÓDIGO', ''))).strip()
            description = str(row.get('DESCRICAO', row.get('DESCRIÇÃO', ''))).strip()
            unit = str(row.get('UNIDADE', '')).strip()
            price_str = str(row.get('PRECO', row.get('PREÇO', '0'))).strip()
            
            # Limpeza e validação
            if not code or not description:
                return None
            
            # Conversão de preço
            try:
                price = float(price_str.replace(',', '.').replace('R$', '').strip())
            except ValueError:
                price = 0.0
            
            # Determinação da fonte
            source = "sinapi"
            if "sp" in self.config.name.lower():
                source = "sinapi_sp"
            elif "ce" in self.config.name.lower():
                source = "sinapi_ce"
            
            return {
                "source": source,
                "origin_file": self.config.data_file,
                "service_code": code,
                "base_date": f"{self.config.year}-{self.config.month:02d}-01",
                "description": description,
                "is_loaded": True,  # SINAPI é sempre onerado
                "value": price
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao parsear linha SINAPI: {e}")
            return None

class SICROSource(BasePriceSource):
    """Fonte de dados SICRO."""
    
    def build(self) -> bool:
        """Constrói dados SICRO."""
        try:
            if not self.config.data_file or not Path(self.config.data_file).exists():
                self.logger.error(f"Arquivo de dados não encontrado: {self.config.data_file}")
                return False
            
            services = self.parse_data(self.config.data_file)
            saved_count = self.save_to_database(services)
            
            self.logger.info(f"Fonte SICRO construída com {saved_count} serviços")
            return saved_count > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao construir fonte SICRO: {e}")
            return False
    
    def parse_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse de dados SICRO."""
        services = []
        
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        service = self._parse_sicro_row(row)
                        if service:
                            services.append(service)
            
            elif file_path.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    service = self._parse_sicro_row(row.to_dict())
                    if service:
                        services.append(service)
        
        except Exception as e:
            self.logger.error(f"Erro ao fazer parse dos dados SICRO: {e}")
        
        return services
    
    def _parse_sicro_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse de uma linha de dados SICRO."""
        try:
            # Mapeamento de colunas SICRO
            code = str(row.get('CODIGO', row.get('CÓDIGO', ''))).strip()
            description = str(row.get('DESCRICAO', row.get('DESCRIÇÃO', ''))).strip()
            unit = str(row.get('UNIDADE', '')).strip()
            price_str = str(row.get('PRECO', row.get('PREÇO', '0'))).strip()
            
            # Limpeza e validação
            if not code or not description:
                return None
            
            # Conversão de preço
            try:
                price = float(price_str.replace(',', '.').replace('R$', '').strip())
            except ValueError:
                price = 0.0
            
            return {
                "source": "sicro",
                "origin_file": self.config.data_file,
                "service_code": code,
                "base_date": f"{self.config.year}-{self.config.month:02d}-01",
                "description": description,
                "is_loaded": True,  # SICRO é sempre onerado
                "value": price
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao parsear linha SICRO: {e}")
            return None

class PriceSourceManager:
    """Gerenciador de fontes de dados de preços."""
    
    def __init__(self):
        self.sources: Dict[str, BasePriceSource] = {}
        self.logger = get_logger("price_source_manager")
        self._load_sources()
    
    def _load_sources(self):
        """Carrega as fontes de dados configuradas."""
        sources_config = get_config("engineering_keywords")
        
        # Configurar fontes baseadas no priceAPI
        self._add_source(SINAPISource(PriceSource(
            name="SINAPI-SP",
            month=1,
            year=2024,
            currency="BRL",
            data_file="data/sinapi_sp.xlsx",
            location="São Paulo",
            description="Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil - SP"
        )))
        
        self._add_source(SICROSource(PriceSource(
            name="SICRO",
            month=1,
            year=2024,
            currency="BRL",
            data_file="data/sicro.xlsx",
            location="Nacional",
            description="Sistema de Custos Rodoviários"
        )))
    
    def _add_source(self, source: BasePriceSource):
        """Adiciona uma fonte de dados."""
        self.sources[source.config.name] = source
        self.logger.info(f"Fonte adicionada: {source.config.name}")
    
    def build_all_sources(self) -> Dict[str, bool]:
        """Constrói todas as fontes de dados."""
        results = {}
        
        for name, source in self.sources.items():
            self.logger.info(f"Construindo fonte: {name}")
            try:
                success = source.build()
                results[name] = success
                self.logger.info(f"Fonte {name}: {'SUCESSO' if success else 'FALHA'}")
            except Exception as e:
                self.logger.error(f"Erro ao construir fonte {name}: {e}")
                results[name] = False
        
        return results
    
    def search_services(self, search_terms: List[str], 
                       source_filter: Optional[str] = None,
                       location_filter: Optional[str] = None,
                       code_filter: Optional[str] = None,
                       cub_conversion: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Busca serviços baseada no sistema do priceAPI.
        
        Args:
            search_terms: Lista de termos de busca (AND)
            source_filter: Filtro por fonte específica
            location_filter: Filtro por localização
            code_filter: Busca por código específico
            cub_conversion: Conversão por CUB
        """
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Construir query base
                query = """
                    SELECT s.*, pf.file_name, pf.ai_classification, pf.ai_confidence
                    FROM services s
                    LEFT JOIN processed_files pf ON s.origin_file = pf.file_path
                    WHERE 1=1
                """
                params = []
                
                # Filtro por fonte
                if source_filter:
                    query += " AND s.source = ?"
                    params.append(source_filter)
                
                # Filtro por localização (se implementado)
                if location_filter:
                    # Implementar quando tivermos dados de localização
                    pass
                
                # Busca por código
                if code_filter:
                    query += " AND s.service_code LIKE ?"
                    params.append(f"%{code_filter.replace('.', '').replace('-', '')}%")
                
                # Busca por termos
                if search_terms:
                    for term in search_terms:
                        query += " AND (s.description LIKE ? OR s.service_code LIKE ?)"
                        params.extend([f"%{term}%", f"%{term}%"])
                
                # Ordenação
                query += " ORDER BY s.source, s.service_code"
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                
                # Conversão por CUB se especificado
                if cub_conversion:
                    results = self._convert_by_cub(results, cub_conversion)
                
                return results
        
        except Exception as e:
            self.logger.error(f"Erro na busca: {e}")
            return []
    
    def _convert_by_cub(self, services: List[Dict[str, Any]], target_cub: float) -> List[Dict[str, Any]]:
        """Converte preços por CUB (baseado no priceAPI)."""
        # Implementar conversão por CUB
        # Por enquanto, retorna os serviços sem conversão
        return services
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas das fontes de dados."""
        return db_manager.get_statistics()

# Instância global do gerenciador
price_source_manager = PriceSourceManager() 