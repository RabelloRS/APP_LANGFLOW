#!/usr/bin/env python3
"""
Script para verificar a classificação das planilhas (orçamento vs planilha_geral)
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Adicionar o diretório src ao path
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.core.rag_planilhas_local import RAGPlanilhasLocal
import pandas as pd

def check_classification():
    """Verifica a classificação das planilhas"""
    print("🔍 VERIFICANDO CLASSIFICAÇÃO DAS PLANILHAS")
    print("=" * 60)
    
    # Inicializar o sistema RAG
    rag = RAGPlanilhasLocal()
    
    # Encontrar todas as planilhas
    planilhas = rag.encontrar_planilhas()
    print(f"📊 Total de planilhas encontradas: {len(planilhas)}")
    print()
    
    # Classificar cada planilha
    orcamentos = []
    planilhas_gerais = []
    
    for i, planilha in enumerate(planilhas, 1):
        print(f"Processando {i}/{len(planilhas)}: {planilha.name}")
        
        try:
            # Extrair dados da planilha
            dados = rag.extrair_dados_planilha(planilha)
            
            if "erro" in dados:
                print(f"  ❌ Erro: {dados['erro']}")
                continue
            
            # Verificar classificação
            tipo = dados.get("tipo_documento", "desconhecido")
            score = dados.get("score_orcamento", 0)
            colunas = dados.get("colunas", [])
            
            print(f"  📋 Colunas: {', '.join(colunas[:5])}{'...' if len(colunas) > 5 else ''}")
            print(f"  🎯 Score orçamento: {score}")
            print(f"  📝 Classificação: {tipo}")
            
            if tipo == "orcamento":
                orcamentos.append({
                    "arquivo": planilha.name,
                    "score": score,
                    "colunas": colunas
                })
            else:
                planilhas_gerais.append({
                    "arquivo": planilha.name,
                    "score": score,
                    "colunas": colunas
                })
            
            print()
            
        except Exception as e:
            print(f"  ❌ Erro ao processar: {e}")
            print()
    
    # Resumo final
    print("=" * 60)
    print("📊 RESUMO DA CLASSIFICAÇÃO")
    print("=" * 60)
    print(f"✅ Planilhas classificadas como ORÇAMENTO: {len(orcamentos)}")
    print(f"📄 Planilhas classificadas como PLANILHA GERAL: {len(planilhas_gerais)}")
    print()
    
    # Mostrar detalhes dos orçamentos
    if orcamentos:
        print("📋 PLANILHAS DE ORÇAMENTO:")
        print("-" * 40)
        for item in sorted(orcamentos, key=lambda x: x["score"], reverse=True):
            print(f"🎯 Score {item['score']}: {item['arquivo']}")
            print(f"   Colunas: {', '.join(item['colunas'][:3])}{'...' if len(item['colunas']) > 3 else ''}")
        print()
    
    # Mostrar detalhes das planilhas gerais
    if planilhas_gerais:
        print("📄 PLANILHAS GERAIS:")
        print("-" * 40)
        for item in sorted(planilhas_gerais, key=lambda x: x["score"], reverse=True):
            print(f"🎯 Score {item['score']}: {item['arquivo']}")
            print(f"   Colunas: {', '.join(item['colunas'][:3])}{'...' if len(item['colunas']) > 3 else ''}")
        print()

if __name__ == "__main__":
    check_classification() 