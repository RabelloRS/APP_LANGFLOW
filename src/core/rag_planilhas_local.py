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

from config.config import RAG_CONFIG

class RAGPlanilhasLocal:
    def __init__(self, pasta_docs: str = RAG_CONFIG["pasta_docs"], db_path: str = RAG_CONFIG["db_path"], on_progress_update: Optional[callable] = None):
        """
        Inicializa o sistema RAG para planilhas
        
        Args:
            pasta_docs: Pasta onde estão as planilhas de orçamento
            db_path: Pasta onde será criado o banco ChromaDB
        """
        self.pasta_docs = Path(pasta_docs)
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self.on_progress_update = on_progress_update # Store the callback
        
        # Inicializar ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Criar ou obter coleção
        self.collection = self.client.get_or_create_collection(
            name="orcamentos_planilhas_chunks",
            metadata={"description": "Chunks de linhas de planilhas de orçamento processadas"}
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
    
    def _criar_chunks_de_linha(self, df: pd.DataFrame, nome_arquivo: str, nome_aba: str, tipo_documento: str) -> List[Dict[str, Any]]:
        """
        Cria uma lista de chunks, onde cada chunk é um dicionário representando uma linha.
        """
        chunks = []
        for i, row in df.iterrows():
            texto_embedding = f"No arquivo '{nome_arquivo}', na aba '{nome_aba}', a linha {i+1} contém os seguintes dados:\n"
            for col, val in row.items():
                texto_embedding += f"- {col}: {val}\n"
            
            chunk = {
                "documento": texto_embedding,
                "metadados": {
                    "arquivo": nome_arquivo,
                    "aba": nome_aba,
                    "linha": i + 1,
                    "tipo_documento": tipo_documento,
                    "colunas": ", ".join(df.columns.tolist())
                }
            }
            chunks.append(chunk)
        return chunks

    def extrair_dados_planilha(self, caminho_planilha: Path) -> List[Dict[str, Any]]:
        """
        Extrai dados de uma planilha e retorna uma lista de chunks de linha.
        """
        todos_chunks = []
        try:
            if caminho_planilha.suffix.lower() in ['.xlsx', '.xls', '.xlsm']:
                if self.on_progress_update:
                    self.on_progress_update(f"Analisando arquivo: {caminho_planilha.name}")
                excel_file = pd.ExcelFile(caminho_planilha)
                for aba in excel_file.sheet_names:
                    try:
                        if self.on_progress_update:
                            self.on_progress_update(f"  Analisando aba '{aba}' em {caminho_planilha.name}...")
                        df = pd.read_excel(caminho_planilha, sheet_name=aba)
                        if df.empty:
                            if self.on_progress_update:
                                self.on_progress_update(f"  Aba '{aba}' em {caminho_planilha.name} está vazia. Pulando.")
                            continue

                        colunas_texto = [str(col).lower() for col in df.columns]
                        palavras_chave_orcamento = [
                            'orcamento', 'preço', 'valor', 'custo', 'total', 'cliente', 'codigo', 'R$', 'unidade', 'Un',
                            'produto', 'serviço', 'quantidade', 'unitário', 'descricao','subtotal'
                        ]
                        score_orcamento = sum(1 for palavra in palavras_chave_orcamento if any(palavra in col for col in colunas_texto))
                        
                        # Analisar também o conteúdo das células para refinar o score
                        amostra_conteudo = " ".join(df.head(10).to_string(index=False).lower().split())
                        score_conteudo = sum(1 for palavra in palavras_chave_orcamento if palavra in amostra_conteudo)
                        score_total = score_orcamento + (1 if score_conteudo > 5 else 0)

                        tipo_documento = "orcamento" if score_total >= 2 else "planilha_geral"
                        if self.on_progress_update:
                            self.on_progress_update(f"  Classificado como: {tipo_documento} (Score: {score_total})")
                        
                        chunks_aba = self._criar_chunks_de_linha(df, caminho_planilha.name, aba, tipo_documento)
                        todos_chunks.extend(chunks_aba)
                        logger.info(f"Processada aba '{aba}' do arquivo {caminho_planilha.name}, {len(chunks_aba)} chunks criados.")
                    except Exception as e:
                        logger.error(f"Erro ao processar aba {aba} do arquivo {caminho_planilha.name}: {e}")
                        if self.on_progress_update:
                            self.on_progress_update(f"  ERRO ao processar aba '{aba}' em {caminho_planilha.name}: {e}")
            elif caminho_planilha.suffix.lower() == '.csv':
                if self.on_progress_update:
                    self.on_progress_update(f"Analisando arquivo CSV: {caminho_planilha.name}")
                df = pd.read_csv(caminho_planilha)
                if df.empty:
                    if self.on_progress_update:
                        self.on_progress_update(f"  Arquivo CSV {caminho_planilha.name} está vazio. Pulando.")
                    return todos_chunks

                colunas_texto = [str(col).lower() for col in df.columns]
                palavras_chave_orcamento = [
                    'orcamento', 'preço', 'valor', 'custo', 'total', 'cliente', 'codigo', 'R$', 'unidade', 'Un',
                    'produto', 'serviço', 'quantidade', 'unitário', 'descricao','subtotal'
                ]
                score_orcamento = sum(1 for palavra in palavras_chave_orcamento if any(palavra in col for col in colunas_texto))
                
                amostra_conteudo = " ".join(df.head(10).to_string(index=False).lower().split())
                score_conteudo = sum(1 for palavra in palavras_chave_orcamento if palavra in amostra_conteudo)
                score_total = score_orcamento + (1 if score_conteudo > 5 else 0)

                tipo_documento = "orcamento" if score_total >= 2 else "planilha_geral"
                if self.on_progress_update:
                    self.on_progress_update(f"  Classificado como: {tipo_documento} (Score: {score_total})")

                chunks_csv = self._criar_chunks_de_linha(df, caminho_planilha.name, "default", tipo_documento)
                todos_chunks.extend(chunks_csv)
                logger.info(f"Processado arquivo CSV {caminho_planilha.name}, {len(chunks_csv)} chunks criados.")
        except Exception as e:
            logger.error(f"Erro ao processar {caminho_planilha}: {e}")
        
        return todos_chunks

    def processar_todas_planilhas(self) -> List[Dict[str, Any]]:
        """
        Processa todas as planilhas encontradas na pasta e retorna uma lista de chunks.
        """
        planilhas = self.encontrar_planilhas()
        if not planilhas:
            if self.on_progress_update:
                self.on_progress_update("Nenhuma planilha encontrada para processar.")
            return []
        
        todos_os_chunks = []
        for i, planilha in enumerate(planilhas):
            if self.on_progress_update:
                self.on_progress_update(f"Processando arquivo {i+1}/{len(planilhas)}: {planilha.name}")
            logger.info(f"Processando: {planilha.name}")
            chunks = self.extrair_dados_planilha(planilha)
            todos_os_chunks.extend(chunks)
        
        logger.info(f"Processadas {len(planilhas)} planilhas, resultando em {len(todos_os_chunks)} chunks.")
        return todos_os_chunks
    
    def adicionar_ao_chromadb(self, chunks: List[Dict[str, Any]]):
        """
        Adiciona os chunks de dados processados ao ChromaDB.
        """
        if not chunks:
            logger.warning("Nenhum chunk para adicionar ao ChromaDB")
            if self.on_progress_update:
                self.on_progress_update("Nenhum chunk para adicionar ao ChromaDB.")
            return
        
        ids = []
        documentos = []
        metadados = []
        
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            meta = chunk['metadados']
            doc_id = f"{meta['arquivo']}_{meta['aba']}_{meta['linha']}"
            ids.append(doc_id)
            documentos.append(chunk['documento'])
            metadados.append(meta)
            
            if self.on_progress_update and (i + 1) % 100 == 0: # Update every 100 chunks
                self.on_progress_update(f"Preparando {i+1}/{total_chunks} chunks para adição ao ChromaDB...")
        
        if ids:
            # Adiciona em lotes para evitar sobrecarga
            batch_size = 1000
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_documents = documentos[i:i+batch_size]
                batch_metadatas = metadados[i:i+batch_size]
                
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                if self.on_progress_update:
                    self.on_progress_update(f"Adicionado lote de {len(batch_ids)} chunks ao ChromaDB. Total: {i + len(batch_ids)}/{total_chunks}")
                logger.info(f"Adicionado lote de {len(batch_ids)} chunks ao ChromaDB.")
            if self.on_progress_update:
                self.on_progress_update(f"Total de {len(ids)} chunks adicionados ao ChromaDB.")
            logger.info(f"Total de {len(ids)} chunks adicionados ao ChromaDB.")
    
    def buscar_orcamentos(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Busca orçamentos baseado em uma consulta.
        """
        try:
            resultados = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not resultados or not resultados.get('ids') or not resultados['ids'][0]:
                logger.info(f"Busca retornou 0 resultados")
                return []
            
            resultados_formatados = []
            for i in range(len(resultados['ids'][0])):
                documentos = resultados.get('documents', [[]])
                metadados = resultados.get('metadatas', [[]])
                distancias = resultados.get('distances', [[]])
                
                resultado = {
                    "id": resultados['ids'][0][i],
                    "documento": documentos[0][i] if documentos and documentos[0] else "",
                    "metadados": metadados[0][i] if metadados and metadados[0] else {},
                    "distancia": distancias[0][i] if distancias and distancias[0] else 0.0
                }
                resultados_formatados.append(resultado)
            
            logger.info(f"Busca retornou {len(resultados_formatados)} resultados")
            return resultados_formatados
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def estatisticas_banco(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do banco de dados.
        """
        try:
            count = self.collection.count()
            return {
                "total_documentos": count,
                "caminho_banco": str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"erro": str(e)}

def main():
    """
    Função principal para demonstrar o uso do sistema RAG.
    """
    print("🚀 Sistema RAG para Planilhas de Orçamento - Solução Local (Chunking por Linha)")
    print("=" * 70)
    
    rag = RAGPlanilhasLocal()
    
    stats = rag.estatisticas_banco()
    if stats.get("total_documentos", 0) > 0:
        print(f"📊 Banco já contém {stats['total_documentos']} documentos (chunks).")
        resposta = input("\nDeseja reprocessar todas as planilhas? (Isso limpará o banco de dados atual) (s/n): ").lower()
        if resposta == 's':
            print("Limpando o banco de dados e reprocessando...")
            rag.client.delete_collection(name=rag.collection.name)
            rag.collection = rag.client.get_or_create_collection(name="orcamentos_planilhas_chunks")
            chunks = rag.processar_todas_planilhas()
            rag.adicionar_ao_chromadb(chunks)
        else:
            print("Usando dados existentes no banco.")
    else:
        print("📁 Processando planilhas pela primeira vez...")
        chunks = rag.processar_todas_planilhas()
        rag.adicionar_ao_chromadb(chunks)
    
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
            print(f"\n📋 Encontrados {len(resultados)} resultados relevantes:")
            for i, resultado in enumerate(resultados, 1):
                meta = resultado['metadados']
                print(f"\n{i}. Origem: Arquivo '{meta.get('arquivo')}', Aba '{meta.get('aba')}', Linha {meta.get('linha')}")
                print(f"   Relevância: {1 - resultado['distancia']:.2%}")
                print(f"   Conteúdo do Chunk:\n{resultado['documento']}")
        else:
            print("❌ Nenhum resultado encontrado.")
    
    print("\n👋 Sistema encerrado!")

if __name__ == "__main__":
    main()
