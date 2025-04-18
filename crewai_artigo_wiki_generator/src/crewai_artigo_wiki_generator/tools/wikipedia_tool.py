from crewai.tools import BaseTool
import requests
from urllib.parse import quote_plus

class WikipediaTool(BaseTool):
    name: str = "wikipedia_tool"
    description: str = "Consulta informações na Wikipedia em português com base em um tema."

    def _run(self, query: str) -> str:

        
        # URL da API da Wikipedia para pegar o resumo do tema
        url = (
            f"https://pt.wikipedia.org/w/api.php?"
            f"action=query&prop=extracts&exlimit=1&exchars=1000&explaintext=1&titles={query[0]}"
            "&format=json&utf8=1&redirects=1"
        )

        try:
            # Fazendo a requisição com timeout para evitar espera indefinida
            response = requests.get(url, timeout=10)  # Timeout de 10 segundos
            response.raise_for_status()  # Verifica se o status da resposta é 200 (OK)

            # Processa a resposta JSON da Wikipedia
            data = response.json()

            # Verifica se há páginas retornadas
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return f"Nenhuma página encontrada para o tema '{query}'."

            # Pega a primeira página retornada
            page = next(iter(pages.values()))
            extract = page.get('extract')

            # Verifica se a resposta contém o resumo
            if not extract:
                return f"Nenhuma descrição encontrada para o tema '{query}'."
            
            return extract

        except requests.exceptions.Timeout:
            return "Erro: A requisição à Wikipedia excedeu o tempo limite (timeout). Tente novamente mais tarde."
        except requests.exceptions.RequestException as e:
            return f"Erro ao acessar a Wikipedia: {e}"
        except ValueError as e:
            return f"Erro ao processar a resposta JSON: {e}"
        except Exception as e:
            return f"Ocorreu um erro inesperado: {e}"
