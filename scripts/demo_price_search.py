#!/usr/bin/env python3
"""
Script de demonstração do sistema de busca de preços de engenharia.
Baseado no priceAPI: https://github.com/yorikvanhavre/priceAPI

Este script demonstra as funcionalidades principais do sistema:
- Busca por termos
- Filtros por fonte
- Busca por código
- Conversão por CUB
- Estatísticas
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.price_source_manager import price_source_manager
from src.core.cli_search import search_services, display_results
from src.utils.logger import get_logger

logger = get_logger("demo_price_search")

def demo_basic_search():
    """Demonstra busca básica por termos."""
    print("\n" + "="*60)
    print("DEMO 1: Busca Básica por Termos")
    print("="*60)
    
    # Busca por alvenaria
    print("\n1. Buscando por 'alvenaria':")
    results = search_services(["alvenaria"])
    
    # Busca por concreto armado
    print("\n2. Buscando por 'concreto armado':")
    results = search_services(["concreto", "armado"])
    
    # Busca com termos OR
    print("\n3. Buscando por 'alvenaria' OU 'concreto':")
    results = search_services(["alvenaria", "concreto"])

def demo_source_filter():
    """Demonstra filtros por fonte."""
    print("\n" + "="*60)
    print("DEMO 2: Filtros por Fonte")
    print("="*60)
    
    # Busca apenas em SINAPI
    print("\n1. Buscando 'alvenaria' apenas em SINAPI:")
    results = search_services(["alvenaria"], source_filter="sinapi")
    
    # Busca apenas em SICRO
    print("\n2. Buscando 'concreto' apenas em SICRO:")
    results = search_services(["concreto"], source_filter="sicro")

def demo_code_search():
    """Demonstra busca por código."""
    print("\n" + "="*60)
    print("DEMO 3: Busca por Código")
    print("="*60)
    
    # Busca por código específico
    print("\n1. Buscando por código '87449':")
    results = search_services([], code_filter="87449")
    
    # Busca por código parcial
    print("\n2. Buscando por código que contenha '874':")
    results = search_services([], code_filter="874")

def demo_cub_conversion():
    """Demonstra conversão por CUB."""
    print("\n" + "="*60)
    print("DEMO 4: Conversão por CUB")
    print("="*60)
    
    # Busca com conversão CUB
    print("\n1. Buscando 'alvenaria' com conversão CUB 5000:")
    results = search_services(["alvenaria"], cub_conversion=5000.0)
    
    print("\n2. Buscando 'concreto' com conversão CUB 3000:")
    results = search_services(["concreto"], cub_conversion=3000.0)

def demo_statistics():
    """Demonstra estatísticas do sistema."""
    print("\n" + "="*60)
    print("DEMO 5: Estatísticas do Sistema")
    print("="*60)
    
    stats = price_source_manager.get_statistics()
    
    print(f"\nEstatísticas do Sistema:")
    print(f"Total de serviços: {stats.get('total_services', 0)}")
    print(f"Fontes de dados: {stats.get('total_sources', 0)}")
    print(f"Arquivos processados: {stats.get('total_files', 0)}")
    
    # Detalhes por fonte
    if 'sources' in stats:
        print(f"\nDetalhes por fonte:")
        for source, count in stats['sources'].items():
            print(f"  {source}: {count} serviços")

def demo_build_sources():
    """Demonstra construção das fontes de dados."""
    print("\n" + "="*60)
    print("DEMO 6: Construção das Fontes de Dados")
    print("="*60)
    
    print("\nConstruindo todas as fontes de dados...")
    results = price_source_manager.build_all_sources()
    
    print("\nResultados da construção:")
    for source, success in results.items():
        status = "✓ SUCESSO" if success else "✗ FALHA"
        print(f"  {source}: {status}")

def create_sample_data():
    """Cria dados de exemplo para demonstração."""
    print("\n" + "="*60)
    print("CRIANDO DADOS DE EXEMPLO")
    print("="*60)
    
    # Criar diretório de dados se não existir
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Dados de exemplo SINAPI
    sinapi_data = [
        {
            "CODIGO": "87449",
            "DESCRICAO": "ALVENARIA DE VEDACAO DE BLOCOS VAZADOS DE CONCRETO DE 14X19X39CM (ESPESSURA 14CM)",
            "UNIDADE": "M2",
            "PRECO": "57.62"
        },
        {
            "CODIGO": "87450", 
            "DESCRICAO": "ALVENARIA DE VEDACAO DE BLOCOS VAZADOS DE CONCRETO DE 19X19X39CM (ESPESSURA 19CM)",
            "UNIDADE": "M2",
            "PRECO": "73.99"
        },
        {
            "CODIGO": "87451",
            "DESCRICAO": "CONCRETO ARMADO EM ESTRUTURAS DE EDIFICIOS - Fck 20 MPa",
            "UNIDADE": "M3",
            "PRECO": "450.00"
        }
    ]
    
    # Salvar dados SINAPI
    import pandas as pd
    df_sinapi = pd.DataFrame(sinapi_data)
    df_sinapi.to_excel("data/sinapi_sp.xlsx", index=False)
    print("✓ Dados SINAPI criados: data/sinapi_sp.xlsx")
    
    # Dados de exemplo SICRO
    sicro_data = [
        {
            "CODIGO": "S001",
            "DESCRICAO": "CONCRETO ASFALTICO USINADO A QUENTE - CBUQ",
            "UNIDADE": "M2",
            "PRECO": "85.50"
        },
        {
            "CODIGO": "S002",
            "DESCRICAO": "PINTURA DE SINALIZACAO HORIZONTAL EM PISTA",
            "UNIDADE": "M2", 
            "PRECO": "12.30"
        }
    ]
    
    df_sicro = pd.DataFrame(sicro_data)
    df_sicro.to_excel("data/sicro.xlsx", index=False)
    print("✓ Dados SICRO criados: data/sicro.xlsx")

def main():
    """Função principal da demonstração."""
    print("🚀 DEMONSTRAÇÃO DO SISTEMA DE BUSCA DE PREÇOS DE ENGENHARIA")
    print("Baseado no priceAPI: https://github.com/yorikvanhavre/priceAPI")
    
    try:
        # Criar dados de exemplo
        create_sample_data()
        
        # Construir fontes
        demo_build_sources()
        
        # Mostrar estatísticas
        demo_statistics()
        
        # Demonstrações de busca
        demo_basic_search()
        demo_source_filter()
        demo_code_search()
        demo_cub_conversion()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
        print("\nPara usar o sistema via linha de comando:")
        print("  python src/core/cli_search.py alvenaria")
        print("  python src/core/cli_search.py --source=sinapi concreto")
        print("  python src/core/cli_search.py --code=87449")
        print("  python src/core/cli_search.py --cub=5000 alvenaria")
        
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"❌ Erro na demonstração: {e}")

if __name__ == "__main__":
    main() 