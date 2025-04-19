from crewai.tools import BaseTool
# from crewai.tools import BaseTool
import requests
from pydantic import BaseModel, Field, ValidationError
import logging

"""
Módulo que define uma ferramenta personalizada para consulta à Wikipedia em português,
utilizando a API pública da enciclopédia. A ferramenta implementa um sistema de cache
para evitar requisições repetidas, além de tratar erros de rede e entradas inválidas.

Usada dentro de ambientes como CrewAI para auxiliar em tarefas de pesquisa.
"""



# Configura o log no console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikipediaToolSchema(BaseModel):
    """
    Schema Pydantic usado para validar a entrada da ferramenta WikipediaTool.
    Espera um campo `query` representando o termo a ser pesquisado na Wikipedia.
    """
    query: str = Field(description="O termo de pesquisa na Wikipedia")


class WikipediaTool(BaseTool):
    
    """
    Ferramenta personalizada para realizar buscas na Wikipedia em português.
    Utiliza a API pública da Wikipedia para recuperar um resumo textual com até 1000 caracteres.
    Implementa um sistema de cache interno para otimizar consultas repetidas.
    """
    name: str = "wikipedia_tool"
    description: str = "Consulta informações na Wikipedia em português com base em um tema."
    
    # Cache para armazenar os tópicos já consultados
    cache : dict = {}

    def _run(self, query: str) -> str:
        
        """
        Executa a consulta ao termo especificado na Wikipedia. Se o resultado já estiver em cache,
        ele é reutilizado. Caso contrário, uma nova requisição à API da Wikipedia é feita.

        Parâmetros:
            query (str): Termo a ser buscado.

        Retorna:
            str: Texto extraído da Wikipedia ou mensagem de erro apropriada.
        """

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
        