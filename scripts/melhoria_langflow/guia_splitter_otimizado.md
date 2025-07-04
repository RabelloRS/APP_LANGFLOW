# 🚀 Guia de Configuração - Obra Price Splitter

## 🎯 **Configurações Recomendadas para Arquivos de Preços**

### **1. Configurações Principais (Visíveis)**

| Parâmetro | Valor Recomendado | Justificativa |
|-----------|-------------------|---------------|
| **Chunk Size** | `1500` | ✅ Otimizado para descrições detalhadas de serviços |
| **Chunk Overlap** | `300` | ✅ Mantém contexto entre chunks de serviços |
| **Separator** | `\n` | ✅ Quebra por linha para manter estrutura |

### **2. Configurações Avançadas**

| Parâmetro | Valor Recomendado | Justificativa |
|-----------|-------------------|---------------|
| **Splitter Type** | `Recursive` | ✅ Melhor para conteúdo variado |
| **Preserve Headers** | `True` | ✅ Mantém cabeçalhos para contexto |
| **Smart Splitting** | `True` | ✅ Evita cortar no meio de serviços |
| **Keep Separator** | `True` | ✅ Mantém separadores para contexto |

## 📊 **Performance Esperada**

### **Com Configuração Padrão:**
- 📄 **Chunks gerados**: ~500-800 chunks por arquivo
- ⏱️ **Tempo de processamento**: ~2-5 segundos
- 💾 **Tamanho médio do chunk**: 1500 caracteres

### **Com Configuração Otimizada:**
- 📄 **Chunks gerados**: ~300-500 chunks (mais inteligentes)
- ⚡ **Tempo de processamento**: ~1-3 segundos
- 💾 **Tamanho médio do chunk**: 1500-2000 caracteres
- 🧠 **Qualidade**: Chunks respeitam limites de serviços

## 🛠️ **Melhorias Implementadas**

### **1. Smart Splitting**
```python
# Detecta padrões de códigos de serviço
if re.match(r'^\d{7}\s+', line):  # 1001001, 2001001, etc.
    # Inicia novo chunk respeitando serviço
```

### **2. Preservação de Headers**
- Mantém cabeçalhos em cada chunk
- Melhora contexto para consultas RAG
- Facilita identificação de colunas

### **3. Recursive Splitting**
- Separa por: `\n\n`, `\n`, `.`, ` `, `""`
- Otimizado para dados estruturados
- Melhor que splitting simples por caractere

### **4. Logs Informativos**
```
📊 Split 3 documents into 450 chunks
⚙️ Chunk size: 1500, Overlap: 300
🧠 Smart splitting: True, Preserve headers: True
```

## 🎯 **Configuração para seu Agente**

### **Fluxo Recomendado:**
1. **Carregar Arquivos** → Obra Price Files Loader
2. **Split Text** → Obra Price Splitter (este componente)
3. **Vector Store** → Embeddings dos chunks
4. **RAG Chain** → Consulta inteligente
5. **Agente** → Análise e recomendação

### **Exemplo de Chunk Gerado:**
```
CODIGO    DESCRICAO    UNIDADE    PRECO_UNITARIO    FONTE
1001001   LIMPEZA MECANIZADA GERAL, INCLUSIVE REMOÇÃO DA COBERTURA VEGETAL - TRONCOS COM DIÂMETRO ATÉ 10CM - SEM TRANSPORTE    M2    1,74    cpos
1001002   DESTOCAMENTO, INCLUSIVE REMOÇÃO DAS RAÍZES - DIÂMETROS DE 10,01 À 30CM    UN    56,90    cpos
```

## 🔧 **Troubleshooting**

### **Problema: Chunks muito pequenos**
- ✅ Aumentar Chunk Size para 2000-3000
- ✅ Reduzir Chunk Overlap para 200
- ✅ Desativar Smart Splitting temporariamente

### **Problema: Chunks muito grandes**
- ✅ Reduzir Chunk Size para 1000-1200
- ✅ Aumentar Chunk Overlap para 400-500
- ✅ Verificar se Smart Splitting está ativo

### **Problema: Serviços cortados no meio**
- ✅ Ativar Smart Splitting
- ✅ Aumentar Chunk Size
- ✅ Verificar padrão de códigos no arquivo

### **Problema: Performance lenta**
- ✅ Usar Splitter Type "Character" em vez de "Recursive"
- ✅ Reduzir Chunk Overlap
- ✅ Desativar Preserve Headers

## 📈 **Monitoramento**

### **Métricas para Acompanhar:**
- 📄 Número de chunks gerados
- ⏱️ Tempo de processamento
- 💾 Tamanho médio dos chunks
- 🧠 Efetividade do Smart Splitting

### **Logs Importantes:**
- Documentos processados vs chunks gerados
- Configurações aplicadas
- Erros de validação de estrutura
- Performance do splitting

## 🎯 **Casos de Uso Específicos**

### **Para Consultas Rápidas:**
- Chunk Size: 1000
- Chunk Overlap: 200
- Smart Splitting: False
- Splitter Type: Character

### **Para Consultas Detalhadas:**
- Chunk Size: 2000
- Chunk Overlap: 400
- Smart Splitting: True
- Splitter Type: Recursive

### **Para Análise Completa:**
- Chunk Size: 1500
- Chunk Overlap: 300
- Smart Splitting: True
- Preserve Headers: True
- Splitter Type: Recursive 