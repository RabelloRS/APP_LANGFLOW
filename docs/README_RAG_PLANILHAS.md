# 📊 Sistema RAG para Planilhas de Orçamento - Solução Local

Este sistema permite criar um RAG (Retrieval-Augmented Generation) completo para analisar planilhas de orçamento usando **soluções 100% locais**, sem necessidade de serviços externos como Astra DB.

## 🎯 **O que o sistema faz:**

### ✅ **Funcionalidades Principais:**
- **Lê automaticamente** todas as planilhas da pasta `D:\docs_baixados`
- **Detecta planilhas de orçamento** baseado em palavras-chave
- **Extrai dados estruturados** (colunas, valores, estatísticas)
- **Cria embeddings locais** usando Sentence Transformers
- **Armazena no ChromaDB** (banco vetorial local)
- **Permite consultas inteligentes** sobre os orçamentos
- **Integra com Langflow** para interface visual

### 🔧 **Tecnologias Utilizadas:**
- **ChromaDB**: Banco de dados vetorial local
- **Ollama**: LLM local (Llama2, Mistral, etc.)
- **Pandas**: Processamento de planilhas
- **Sentence Transformers**: Embeddings locais
- **Langflow**: Interface visual para fluxos

---

## 🚀 **Instalação e Configuração**

### **1. Configuração Automática**
```bash
# Execute o script de configuração
python setup_rag_planilhas.py
```

### **2. Instalação Manual (se necessário)**
```bash
# Instalar dependências
pip install chromadb pandas openpyxl sentence-transformers numpy requests

# Ou usar o arquivo requirements
pip install -r requirements_rag.txt
```

### **3. Configurar Ollama**
```bash
# Baixar Ollama: https://ollama.ai/download
# Instalar e executar
ollama serve

# Baixar modelo (recomendado)
ollama pull llama2
```

---

## 📁 **Estrutura de Arquivos**

```
APP_LANGFLOW/
├── 📄 rag_planilhas_local.py          # Sistema RAG principal
├── 🎨 RAG_Planilhas_Local_Langflow.json # Fluxo para Langflow
├── ⚙️ setup_rag_planilhas.py          # Script de configuração
├── 📋 requirements_rag.txt            # Dependências
├── 📚 README_RAG_PLANILHAS.md         # Esta documentação
├── 📊 chroma_db/                      # Banco de dados local (criado automaticamente)
└── 📁 D:\docs_baixados\               # Pasta com suas planilhas
```

---

## 🔄 **Como Usar**

### **1. Preparar as Planilhas**
- Crie a pasta: `D:\docs_baixados`
- Coloque suas planilhas de orçamento (.xlsx, .xls, .csv)
- O sistema detectará automaticamente planilhas de orçamento

### **2. Processar as Planilhas**
```bash
# Executar o sistema RAG
python rag_planilhas_local.py
```

**O que acontece:**
1. ✅ Lê todas as planilhas da pasta
2. ✅ Extrai dados estruturados
3. ✅ Cria embeddings locais
4. ✅ Armazena no ChromaDB
5. ✅ Abre interface de consulta

### **3. Fazer Consultas**
Exemplos de perguntas que você pode fazer:
- "Quais orçamentos temos para clientes corporativos?"
- "Qual o valor total dos orçamentos de janeiro?"
- "Quais produtos aparecem mais nos orçamentos?"
- "Mostre orçamentos com valores acima de R$ 10.000"
- "Quais clientes têm mais orçamentos?"

### **4. Usar no Langflow**
1. Abra o Langflow
2. Clique em "Import"
3. Selecione o arquivo `RAG_Planilhas_Local_Langflow.json`
4. Configure a conexão com Ollama
5. Teste o fluxo

---

## 🎨 **Fluxo no Langflow**

O fluxo criado inclui:

### **Componentes:**
1. **Input Node**: Para inserir perguntas
2. **Text Splitter**: Divide o texto em chunks
3. **ChromaDB Node**: Busca no banco vetorial
4. **Prompt Template**: Formata a pergunta com contexto
5. **Ollama Node**: Gera resposta usando LLM local
6. **Output Node**: Exibe o resultado

### **Configuração:**
- **Coleção ChromaDB**: `orcamentos_planilhas`
- **Modelo Ollama**: `llama2` (configurável)
- **Número de resultados**: 5 (configurável)
- **Temperatura**: 0.7 (configurável)

---

## 📊 **Detecção de Planilhas de Orçamento**

O sistema detecta automaticamente se uma planilha é de orçamento baseado em palavras-chave:

### **Palavras-chave procuradas:**
- `orcamento`, `preço`, `valor`, `custo`
- `total`, `cliente`, `produto`, `serviço`
- `quantidade`, `unitário`, `subtotal`

### **Score de detecção:**
- **Score ≥ 2**: Classificado como "orcamento"
- **Score < 2**: Classificado como "planilha_geral"

---

## 🔍 **Exemplos de Consultas**

### **Consulta 1: Análise de Clientes**
```
Pergunta: "Quais são os principais clientes nos orçamentos?"
```

**Resposta esperada:**
- Lista de clientes mais frequentes
- Valores totais por cliente
- Análise de padrões

### **Consulta 2: Análise de Valores**
```
Pergunta: "Qual o valor médio dos orçamentos?"
```

**Resposta esperada:**
- Valor médio calculado
- Distribuição de valores
- Orçamentos mais altos/baixos

### **Consulta 3: Análise Temporal**
```
Pergunta: "Como evoluíram os orçamentos ao longo do tempo?"
```

**Resposta esperada:**
- Tendências temporais
- Sazonalidade
- Crescimento/queda

---

## ⚙️ **Configurações Avançadas**

### **Modificar Pasta de Documentos**
No arquivo `rag_planilhas_local.py`, linha 35:
```python
def __init__(self, pasta_docs: str = "D:\\docs_baixados", db_path: str = "./chroma_db"):
```

### **Ajustar Detecção de Orçamentos**
No arquivo `rag_planilhas_local.py`, linhas 95-100:
```python
palavras_chave_orcamento = [
    'orcamento', 'preço', 'valor', 'custo', 'total', 'cliente',
    'produto', 'serviço', 'quantidade', 'unitário', 'subtotal'
]
```

### **Configurar ChromaDB**
O banco é criado automaticamente na pasta `./chroma_db`. Para limpar:
```bash
# Remover banco existente
rm -rf ./chroma_db
```

---

## 🐛 **Solução de Problemas**

### **Erro: "Pasta não encontrada"**
```bash
# Criar pasta de documentos
mkdir "D:\docs_baixados"
```

### **Erro: "ChromaDB não conecta"**
```bash
# Verificar se a pasta chroma_db existe
ls -la ./chroma_db

# Recriar se necessário
rm -rf ./chroma_db
python rag_planilhas_local.py
```

### **Erro: "Ollama não responde"**
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama se necessário
ollama serve
```

### **Erro: "Modelo não encontrado"**
```bash
# Baixar modelo
ollama pull llama2

# Ou usar outro modelo disponível
ollama list
```

### **Planilhas não são detectadas**
- Verificar extensões: `.xlsx`, `.xls`, `.csv`
- Verificar encoding (UTF-8 recomendado)
- Verificar se não estão corrompidas

---

## 📈 **Monitoramento e Estatísticas**

O sistema fornece estatísticas detalhadas:

### **Estatísticas do Banco:**
- Total de documentos processados
- Tipos de documento (orcamento vs geral)
- Total de linhas processadas
- Arquivos por tipo de extensão

### **Estatísticas por Planilha:**
- Número de linhas e colunas
- Tipos de dados (numérico, texto, data)
- Valores únicos por coluna
- Score de detecção de orçamento

---

## 🔄 **Atualizações e Manutenção**

### **Adicionar Novas Planilhas:**
1. Coloque as novas planilhas na pasta `D:\docs_baixados`
2. Execute: `python rag_planilhas_local.py`
3. O sistema detectará e processará automaticamente

### **Reprocessar Todas as Planilhas:**
```bash
# Remover banco existente
rm -rf ./chroma_db

# Reprocessar
python rag_planilhas_local.py
```

### **Backup do Banco:**
```bash
# Fazer backup
cp -r ./chroma_db ./chroma_db_backup

# Restaurar backup
cp -r ./chroma_db_backup ./chroma_db
```

---

## 🎯 **Vantagens da Solução Local**

### ✅ **Privacidade Total:**
- Dados ficam no seu computador
- Sem envio para serviços externos
- Controle total sobre os dados

### ✅ **Sem Custos:**
- Não há cobrança por token
- Não há limites de uso
- Funciona offline

### ✅ **Performance:**
- Respostas rápidas
- Sem latência de rede
- Processamento local

### ✅ **Customização:**
- Controle total sobre modelos
- Ajustes específicos para seu caso
- Integração com outros sistemas

---

## 📞 **Suporte e Dúvidas**

### **Logs e Debug:**
O sistema gera logs detalhados. Para mais informações:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Verificar Status:**
```bash
# Verificar dependências
pip list | grep -E "(chromadb|pandas|ollama)"

# Verificar Ollama
ollama list

# Verificar pasta de documentos
ls -la "D:\docs_baixados"
```

---

## 🎉 **Conclusão**

Agora você tem um sistema RAG completo para planilhas de orçamento que:

1. ✅ **Funciona 100% localmente**
2. ✅ **Não usa Astra DB ou serviços externos**
3. ✅ **Detecta automaticamente planilhas de orçamento**
4. ✅ **Permite consultas inteligentes**
5. ✅ **Integra com Langflow**
6. ✅ **É totalmente customizável**

**Pronto para usar! 🚀** 