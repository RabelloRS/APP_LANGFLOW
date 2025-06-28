#!/usr/bin/env python3
"""
Sistema RAG para Planilhas de Orçamento - Solução Local
=======================================================

Este script cria um sistema RAG completo para processar planilhas de orçamento
usando ChromaDB (banco vetorial local) e Ollama (LLM local).

Funcionalidades:
- Lê todas as planilhas da pasta especificada
- Extrai dados estruturados das planilhas
- Cria embeddings usando modelo local
- Armazena no ChromaDB local
- Permite consultas inteligentes sobre orçamentos
"""

import os
import pandas as pd
import json
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGPlanilhasLocal:
    def __init__(self, pasta_docs: str = "D:\\docs_baixados", db_path: str = "./chroma_db"):
        """
        Inicializa o sistema RAG para planilhas
        
        Args:
            pasta_docs: Pasta onde estão as planilhas de orçamento
            db_path: Pasta onde será criado o banco ChromaDB
        """
        self.pasta_docs = Path(pasta_docs)
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Criar ou obter coleção
        self.collection = self.client.get_or_create_collection(
            name="orcamentos_planilhas",
            metadata={"description": "Planilhas de orçamento processadas"}
        )
        
        logger.info(f"Sistema RAG inicializado - Pasta: {self.pasta_docs}, DB: {self.db_path}")
    
    def encontrar_planilhas(self) -> List[Path]:
        """
        Encontra todas as planilhas na pasta especificada e subpastas
        
        Returns:
            Lista de caminhos para as planilhas encontradas
        """
        if not self.pasta_docs.exists():
            logger.error(f"Pasta não encontrada: {self.pasta_docs}")
            return []
        
        # Padrões de arquivos de planilha
        padroes = ["*.xlsx", "*.xls", "*.csv", "*.xlsm"]
        planilhas = []
        
        # Procurar recursivamente em todas as subpastas
        for padrao in padroes:
            arquivos = list(self.pasta_docs.rglob(padrao))  # rglob para busca recursiva
            planilhas.extend(arquivos)
        
        logger.info(f"Encontradas {len(planilhas)} planilhas em {self.pasta_docs} (incluindo subpastas)")
        return planilhas
    
    def extrair_dados_planilha(self, caminho_planilha: Path) -> Dict[str, Any]:
        """
        Extrai dados estruturados de uma planilha
        
        Args:
            caminho_planilha: Caminho para a planilha
            
        Returns:
            Dicionário com dados extraídos
        """
        try:
            # Detectar tipo de arquivo
            extensao = caminho_planilha.suffix.lower()
            
            if extensao == '.csv':
                df = pd.read_csv(caminho_planilha, encoding='utf-8')
            else:
                df = pd.read_excel(caminho_planilha)
            
            # Informações básicas
            dados = {
                "arquivo": caminho_planilha.name,
                "caminho": str(caminho_planilha),
                "tamanho_arquivo": caminho_planilha.stat().st_size,
                "data_modificacao": datetime.fromtimestamp(caminho_planilha.stat().st_mtime).isoformat(),
                "colunas": df.columns.tolist(),
                "linhas": len(df),
                "colunas_count": len(df.columns),
                "tipos_dados": df.dtypes.to_dict()
            }
            
            # Detectar se é planilha de orçamento
            colunas_texto = [col.lower() for col in df.columns]
            palavras_chave_orcamento = [
                'orcamento', 'preço', 'valor', 'custo', 'total', 'cliente',
                'produto', 'serviço', 'quantidade', 'unitário', 'subtotal'
            ]
            
            score_orcamento = sum(1 for palavra in palavras_chave_orcamento 
                                if any(palavra in col for col in colunas_texto))
            
            dados["tipo_documento"] = "orcamento" if score_orcamento >= 2 else "planilha_geral"
            dados["score_orcamento"] = score_orcamento
            
            # Extrair amostra de dados (primeiras 5 linhas)
            dados["amostra_dados"] = df.head().to_dict('records')
            
            # Estatísticas básicas
            dados["estatisticas"] = {
                "colunas_numericas": len(df.select_dtypes(include=[np.number]).columns),
                "colunas_texto": len(df.select_dtypes(include=['object']).columns),
                "colunas_data": len(df.select_dtypes(include=['datetime']).columns),
                "valores_unicos_por_coluna": {col: df[col].nunique() for col in df.columns}
            }
            
            # Criar texto para embedding
            texto_embedding = self._criar_texto_embedding(df, dados)
            dados["texto_embedding"] = texto_embedding
            
            logger.info(f"Extraídos dados de: {caminho_planilha.name} ({len(df)} linhas)")
            return dados
            
        except Exception as e:
            logger.error(f"Erro ao processar {caminho_planilha}: {e}")
            return {
                "arquivo": caminho_planilha.name,
                "erro": str(e),
                "texto_embedding": f"Erro ao processar arquivo {caminho_planilha.name}: {e}"
            }
    
    def _criar_texto_embedding(self, df: pd.DataFrame, dados: Dict) -> str:
        """
        Cria texto estruturado para embedding baseado nos dados da planilha
        
        Args:
            df: DataFrame da planilha
            dados: Dados extraídos da planilha
            
        Returns:
            Texto estruturado para embedding
        """
        linhas = []
        
        # Informações do arquivo
        linhas.append(f"Arquivo: {dados['arquivo']}")
        linhas.append(f"Tipo: {dados['tipo_documento']}")
        linhas.append(f"Colunas: {', '.join(dados['colunas'])}")
        linhas.append(f"Total de linhas: {dados['linhas']}")
        
        # Cabeçalho
        linhas.append(f"Cabeçalho: {' | '.join(dados['colunas'])}")
        
        # Amostra de dados (primeiras 3 linhas)
        for i, linha in enumerate(dados['amostra_dados'][:3]):
            valores = [str(v) for v in linha.values()]
            linhas.append(f"Linha {i+1}: {' | '.join(valores)}")
        
        # Estatísticas
        stats = dados['estatisticas']
        linhas.append(f"Colunas numéricas: {stats['colunas_numericas']}")
        linhas.append(f"Colunas de texto: {stats['colunas_texto']}")
        
        # Valores únicos importantes
        for col, unicos in stats['valores_unicos_por_coluna'].items():
            if unicos <= 20 and unicos > 1:  # Colunas com poucos valores únicos
                valores_unicos = df[col].dropna().unique()[:5]  # Primeiros 5 valores
                linhas.append(f"Valores únicos em {col}: {', '.join(map(str, valores_unicos))}")
        
        return "\n".join(linhas)
    
    def processar_todas_planilhas(self) -> List[Dict[str, Any]]:
        """
        Processa todas as planilhas encontradas na pasta
        
        Returns:
            Lista com dados de todas as planilhas processadas
        """
        planilhas = self.encontrar_planilhas()
        if not planilhas:
            return []
        
        dados_processados = []
        
        for planilha in planilhas:
            logger.info(f"Processando: {planilha.name}")
            dados = self.extrair_dados_planilha(planilha)
            dados_processados.append(dados)
        
        logger.info(f"Processadas {len(dados_processados)} planilhas")
        return dados_processados
    
    def adicionar_ao_chromadb(self, dados_planilhas: List[Dict[str, Any]]):
        """
        Adiciona os dados processados ao ChromaDB
        
        Args:
            dados_planilhas: Lista com dados das planilhas processadas
        """
        if not dados_planilhas:
            logger.warning("Nenhum dado para adicionar ao ChromaDB")
            return
        
        # Preparar dados para ChromaDB
        ids = []
        documentos = []
        metadados = []
        
        for i, dados in enumerate(dados_planilhas):
            if "erro" in dados:
                continue  # Pular arquivos com erro
            
            doc_id = f"planilha_{i}_{dados['arquivo']}"
            ids.append(doc_id)
            documentos.append(dados['texto_embedding'])
            
            # Metadados para busca
            metadados.append({
                "arquivo": dados['arquivo'],
                "tipo": dados['tipo_documento'],
                "colunas": ", ".join(dados['colunas']),
                "linhas": dados['linhas'],
                "data_modificacao": dados['data_modificacao'],
                "score_orcamento": dados['score_orcamento']
            })
        
        # Adicionar ao ChromaDB
        if ids:
            self.collection.add(
                ids=ids,
                documents=documentos,
                metadatas=metadados
            )
            logger.info(f"Adicionados {len(ids)} documentos ao ChromaDB")
    
    def buscar_orcamentos(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Busca orçamentos baseado em uma consulta
        
        Args:
            query: Texto da consulta
            n_results: Número de resultados a retornar
            
        Returns:
            Lista com resultados da busca
        """
        try:
            # Buscar no ChromaDB
            resultados = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Verificar se há resultados
            if not resultados or not resultados.get('ids') or not resultados['ids'][0]:
                logger.info(f"Busca retornou 0 resultados")
                return []
            
            # Formatar resultados
            resultados_formatados = []
            for i in range(len(resultados['ids'][0])):
                documentos = resultados.get('documents', [[]])
                metadados = resultados.get('metadatas', [[]])
                distancias = resultados.get('distances', [[]])
                
                resultado = {
                    "id": resultados['ids'][0][i],
                    "documento": documentos[0][i] if documentos and documentos[0] and i < len(documentos[0]) else "",
                    "metadados": metadados[0][i] if metadados and metadados[0] and i < len(metadados[0]) else {},
                    "distancia": distancias[0][i] if distancias and distancias[0] and i < len(distancias[0]) else 0.0
                }
                resultados_formatados.append(resultado)
            
            logger.info(f"Busca retornou {len(resultados_formatados)} resultados")
            return resultados_formatados
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def estatisticas_banco(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            count = self.collection.count()
            
            # Buscar todos os metadados para estatísticas
            todos = self.collection.get()
            
            tipos_documento = {}
            total_linhas = 0
            arquivos_por_tipo = {}
            
            if todos and todos.get('metadatas') and todos['metadatas']:
                for metadata in todos['metadatas']:
                    if metadata:
                        tipo = metadata.get('tipo', 'desconhecido')
                        tipos_documento[tipo] = tipos_documento.get(tipo, 0) + 1
                        
                        linhas = metadata.get('linhas', 0)
                        if isinstance(linhas, (int, float)):
                            total_linhas += int(linhas)
                        
                        arquivo = metadata.get('arquivo', '')
                        if arquivo:
                            extensao = Path(str(arquivo)).suffix.lower()
                            arquivos_por_tipo[extensao] = arquivos_por_tipo.get(extensao, 0) + 1
            
            return {
                "total_documentos": count,
                "tipos_documento": tipos_documento,
                "total_linhas": total_linhas,
                "arquivos_por_tipo": arquivos_por_tipo,
                "caminho_banco": str(self.db_path)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"erro": str(e)}

def main():
    """
    Função principal para demonstrar o uso do sistema RAG
    """
    print("🚀 Sistema RAG para Planilhas de Orçamento - Solução Local")
    print("=" * 60)
    
    # Inicializar sistema
    rag = RAGPlanilhasLocal()
    
    # Verificar se já existem dados no banco
    stats = rag.estatisticas_banco()
    if stats.get("total_documentos", 0) > 0:
        print(f"📊 Banco já contém {stats['total_documentos']} documentos")
        print(f"   Tipos: {stats.get('tipos_documento', {})}")
        print(f"   Total de linhas: {stats.get('total_linhas', 0)}")
        
        resposta = input("\nDeseja reprocessar todas as planilhas? (s/n): ").lower()
        if resposta != 's':
            print("Usando dados existentes no banco.")
        else:
            print("Reprocessando planilhas...")
            dados = rag.processar_todas_planilhas()
            rag.adicionar_ao_chromadb(dados)
    else:
        print("📁 Processando planilhas pela primeira vez...")
        dados = rag.processar_todas_planilhas()
        rag.adicionar_ao_chromadb(dados)
    
    # Interface de consulta
    print("\n🔍 Interface de Consulta")
    print("Digite 'sair' para encerrar")
    print("-" * 40)
    
    while True:
        query = input("\n❓ Sua pergunta sobre os orçamentos: ").strip()
        
        if query.lower() in ['sair', 'exit', 'quit']:
            break
        
        if not query:
            continue
        
        print(f"\n🔍 Buscando: '{query}'")
        resultados = rag.buscar_orcamentos(query, n_results=3)
        
        if resultados:
            print(f"\n📋 Encontrados {len(resultados)} resultados:")
            for i, resultado in enumerate(resultados, 1):
                print(f"\n{i}. Arquivo: {resultado['metadados']['arquivo']}")
                print(f"   Tipo: {resultado['metadados']['tipo']}")
                print(f"   Linhas: {resultado['metadados']['linhas']}")
                print(f"   Colunas: {resultado['metadados']['colunas']}")
                print(f"   Relevância: {1 - resultado['distancia']:.2%}")
                print(f"   Conteúdo: {resultado['documento'][:200]}...")
        else:
            print("❌ Nenhum resultado encontrado.")
    
    print("\n👋 Sistema encerrado!")

if __name__ == "__main__":
    main() 