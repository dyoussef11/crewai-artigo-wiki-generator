from crewai.tools import BaseTool
import requests
from pydantic import BaseModel, Field, ValidationError
import logging
from urllib.parse import quote
import re
import time
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class WikipediaToolSchema(BaseModel):
    """
    Schema for Wikipedia search tool input validation
    """
    query: str = Field(...,
                     description="Termo de pesquisa na Wikipedia em português",
                     min_length=2,
                     max_length=100,
                     examples=["Inteligência Artificial", "História do Brasil"])

class WikipediaTool(BaseTool):
    """
    Ferramenta avançada de pesquisa na Wikipedia em português com:
    - Sistema de tentativas com backoff exponencial
    - Normalização inteligente de consultas
    - Cache otimizado
    - Tratamento robusto de erros
    - Variações automáticas de termos
    """
    name: str = "wikipedia_tool"
    description: str = (
        "Ferramenta especializada para pesquisa na Wikipedia em português. "
        "Fornece resumos concisos e confiáveis, com tratamento especial para "
        "termos técnicos e históricos."
    )
    
    # Configurações avançadas
    _cache: Dict[str, str] = {}
    _MAX_CACHE_SIZE = 200
    _MAX_RETRIES = 3
    _INITIAL_TIMEOUT = 5
    _USER_AGENT = "CrewAI-ResearchBot/2.0 (https://github.com/org/repo; contact@email.com)"
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza a consulta para melhor correspondência na Wikipedia"""
        # Remove caracteres especiais e normaliza espaços
        query = re.sub(r'[^\w\sáéíóúâêîôûãõç-]', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Padroniza variações comuns
        replacements = {
            "video game": "videogame",
            "video games": "videogames",
            "historia": "história",
            "evolucao": "evolução"
        }
        
        for term, replacement in replacements.items():
            query = re.sub(r'\b' + term + r'\b', replacement, query, flags=re.IGNORECASE)
        
        return query.title()  # Capitaliza cada palavra

    def _make_api_request(self, query: str) -> Optional[Dict]:
        """Faz requisição à API da Wikipedia com tratamento de erros"""
        encoded_query = quote(query)
        url = (
            "https://pt.wikipedia.org/w/api.php?"
            "action=query&"
            "prop=extracts&"
            "exlimit=1&"
            "exchars=1500&"  # Aumentado para mais conteúdo
            "explaintext=1&"
            "exintro=1&"
            f"titles={encoded_query}&"
            "format=json&"
            "utf8=1&"
            "redirects=1"
        )
        
        for attempt in range(self._MAX_RETRIES):
            try:
                timeout = self._INITIAL_TIMEOUT * (attempt + 1)
                response = requests.get(
                    url,
                    timeout=timeout,
                    headers={'User-Agent': self._USER_AGENT}
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou para '{query}': {str(e)}")
                if attempt < self._MAX_RETRIES - 1:
                    time.sleep(1 * (attempt + 1))  # Backoff exponencial
                continue
                
        return None

    def _try_variations(self, original_query: str) -> str:
        """Tenta variações alternativas para a consulta"""
        variations = [
            original_query,
            f"História {original_query}",
            f"Evolução {original_query}",
            original_query.replace("Video Game", "Videogame"),
            original_query.replace("Games", "Jogos"),
            original_query + " (informática)",
            original_query + " (tecnologia)"
        ]
        
        for query in variations:
            result = self._search_wikipedia(query)
            if "não encontrada" not in result.lower() and "não disponível" not in result.lower():
                return result
                
        return f"Nenhum resultado encontrado para '{original_query}' ou variações relacionadas"

    def _search_wikipedia(self, query: str) -> str:
        """Executa a pesquisa na Wikipedia e processa os resultados"""
        data = self._make_api_request(query)
        if not data:
            return "Erro ao conectar com a Wikipedia. Tente novamente mais tarde."
            
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return f"Nenhum resultado encontrado para: {query}"
            
        page = next(iter(pages.values()))
        if "missing" in page:
            return f"Página não encontrada para: {query}"
            
        text = page.get("extract", "")
        if not text:
            return f"Conteúdo não disponível para: {query}"
            
        # Limpeza do texto
        text = re.sub(r'\[\d+\]', '', text)  # Remove citações [1], [2], etc.
        text = re.sub(r'\n{3,}', '\n\n', text)  # Normaliza quebras de linha
        return text.strip()

    def _run(self, query: str) -> str:
        """
        Método principal para execução da ferramenta
        
        Args:
            query: Termo de pesquisa (2-100 caracteres)
            
        Returns:
            Texto formatado ou mensagem de erro descritiva
        """
        try:
            # Validação e normalização
            if isinstance(query, dict):
                query = query.get('query', '') if 'query' in query else str(query)
            
            
            validated = WikipediaToolSchema(query=query)
            clean_query = self._normalize_query(validated.query)
            
            # Verifica cache primeiro
            if clean_query in self._cache:
                logger.debug(f"Cache hit para: {clean_query}")
                return self._cache[clean_query]
            
            # Tenta a pesquisa principal
            result = self._search_wikipedia(clean_query)
            
            # Se não encontrado, tenta variações
            if "não encontrada" in result.lower():
                result = self._try_variations(clean_query)
            
            # Atualiza cache
            if len(self._cache) >= self._MAX_CACHE_SIZE:
                self._cache.pop(next(iter(self._cache)))
            self._cache[clean_query] = result
            
            return result
            
        except ValidationError as ve:
            logger.error(f"Consulta inválida: {query} - {ve}")
            return "Por favor, use um termo entre 2 e 100 caracteres."
        except Exception as e:
            logger.exception(f"Erro inesperado processando: {query}")
            return "Ocorreu um erro inesperado. Tente novamente com termos diferentes."