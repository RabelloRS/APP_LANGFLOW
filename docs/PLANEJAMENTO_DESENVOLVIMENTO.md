# Planejamento de Desenvolvimento - Sistema RAG para Planilhas

## Visão Geral do Projeto

### Objetivo Principal
Desenvolver um sistema RAG (Retrieval-Augmented Generation) para processamento automatizado de planilhas de preços de referência de obras públicas, com capacidade de extração, classificação e consulta inteligente de dados.

### Escopo do Sistema
- Monitoramento automático de pasta de documentos (PDF, Word, planilhas, arquivos compactados)
- Extração e processamento de planilhas de preços
- Descompactação automática de arquivos
- **Classificação inteligente por IA** para identificar planilhas de serviços de engenharia
- Identificação e classificação de tipos de planilhas
- Armazenamento estruturado em banco de dados
- Interface de consulta via Langflow

## Arquitetura do Sistema

### Componentes Principais

1. **File Monitor** (`src/processors/file_monitor.py`)
   - Monitora pasta "D:\docs_baixados" e subpastas
   - Detecta novos arquivos (PDF, Word, planilhas, compactados)
   - Mantém catálogo de arquivos processados
   - Sistema de logs de atividades

2. **Archive Extractor** (`src/processors/archive_extractor.py`)
   - Descompacta arquivos ZIP, 7ZIP, RAR
   - Remove arquivos compactados após extração
   - Organiza arquivos extraídos

3. **AI Document Classifier** (`src/processors/ai_classifier.py`)
   - **IA para classificação inteligente de documentos**
   - Identifica planilhas de serviços de engenharia
   - Treinamento com modelos de referência
   - Classificação por relevância e tipo
   - Sistema de confiança e validação

4. **File Classifier** (`src/processors/file_classifier.py`)
   - Classifica arquivos por tipo
   - Identifica planilhas em documentos
   - Move arquivos sem planilhas para pasta de descarte
   - Integração com AI Classifier

5. **PDF Processor** (`src/processors/pdf_processor.py`)
   - Extrai dados de planilhas de PDFs
   - Identifica tabelas e estruturas de dados
   - Converte para formato estruturado

6. **Word Processor** (`src/processors/word_processor.py`)
   - Extrai dados de planilhas de documentos Word
   - Identifica tabelas e estruturas de dados
   - Converte para formato estruturado

7. **Spreadsheet Processor** (`src/processors/spreadsheet_processor.py`)
   - Processa planilhas Excel, CSV, etc.
   - Identifica planilhas de preços de referência
   - Classifica por tipo (SINAPI, SICRO, CPOS, EMOP, etc.)
   - Filtra planilhas não relevantes

8. **Database Manager** (`src/database/db_manager.py`)
   - Gerencia conexão com banco de dados
   - Operações CRUD para serviços
   - Índices para consultas eficientes

9. **Data Models** (`src/models/`)
   - Modelos de dados para serviços
   - Schemas de validação
   - DTOs para transferência de dados

10. **RAG Engine** (`src/core/rag_engine.py`)
    - Sistema de recuperação de informações
    - Integração com Langflow
    - Processamento de consultas

## Sistema de IA para Classificação

### Componente: AI Document Classifier

#### Funcionalidades Principais
- **Análise de Conteúdo**: Extração e análise de texto de documentos
- **Classificação por Relevância**: Identifica se o documento contém planilhas de serviços de engenharia
- **Classificação por Tipo**: Identifica o tipo específico (SINAPI, SICRO, CPOS, EMOP, etc.)
- **Sistema de Confiança**: Score de confiança para cada classificação
- **Aprendizado Contínuo**: Melhoria baseada em feedback do usuário

#### Modelos de Treinamento
1. **Modelos de Referência SINAPI**
   - Planilhas oficiais do SINAPI
   - Estruturas típicas de composições
   - Padrões de códigos e descrições

2. **Modelos de Referência SICRO**
   - Planilhas oficiais do SICRO
   - Estruturas específicas de serviços rodoviários
   - Padrões de códigos rodoviários

3. **Modelos de Referência CPOS**
   - Planilhas de preços de referência
   - Estruturas de orçamentos
   - Padrões de composições

4. **Modelos de Referência EMOP**
   - Planilhas de empresas públicas
   - Estruturas específicas de cada empresa
   - Padrões de códigos internos

5. **Modelos de Referência CRIADA**
   - Planilhas criadas internamente
   - Estruturas customizadas
   - Padrões específicos da organização

#### Técnicas de IA Utilizadas
- **NLP (Natural Language Processing)**: Análise de texto e contexto
- **Machine Learning**: Classificação supervisionada
- **Embeddings**: Representação vetorial de documentos
- **Similarity Matching**: Comparação com modelos de referência
- **Confidence Scoring**: Avaliação de confiança das classificações

#### Fluxo de Classificação
1. **Extração de Texto**: Extrai texto do documento
2. **Análise de Estrutura**: Identifica tabelas e estruturas
3. **Classificação por IA**: Usa modelo treinado para classificar
4. **Validação**: Confirma classificação com regras específicas
5. **Score de Confiança**: Calcula nível de confiança
6. **Feedback Loop**: Aprende com resultados

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
    file_type VARCHAR(50) NOT NULL,        -- pdf, doc, xlsx, csv, etc.
    original_archive VARCHAR(500),          -- Arquivo compactado original
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processed', -- processed, failed, pending, discarded
    error_message TEXT,
    services_count INTEGER DEFAULT 0,
    has_spreadsheets BOOLEAN DEFAULT FALSE, -- Se contém planilhas
    ai_classification VARCHAR(100),         -- Classificação da IA
    ai_confidence DECIMAL(3,2),            -- Score de confiança (0.00-1.00)
    ai_relevant BOOLEAN DEFAULT FALSE       -- Se é relevante para engenharia
);
```

### Tabela: FileOperations
```sql
CREATE TABLE file_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type VARCHAR(50) NOT NULL,   -- extract, move, delete, process, classify
    file_path VARCHAR(500) NOT NULL,
    target_path VARCHAR(500),              -- Para operações de movimentação
    operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    error_message TEXT
);
```

### Tabela: AIModels
```sql
CREATE TABLE ai_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(100) NOT NULL,      -- Nome do modelo
    model_type VARCHAR(50) NOT NULL,       -- classification, extraction, validation
    model_version VARCHAR(20) NOT NULL,    -- Versão do modelo
    training_data_path VARCHAR(500),       -- Caminho dos dados de treinamento
    accuracy DECIMAL(5,4),                 -- Precisão do modelo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Tabela: TrainingData
```sql
CREATE TABLE training_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path VARCHAR(500) NOT NULL,
    classification VARCHAR(100) NOT NULL,  -- Classificação manual
    is_relevant BOOLEAN NOT NULL,          -- Se é relevante
    confidence_score DECIMAL(3,2),         -- Score de confiança manual
    notes TEXT,                            -- Observações
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Cronograma de Desenvolvimento

### Fase 1: Estrutura Base (Semana 1) ✅
- [x] Organização do projeto
- [x] Configuração do Git
- [x] Estrutura de pastas
- [x] Documentação inicial

### Fase 2: Sistema de Monitoramento e IA (Semana 2-3)
- [ ] **Módulo File Monitor**
  - Classe `FileMonitor` para monitorar pasta e subpastas
  - Sistema de detecção de novos arquivos
  - Suporte a múltiplos formatos (PDF, Word, planilhas, compactados)
  - Catálogo de arquivos processados
  - Logs de atividades

- [ ] **Módulo Archive Extractor**
  - Descompactação de ZIP, 7ZIP, RAR
  - Remoção automática de arquivos compactados
  - Organização de arquivos extraídos
  - Tratamento de erros de extração

- [ ] **Módulo AI Document Classifier**
  - **Sistema de IA para classificação de documentos**
  - Treinamento com modelos de referência
  - Classificação por relevância e tipo
  - Sistema de confiança e validação
  - Interface para feedback e melhoria

- [ ] **Módulo File Classifier**
  - Classificação de arquivos por tipo
  - Integração com AI Classifier
  - Movimentação para pasta de descarte
  - Logs de operações

- [ ] **Módulo Database Manager**
  - Configuração do SQLite
  - Criação das tabelas (Services, ProcessedFiles, FileOperations, AIModels, TrainingData)
  - Operações básicas CRUD
  - Sistema de migrações

- [ ] **Módulo Logger**
  - Sistema de logging estruturado
  - Rotação de logs
  - Diferentes níveis de log
  - Logs específicos por operação

### Fase 3: Processamento de Documentos (Semana 4-5)
- [ ] **Módulo PDF Processor**
  - Extração de texto de PDFs
  - Identificação de tabelas
  - Conversão para dados estruturados
  - Tratamento de erros

- [ ] **Módulo Word Processor**
  - Extração de texto de documentos Word
  - Identificação de tabelas
  - Conversão para dados estruturados
  - Tratamento de erros

- [ ] **Módulo Spreadsheet Processor**
  - Processamento de Excel, CSV, etc.
  - Identificação de planilhas de preços
  - Classificação por tipo
  - Filtros de relevância
  - Validação de dados

### Fase 4: Sistema RAG (Semana 6-7)
- [ ] **Módulo RAG Engine**
  - Integração com ChromaDB
  - Sistema de embeddings
  - Recuperação de informações
  - Processamento de consultas

- [ ] **Integração com Langflow**
  - Configuração do fluxo
  - Interface de consulta
  - Relatórios e visualizações

### Fase 5: Testes e Refinamentos (Semana 8)
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
- **python-docx**: Processamento de documentos Word
- **pandas/openpyxl**: Manipulação de planilhas
- **pydantic**: Validação de dados
- **py7zr/zipfile/rarfile**: Descompactação de arquivos

### IA e Machine Learning
- **scikit-learn**: Machine Learning para classificação
- **transformers**: Modelos de NLP
- **sentence-transformers**: Embeddings de texto
- **torch**: Framework de deep learning
- **numpy**: Computação numérica

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
- **Strategy Pattern**: Diferentes processadores de arquivo
- **Pipeline Pattern**: Fluxo de processamento

### Testes
- **pytest**: Framework de testes
- **unittest.mock**: Mocks para testes
- **coverage**: Cobertura de código

## Métricas de Sucesso

### Funcionalidade
- [ ] Processamento de 100% dos arquivos válidos
- [ ] Descompactação automática de 95% dos arquivos
- [ ] **Classificação correta de 90% das planilhas por IA**
- [ ] **Identificação de 95% dos documentos relevantes**
- [ ] Tempo de resposta < 2s para consultas
- [ ] Zero perda de dados durante processamento

### Qualidade
- [ ] 90% de cobertura de testes
- [ ] Zero erros críticos em produção
- [ ] Documentação completa
- [ ] Código revisado e aprovado

### Performance
- [ ] Processamento de 100 arquivos/hora
- [ ] Descompactação eficiente
- [ ] **Classificação por IA em < 5s por arquivo**
- [ ] Armazenamento eficiente de dados
- [ ] Consultas otimizadas
- [ ] Uso de memória controlado

## Riscos e Mitigações

### Riscos Técnicos
1. **Arquivos compactados corrompidos**
   - Mitigação: Validação antes da extração
   - Fallback para processamento manual

2. **PDFs/Word com estrutura complexa**
   - Mitigação: Múltiplas estratégias de extração
   - Fallback para processamento manual

3. **Performance com muitos arquivos**
   - Mitigação: Processamento em lotes
   - Sistema de filas assíncrono

4. **Qualidade dos dados extraídos**
   - Mitigação: Validação rigorosa
   - Sistema de correção manual

5. **Precisão da IA de classificação**
   - Mitigação: Treinamento com dados de qualidade
   - Sistema de feedback e melhoria contínua
   - Validação manual para casos de baixa confiança

### Riscos de Projeto
1. **Prazo de entrega**
   - Mitigação: Sprints bem definidos
   - Priorização de funcionalidades críticas

2. **Mudanças de requisitos**
   - Mitigação: Arquitetura flexível
   - Comunicação constante com stakeholders

## Próximos Passos

1. **Imediato** (Esta semana)
   - Implementar File Monitor com suporte a subpastas
   - Criar Archive Extractor
   - **Desenvolver AI Document Classifier básico**
   - Implementar File Classifier
   - Configurar banco de dados expandido

2. **Curto Prazo** (Próximas 2 semanas)
   - **Treinar IA com modelos de referência**
   - Desenvolver processadores de PDF e Word
   - Implementar Spreadsheet Processor
   - Testes unitários básicos

3. **Médio Prazo** (Próximas 4 semanas)
   - **Melhorar precisão da IA**
   - Sistema RAG completo
   - Integração com Langflow
   - Testes de integração

4. **Longo Prazo** (Próximas 8 semanas)
   - **Sistema de IA autodidata**
   - Otimizações de performance
   - Documentação completa
   - Deploy em produção 