from crewai.tools import BaseTool
import requests
from pydantic import BaseModel, Field, ValidationError
import logging

# Configura o log no console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WikipediaToolSchema(BaseModel):
    query: str = Field(description="O termo de pesquisa na Wikipedia")


class WikipediaTool(BaseTool):
    name: str = "wikipedia_tool"
    description: str = "Consulta informações na Wikipedia em português com base em um tema."
    
    # Cache para armazenar os tópicos já consultados
    cache : dict = {}

    def _run(self, query: str) -> str:
        try:
            # Verifica se o tópico já foi consultado e retorna a resposta cacheada
            if query in self.cache:
                logger.info(f"Tópico '{query}' já consultado anteriormente. Usando cache.")
                return self.cache[query]

            # Valida o tipo da entrada para garantir que seja uma string
            if not isinstance(query, str):
                raise ValueError(f"Argumento inválido para 'query': esperado str, recebido {type(query)} - valor: {query}")

            url = (
                f"https://pt.wikipedia.org/w/api.php?"
                f"action=query&prop=extracts&exlimit=1&exchars=1000&explaintext=1&titles={query}"
                "&format=json&utf8=1&redirects=1"
            )

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            page = next(iter(data["query"]["pages"].values()))
            texto = page.get("extract", None)

            if not texto:
                logger.warning(f"Nenhum conteúdo encontrado para o tópico: {query}")
                return "Não foi possível encontrar informações para esse tópico."
                
            # Armazena a resposta no cache para futuras consultas
            self.cache[query] = texto

            return texto

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição HTTP para o tópico '{query}': {e}")
            return "Erro ao acessar a Wikipedia. Verifique sua conexão ou tente novamente mais tarde."

        except ValueError as ve:
            logger.error(f"Erro de validação de argumento: {ve}")
            return f"Erro: argumento inválido passado para a ferramenta. {ve}"

        except Exception as ex:
            logger.exception(f"Erro inesperado ao consultar o tópico '{query}': {ex}")
            return "Ocorreu um erro inesperado ao processar sua solicitação."
        