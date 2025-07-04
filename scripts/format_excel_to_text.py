import os
import pandas as pd
from datetime import datetime
import locale
import re

def setup_brazilian_locale():
    """Configura o locale para o padrão brasileiro"""
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except locale.Error:
            print("Aviso: Não foi possível configurar o locale brasileiro. Usando padrão do sistema.")

def format_brazilian_currency(value):
    """Formata valores como moeda brasileira"""
    if pd.isna(value):
        return ""
    try:
        # Remove espaços extras antes de formatar
        clean_value = str(value).strip()
        return locale.currency(float(clean_value), grouping=True, symbol=False)
    except (ValueError, TypeError):
        return str(value)

def clean_text(text):
    """Remove espaços extras e caracteres desnecessários do texto"""
    if pd.isna(text):
        return ""
    # Remove espaços no início e fim
    text = str(text).strip()
    # Substitui múltiplos espaços por um único espaço
    text = re.sub(r'\s+', ' ', text)
    return text

def standardize_columns(df, file_name):
    """
    Padroniza as colunas do DataFrame e adiciona a coluna fonte
    """
    # Remove a primeira linha se for cabeçalho existente
    if len(df) > 0:
        # Verifica se a primeira linha parece ser um cabeçalho (contém strings)
        first_row = df.iloc[0]
        if all(isinstance(val, str) for val in first_row if pd.notna(val)):
            df = df.iloc[1:].reset_index(drop=True)
    
    # Limpa os nomes das colunas existentes
    df.columns = [clean_text(col).lower() for col in df.columns]
    
    # Mapeia colunas existentes para o padrão esperado
    column_mapping = {}
    
    # Mapeia possíveis nomes de colunas para o padrão
    possible_codigo = ['codigo', 'código', 'cod', 'cód', 'item', 'número', 'numero']
    possible_descricao = ['descricao', 'descrição', 'desc', 'denominacao', 'denominação', 'nome', 'texto', 'nome do serviço', 'nome do servico']
    possible_unidade = ['unidade', 'und', 'um', 'medida', 'unit', 'unid']
    possible_preco = ['preco', 'preço', 'valor', 'custo', 'price', 'unitario', 'unitário']
    
    # Encontra as colunas correspondentes
    for col in df.columns:
        col_lower = col.lower()
        
        if any(term in col_lower for term in possible_codigo) and 'codigo' not in column_mapping:
            column_mapping[col] = 'codigo'
        elif any(term in col_lower for term in possible_descricao) and 'descricao' not in column_mapping:
            column_mapping[col] = 'descricao'
        elif any(term in col_lower for term in possible_unidade) and 'unidade' not in column_mapping:
            column_mapping[col] = 'unidade'
        elif any(term in col_lower for term in possible_preco) and 'preco_unitario' not in column_mapping:
            column_mapping[col] = 'preco_unitario'
    
    # Renomeia as colunas encontradas
    df = df.rename(columns=column_mapping)
    
    # Adiciona colunas faltantes com valores padrão
    if 'codigo' not in df.columns:
        df['codigo'] = ''
    if 'descricao' not in df.columns:
        df['descricao'] = ''
    if 'unidade' not in df.columns:
        df['unidade'] = ''
    if 'preco_unitario' not in df.columns:
        df['preco_unitario'] = ''
    
    # Adiciona a coluna fonte com o nome do arquivo
    df['fonte'] = os.path.splitext(file_name)[0]
    
    # Reordena as colunas conforme especificado
    expected_columns = ['codigo', 'descricao', 'unidade', 'preco_unitario', 'fonte']
    return df[expected_columns]

def excel_to_text(file_path, output_dir, output_format='txt'):
    """
    Converte um arquivo Excel para texto formatado (TXT ou MD)
    com validação de colunas e limpeza de dados
    
    Args:
        file_path (str): Caminho do arquivo Excel
        output_dir (str): Pasta de saída
        output_format (str): 'txt' ou 'md' para o formato de saída
    """
    try:
        # Lê o arquivo Excel
        xls = pd.ExcelFile(file_path)
        file_name = os.path.basename(file_path)
        
        # Processa cada planilha no arquivo
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Padroniza as colunas e adiciona fonte
            df = standardize_columns(df, file_name)
            
            # Aplica limpeza em todos os campos
            df = df.map(clean_text)
            
            # Formata o preço unitário
            df['preco_unitario'] = df['preco_unitario'].apply(format_brazilian_currency)
            
            # Determina o nome do arquivo de saída
            base_name = os.path.splitext(file_name)[0]
            output_file = f"{base_name}_{sheet_name}.{output_format}"
            output_path = os.path.join(output_dir, output_file)
            
            # Cria o conteúdo formatado
            lines = []
            
            if output_format == 'md':
                lines.append(f"# {base_name} - {sheet_name}\n")
                lines.append(f"*Arquivo convertido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n")
                lines.append("\n")
                
                # Cabeçalho da tabela Markdown
                headers = "| " + " | ".join(df.columns) + " |"
                separators = "| " + " | ".join(["---"] * len(df.columns)) + " |"
                lines.extend([headers, separators])
                
                # Linhas da tabela
                for _, row in df.iterrows():
                    line = "| " + " | ".join(row) + " |"
                    lines.append(line)
            else:  # TXT
                lines.append(f"ARQUIVO: {base_name} - PLANILHA: {sheet_name}")
                lines.append(f"DATA DA CONVERSÃO: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                lines.append("\n")
                
                # Determina a largura das colunas
                col_widths = [
                    max(df[col].astype(str).str.len().max(), len(col)) 
                    for col in df.columns
                ]
                
                # Cabeçalho padronizado
                header = "  ".join(
                    col.upper().ljust(width) 
                    for col, width in zip(df.columns, col_widths)
                )
                lines.append(header)
                lines.append("-" * len(header))
                
                # Linhas
                for _, row in df.iterrows():
                    formatted_row = []
                    for value, width in zip(row, col_widths):
                        formatted_value = str(value).ljust(width)
                        formatted_row.append(formatted_value)
                    line = "  ".join(formatted_row)
                    lines.append(line)
            
            # Escreve o arquivo de saída
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            print(f"Arquivo convertido com sucesso: {output_path}")
            print(f"  - Linhas processadas: {len(df)}")
            print(f"  - Colunas: {', '.join(df.columns)}")
    
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {str(e)}")

def process_formatado_folder():
    """Processa automaticamente a pasta data/formatado"""
    # Configura o locale brasileiro
    setup_brazilian_locale()
    
    # Define os caminhos
    input_dir = os.path.join("data", "formatado")
    output_dir = os.path.join("data", "formatado")
    output_format = 'txt'  # Pode ser alterado para 'md' se desejar
    
    # Verifica se a pasta de entrada existe
    if not os.path.exists(input_dir):
        print(f"Pasta de entrada não encontrada: {input_dir}")
        return
    
    # Cria a pasta de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Conta arquivos Excel encontrados
    excel_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.xls', '.xlsx'))]
    
    if not excel_files:
        print(f"Nenhum arquivo Excel encontrado em: {input_dir}")
        return
    
    print(f"Encontrados {len(excel_files)} arquivo(s) Excel para processar:")
    for file in excel_files:
        print(f"  - {file}")
    
    print(f"\nIniciando conversão para formato {output_format.upper()}...")
    print("Padronizando cabeçalhos e adicionando coluna 'fonte'...")
    
    # Processa todos os arquivos Excel na pasta
    for filename in excel_files:
        file_path = os.path.join(input_dir, filename)
        print(f"\nProcessando: {filename}")
        excel_to_text(file_path, output_dir, output_format)
    
    print("\nConversão concluída!")

if __name__ == "__main__":
    process_formatado_folder() 