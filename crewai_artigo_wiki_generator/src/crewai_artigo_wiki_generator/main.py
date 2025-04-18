
import sys
from urllib import request
import warnings
from datetime import datetime
# from crewai_artigo_wiki_generator.crew import CrewaiArtigoWikiGenerator
from crew import CrewaiArtigoWikiGenerator
from models.article_model import Artigo, Paragrafo
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from flask import Flask, request, jsonify
import logging
from litellm import RateLimitError 

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ignorar avisos de syntax warning relacionados ao pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Definir o modelo de dados para a requisição
class ArticleRequest(BaseModel):
    topic: str

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  # <- certifique-se que o pacote 'litellm' está instalado e importado

def execute_crew_process(topic: str):
    logger.info(f"Iniciando a geração do artigo sobre o tópico: {topic}")
    
    try:
        inputs = {"topic": topic}
        response = CrewaiArtigoWikiGenerator().crew().kickoff(inputs=inputs)

        if "titulo" not in response:
            logger.error(f"Chave 'titulo' não encontrada na resposta do CrewAI para o tópico: {topic}")
            return {"error": "Falha ao gerar o artigo. Chave 'titulo' não encontrada."}

        artigo = {
            "titulo": response["titulo"],
            "topico": response.get("topico", "Informações não encontradas"),
            "data_criacao": response.get("data_criacao", "Data não disponível"),
            "autor": response.get("autor", "Autor desconhecido"),
            "paragrafos": response.get("paragrafos", []),
            "referencias": response.get("referencias", []),
        }

        return artigo

    except RateLimitError as e:
        logger.warning(f"Limite de uso atingido: {e}")
        return {"error": "Limite de uso da API atingido. Tente novamente em alguns minutos."}

    except Exception as e:
        logger.error(f"Erro ao gerar o artigo: {e}")
        return {"error": f"Erro ao gerar o artigo: {e}"}









@app.route("/generate_article", methods=["POST", "GET"])

def generate_article():
    if request.method == "GET":
        # Tópico passado como parâmetro de consulta na URL
        topic = request.args.get('topic', '').strip()

        if not topic:
            return jsonify({"error": "O tópico não pode estar vazio."}), 400

        artigo = execute_crew_process(topic)

        if "error" in artigo:
            return jsonify(artigo), 500

        return jsonify(artigo), 200

    if request.method == "POST":
        # Caso seja um POST, recebe o JSON como entrada
        data = request.get_json()
        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"error": "O tópico não pode estar vazio."}), 400

        artigo = execute_crew_process(topic)

        if "error" in artigo:
            return jsonify(artigo), 500

        return jsonify(artigo), 200



@app.post("/train_crew/")
async def train_crew(iterations: int, filename: str):
    """
    Endpoint para treinar o CrewAI com o número de iterações e nome do arquivo fornecido.
    """
    inputs = {
        "topic": "AI LLMs"
    }

    try:
        logger.info(f"Iniciando treinamento do CrewAI com {iterations} iterações usando o arquivo {filename}...")
        CrewaiArtigoWikiGenerator().crew().train(n_iterations=iterations, filename=filename, inputs=inputs)

        logger.info(f"CrewAI treinado com {iterations} iterações.")
        return {"message": f"CrewAI treinado com {iterations} iterações."}
    except Exception as e:
        logger.error(f"Erro ao treinar o CrewAI: {e}")
        raise HTTPException(status_code=500, detail="Erro ao treinar o CrewAI.")

@app.post("/replay_task/")
async def replay_task(task_id: str):
    """
    Endpoint para reproduzir a execução do CrewAI a partir de um task_id específico.
    """
    try:
        logger.info(f"Iniciando o replay do task {task_id}...")
        CrewaiArtigoWikiGenerator().crew().replay(task_id=task_id)

        logger.info(f"Replay do task {task_id} iniciado com sucesso.")
        return {"message": f"Replay do task {task_id} iniciado com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao reproduzir o task: {e}")
        raise HTTPException(status_code=500, detail="Erro ao reproduzir a execução do CrewAI.")

@app.post("/test_crew/")
async def test_crew(iterations: int, openai_model_name: str):
    """
    Endpoint para testar a execução do CrewAI com um número específico de iterações e modelo OpenAI.
    """
    inputs = {
        "topic": "Games",
        "current_year": str(datetime.now().year)
    }

    try:
        logger.info(f"Iniciando teste do CrewAI com {iterations} iterações e modelo OpenAI {openai_model_name}...")
        CrewaiArtigoWikiGenerator().crew().test(n_iterations=iterations, openai_model_name=openai_model_name, inputs=inputs)

        logger.info(f"Teste do CrewAI com {iterations} iterações e modelo {openai_model_name} concluído com sucesso.")
        return {"message": f"Teste do CrewAI com {iterations} iterações e modelo {openai_model_name} concluído com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao testar o CrewAI: {e}")
        raise HTTPException(status_code=500, detail="Erro ao testar o CrewAI.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

    app.run(debug=True)