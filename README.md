# Sistema RAG para Planilhas de Obras Públicas

## Descrição do Projeto

Este projeto implementa um sistema RAG (Retrieval-Augmented Generation) para processamento e análise de planilhas de preços de referência de obras públicas. O sistema é capaz de:

- Monitorar uma pasta de documentos PDF
- Extrair dados de planilhas de preços de referência
- Identificar e filtrar planilhas relevantes (SINAPI, SICRO, CPOS, EMOP, etc.)
- Armazenar dados estruturados em banco de dados
- Fornecer interface via Langflow para consultas

## Estrutura do Projeto

```
APP_LANGFLOW/
├── src/                    # Código fonte principal
│   ├── core/              # Módulos principais do sistema (e.g., file_monitor, ai_classifier, cli_search, price_source_manager)
│   ├── processors/        # Processadores de documentos (e.g., government_spreadsheet_processor)
│   ├── database/          # Camada de acesso a dados (e.g., db_manager)
│   ├── utils/             # Utilitários e helpers (e.g., logger)
│   ├── models/            # Modelos de dados (e.g., processed_file, service)
│   └── web/               # Interface web (e.g., app.py, templates/)
├── config/                # Arquivos de configuração
├── data/                  # Dados de exemplo e processados
├── database/              # Banco de dados e índices
├── docs/                  # Documentação
├── scripts/               # Scripts de inicialização
├── tests/                 # Testes automatizados
└── old/                   # Arquivos antigos não relacionados
```

## Funcionalidades Principais

### ✅ Concluído
- [x] Script para iniciar Langflow por ícone na área de trabalho
- [x] Estrutura básica do projeto
- [x] Configuração inicial do RAG

### 🚧 Em Desenvolvimento
- [ ] Sistema de monitoramento da pasta "D:\docs_baixados"
- [ ] Processador de PDF para extração de planilhas
- [ ] Identificador de planilhas de preços de referência
- [ ] Banco de dados para armazenamento de serviços
- [ ] Interface de consulta via Langflow

## Banco de Dados

O sistema armazenará as seguintes informações para cada serviço:

- **Fonte**: SINAPI, SICRO, CPOS, EMOP, CRIADA
- **Origem da Informação**: Arquivo de onde foi extraído
- **Código do Serviço**: Código alfanumérico do sistema de preços
- **Data Base**: Data de referência do preço
- **Descrição do Serviço**: Descrição detalhada
- **Tipo**: Onerado ou Desonerado
- **Valor**: Preço em R$ (Brasil)

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Ollama (para LLM local)
- Langflow

### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd APP_LANGFLOW

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente
python src/core/setup_rag_planilhas.py
```

### Inicialização
```bash
# Inicie o Langflow
./scripts/start_langflow.bat
```

## Desenvolvimento

### Estrutura de Módulos

1. **Core**: Módulos principais do sistema RAG
2. **Processors**: Processadores de documentos PDF
3. **Database**: Camada de acesso e modelos de dados
4. **Utils**: Utilitários e helpers
5. **Models**: Modelos de dados e schemas

### Padrões de Desenvolvimento

- Código em português para comentários e documentação
- Nomes de variáveis e funções em inglês
- Documentação inline para funções complexas
- Testes unitários para módulos críticos

## Roadmap

### Fase 1 - Estrutura Base ✅
- [x] Organização do projeto
- [x] Configuração do Git
- [x] Estrutura de pastas

### Fase 2 - Processamento de Documentos 🚧
- [ ] Monitor de pasta
- [ ] Extrator de PDF
- [ ] Identificador de planilhas

### Fase 3 - Banco de Dados 🚧
- [ ] Modelo de dados
- [ ] Sistema de armazenamento
- [ ] APIs de consulta

### Fase 4 - Interface e Integração 🚧
- [ ] Interface Langflow
- [ ] Sistema de consultas
- [ ] Relatórios

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é de uso interno para processamento de planilhas de obras públicas.

## Contato

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento. 