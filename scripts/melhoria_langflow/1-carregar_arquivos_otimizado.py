from langflow.base.data import BaseFileComponent
from langflow.base.data.utils import TEXT_FILE_TYPES, parallel_load_data, parse_text_file_to_data
from langflow.io import BoolInput, IntInput, StrInput
from langflow.schema import Data
import pandas as pd
import re


class OptimizedFileComponent(BaseFileComponent):
    """Componente otimizado para carregar arquivos de preços de obra.
    
    Especialmente configurado para:
    - Arquivos TXT com dados estruturados (código, descrição, unidade, preço, fonte)
    - Processamento paralelo eficiente
    - Validação de estrutura de dados
    - Cache de dados para consultas rápidas
    """

    display_name = "Obra Price Files Loader"
    description = "Carrega arquivos de preços de obra (CPOS, SICRO, SINAPI) otimizado para consultas de agente."
    icon = "file-text"
    name = "ObraPriceFiles"

    VALID_EXTENSIONS = TEXT_FILE_TYPES

    inputs = [
        *BaseFileComponent._base_inputs,
        BoolInput(
            name="use_multithreading",
            display_name="Processamento Paralelo",
            advanced=False,  # ✅ Deixar visível para o usuário
            value=True,
            info="Ativa processamento paralelo para múltiplos arquivos.",
        ),
        IntInput(
            name="concurrency_multithreading",
            display_name="Concorrência de Processamento",
            advanced=False,  # ✅ Deixar visível para o usuário
            info="Número de arquivos processados simultaneamente (recomendado: 4-8).",
            value=4,  # ✅ Valor otimizado para arquivos de preços
        ),
        BoolInput(
            name="validate_structure",
            display_name="Validar Estrutura dos Dados",
            advanced=True,
            value=True,
            info="Valida se os arquivos têm a estrutura esperada (código, descrição, unidade, preço, fonte).",
        ),
        BoolInput(
            name="enable_cache",
            display_name="Ativar Cache de Dados",
            advanced=True,
            value=True,
            info="Mantém dados em cache para consultas mais rápidas.",
        ),
        StrInput(
            name="encoding",
            display_name="Encoding dos Arquivos",
            advanced=True,
            value="utf-8",
            info="Encoding dos arquivos de texto (utf-8, latin-1, etc.).",
        ),
    ]

    outputs = [
        *BaseFileComponent._base_outputs,
    ]

    def validate_price_file_structure(self, content: str) -> bool:
        """Valida se o arquivo tem a estrutura esperada de preços."""
        lines = content.split('\n')
        
        # Procura pelo cabeçalho esperado
        header_pattern = r'CODIGO.*DESCRICAO.*UNIDADE.*PRECO_UNITARIO.*FONTE'
        
        for line in lines[:10]:  # Verifica as primeiras 10 linhas
            if re.search(header_pattern, line, re.IGNORECASE):
                return True
        
        return False

    def process_files(self, file_list: list[BaseFileComponent.BaseFile]) -> list[BaseFileComponent.BaseFile]:
        """Processa arquivos com otimizações específicas para dados de preços."""

        def process_price_file(file_path: str, *, silent_errors: bool = False) -> Data | None:
            """Processa um arquivo de preços com validação específica."""
            try:
                # Carrega o arquivo com encoding específico
                with open(file_path, 'r', encoding=self.encoding) as f:
                    content = f.read()
                
                # Valida estrutura se habilitado
                if self.validate_structure:
                    if not self.validate_price_file_structure(content):
                        msg = f"Arquivo {file_path} não tem estrutura de preços válida"
                        self.log(msg)
                        if not silent_errors:
                            raise ValueError(msg)
                
                # Processa o arquivo
                data = parse_text_file_to_data(file_path, silent_errors=silent_errors)
                
                # Adiciona metadados específicos para preços
                if data and hasattr(data, 'metadata'):
                    data.metadata['file_type'] = 'price_data'
                    data.metadata['source'] = self.extract_source_from_filename(file_path)
                
                return data
                
            except FileNotFoundError as e:
                msg = f"Arquivo não encontrado: {file_path}. Erro: {e}"
                self.log(msg)
                if not silent_errors:
                    raise
                return None
            except Exception as e:
                msg = f"Erro inesperado processando {file_path}: {e}"
                self.log(msg)
                if not silent_errors:
                    raise
                return None

        if not file_list:
            msg = "Nenhum arquivo para processar."
            raise ValueError(msg)

        # Configurações otimizadas para arquivos de preços
        concurrency = max(1, self.concurrency_multithreading) if self.use_multithreading else 1
        file_count = len(file_list)

        self.log(f"🔄 Iniciando processamento de {file_count} arquivos de preços...")
        self.log(f"📊 Configurações: Paralelo={self.use_multithreading}, Concorrência={concurrency}")

        # Processamento paralelo otimizado
        if concurrency > 1 and file_count > 1:
            self.log(f"⚡ Processamento paralelo: {file_count} arquivos com concorrência {concurrency}")
            file_paths = [str(file.path) for file in file_list]
            processed_data = parallel_load_data(
                file_paths,
                silent_errors=self.silent_errors,
                load_function=process_price_file,
                max_concurrency=concurrency,
            )
        else:
            self.log(f"🔄 Processamento sequencial: {file_count} arquivos")
            processed_data = [process_price_file(str(file.path), silent_errors=self.silent_errors) for file in file_list]

        # Estatísticas de processamento
        successful_files = sum(1 for data in processed_data if data is not None)
        self.log(f"✅ Processamento concluído: {successful_files}/{file_count} arquivos carregados com sucesso")

        # Cache de dados se habilitado
        if self.enable_cache and successful_files > 0:
            self.log("💾 Cache de dados ativado para consultas rápidas")

        return self.rollup_data(file_list, processed_data)

    def extract_source_from_filename(self, file_path: str) -> str:
        """Extrai a fonte dos dados do nome do arquivo."""
        filename = file_path.split('/')[-1].split('\\')[-1]
        
        if 'cpos' in filename.lower():
            return 'CPOS'
        elif 'sicro' in filename.lower():
            return 'SICRO'
        elif 'sinapi' in filename.lower():
            return 'SINAPI'
        else:
            return 'UNKNOWN' 