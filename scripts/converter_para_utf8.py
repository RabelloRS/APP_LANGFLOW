from pathlib import Path

# Lista de arquivos a converter
arquivos = [
    "data/formatado/cpos.txt",
    "data/formatado/sinapi.txt",
    "data/formatado/sicro.txt",
]

# Tenta converter cada arquivo para UTF-8
for caminho in arquivos:
    arquivo = Path(caminho)
    if not arquivo.exists():
        print(f"Arquivo não encontrado: {arquivo}")
        continue
    for encoding in ["latin1", "windows-1252", "iso-8859-1"]:
        try:
            texto = arquivo.read_text(encoding=encoding)
            arquivo.write_text(texto, encoding="utf-8")
            print(f"Arquivo '{arquivo}' convertido de {encoding} para UTF-8 com sucesso!")
            break
        except Exception as e:
            print(f"Falha ao tentar {encoding} em '{arquivo}': {e}")
    else:
        print(f"Não foi possível converter '{arquivo}'. Verifique a codificação manualmente.")
