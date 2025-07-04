import pandas as pd

# Exemplo para o arquivo SINAPI (Caixa)
df_sinapi = pd.read_csv("data/formatado/sinapi.txt", sep="\t")  # ajuste o separador se necessário
df_sinapi["orgao"] = "Caixa"

# Exemplo para o arquivo SICRO (DNIT)
df_sicro = pd.read_csv("data/formatado/sicro.txt", sep="\t")
df_sicro["orgao"] = "DNIT"

# Exemplo para o arquivo de São Paulo (usando cpos.txt)
df_sp = pd.read_csv("data/formatado/cpos.txt", sep="\t")
df_sp["orgao"] = "Governo de São Paulo"

# Agora você pode passar esses DataFrames para o Langflow!