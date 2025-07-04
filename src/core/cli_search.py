"""
Interface de linha de comando para busca de serviços de engenharia.
Baseado no priceAPI: https://github.com/yorikvanhavre/priceAPI
"""

import argparse
import sys
from typing import List, Optional
from tabulate import tabulate

from src.core.price_source_manager import price_source_manager
from src.utils.logger import get_logger

logger = get_logger("cli_search")

def format_price(price: float) -> str:
    """Formata preço para exibição."""
    return f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def display_results(results: List[dict], show_confidence: bool = False):
    """Exibe resultados em formato tabular."""
    if not results:
        print("Nenhum resultado encontrado.")
        return
    
    # Preparar dados para tabela
    table_data = []
    for result in results:
        row = [
            result.get('source', 'N/A'),
            result.get('service_code', 'N/A'),
            result.get('description', 'N/A')[:80] + '...' if len(result.get('description', '')) > 80 else result.get('description', 'N/A'),
            format_price(result.get('value', 0)),
            result.get('base_date', 'N/A')
        ]
        
        if show_confidence:
            confidence = result.get('ai_confidence', 0)
            row.append(f"{confidence:.1f}%" if confidence else 'N/A')
        
        table_data.append(row)
    
    # Definir cabeçalhos
    headers = ['Fonte', 'Código', 'Descrição', 'Preço', 'Data Base']
    if show_confidence:
        headers.append('Confiança IA')
    
    # Exibir tabela
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print(f"\nTotal de resultados: {len(results)}")

def search_services(search_terms: List[str], 
                   source_filter: Optional[str] = None,
                   location_filter: Optional[str] = None,
                   code_filter: Optional[str] = None,
                   cub_conversion: Optional[float] = None,
                   show_confidence: bool = False):
    """Executa busca de serviços."""
    try:
        logger.info(f"Executando busca: {search_terms}")
        
        results = price_source_manager.search_services(
            search_terms=search_terms,
            source_filter=source_filter,
            location_filter=location_filter,
            code_filter=code_filter,
            cub_conversion=cub_conversion
        )
        
        display_results(results, show_confidence)
        
        return results
    
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        print(f"Erro na busca: {e}")
        return []

def main():
    """Função principal da interface CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de busca de serviços de engenharia baseado no priceAPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python cli_search.py alvenaria 14cm
  python cli_search.py --source=sinapi alvenaria
  python cli_search.py --code=87449
  python cli_search.py --cub=5000 alvenaria
  python cli_search.py "concreto armado" | "estrutura"
        """
    )
    
    # Argumentos de busca
    parser.add_argument('search_terms', nargs='*', 
                       help='Termos de busca (separados por espaço para AND, | para OR)')
    
    # Filtros
    parser.add_argument('--source', '-s',
                       help='Filtrar por fonte específica (sinapi, sicro, etc.)')
    
    parser.add_argument('--location', '-l',
                       help='Filtrar por localização')
    
    parser.add_argument('--code', '-c',
                       help='Buscar por código específico')
    
    parser.add_argument('--cub', type=float,
                       help='Converter preços por CUB')
    
    # Opções de exibição
    parser.add_argument('--confidence', action='store_true',
                       help='Mostrar confiança da classificação IA')
    
    parser.add_argument('--json', action='store_true',
                       help='Saída em formato JSON')
    
    parser.add_argument('--csv', action='store_true',
                       help='Saída em formato CSV')
    
    # Comandos administrativos
    parser.add_argument('--build-sources', action='store_true',
                       help='Constrói todas as fontes de dados')
    
    parser.add_argument('--statistics', action='store_true',
                       help='Mostra estatísticas do sistema')
    
    args = parser.parse_args()
    
    # Comandos administrativos
    if args.build_sources:
        print("Construindo fontes de dados...")
        results = price_source_manager.build_all_sources()
        for source, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {source}")
        return
    
    if args.statistics:
        stats = price_source_manager.get_statistics()
        print("Estatísticas do Sistema:")
        print(f"Total de serviços: {stats.get('total_services', 0)}")
        print(f"Fontes de dados: {stats.get('total_sources', 0)}")
        print(f"Arquivos processados: {stats.get('total_files', 0)}")
        return
    
    # Validação de argumentos de busca
    if not args.search_terms and not args.code:
        parser.print_help()
        return
    
    # Processar termos de busca
    search_terms = []
    if args.search_terms:
        # Separar termos por | (OR) e espaço (AND)
        for term_group in args.search_terms:
            if '|' in term_group:
                # Termos OR
                or_terms = [t.strip() for t in term_group.split('|')]
                search_terms.extend(or_terms)
            else:
                # Termo único
                search_terms.append(term_group)
    
    # Executar busca
    results = search_services(
        search_terms=search_terms,
        source_filter=args.source,
        location_filter=args.location,
        code_filter=args.code,
        cub_conversion=args.cub,
        show_confidence=args.confidence
    )
    
    # Formatos de saída especiais
    if args.json:
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.csv:
        import csv
        import io
        
        output = io.StringIO()
        if results:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(output.getvalue())

if __name__ == "__main__":
    main() 