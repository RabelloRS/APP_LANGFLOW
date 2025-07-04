"""
Classificador AI para o Sistema RAG de Planilhas.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime

from src.database.db_manager import db_manager
from src.utils.logger import get_logger

class AIClassifier:
    """Classificador AI para planilhas de preços."""
    
    def __init__(self, model_path=None, training_data_path=None):
        self.logger = get_logger("ai_classifier")
        
        # Caminhos
        self.model_path = Path(model_path) if model_path else Path("data/ai_models/classifier_model.pkl")
        self.training_data_path = Path(training_data_path) if training_data_path else Path("data/training_data")
        
        # Criar diretórios
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.training_data_path.mkdir(parents=True, exist_ok=True)
        
        # Modelo
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Palavras-chave
        self.price_keywords = {
            'sinapi': ['sinapi', 'sistema nacional', 'caixa econômica'],
            'sicro': ['sicro', 'sistema de custos', 'dnit'],
            'siconv': ['siconv', 'sistema de convênios'],
            'preços': ['preço', 'valor', 'custo', 'composição'],
            'serviços': ['serviço', 'item', 'código', 'descrição']
        }
        
        self.load_model()
        self.logger.info("AI Classifier inicializado")
    
    def load_model(self):
        """Carrega modelo treinado."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.feature_names = model_data['feature_names']
                    self.is_trained = True
                    self.logger.info("Modelo carregado")
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {e}")
    
    def save_model(self):
        """Salva modelo treinado."""
        try:
            if self.model is not None:
                model_data = {
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'trained_at': datetime.now()
                }
                with open(self.model_path, 'wb') as f:
                    pickle.dump(model_data, f)
                self.logger.info("Modelo salvo")
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo: {e}")
    
    def extract_features(self, file_path: Path) -> Dict[str, float]:
        """Extrai features de um arquivo."""
        features = {}
        
        try:
            features['file_size'] = file_path.stat().st_size
            features['file_extension'] = file_path.suffix.lower()
            
            content = self.extract_file_content(file_path)
            
            if content:
                # Features de palavras-chave
                for category, keywords in self.price_keywords.items():
                    count = sum(content.lower().count(keyword.lower()) for keyword in keywords)
                    features[f'keyword_{category}'] = count
                
                # Features estruturais
                features['has_tables'] = 1.0 if any(marker in content.lower() for marker in ['tabela', 'planilha']) else 0.0
                features['has_numbers'] = 1.0 if any(char.isdigit() for char in content) else 0.0
                features['has_currency'] = 1.0 if any(marker in content for marker in ['r$', 'valor']) else 0.0
                features['content_length'] = len(content)
                features['word_count'] = len(content.split())
            else:
                # Valores padrão
                for category in self.price_keywords.keys():
                    features[f'keyword_{category}'] = 0.0
                features['has_tables'] = 0.0
                features['has_numbers'] = 0.0
                features['has_currency'] = 0.0
                features['content_length'] = 0.0
                features['word_count'] = 0.0
        
        except Exception as e:
            self.logger.error(f"Erro ao extrair features: {e}")
            for category in self.price_keywords.keys():
                features[f'keyword_{category}'] = 0.0
            features['has_tables'] = 0.0
            features['has_numbers'] = 0.0
            features['has_currency'] = 0.0
            features['content_length'] = 0.0
            features['word_count'] = 0.0
        
        return features
    
    def extract_file_content(self, file_path: Path) -> Optional[str]:
        """Extrai conteúdo do arquivo."""
        try:
            extension = file_path.suffix.lower()
            
            if extension in ['.txt', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            elif extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=None)
                content = ""
                for sheet_name, sheet_df in df.items():
                    content += f"Sheet: {sheet_name}\n"
                    content += sheet_df.to_string() + "\n\n"
                return content
            
            elif extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except:
                    return f"Binary file: {file_path.name}"
        
        except Exception as e:
            self.logger.error(f"Erro ao extrair conteúdo: {e}")
            return None
    
    def classify_file(self, file_path: Path) -> Dict[str, any]:
        """Classifica um arquivo."""
        try:
            features = self.extract_features(file_path)
            
            if not self.is_trained:
                return self.classify_with_rules(features, file_path)
            
            return self.classify_with_model(features, file_path)
        
        except Exception as e:
            self.logger.error(f"Erro ao classificar: {e}")
            return {
                'is_relevant': False,
                'confidence': 0.0,
                'reason': f'Erro: {str(e)}',
                'features': {}
            }
    
    def classify_with_rules(self, features: Dict[str, float], file_path: Path) -> Dict[str, any]:
        """Classificação baseada em regras."""
        score = 0.0
        reasons = []
        
        # Verificar extensão
        if features['file_extension'] in ['.xlsx', '.xls', '.csv']:
            score += 0.3
            reasons.append("Arquivo de planilha")
        
        # Verificar palavras-chave
        for category, keywords in self.price_keywords.items():
            if features[f'keyword_{category}'] > 0:
                score += 0.2
                reasons.append(f"Contém {category}")
        
        # Verificar estrutura
        if features['has_tables']:
            score += 0.2
            reasons.append("Possui tabelas")
        
        if features['has_currency']:
            score += 0.2
            reasons.append("Contém valores")
        
        is_relevant = score >= 0.5
        
        return {
            'is_relevant': is_relevant,
            'confidence': min(score, 1.0),
            'reason': '; '.join(reasons) if reasons else 'Sem características relevantes',
            'features': features,
            'method': 'rules'
        }
    
    def classify_with_model(self, features: Dict[str, float], file_path: Path) -> Dict[str, any]:
        """Classificação com modelo."""
        try:
            if self.model is None:
                return self.classify_with_rules(features, file_path)
            
            feature_vector = [features.get(feature_name, 0.0) for feature_name in self.feature_names]
            
            prediction = self.model.predict([feature_vector])[0]
            probability = self.model.predict_proba([feature_vector])[0]
            
            confidence = max(probability)
            is_relevant = bool(prediction)
            
            return {
                'is_relevant': is_relevant,
                'confidence': confidence,
                'reason': f'Modelo (confiança: {confidence:.2f})',
                'features': features,
                'method': 'model'
            }
        
        except Exception as e:
            self.logger.error(f"Erro no modelo: {e}")
            return self.classify_with_rules(features, file_path)
    
    def get_status(self):
        """Retorna status do classificador."""
        return {
            "is_trained": self.is_trained,
            "model_path": str(self.model_path),
            "training_data_path": str(self.training_data_path),
            "feature_count": len(self.feature_names) if self.feature_names else 0
        }

# Instância global
ai_classifier = AIClassifier() 