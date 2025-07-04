# Contexto do Projeto para o Gemini CLI

Este documento complementa o `README.md` e fornece informações adicionais sobre o contexto e os objetivos atuais do projeto para o Gemini CLI.

## Objetivo Principal Atual

O objetivo principal atual do projeto é desenvolver uma aplicação que, ao ser iniciada pelo usuário, realize uma varredura na pasta `D:\docs_baixados`. Esta varredura tem como finalidade identificar e processar arquivos que contenham tabelas de preços ou orçamentos de obras.

### Detalhes da Varredura e Processamento:

- **Tipos de Arquivos Suportados**: A aplicação deve ser capaz de ler e extrair informações de:
    - Planilhas (Excel: `.xlsx`, `.xls`, etc.), abrangendo todas as abas.
    - Documentos PDF, com foco em orçamentos de obras.
    - Arquivos JSON.
    - Documentos de texto (Word: `.doc`, `.docx`, e TXT: `.txt`), buscando listas ou tabelas.

- **Informações a Serem Extraídas**: Para cada item encontrado nas tabelas, o sistema deve extrair:
    - Referência de preço (ex: SINAPI, SICRO, SCO, EMOP).
    - Código do serviço.
    - Descrição do serviço.
    - Unidade de medida.
    - Preço unitário.

- **Armazenamento de Dados**: As informações extraídas serão incluídas em um banco de dados de forma estruturada. Este banco de dados servirá como fonte de informação para uma Large Language Model (LLM).

- **Análise Assistida por LLM**: Para garantir a precisão na busca e leitura dos dados, a análise dos arquivos será acompanhada e avaliada por uma LLM. Esta LLM deverá ser especificamente treinada para a tarefa de validação e refinamento da extração de dados de orçamentos e tabelas de preços.

Este novo foco expande as capacidades do sistema RAG existente, permitindo uma ingestão mais abrangente e inteligente de dados de diversas fontes para enriquecer a base de conhecimento da LLM.

## Componentes Estruturais Relevantes para o Objetivo Atual

Para suportar o objetivo de varredura e processamento de planilhas, os seguintes componentes foram adicionados ou são de particular importância:

- **`src/web/`**: Contém a interface web da aplicação, incluindo `app.py` (lógica do servidor) e `templates/` (arquivos HTML para a interface do usuário, como `index.html`, `search.html`, `database.html`, `banco_dados.html`, `processar_planilhas.html`).
- **`src/core/file_monitor.py`**: Responsável por monitorar a pasta `D:\docs_baixados` em busca de novos arquivos.
- **`src/core/ai_classifier.py`**: Provavelmente utilizado para classificar os documentos encontrados e determinar se são planilhas de preços/orçamentos.
- **`src/processors/government_spreadsheet_processor.py`**: Um processador específico para extrair dados de planilhas governamentais.
- **`src/database/db_manager.py`**: Gerencia a interação com o banco de dados onde os dados extraídos são armazenados.
- **`src/models/service.py` e `src/models/processed_file.py`**: Definem os modelos de dados para os serviços e arquivos processados, respectivamente.
- **`scripts/start_system.py` e `scripts/start_web_interface.bat`**: Scripts para iniciar a aplicação e a interface web.
