from crewai.tools import BaseTool
import requests

class WikipediaTool(BaseTool):
    name: str = "wikipedia_tool"
    description: str = "Consulta informações na Wikipedia em português com base em um tema."

    def _run(self, query: str) -> str:
        url = (
            "https://pt.wikipedia.org/w/api.php?"
            f"action=query&prop=extracts&exlimit=1&explaintext=1&titles={query}"
            "&format=json&utf8=1&redirects=1"
        )
        response = requests.get(url)
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        return page.get('extract', 'Nenhuma informação encontrada.')