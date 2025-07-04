#!/usr/bin/env python3
"""
Script de demonstração do processador de planilhas governamentais.
Baseado no SICONV: https://github.com/fbrandao2k/SICONV

Este script demonstra o processamento de planilhas governamentais brasileiras:
- Identificação automática de sistemas (SINAPI, SICRO, SICONV)
- Processamento de múltiplas abas
- Cálculo de BDI
- Validação de dados
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.government_spreadsheet_processor import government_processor
from src.utils.logger import get_logger

logger = get_logger("demo_government_processor")

def create_sample_siconv_data():
    """Cria dados de exemplo SICONV."""
    print("\n" + "="*60)
    print("CRIANDO DADOS DE EXEMPLO SICONV")
    print("="*60)
    
    # Criar diretório de dados se não existir
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Dados de exemplo para aba ORÇAMENTO
    orcamento_data = [
        {
            "CODIGO": "87449",
            "DESCRICAO": "ALVENARIA DE VEDACAO DE BLOCOS VAZADOS DE CONCRETO 14CM",
            "UNIDADE": "M2",
            "PRECO": "57.62",
            "BDI": "15.5",
            "QUANTIDADE": "100.0"
        },
        {
            "CODIGO": "87450",
            "DESCRICAO": "CONCRETO ARMADO EM ESTRUTURAS - Fck 20 MPa",
            "UNIDADE": "M3",
            "PRECO": "450.00",
            "BDI": "12.0",
            "QUANTIDADE": "50.0"
        },
        {
            "CODIGO": "87451",
            "DESCRICAO": "IMPERMEABILIZACAO COM MANTAS ASFALTICAS",
            "UNIDADE": "M2",
            "PRECO": "85.30",
            "BDI": "18.0",
            "QUANTIDADE": "200.0"
        }
    ]
    
    # Dados de exemplo para aba CÁLCULO
    calculo_data = [
        {
            "CODIGO": "CALC001",
            "DESCRICAO": "CALCULO DE AREA TOTAL",
            "UNIDADE": "M2",
            "PRECO": "0.00",
            "BDI": "0.0",
            "QUANTIDADE": "1.0"
        },
        {
            "CODIGO": "CALC002",
            "DESCRICAO": "CALCULO DE VOLUME DE CONCRETO",
            "UNIDADE": "M3",
            "PRECO": "0.00",
            "BDI": "0.0",
            "QUANTIDADE": "1.0"
        }
    ]
    
    # Criar planilha SICONV com múltiplas abas
    with pd.ExcelWriter("data/siconv_example.xlsx", engine='openpyxl') as writer:
        df_orcamento = pd.DataFrame(orcamento_data)
        df_calculo = pd.DataFrame(calculo_data)
        
        df_orcamento.to_excel(writer, sheet_name='ORÇAMENTO', index=False)
        df_calculo.to_excel(writer, sheet_name='CÁLCULO', index=False)
    
    print("✓ Dados SICONV criados: data/siconv_example.xlsx")
    print("  - Aba ORÇAMENTO: 3 itens")
    print("  - Aba CÁLCULO: 2 itens")

def create_sample_sinapi_data():
    """Cria dados de exemplo SINAPI."""
    print("\n" + "="*60)
    print("CRIANDO DADOS DE EXEMPLO SINAPI")
    print("="*60)
    
    # Dados de exemplo SINAPI
    sinapi_data = [
        {
            "CODIGO": "87449",
            "DESCRICAO": "ALVENARIA DE VEDACAO DE BLOCOS VAZADOS DE CONCRETO DE 14X19X39CM",
            "UNIDADE": "M2",
            "PRECO": "57.62",
            "DATA": "2024-01-01"
        },
        {
            "CODIGO": "87450",
            "DESCRICAO": "ALVENARIA DE VEDACAO DE BLOCOS VAZADOS DE CONCRETO DE 19X19X39CM",
            "UNIDADE": "M2",
            "PRECO": "73.99",
            "DATA": "2024-01-01"
        },
        {
            "CODIGO": "87451",
            "DESCRICAO": "CONCRETO ARMADO EM ESTRUTURAS DE EDIFICIOS - Fck 20 MPa",
            "UNIDADE": "M3",
            "PRECO": "450.00",
            "DATA": "2024-01-01"
        }
    ]
    
    df_sinapi = pd.DataFrame(sinapi_data)
    df_sinapi.to_excel("data/sinapi_example.xlsx", index=False)
    
    print("✓ Dados SINAPI criados: data/sinapi_example.xlsx")
    print("  - 3 serviços de alvenaria e concreto")

def create_sample_sicro_data():
    """Cria dados de exemplo SICRO."""
    print("\n" + "="*60)
    print("CRIANDO DADOS DE EXEMPLO SICRO")
    print("="*60)
    
    # Dados de exemplo SICRO
    sicro_data = [
        {
            "CODIGO": "S001",
            "DESCRICAO": "CONCRETO ASFALTICO USINADO A QUENTE - CBUQ",
            "UNIDADE": "M2",
            "PRECO": "85.50",
            "FRENTE": "PAVIMENTACAO"
        },
        {
            "CODIGO": "S002",
            "DESCRICAO": "PINTURA DE SINALIZACAO HORIZONTAL EM PISTA",
            "UNIDADE": "M2",
            "PRECO": "12.30",
            "FRENTE": "SINALIZACAO"
        },
        {
            "CODIGO": "S003",
            "DESCRICAO": "TERRAPLENAGEM COM MATERIAL DE EMPRESTIMO",
            "UNIDADE": "M3",
            "PRECO": "25.80",
            "FRENTE": "TERRAPLENAGEM"
        }
    ]
    
    df_sicro = pd.DataFrame(sicro_data)
    df_sicro.to_excel("data/sicro_example.xlsx", index=False)
    
    print("✓ Dados SICRO criados: data/sicro_example.xlsx")
    print("  - 3 serviços rodoviários")

def demo_system_identification():
    """Demonstra identificação automática de sistemas."""
    print("\n" + "="*60)
    print("DEMO 1: Identificação Automática de Sistemas")
    print("="*60)
    
    test_files = [
        "data/siconv_example.xlsx",
        "data/sinapi_example.xlsx",
        "data/sicro_example.xlsx"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            system = government_processor.identify_government_system(file_path)
            print(f"\nArquivo: {file_path}")
            print(f"Sistema identificado: {system.upper() if system else 'DESCONHECIDO'}")
        else:
            print(f"\nArquivo não encontrado: {file_path}")

def demo_siconv_processing():
    """Demonstra processamento SICONV."""
    print("\n" + "="*60)
    print("DEMO 2: Processamento SICONV")
    print("="*60)
    
    file_path = "data/siconv_example.xlsx"
    if Path(file_path).exists():
        system, services = government_processor.process_government_spreadsheet(file_path)
        
        print(f"\nSistema processado: {system.upper()}")
        print(f"Total de serviços: {len(services)}")
        
        if services:
            print("\nPrimeiros 3 serviços:")
            for i, service in enumerate(services[:3], 1):
                print(f"\n{i}. Código: {service.get('service_code')}")
                print(f"   Descrição: {service.get('description')}")
                print(f"   Preço: R$ {service.get('value', 0):.2f}")
                print(f"   BDI: {service.get('bdi', 0):.1f}%")
                print(f"   Quantidade: {service.get('quantity', 1):.1f}")
    else:
        print(f"Arquivo não encontrado: {file_path}")

def demo_sinapi_processing():
    """Demonstra processamento SINAPI."""
    print("\n" + "="*60)
    print("DEMO 3: Processamento SINAPI")
    print("="*60)
    
    file_path = "data/sinapi_example.xlsx"
    if Path(file_path).exists():
        system, services = government_processor.process_government_spreadsheet(file_path)
        
        print(f"\nSistema processado: {system.upper()}")
        print(f"Total de serviços: {len(services)}")
        
        if services:
            print("\nPrimeiros 3 serviços:")
            for i, service in enumerate(services[:3], 1):
                print(f"\n{i}. Código: {service.get('service_code')}")
                print(f"   Descrição: {service.get('description')}")
                print(f"   Preço: R$ {service.get('value', 0):.2f}")
                print(f"   Data base: {service.get('base_date')}")
    else:
        print(f"Arquivo não encontrado: {file_path}")

def demo_sicro_processing():
    """Demonstra processamento SICRO."""
    print("\n" + "="*60)
    print("DEMO 4: Processamento SICRO")
    print("="*60)
    
    file_path = "data/sicro_example.xlsx"
    if Path(file_path).exists():
        system, services = government_processor.process_government_spreadsheet(file_path)
        
        print(f"\nSistema processado: {system.upper()}")
        print(f"Total de serviços: {len(services)}")
        
        if services:
            print("\nPrimeiros 3 serviços:")
            for i, service in enumerate(services[:3], 1):
                print(f"\n{i}. Código: {service.get('service_code')}")
                print(f"   Descrição: {service.get('description')}")
                print(f"   Preço: R$ {service.get('value', 0):.2f}")
                print(f"   Frente: {service.get('frente_trabalho', 'N/A')}")
    else:
        print(f"Arquivo não encontrado: {file_path}")

def demo_bdi_calculation():
    """Demonstra cálculo de BDI."""
    print("\n" + "="*60)
    print("DEMO 5: Cálculo de BDI (Budget Difference Index)")
    print("="*60)
    
    base_prices = [100.0, 500.0, 1000.0]
    bdi_percentages = [10.0, 15.0, 20.0]
    
    print("\nExemplos de cálculo de BDI:")
    for base_price in base_prices:
        for bdi_pct in bdi_percentages:
            final_price = government_processor.calculate_bdi(base_price, bdi_pct)
            print(f"Preço base: R$ {base_price:.2f} + BDI {bdi_pct:.1f}% = R$ {final_price:.2f}")

def demo_data_validation():
    """Demonstra validação de dados."""
    print("\n" + "="*60)
    print("DEMO 6: Validação de Dados Governamentais")
    print("="*60)
    
    # Dados de teste com problemas
    test_services = [
        {
            "source": "sinapi",
            "service_code": "87449",
            "description": "ALVENARIA DE VEDACAO",
            "value": 57.62
        },
        {
            "source": "sinapi",
            "service_code": "INVALID",
            "description": "CODIGO INVALIDO",
            "value": 0.0
        },
        {
            "source": "sicro",
            "service_code": "S001",
            "description": "CONCRETO ASFALTICO",
            "value": 85.50
        },
        {
            "source": "sicro",
            "service_code": "INVALID",
            "description": "CODIGO INVALIDO",
            "value": 25.80
        }
    ]
    
    validated_services = government_processor.validate_government_data(test_services)
    
    print(f"\nServiços originais: {len(test_services)}")
    print(f"Serviços válidos: {len(validated_services)}")
    print(f"Serviços rejeitados: {len(test_services) - len(validated_services)}")

def main():
    """Função principal da demonstração."""
    print("🚀 DEMONSTRAÇÃO DO PROCESSADOR DE PLANILHAS GOVERNAMENTAIS")
    print("Baseado no SICONV: https://github.com/fbrandao2k/SICONV")
    
    try:
        # Criar dados de exemplo
        create_sample_siconv_data()
        create_sample_sinapi_data()
        create_sample_sicro_data()
        
        # Demonstrações
        demo_system_identification()
        demo_siconv_processing()
        demo_sinapi_processing()
        demo_sicro_processing()
        demo_bdi_calculation()
        demo_data_validation()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
        print("\nFuncionalidades demonstradas:")
        print("✓ Identificação automática de sistemas governamentais")
        print("✓ Processamento de planilhas SICONV com múltiplas abas")
        print("✓ Processamento de planilhas SINAPI")
        print("✓ Processamento de planilhas SICRO")
        print("✓ Cálculo automático de BDI")
        print("✓ Validação de dados governamentais")
        print("✓ Integração com banco de dados")
        
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"❌ Erro na demonstração: {e}")

if __name__ == "__main__":
    main() 