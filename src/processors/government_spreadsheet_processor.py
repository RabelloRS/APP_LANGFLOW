"""
Processador de planilhas governamentais baseado no SICONV.
Adaptado do projeto: https://github.com/fbrandao2k/SICONV

Este módulo processa planilhas de orçamento governamental brasileiro,
incluindo SINAPI, SICRO e outros sistemas oficiais.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

from config.config import get_config
from src.utils.logger import get_logger
from src.database.db_manager import db_manager

logger = get_logger("government_spreadsheet_processor")

class GovernmentSpreadsheetProcessor:
    """Processador de planilhas governamentais brasileiras."""
    
    def __init__(self):
        self.config = get_config("engineering_keywords")
        self.logger = get_logger("government_processor")
        
        # Padrões de identificação de planilhas governamentais
        self.government_patterns = {
            'sinapi': [
                r'sinapi',
                r'sistema.*nacional.*pesquisa.*custos',
                r'caixa.*econômica.*federal',
                r'preços.*unitários'
            ],
            'sicro': [
                r'sicro',
                r'sistema.*custos.*rodoviários',
                r'dnit',
                r'rodovias'
            ],
            'siconv': [
                r'siconv',
                r'sistema.*convênios',
                r'convênios.*transferência',
                r'governo.*federal'
            ],
            'cpos': [
                r'cpos',
                r'composição.*preços.*serviços',
                r'composições.*preços'
            ],
            'emop': [
                r'emop',
                r'empresa.*municipal.*obras',
                r'prefeitura.*municipal'
            ]
        }
        
        # Estruturas de dados esperadas
        self.expected_columns = {
            'sinapi': ['CODIGO', 'DESCRICAO', 'UNIDADE', 'PRECO', 'DATA'],
            'sicro': ['CODIGO', 'DESCRICAO', 'UNIDADE', 'PRECO', 'FRENTE'],
            'siconv': ['CODIGO', 'DESCRICAO', 'UNIDADE', 'PRECO', 'BDI'],
            'cpos': ['CODIGO', 'DESCRICAO', 'UNIDADE', 'PRECO', 'COMPOSICAO'],
            'emop': ['CODIGO', 'DESCRICAO', 'UNIDADE', 'PRECO', 'MUNICIPIO']
        }
    
    def identify_government_system(self, file_path: str) -> Optional[str]:
        """
        Identifica o sistema governamental baseado no conteúdo da planilha.
        Baseado na análise do SICONV.
        """
        try:
            # Ler todas as abas da planilha
            excel_file = pd.ExcelFile(file_path)
            
            # Verificar nomes das abas
            sheet_names = [sheet.lower() for sheet in excel_file.sheet_names]
            
            # Padrões de abas específicas
            if 'orçamento' in sheet_names or 'orcamento' in sheet_names:
                if 'cálculo' in sheet_names or 'calculo' in sheet_names:
                    return 'siconv'
            
            # Verificar conteúdo das abas
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
                
                # Verificar colunas
                columns = [col.lower() for col in df.columns]
                
                # Padrões específicos por sistema
                for system, patterns in self.government_patterns.items():
                    for pattern in patterns:
                        # Verificar em colunas
                        for col in columns:
                            if re.search(pattern, col, re.IGNORECASE):
                                return system
                        
                        # Verificar em dados
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                sample_data = df[col].dropna().astype(str).str.lower()
                                if any(sample_data.str.contains(pattern, regex=True, na=False)):
                                    return system
            
            return None
        
        except Exception as e:
            self.logger.error(f"Erro ao identificar sistema governamental: {e}")
            return None
    
    def process_siconv_spreadsheet(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Processa planilha SICONV baseado no projeto original.
        """
        services = []
        
        try:
            # Ler abas específicas do SICONV
            orcamento_df = pd.read_excel(file_path, sheet_name='ORÇAMENTO')
            calculo_df = pd.read_excel(file_path, sheet_name='CÁLCULO')
            
            self.logger.info(f"Processando planilha SICONV: {file_path}")
            self.logger.info(f"Orçamento: {len(orcamento_df)} linhas")
            self.logger.info(f"Cálculo: {len(calculo_df)} linhas")
            
            # Processar dados de orçamento
            for _, row in orcamento_df.iterrows():
                service = self._parse_siconv_row(row, 'orcamento', file_path)
                if service:
                    services.append(service)
            
            # Processar dados de cálculo
            for _, row in calculo_df.iterrows():
                service = self._parse_siconv_row(row, 'calculo', file_path)
                if service:
                    services.append(service)
            
            self.logger.info(f"Processados {len(services)} serviços SICONV")
            return services
        
        except Exception as e:
            self.logger.error(f"Erro ao processar planilha SICONV: {e}")
            return []
    
    def _parse_siconv_row(self, row: pd.Series, sheet_type: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse de uma linha de dados SICONV."""
        try:
            # Mapeamento de colunas SICONV
            code = str(row.get('CODIGO', row.get('CÓDIGO', ''))).strip()
            description = str(row.get('DESCRICAO', row.get('DESCRIÇÃO', ''))).strip()
            unit = str(row.get('UNIDADE', '')).strip()
            price_str = str(row.get('PRECO', row.get('PREÇO', '0'))).strip()
            bdi = row.get('BDI', 0)
            quantity = row.get('QUANTIDADE', row.get('QTD', 1))
            
            # Validação básica
            if not code or not description:
                return None
            
            # Conversão de preço
            try:
                price = float(price_str.replace(',', '.').replace('R$', '').strip())
            except ValueError:
                price = 0.0
            
            # Cálculo de BDI (Budget Difference Index)
            bdi_value = 0.0
            if pd.notna(bdi):
                try:
                    bdi_value = float(bdi)
                except (ValueError, TypeError):
                    bdi_value = 0.0
            
            final_price = price * (1 + bdi_value / 100) if bdi_value > 0 else price
            
            # Processamento de quantidade
            quantity_value = 1.0
            if pd.notna(quantity):
                try:
                    quantity_value = float(quantity)
                except (ValueError, TypeError):
                    quantity_value = 1.0
            
            return {
                "source": "siconv",
                "origin_file": str(file_path),
                "service_code": code,
                "base_date": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "is_loaded": True,  # SICONV é sempre onerado
                "value": final_price,
                "unit": unit,
                "bdi": bdi_value,
                "quantity": quantity_value,
                "sheet_type": sheet_type
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao parsear linha SICONV: {e}")
            return None
    
    def process_sinapi_spreadsheet(self, file_path: str) -> List[Dict[str, Any]]:
        """Processa planilha SINAPI."""
        services = []
        
        try:
            df = pd.read_excel(file_path)
            self.logger.info(f"Processando planilha SINAPI: {file_path}")
            
            for _, row in df.iterrows():
                service = self._parse_sinapi_row(row, file_path)
                if service:
                    services.append(service)
            
            self.logger.info(f"Processados {len(services)} serviços SINAPI")
            return services
        
        except Exception as e:
            self.logger.error(f"Erro ao processar planilha SINAPI: {e}")
            return []
    
    def _parse_sinapi_row(self, row: pd.Series, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse de uma linha de dados SINAPI."""
        try:
            # Mapeamento de colunas SINAPI
            code = str(row.get('CODIGO', row.get('CÓDIGO', ''))).strip()
            description = str(row.get('DESCRICAO', row.get('DESCRIÇÃO', ''))).strip()
            unit = str(row.get('UNIDADE', '')).strip()
            price_str = str(row.get('PRECO', row.get('PREÇO', '0'))).strip()
            date_str = str(row.get('DATA', row.get('DATA_BASE', ''))).strip()
            
            # Validação
            if not code or not description:
                return None
            
            # Conversão de preço
            try:
                price = float(price_str.replace(',', '.').replace('R$', '').strip())
            except ValueError:
                price = 0.0
            
            # Processamento de data
            try:
                if pd.notna(date_str) and date_str.strip():
                    base_date = pd.to_datetime(date_str).strftime("%Y-%m-%d")
                else:
                    base_date = datetime.now().strftime("%Y-%m-%d")
            except:
                base_date = datetime.now().strftime("%Y-%m-%d")
            
            return {
                "source": "sinapi",
                "origin_file": str(file_path),
                "service_code": code,
                "base_date": base_date,
                "description": description,
                "is_loaded": True,
                "value": price,
                "unit": unit
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao parsear linha SINAPI: {e}")
            return None
    
    def process_sicro_spreadsheet(self, file_path: str) -> List[Dict[str, Any]]:
        """Processa planilha SICRO."""
        services = []
        
        try:
            df = pd.read_excel(file_path)
            self.logger.info(f"Processando planilha SICRO: {file_path}")
            
            for _, row in df.iterrows():
                service = self._parse_sicro_row(row, file_path)
                if service:
                    services.append(service)
            
            self.logger.info(f"Processados {len(services)} serviços SICRO")
            return services
        
        except Exception as e:
            self.logger.error(f"Erro ao processar planilha SICRO: {e}")
            return []
    
    def _parse_sicro_row(self, row: pd.Series, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse de uma linha de dados SICRO."""
        try:
            # Mapeamento de colunas SICRO
            code = str(row.get('CODIGO', row.get('CÓDIGO', ''))).strip()
            description = str(row.get('DESCRICAO', row.get('DESCRIÇÃO', ''))).strip()
            unit = str(row.get('UNIDADE', '')).strip()
            price_str = str(row.get('PRECO', row.get('PREÇO', '0'))).strip()
            frente = str(row.get('FRENTE', row.get('FRENTE_TRABALHO', ''))).strip()
            
            # Validação
            if not code or not description:
                return None
            
            # Conversão de preço
            try:
                price = float(price_str.replace(',', '.').replace('R$', '').strip())
            except ValueError:
                price = 0.0
            
            return {
                "source": "sicro",
                "origin_file": str(file_path),
                "service_code": code,
                "base_date": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "is_loaded": True,
                "value": price,
                "unit": unit,
                "frente_trabalho": frente
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao parsear linha SICRO: {e}")
            return None
    
    def process_government_spreadsheet(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Processa planilha governamental identificando automaticamente o sistema.
        """
        try:
            # Identificar sistema governamental
            system = self.identify_government_system(file_path)
            
            if not system:
                self.logger.warning(f"Sistema governamental não identificado: {file_path}")
                return "unknown", []
            
            self.logger.info(f"Sistema identificado: {system} para {file_path}")
            
            # Processar baseado no sistema
            if system == 'siconv':
                services = self.process_siconv_spreadsheet(file_path)
            elif system == 'sinapi':
                services = self.process_sinapi_spreadsheet(file_path)
            elif system == 'sicro':
                services = self.process_sicro_spreadsheet(file_path)
            else:
                self.logger.warning(f"Sistema não suportado: {system}")
                return system, []
            
            # Salvar no banco de dados
            saved_count = 0
            for service in services:
                try:
                    service_id = db_manager.insert_service(service)
                    if service_id:
                        saved_count += 1
                except Exception as e:
                    self.logger.error(f"Erro ao salvar serviço: {e}")
            
            self.logger.info(f"Salvos {saved_count} serviços do sistema {system}")
            return system, services
        
        except Exception as e:
            self.logger.error(f"Erro ao processar planilha governamental: {e}")
            return "error", []
    
    def calculate_bdi(self, base_price: float, bdi_percentage: float) -> float:
        """
        Calcula preço com BDI (Budget Difference Index).
        Baseado no SICONV.
        """
        return base_price * (1 + bdi_percentage / 100)
    
    def validate_government_data(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valida dados governamentais baseado em regras específicas.
        """
        validated_services = []
        
        for service in services:
            # Validações básicas
            if not service.get('service_code'):
                self.logger.warning(f"Serviço sem código: {service.get('description', 'N/A')}")
                continue
            
            if not service.get('description'):
                self.logger.warning(f"Serviço sem descrição: {service.get('service_code', 'N/A')}")
                continue
            
            if service.get('value', 0) <= 0:
                self.logger.warning(f"Serviço com preço inválido: {service.get('service_code', 'N/A')}")
                continue
            
            # Validações específicas por fonte
            source = service.get('source', '')
            
            if source == 'sinapi':
                # Validar formato de código SINAPI
                code = service.get('service_code', '')
                if not re.match(r'^\d{5,6}$', code.replace('.', '').replace('-', '')):
                    self.logger.warning(f"Código SINAPI inválido: {code}")
                    continue
            
            elif source == 'sicro':
                # Validar formato de código SICRO
                code = service.get('service_code', '')
                if not re.match(r'^[A-Z]\d{3,4}$', code):
                    self.logger.warning(f"Código SICRO inválido: {code}")
                    continue
            
            validated_services.append(service)
        
        self.logger.info(f"Validados {len(validated_services)} de {len(services)} serviços")
        return validated_services

# Instância global do processador
government_processor = GovernmentSpreadsheetProcessor() 