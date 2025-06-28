# Planejamento de Desenvolvimento - Sistema RAG para Planilhas

## Visão Geral do Projeto

### Objetivo Principal
Desenvolver um sistema RAG (Retrieval-Augmented Generation) para processamento automatizado de planilhas de preços de referência de obras públicas, com capacidade de extração, classificação e consulta inteligente de dados.

### Escopo do Sistema
- Monitoramento automático de pasta de documentos PDF
- Extração e processamento de planilhas de preços
- Identificação e classificação de tipos de planilhas
- Armazenamento estruturado em banco de dados
- Interface de consulta via Langflow

## Arquitetura do Sistema

### Componentes Principais

1. **File Monitor** (`src/processors/file_monitor.py`)
   - Monitora pasta "D:\docs_baixados"
   - Detecta novos arquivos PDF
   - Mantém catálogo de arquivos processados

2. **PDF Processor** (`src/processors/pdf_processor.py`)
   - Extrai dados de planilhas de PDFs
   - Identifica tabelas e estruturas de dados
   - Converte para formato estruturado

3. **Spreadsheet Classifier** (`src/processors/spreadsheet_classifier.py`)
   - Identifica planilhas de preços de referência
   - Classifica por tipo (SINAPI, SICRO, CPOS, EMOP, etc.)
   - Filtra planilhas não relevantes

4. **Database Manager** (`src/database/db_manager.py`)
   - Gerencia conexão com banco de dados
   - Operações CRUD para serviços
   - Índices para consultas eficientes

5. **Data Models** (`src/models/`)
   - Modelos de dados para serviços
   - Schemas de validação
   - DTOs para transferência de dados

6. **RAG Engine** (`src/core/rag_engine.py`)
   - Sistema de recuperação de informações
   - Integração com Langflow
   - Processamento de consultas

## Estrutura de Dados

### Tabela: Services
```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50) NOT NULL,           -- SINAPI, SICRO, CPOS, EMOP, CRIADA
    origin_file VARCHAR(500) NOT NULL,     -- Arquivo de origem
    service_code VARCHAR(100) NOT NULL,    -- Código do serviço
    base_date DATE NOT NULL,               -- Data base do preço
    description TEXT NOT NULL,             -- Descrição do serviço
    is_loaded BOOLEAN NOT NULL,            -- Onerado/Desonerado
    value DECIMAL(15,2) NOT NULL,          -- Valor em R$
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: ProcessedFiles
```sql
CREATE TABLE processed_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path VARCHAR(500) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processed', -- processed, failed, pending
    error_message TEXT,
    services_count INTEGER DEFAULT 0
);
```

## Cronograma de Desenvolvimento

### Fase 1: Estrutura Base (Semana 1) ✅
- [x] Organização do projeto
- [x] Configuração do Git
- [x] Estrutura de pastas
- [x] Documentação inicial

### Fase 2: Sistema de Monitoramento (Semana 2)
- [ ] **Módulo File Monitor**
  - Classe `FileMonitor` para monitorar pasta
  - Sistema de detecção de novos arquivos
  - Catálogo de arquivos processados
  - Logs de atividades

- [ ] **Módulo Database Manager**
  - Configuração do SQLite
  - Criação das tabelas
  - Operações básicas CRUD
  - Sistema de migrações

### Fase 3: Processamento de PDF (Semana 3-4)
- [ ] **Módulo PDF Processor**
  - Extração de texto de PDFs
  - Identificação de tabelas
  - Conversão para dados estruturados
  - Tratamento de erros

- [ ] **Módulo Spreadsheet Classifier**
  - Identificação de planilhas de preços
  - Classificação por tipo
  - Filtros de relevância
  - Validação de dados

### Fase 4: Sistema RAG (Semana 5-6)
- [ ] **Módulo RAG Engine**
  - Integração com ChromaDB
  - Sistema de embeddings
  - Recuperação de informações
  - Processamento de consultas

- [ ] **Integração com Langflow**
  - Configuração do fluxo
  - Interface de consulta
  - Relatórios e visualizações

### Fase 5: Testes e Refinamentos (Semana 7-8)
- [ ] **Testes Unitários**
  - Testes para cada módulo
  - Testes de integração
  - Testes de performance

- [ ] **Otimizações**
  - Melhorias de performance
  - Tratamento de erros
  - Documentação final

## Tecnologias e Dependências

### Backend
- **Python 3.8+**: Linguagem principal
- **SQLite**: Banco de dados local
- **ChromaDB**: Vector database para RAG
- **PyPDF2/pdfplumber**: Processamento de PDFs
- **pandas**: Manipulação de dados
- **pydantic**: Validação de dados

### Frontend/Interface
- **Langflow**: Interface de consulta
- **Streamlit** (opcional): Dashboard adicional

### Infraestrutura
- **Ollama**: LLM local
- **Git**: Controle de versão
- **Docker** (opcional): Containerização

## Padrões de Desenvolvimento

### Código
- **PEP 8**: Padrão de estilo Python
- **Type Hints**: Tipagem estática
- **Docstrings**: Documentação inline
- **Logging**: Sistema de logs estruturado

### Arquitetura
- **MVC**: Separação de responsabilidades
- **Repository Pattern**: Acesso a dados
- **Factory Pattern**: Criação de objetos
- **Observer Pattern**: Monitoramento de eventos

### Testes
- **pytest**: Framework de testes
- **unittest.mock**: Mocks para testes
- **coverage**: Cobertura de código

## Métricas de Sucesso

### Funcionalidade
- [ ] Processamento de 100% dos PDFs válidos
- [ ] Identificação correta de 95% das planilhas
- [ ] Tempo de resposta < 2s para consultas
- [ ] Zero perda de dados durante processamento

### Qualidade
- [ ] 90% de cobertura de testes
- [ ] Zero erros críticos em produção
- [ ] Documentação completa
- [ ] Código revisado e aprovado

### Performance
- [ ] Processamento de 100 PDFs/hora
- [ ] Armazenamento eficiente de dados
- [ ] Consultas otimizadas
- [ ] Uso de memória controlado

## Riscos e Mitigações

### Riscos Técnicos
1. **PDFs com estrutura complexa**
   - Mitigação: Múltiplas estratégias de extração
   - Fallback para processamento manual

2. **Performance com muitos arquivos**
   - Mitigação: Processamento em lotes
   - Sistema de filas assíncrono

3. **Qualidade dos dados extraídos**
   - Mitigação: Validação rigorosa
   - Sistema de correção manual

### Riscos de Projeto
1. **Prazo de entrega**
   - Mitigação: Sprints bem definidos
   - Priorização de funcionalidades críticas

2. **Mudanças de requisitos**
   - Mitigação: Arquitetura flexível
   - Comunicação constante com stakeholders

## Próximos Passos

1. **Imediato** (Esta semana)
   - Implementar File Monitor
   - Configurar banco de dados
   - Criar modelos de dados

2. **Curto Prazo** (Próximas 2 semanas)
   - Desenvolver PDF Processor
   - Implementar Spreadsheet Classifier
   - Testes unitários básicos

3. **Médio Prazo** (Próximas 4 semanas)
   - Sistema RAG completo
   - Integração com Langflow
   - Testes de integração

4. **Longo Prazo** (Próximas 8 semanas)
   - Otimizações de performance
   - Documentação completa
   - Deploy em produção 