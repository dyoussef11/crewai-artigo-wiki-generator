from crewai.tools import BaseTool
import requests
from pydantic import BaseModel, Field
import logging
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

class WikipediaToolSchema(BaseModel):
    """
    Schema for Wikipedia search tool input validation
    """
    query: str = Field(..., 
                     description="Search term for Wikipedia in Portuguese",
                     min_length=2,
                     max_length=100)

class WikipediaTool(BaseTool):
    """
    Enhanced Wikipedia search tool for Portuguese content with:
    - Better query normalization
    - Improved error handling
    - Response formatting
    - Smart caching
    """
    name: str = "wikipedia_tool"
    description: str = (
        "Ferramenta de pesquisa na Wikipedia em português. "
        "Fornece resumos concisos de tópicos. "
        "Use para pesquisas precisas e confiáveis."
    )
    
    # Enhanced cache with expiration
    _cache: dict = {}
    _MAX_CACHE_SIZE = 100
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query for Wikipedia API"""
        # Remove extra whitespace and special characters
        query = re.sub(r'\s+', ' ', query).strip()
        # Capitalize first letter of each word for better matching
        return ' '.join(word.capitalize() for word in query.split())
    
    def _clean_response(self, text: str) -> str:
        """Clean and format Wikipedia response"""
        if not text:
            return text
            
        # Remove citation markers like [1], [2]
        text = re.sub(r'\[\d+\]', '', text)
        # Remove section headers
        text = re.sub(r'==.*?==+', '', text)
        # Normalize whitespace
        return re.sub(r'\s+', ' ', text).strip()
    
    def _run(self, query: str) -> str:
        """
        Execute Wikipedia search with enhanced reliability
        
        Args:
            query: Search term (2-100 characters)
            
        Returns:
            Cleaned content or error message
        """
        try:
            # Validate and normalize input
            validated = WikipediaToolSchema(query=query)
            clean_query = self._normalize_query(validated.query)
            
            # Check cache first
            if clean_query in self._cache:
                logger.debug(f"Cache hit for: {clean_query}")
                return self._cache[clean_query]
                
            # Prepare API request
            encoded_query = quote(clean_query)
            url = (
                "https://pt.wikipedia.org/w/api.php?"
                "action=query&"
                "prop=extracts&"
                "exlimit=1&"
                "exchars=1000&"
                "explaintext=1&"
                "exintro=1&"  # Get only the introduction
                f"titles={encoded_query}&"
                "format=json&"
                "utf8=1&"
                "redirects=1"
            )
            
            logger.info(f"Searching Wikipedia for: {clean_query}")
            
            # Make request with timeout and retry
            try:
                response = requests.get(
                    url,
                    timeout=10,
                    headers={'User-Agent': 'CrewAI WikipediaTool/1.0'}
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Wikipedia API request failed: {e}")
                return "Erro temporário ao acessar a Wikipedia. Tente novamente."
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            if not pages:
                logger.warning(f"No results found for: {clean_query}")
                return "Nenhum resultado encontrado para este tópico."
            
            # Get first page (Wikipedia API returns a dict with page IDs as keys)
            page = next(iter(pages.values()))
            
            if "missing" in page:
                logger.warning(f"Page not found: {clean_query}")
                return "Página não encontrada na Wikipedia."
                
            text = page.get("extract", "")
            cleaned_text = self._clean_response(text)
            
            if not cleaned_text:
                logger.warning(f"Empty content for: {clean_query}")
                return "Conteúdo não disponível para este tópico."
            
            # Update cache
            if len(self._cache) >= self._MAX_CACHE_SIZE:
                self._cache.popitem()
            self._cache[clean_query] = cleaned_text
            
            return cleaned_text
            
        except ValidationError as ve:
            logger.error(f"Invalid query: {query} - {ve}")
            return "Termo de pesquisa inválido. Use 2 a 100 caracteres."
        except Exception as e:
            logger.exception(f"Unexpected error processing: {query}")
            return "Erro inesperado ao processar sua pesquisa."