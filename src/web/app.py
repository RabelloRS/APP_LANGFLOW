"""
Interface Web para o Sistema RAG de Planilhas de Preços.
Painel de controle para processamento, busca e monitoramento do RAG.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO # Adicionado
import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path para encontrar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuração de logging padronizada
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.core.rag_planilhas_local import RAGPlanilhasLocal

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rag_planilhas_secret_key_2024'
socketio = SocketIO(app) # Adicionado

# --- Páginas da Interface ---

@app.route('/')
def index():
    """Página principal do painel de controle."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Página para busca no RAG."""
    return render_template('search.html')

@app.route('/database')
def database():
    """Página para visualizar o status do banco de dados vetorial."""
    return render_template('database.html')

@app.route('/process_spreadsheets')
def process_spreadsheets_page():
    """Página para processar planilhas."""
    return render_template('processar_planilhas.html')

# --- API Endpoints ---

@app.route('/api/process_spreadsheets', methods=['POST'])
def api_process_spreadsheets():
    """
    API para encontrar, processar e adicionar todas as planilhas ao ChromaDB.
    """
    logger.info("Recebida requisição para processar planilhas.")
    def progress_callback(message):
        socketio.emit('progress_update', {'data': message})
        logger.info(f"Progress: {message}")

    try:
        rag = RAGPlanilhasLocal(on_progress_update=progress_callback)
        
        progress_callback("Iniciando processamento de planilhas...")
        logger.info("Limpando coleção existente no ChromaDB...")
        rag.client.delete_collection(name=rag.collection.name)
        rag.collection = rag.client.get_or_create_collection(name="orcamentos_planilhas_chunks")
        progress_callback("Coleção ChromaDB limpa e pronta.")
        
        logger.info("Iniciando processamento das planilhas...")
        chunks = rag.processar_todas_planilhas()
        
        progress_callback(f"Encontrados {len(chunks)} chunks. Adicionando ao ChromaDB...")
        logger.info(f"Encontrados {len(chunks)} chunks. Adicionando ao ChromaDB...")
        rag.adicionar_ao_chromadb(chunks)
        
        progress_callback("Processamento concluído. Obtendo estatísticas finais...")
        logger.info("Processamento concluído. Obtendo estatísticas finais...")
        stats = rag.estatisticas_banco()
        
        return jsonify({
            "success": True,
            "message": f"{stats.get('total_documentos', 0)} chunks foram processados e adicionados ao banco de dados.",
            "statistics": stats
        })
    except Exception as e:
        logger.error(f"Erro no processamento das planilhas: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rag_search', methods=['GET'])
def api_rag_search():
    """API para realizar buscas no sistema RAG."""
    query = request.args.get('query', '')
    if not query:
        return jsonify({"success": False, "error": "O termo de busca não pode ser vazio."}), 400
    
    logger.info(f"Recebida busca RAG para: '{query}'")
    try:
        rag = RAGPlanilhasLocal()
        resultados = rag.buscar_orcamentos(query, n_results=10)
        return jsonify({"success": True, "results": resultados})
    except Exception as e:
        logger.error(f"Erro na busca RAG: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/db_stats', methods=['GET'])
def api_db_stats():
    """API para obter estatísticas do ChromaDB."""
    logger.info("Recebida requisição de estatísticas do DB.")
    try:
        rag = RAGPlanilhasLocal()
        stats = rag.estatisticas_banco()
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do DB: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Iniciando interface web...")
    socketio.run(app, host='0.0.0.0', port=5003)
