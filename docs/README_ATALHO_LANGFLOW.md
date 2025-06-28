# Atalho para Langflow - Windows (Ambiente Virtual)

Este diretório contém scripts para criar um atalho na área de trabalho do Windows que inicia automaticamente o Langflow **usando o ambiente virtual local**.

## 📋 Pré-requisitos

### **Ambiente Virtual:**
- ✅ Ambiente virtual `.venv` já criado no diretório
- ✅ Langflow instalado no ambiente virtual
- ✅ Python 3.8+ instalado no sistema

## Scripts Disponíveis

### 1. `start_langflow.bat` (Script Batch)
- **Uso**: Duplo clique no arquivo
- **Vantagens**: Funciona em qualquer versão do Windows
- **Desvantagens**: Interface mais simples

### 2. `start_langflow.ps1` (Script PowerShell)
- **Uso**: Clique direito → "Executar com PowerShell"
- **Vantagens**: Interface colorida, melhor tratamento de erros
- **Desvantagens**: Pode precisar de permissões de execução

## Como Criar o Atalho na Área de Trabalho

### Opção 1: Script Batch (Recomendado)
1. Clique com o botão direito na área de trabalho
2. Selecione "Novo" → "Atalho"
3. Em "Local do item", digite o caminho completo para o script:
   ```
   "C:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\start_langflow.bat"
   ```
4. Clique em "Próximo"
5. Digite um nome para o atalho (ex: "Langflow")
6. Clique em "Concluir"

### Opção 2: Script PowerShell
1. Clique com o botão direito na área de trabalho
2. Selecione "Novo" → "Atalho"
3. Em "Local do item", digite:
   ```
   powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Rodrigo\OneDrive\Documentos\APP\APP_LANGFLOW\start_langflow.ps1"
   ```
4. Clique em "Próximo"
5. Digite um nome para o atalho (ex: "Langflow")
6. Clique em "Concluir"

## Personalizar o Ícone do Atalho

1. Clique com o botão direito no atalho criado
2. Selecione "Propriedades"
3. Clique em "Alterar ícone"
4. Você pode usar ícones do sistema ou baixar um ícone personalizado

## O que o Script Faz

1. **Verifica se o ambiente virtual `.venv` existe**
2. **Ativa o ambiente virtual automaticamente**
3. **Verifica se o Langflow está instalado** (instala automaticamente se necessário)
4. **Inicia o servidor Langflow** na porta 3000
5. **Abre automaticamente o navegador** em `http://localhost:3000`
6. **Mantém o servidor rodando** até você fechar a janela

## Vantagens do Ambiente Virtual

### ✅ **Isolamento:**
- Dependências isoladas do sistema
- Sem conflitos com outros projetos
- Versões específicas garantidas

### ✅ **Portabilidade:**
- Funciona em qualquer máquina com Python
- Fácil de compartilhar com outros desenvolvedores
- Backup simples (apenas copiar a pasta)

### ✅ **Segurança:**
- Não afeta o Python global
- Fácil de remover se necessário
- Controle total sobre as dependências

## Solução de Problemas

### Erro: "Ambiente virtual .venv não encontrado"
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Erro: "Python não encontrado no ambiente virtual"
- Verifique se o Python está instalado no sistema
- Reinstale o ambiente virtual se necessário

### Erro: "Falha ao instalar Langflow"
- Verifique sua conexão com a internet
- Execute como administrador se necessário
- Tente: `pip install --upgrade pip`

### Erro: "Porta 3000 já em uso"
- Feche outros aplicativos que possam estar usando a porta 3000
- Ou modifique o script para usar outra porta

### Script PowerShell não executa
- Abra o PowerShell como administrador
- Execute: `Set-ExecutionPolicy RemoteSigned`
- Ou use o script batch como alternativa

## Comandos Manuais

Se preferir usar comandos manuais:

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Verificar se Langflow está instalado
pip list | findstr langflow

# Instalar Langflow (se necessário)
pip install langflow

# Iniciar Langflow
langflow run --host 0.0.0.0 --port 3000
```

## Gerenciamento do Ambiente Virtual

### **Ativar Ambiente Virtual:**
```bash
# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### **Desativar Ambiente Virtual:**
```bash
deactivate
```

### **Instalar Dependências:**
```bash
# Com ambiente virtual ativado
pip install -r requirements.txt
```

### **Verificar Dependências:**
```bash
pip list
```

### **Remover Ambiente Virtual:**
```bash
# Desativar primeiro
deactivate

# Remover pasta
rmdir /s .venv
```

## Notas Importantes

- ✅ O servidor Langflow continuará rodando até você fechar a janela do script
- ✅ Para parar o servidor, feche a janela do script ou pressione Ctrl+C
- ✅ O Langflow salva automaticamente seus fluxos no diretório local
- ✅ Certifique-se de ter pelo menos 2GB de RAM livre para o Langflow funcionar adequadamente
- ✅ O ambiente virtual mantém todas as dependências isoladas
- ✅ Sempre use o ambiente virtual para manter a consistência do projeto

## Estrutura do Projeto

```
APP_LANGFLOW/
├── .venv/                    # Ambiente virtual
├── start_langflow.bat        # Script batch
├── start_langflow.ps1        # Script PowerShell
├── requirements.txt          # Dependências
├── README_ATALHO_LANGFLOW.md # Este arquivo
└── [outros arquivos do projeto]
```

---

**🎉 Agora você pode iniciar o Langflow com um clique, usando o ambiente virtual isolado!** 