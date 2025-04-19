import os
import sys
from urllib import request
import warnings
from datetime import datetime
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
    """
    Modelo para a requisição de geração de artigo.

    Atributos:
        topic (str): Tópico do artigo a ser gerado.
    """
    topic: str

# Inicializando o aplicativo Flask
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_crew_process(topic: str):
    """
    Função para executar o processo do CrewAI e gerar o artigo com base no tópico fornecido.

    Args:
        topic (str): Tópico do artigo a ser gerado.

    Returns:
        dict: Retorna um dicionário com os dados do artigo gerado ou um erro.
    """
    logger.info(f"Iniciando a geração do artigo sobre o tópico: {topic}")
    
    try:
        inputs = {"topic": topic}
        response = CrewaiArtigoWikiGenerator().crew().kickoff(inputs=inputs)

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
    """
    Endpoint para gerar um artigo a partir de um tópico.

    Suporta os métodos HTTP GET e POST:
        - GET: Obtém o tópico a partir do parâmetro de consulta.
        - POST: Recebe o JSON com o tópico para gerar o artigo.

    Retorna:
        dict: Resultado da geração do artigo ou erro.
    """
    if request.method == "GET":
        topic = request.args.get("topic")

        # Verifica se o tópico foi fornecido
        if not topic:
            return jsonify({"error": "O tópico não pode estar vazio."}), 400

        artigo = execute_crew_process(topic)

        if "error" in artigo:
            return jsonify(artigo), 500

        return jsonify(artigo), 200



@app.post("/train_crew/")
async def train_crew(iterations: int, filename: str):
    """
    Endpoint para treinar o CrewAI com o número de iterações e o nome do arquivo fornecido.

    Args:
        iterations (int): Número de iterações para o treinamento.
        filename (str): Nome do arquivo com os dados de treinamento.

    Returns:
        dict: Mensagem de sucesso ou erro.
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

    Args:
        task_id (str): ID do task a ser reproduzido.

    Returns:
        dict: Mensagem de sucesso ou erro.
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

    Args:
        iterations (int): Número de iterações para o teste.
        openai_model_name (str): Nome do modelo OpenAI a ser utilizado.

    Returns:
        dict: Mensagem de sucesso ou erro.
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
    """
    Inicia o servidor Flask na porta 5000.
    """
    initial_topic = None
    if len(sys.argv) > 1:
        initial_topic = sys.argv[1]
        logger.info(f"Tópico inicial recebido via linha de comando: {initial_topic}")
        # You could potentially trigger the article generation here
        # or store this topic to be used when the /generate_article
        # endpoint is accessed.
        execute_crew_process(initial_topic)
        
        
    
    app.run(host="0.0.0.0", port=5000, debug=True)
    
