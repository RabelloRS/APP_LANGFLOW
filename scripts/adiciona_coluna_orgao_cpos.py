import pandas as pd

# Caminho do arquivo
arquivo = r"c:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\data\formatado\cpos.txt"

# Lê o arquivo, assumindo separador TAB e sem cabeçalho
df = pd.read_csv(arquivo, sep='\t', header=None, dtype=str)

# Adiciona a coluna 'orgao' com valor 'CPOS'
df['orgao'] = 'CPOS'

# Salva sobrescrevendo o arquivo, mantendo separador TAB e sem índice
df.to_csv(arquivo, sep='\t', header=False, index=False)
