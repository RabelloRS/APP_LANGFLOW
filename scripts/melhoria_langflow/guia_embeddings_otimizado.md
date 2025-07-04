# 🧠 Guia Completo - Obra Price Embeddings

## 🎯 **O que são Embeddings e para que servem?**

### **Embeddings = Representação Numérica do Texto**

Os embeddings convertem texto em vetores numéricos que capturam o **significado semântico**. Para seu caso:

```
"LIMPEZA MECANIZADA GERAL" → [0.123, -0.456, 0.789, ...] (1536 números)
"CARGA MANUAL DE ENTULHO"  → [0.234, -0.567, 0.890, ...] (1536 números)
```

### **Por que são importantes para seu agente?**

1. **Busca Semântica**: Encontra serviços similares mesmo com palavras diferentes
2. **Comparação Inteligente**: Compara significados, não apenas palavras exatas
3. **RAG Eficiente**: Permite consultas precisas no banco de dados vetorial

## 🚀 **Otimizações Implementadas**

### **1. Configurações Principais (Visíveis)**

| Parâmetro | Valor Otimizado | Justificativa |
|-----------|-----------------|---------------|
| **Model** | `text-embedding-3-small` | ✅ Melhor custo-benefício ($0.00002/1K tokens) |
| **Chunk Size** | `1000` | ✅ Otimizado para descrições de serviços |
| **Max Retries** | `5` | ✅ Aumentado para dados críticos |

### **2. Configurações de Performance**

| Parâmetro | Valor Otimizado | Justificativa |
|-----------|-----------------|---------------|
| **Request Timeout** | `60.0s` | ✅ Timeout maior para arquivos grandes |
| **Show Progress Bar** | `True` | ✅ Acompanhar progresso |
| **Skip Empty** | `True` | ✅ Pular chunks vazios |

### **3. Configurações de Qualidade**

| Parâmetro | Valor Otimizado | Justificativa |
|-----------|-----------------|---------------|
| **Embedding Context Length** | `8192` | ✅ Aumentado para descrições longas |
| **Dimensions** | `1536` | ✅ Dimensões padrão do modelo |

## 📊 **Fluxo Completo do Sistema**

### **1. Carregamento de Arquivos**
```
CPOS.xlsx → cpos_Comp EDIF Sem Des Julho24.txt
SICRO.xlsx → sicro_Sheet1.txt  
SINAPI.xlsx → sinapi_Planilha1.txt
```

### **2. Splitting Inteligente**
```
Arquivo → Chunks de 1500 caracteres
Cada chunk mantém: Código + Descrição + Preço + Fonte
```

### **3. Geração de Embeddings**
```
Chunk → Vetor de 1536 dimensões
Exemplo: "1001001 LIMPEZA MECANIZADA..." → [0.123, -0.456, ...]
```

### **4. Armazenamento no Vector DB**
```
Vetor + Metadados → AstraDB
Metadados: código, descrição, preço, fonte, chunk_id
```

### **5. Consulta do Agente**
```
"Preciso de limpeza de terreno" → Embedding → Busca similar → Resultados
```

## 💰 **Análise de Custos**

### **Estimativa para seus arquivos:**

| Arquivo | Linhas | Chunks Estimados | Tokens Estimados | Custo Estimado |
|---------|--------|------------------|------------------|----------------|
| **CPOS** | 2.557 | ~500 | ~50.000 | $0.001 |
| **SICRO** | 6.489 | ~1.000 | ~100.000 | $0.002 |
| **SINAPI** | 9.723 | ~1.500 | ~150.000 | $0.003 |
| **TOTAL** | 18.769 | ~3.000 | ~300.000 | **$0.006** |

### **Custo por consulta:**
- **Consulta única**: ~$0.0001
- **100 consultas/mês**: ~$0.01
- **1.000 consultas/mês**: ~$0.10

## 🎯 **Configurações Recomendadas por Caso de Uso**

### **Para Desenvolvimento/Teste:**
```python
model = "text-embedding-3-small"
chunk_size = 1000
max_retries = 3
show_progress_bar = True
```

### **Para Produção:**
```python
model = "text-embedding-3-small"
chunk_size = 1500
max_retries = 5
request_timeout = 60.0
skip_empty = True
```

### **Para Alta Performance:**
```python
model = "text-embedding-3-large"  # Mais preciso, mais caro
chunk_size = 2000
embedding_ctx_length = 8192
max_retries = 7
```

## 🔧 **Troubleshooting**

### **Problema: Erro de API Key**
- ✅ Verificar se a chave está correta
- ✅ Verificar se tem créditos na conta
- ✅ Verificar se a chave tem permissões de embedding

### **Problema: Timeout**
- ✅ Aumentar Request Timeout para 120.0
- ✅ Reduzir Chunk Size para 800
- ✅ Verificar conexão com internet

### **Problema: Qualidade baixa dos resultados**
- ✅ Usar text-embedding-3-large
- ✅ Aumentar Chunk Size para 2000
- ✅ Verificar se o splitting está correto

### **Problema: Custos altos**
- ✅ Usar text-embedding-3-small
- ✅ Reduzir Chunk Size para 800
- ✅ Ativar Skip Empty

## 📈 **Monitoramento e Métricas**

### **Logs Importantes:**
```
🔧 Configurando embeddings para dados de preços...
📊 Modelo: text-embedding-3-small
📏 Chunk Size: 1000
🔄 Max Retries: 5
⏱️ Timeout: 60.0
✅ Embeddings configurados com sucesso!
🎯 Otimizado para: Dados de preços de obra (CPOS, SICRO, SINAPI)
```

### **Métricas para Acompanhar:**
- ⏱️ Tempo de geração de embeddings
- 💰 Custo por arquivo processado
- 📊 Qualidade dos resultados de busca
- 🔄 Taxa de sucesso das requisições

## 🎯 **Integração com seu Agente**

### **Prompt Sugerido para o Agente:**
```
"Você é um especialista em análise de preços de obra. 

Use os embeddings dos arquivos de preços (CPOS, SICRO, SINAPI) para encontrar 
os serviços que mais se aproximam da descrição fornecida.

Para cada serviço encontrado, forneça:
- Código do serviço
- Descrição completa
- Preço unitário
- Fonte (CPOS/SICRO/SINAPI)
- Grau de similaridade (0-100%)
- Justificativa da similaridade

Priorize serviços com maior similaridade semântica."
```

### **Resultado Esperado:**
```
Serviço encontrado:
- Código: 1001001
- Descrição: LIMPEZA MECANIZADA GERAL, INCLUSIVE REMOÇÃO DA COBERTURA VEGETAL
- Preço: R$ 1,74
- Fonte: CPOS
- Similaridade: 95%
- Justificativa: Descrição muito similar, mesmo tipo de serviço
``` 