from langchain_openai import OpenAIEmbeddings

from langflow.base.embeddings.model import LCEmbeddingsModel
from langflow.base.models.openai_constants import OPENAI_EMBEDDING_MODEL_NAMES
from langflow.field_typing import Embeddings
from langflow.io import BoolInput, DictInput, DropdownInput, FloatInput, IntInput, MessageTextInput, SecretStrInput
import time


class OptimizedOpenAIEmbeddingsComponent(LCEmbeddingsModel):
    display_name = "Obra Price Embeddings"
    description = "Generate embeddings optimized for construction price data (CPOS, SICRO, SINAPI)."
    icon = "OpenAI"
    name = "ObraPriceEmbeddings"

    inputs = [
        # Configurações principais (visíveis)
        SecretStrInput(
            name="openai_api_key", 
            display_name="OpenAI API Key", 
            value="OPENAI_API_KEY", 
            required=True,
            info="Sua chave da API OpenAI para gerar embeddings."
        ),
        DropdownInput(
            name="model",
            display_name="Embedding Model",
            advanced=False,  # ✅ Deixar visível para o usuário
            options=OPENAI_EMBEDDING_MODEL_NAMES,
            value="text-embedding-3-small",  # ✅ Modelo otimizado para custo/performance
            info="Modelo de embedding recomendado: text-embedding-3-small para melhor custo-benefício."
        ),
        IntInput(
            name="chunk_size", 
            display_name="Chunk Size", 
            advanced=False,  # ✅ Deixar visível para o usuário
            value=1000,
            info="Tamanho do chunk para processamento. Otimizado para dados de preços."
        ),
        
        # Configurações de performance
        IntInput(
            name="max_retries", 
            display_name="Max Retries", 
            value=5,  # ✅ Aumentado para dados críticos
            advanced=True,
            info="Número máximo de tentativas em caso de erro. Aumentado para dados de preços."
        ),
        FloatInput(
            name="request_timeout", 
            display_name="Request Timeout", 
            advanced=True,
            value=60.0,  # ✅ Timeout maior para arquivos grandes
            info="Timeout da requisição em segundos. Aumentado para processar arquivos grandes."
        ),
        BoolInput(
            name="show_progress_bar", 
            display_name="Show Progress Bar", 
            advanced=True,
            value=True,  # ✅ Ativar para acompanhar progresso
            info="Mostra barra de progresso durante o processamento."
        ),
        
        # Configurações de qualidade
        BoolInput(
            name="skip_empty", 
            display_name="Skip Empty Chunks", 
            advanced=True,
            value=True,  # ✅ Pular chunks vazios
            info="Pula chunks vazios para otimizar processamento."
        ),
        IntInput(
            name="embedding_ctx_length", 
            display_name="Embedding Context Length", 
            advanced=True, 
            value=8192,  # ✅ Aumentado para descrições longas
            info="Comprimento máximo do contexto. Aumentado para descrições detalhadas de serviços."
        ),
        
        # Configurações avançadas
        IntInput(
            name="dimensions",
            display_name="Dimensions",
            info="Número de dimensões dos embeddings. 1536 para text-embedding-3-small.",
            advanced=True,
            value=1536,  # ✅ Dimensões padrão do modelo
        ),
        BoolInput(
            name="tiktoken_enable",
            display_name="Enable TikToken",
            advanced=True,
            value=True,
            info="Usar TikToken para tokenização. Mantém compatibilidade."
        ),
        MessageTextInput(
            name="tiktoken_model_name",
            display_name="TikToken Model Name",
            advanced=True,
            info="Nome do modelo TikToken para tokenização."
        ),
        
        # Configurações de API (avançadas)
        DictInput(
            name="default_headers",
            display_name="Default Headers",
            advanced=True,
            info="Headers padrão para requisições da API.",
        ),
        DictInput(
            name="default_query",
            display_name="Default Query",
            advanced=True,
            info="Parâmetros de query padrão para requisições da API.",
        ),
        DictInput(
            name="model_kwargs", 
            display_name="Model Kwargs", 
            advanced=True,
            info="Argumentos adicionais para o modelo."
        ),
        MessageTextInput(
            name="client", 
            display_name="Client", 
            advanced=True,
            info="Cliente OpenAI customizado."
        ),
        MessageTextInput(
            name="deployment", 
            display_name="Deployment", 
            advanced=True,
            info="Deployment específico da OpenAI."
        ),
        MessageTextInput(
            name="openai_api_base", 
            display_name="OpenAI API Base", 
            advanced=True,
            info="URL base da API OpenAI."
        ),
        MessageTextInput(
            name="openai_api_type", 
            display_name="OpenAI API Type", 
            advanced=True,
            info="Tipo da API OpenAI."
        ),
        MessageTextInput(
            name="openai_api_version", 
            display_name="OpenAI API Version", 
            advanced=True,
            info="Versão da API OpenAI."
        ),
        MessageTextInput(
            name="openai_organization",
            display_name="OpenAI Organization",
            advanced=True,
            info="Organização OpenAI."
        ),
        MessageTextInput(
            name="openai_proxy", 
            display_name="OpenAI Proxy", 
            advanced=True,
            info="Proxy para requisições OpenAI."
        ),
    ]

    def build_embeddings(self) -> Embeddings:
        """Constrói o modelo de embeddings com configurações otimizadas."""
        
        # Log das configurações
        self.log(f"🔧 Configurando embeddings para dados de preços...")
        self.log(f"📊 Modelo: {self.model}")
        self.log(f"📏 Chunk Size: {self.chunk_size}")
        self.log(f"🔄 Max Retries: {self.max_retries}")
        self.log(f"⏱️ Timeout: {self.request_timeout}")
        
        # Validações específicas para dados de preços
        if self.chunk_size > 2000:
            self.log("⚠️ Chunk size muito grande pode afetar qualidade dos embeddings")
        
        if self.max_retries < 3:
            self.log("⚠️ Max retries baixo pode causar falhas em arquivos grandes")
        
        # Configurações otimizadas para dados de preços
        embeddings_config = {
            "client": self.client or None,
            "model": self.model,
            "dimensions": self.dimensions or None,
            "deployment": self.deployment or None,
            "api_version": self.openai_api_version or None,
            "base_url": self.openai_api_base or None,
            "openai_api_type": self.openai_api_type or None,
            "openai_proxy": self.openai_proxy or None,
            "embedding_ctx_length": self.embedding_ctx_length,
            "api_key": self.openai_api_key or None,
            "organization": self.openai_organization or None,
            "allowed_special": "all",
            "disallowed_special": "all",
            "chunk_size": self.chunk_size,
            "max_retries": self.max_retries,
            "timeout": self.request_timeout or None,
            "tiktoken_enabled": self.tiktoken_enable,
            "tiktoken_model_name": self.tiktoken_model_name or None,
            "show_progress_bar": self.show_progress_bar,
            "model_kwargs": self.model_kwargs,
            "skip_empty": self.skip_empty,
            "default_headers": self.default_headers or None,
            "default_query": self.default_query or None,
        }
        
        try:
            embeddings = OpenAIEmbeddings(**embeddings_config)
            self.log(f"✅ Embeddings configurados com sucesso!")
            self.log(f"🎯 Otimizado para: Dados de preços de obra (CPOS, SICRO, SINAPI)")
            return embeddings
            
        except Exception as e:
            self.log(f"❌ Erro ao configurar embeddings: {str(e)}")
            raise

    def get_embedding_stats(self, texts: list[str]) -> dict:
        """Retorna estatísticas dos embeddings para monitoramento."""
        if not texts:
            return {"total_texts": 0, "avg_length": 0, "estimated_cost": 0}
        
        total_texts = len(texts)
        avg_length = sum(len(text) for text in texts) / total_texts
        
        # Estimativa de custo (aproximada)
        estimated_tokens = sum(len(text.split()) * 1.3 for text in texts)  # 1.3 tokens por palavra
        estimated_cost = (estimated_tokens / 1000) * 0.00002  # Custo aproximado do text-embedding-3-small
        
        return {
            "total_texts": total_texts,
            "avg_length": round(avg_length, 2),
            "estimated_tokens": round(estimated_tokens),
            "estimated_cost_usd": round(estimated_cost, 4)
        } 