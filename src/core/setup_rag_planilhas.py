#!/usr/bin/env python3
"""
Configuração do Sistema RAG para Planilhas - Solução Local
==========================================================

Este script configura todas as dependências necessárias para o sistema RAG
de planilhas usando ChromaDB local e Ollama.

Dependências instaladas:
- chromadb: Banco de dados vetorial local
- pandas: Processamento de planilhas
- openpyxl: Leitura de arquivos Excel
- sentence-transformers: Embeddings locais
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencia(pacote, descricao=""):
    """Instala uma dependência com feedback visual"""
    print(f"📦 Instalando {pacote}...")
    if descricao:
        print(f"   {descricao}")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
        print(f"✅ {pacote} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {pacote}: {e}")
        return False

def verificar_pasta_docs():
    """Verifica se a pasta de documentos existe"""
    pasta_docs = Path("D:\\docs_baixados")
    
    if pasta_docs.exists():
        print(f"✅ Pasta encontrada: {pasta_docs}")
        
        # Contar arquivos de planilha
        planilhas = list(pasta_docs.glob("*.xlsx")) + list(pasta_docs.glob("*.xls")) + list(pasta_docs.glob("*.csv"))
        print(f"📊 Encontradas {len(planilhas)} planilhas na pasta")
        
        if planilhas:
            print("   Primeiros arquivos:")
            for i, planilha in enumerate(planilhas[:5], 1):
                print(f"   {i}. {planilha.name}")
            if len(planilhas) > 5:
                print(f"   ... e mais {len(planilhas) - 5} arquivos")
        
        return True
    else:
        print(f"⚠️  Pasta não encontrada: {pasta_docs}")
        print("   Crie a pasta ou modifique o caminho no script rag_planilhas_local.py")
        return False

def verificar_ollama():
    """Verifica se o Ollama está instalado e rodando"""
    try:
        # Tentar conectar com Ollama
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama está rodando na porta 11434")
            
            # Listar modelos disponíveis
            models = response.json().get("models", [])
            if models:
                print("   Modelos disponíveis:")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("   ⚠️  Nenhum modelo encontrado")
                print("   Execute: ollama pull llama2")
            
            return True
        else:
            print("❌ Ollama não respondeu corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Ollama: {e}")
        print("   Certifique-se de que o Ollama está instalado e rodando")
        print("   Download: https://ollama.ai/download")
        return False

def criar_arquivo_requirements():
    """Cria arquivo requirements.txt com as dependências"""
    requirements = """# Dependências para Sistema RAG de Planilhas
chromadb>=0.4.0
pandas>=2.0.0
openpyxl>=3.1.0
sentence-transformers>=2.2.0
numpy>=1.24.0
requests>=2.31.0
pathlib2>=2.3.0
"""
    
    with open("requirements_rag.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    print("✅ Arquivo requirements_rag.txt criado")

def main():
    """Função principal de configuração"""
    print("🚀 Configuração do Sistema RAG para Planilhas")
    print("=" * 50)
    
    # Lista de dependências
    dependencias = [
        ("chromadb", "Banco de dados vetorial local"),
        ("pandas", "Processamento de planilhas"),
        ("openpyxl", "Leitura de arquivos Excel"),
        ("sentence-transformers", "Modelos de embedding locais"),
        ("numpy", "Computação numérica"),
        ("requests", "Requisições HTTP")
    ]
    
    # Instalar dependências
    print("\n📦 Instalando dependências...")
    sucessos = 0
    
    for pacote, descricao in dependencias:
        if instalar_dependencia(pacote, descricao):
            sucessos += 1
        print()
    
    print(f"✅ {sucessos}/{len(dependencias)} dependências instaladas com sucesso!")
    
    # Verificar pasta de documentos
    print("\n📁 Verificando pasta de documentos...")
    verificar_pasta_docs()
    
    # Verificar Ollama
    print("\n🤖 Verificando Ollama...")
    verificar_ollama()
    
    # Criar arquivo requirements
    print("\n📄 Criando arquivo de dependências...")
    criar_arquivo_requirements()
    
    # Instruções finais
    print("\n" + "=" * 50)
    print("🎉 Configuração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Certifique-se de que a pasta 'D:\\docs_baixados' existe")
    print("2. Coloque suas planilhas de orçamento na pasta")
    print("3. Execute: python rag_planilhas_local.py")
    print("4. No Langflow, importe o arquivo 'RAG_Planilhas_Local_Langflow.json'")
    print("\n🔧 Configurações importantes:")
    print("- ChromaDB será criado na pasta './chroma_db'")
    print("- Ollama deve estar rodando na porta 11434")
    print("- Modelo recomendado: llama2 (execute: ollama pull llama2)")
    
    print("\n📚 Arquivos criados:")
    print("- rag_planilhas_local.py: Sistema RAG principal")
    print("- RAG_Planilhas_Local_Langflow.json: Fluxo para Langflow")
    print("- requirements_rag.txt: Dependências")
    print("- setup_rag_planilhas.py: Este script de configuração")

if __name__ == "__main__":
    main() 