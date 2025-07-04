import os
import re

# Lista de arquivos a tratar
arquivos = [
    r"c:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\data\formatado\sinapi.txt",
    r"c:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\data\formatado\sicro.txt",
    r"c:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\data\formatado\cpos.txt"
]

def limpar_linha(linha):
    # Remove caracteres invisíveis comuns (exceto tabulação e quebra de linha)
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u200b\ufeff]', '', linha)

for arquivo in arquivos:
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    linhas_limpa = [limpar_linha(l) for l in linhas]
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.writelines(linhas_limpa)

print('Arquivos tratados e salvos.')
