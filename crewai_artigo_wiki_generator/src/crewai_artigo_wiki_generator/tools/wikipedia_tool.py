from crewai.tools import BaseTool
import requests
from pydantic import BaseModel, Field, ValidationError, field_validator
import logging
from urllib.parse import quote
import re
import time
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

class WikipediaToolSchema(BaseModel):
    query: str = Field(..., min_length=2, max_length=100, 
                      description="Termo de pesquisa para a Wikipedia")
    
    @field_validator('query', mode='before')
    def extract_query_from_dict(cls, v: Union[str, dict]) -> str:
        """Extract query from either string or dict input"""
        if isinstance(v, dict):
            if 'query' in v:
                return v['query']
            elif 'description' in v:
                return v['description']
            raise ValueError("Input dict must contain 'query' or 'description'")
        return v

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
    _MAX_RETRIES = 20
    _INITIAL_TIMEOUT = 5
    _USER_AGENT = "CrewAI-ResearchBot/2.0 (https://github.com/org/repo; contact@email.com)"
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza a consulta para melhor correspondência na Wikipedia"""
        # Decodifica primeiro se vier codificado
        print(query)
        if '%' in query:
            from urllib.parse import unquote
            query = unquote(query)
        
        # Remove caracteres especiais e normaliza espaços
        query = re.sub(r'[^\w\sáéíóúâêîôûãõç-]', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query.title()

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

    def _get_search_fallbacks(self, query: str) -> list:
        """Gera uma sequência hierárquica de estratégias de fallback"""
        strategies = [
            # 1. Tentar o termo exato (já normalizado)
            lambda q: [q],
            
            # 2. Variações linguísticas
            lambda q: [
                q,
                q.lower(),
                q.title(),
                q.capitalize(),
                re.sub(r'(?i)(?:ões|ães|ais|res|ns)$', '', q),  # singular
                re.sub(r'(?i)([^s])$', r'\1s', q),  # plural
            ],
            
            # 3. Redirecionamentos conhecidos
            lambda q: [
                f"História de {q}",
                f"Evolução de {q}",
                f"Introdução a {q}",
                f"O que é {q}",
                f"{q} (desambiguação)",
                f"Categoria:{q}"
            ],
            
            # 4. Busca por prefixos/sufixos comuns
            lambda q: [
                f"Teoria de {q}",
                f"Filosofia de {q}",
                f"Ciência de {q}",
                f"Tecnologia de {q}",
                f"{q} no Brasil",
                f"{q} em Portugal"
            ],
            
            # 5. Busca fonética aproximada (sem acentos)
            lambda q: [''.join(
                {'á':'a','é':'e','í':'i','ó':'o','ú':'u',
                 'â':'a','ê':'e','î':'i','ô':'o','û':'u',
                 'ã':'a','õ':'o','ç':'c'}.get(c, c) for c in q
            )]
        ]
        
        # Gera todas as variações sem duplicatas
        variations = []
        seen = set()
        for strategy in strategies:
            for variation in strategy(query):
                if variation not in seen:
                    seen.add(variation)
                    variations.append(variation)
        
        return variations

    def _search_with_fallbacks(self, query: str) -> str:
        """Executa a pesquisa com todas as estratégias de fallback"""
        # 1. Primeiro tenta a pesquisa direta
        result = self._search_wikipedia(query)
        if self._is_valid_result(result):
            return result
        
        # 2. Obtém todas as variações possíveis
        fallbacks = self._get_search_fallbacks(query)
        
        # 3. Tenta cada variação com timeout progressivo
        for i, variation in enumerate(fallbacks[:20]):  # Limita a 20 tentativas
            try:
                result = self._search_wikipedia(variation)
                if self._is_valid_result(result):
                    # Adiciona contexto sobre o redirecionamento
                    if variation != query:
                        result = f"(Redirecionado de '{query}' para '{variation}')\n\n{result}"
                    return result
            except Exception as e:
                logger.warning(f"Falha na variação {variation}: {str(e)}")
                continue
        
        # 4. Como último recurso, tenta a API de busca
        return self._try_search_api(query)

    def _is_valid_result(self, result: str) -> bool:
        """Verifica se o resultado é válido (não é mensagem de erro)"""
        invalid_phrases = [
            "não encontrada",
            "não disponível",
            "sem conteúdo",
            "página inexistente",
            "invalid title"
        ]
        return not any(phrase in result.lower() for phrase in invalid_phrases)

    def _try_search_api(self, query: str) -> str:
        """Usa a API de busca quando não encontra por título exato"""
        search_url = (
            "https://pt.wikipedia.org/w/api.php?"
            "action=query&"
            "list=search&"
            "srlimit=5&"
            "srprop=size&"
            f"srsearch={quote(query)}&"
            "format=json"
        )
        
        try:
            response = requests.get(search_url, timeout=10)
            data = response.json()
            if 'query' in data and data['query']['search']:
                top_results = [item['title'] for item in data['query']['search'][:3]]
                return (
                    f"Não encontrado exatamente '{query}', mas talvez queira:\n" +
                    "\n".join(f"- {title}" for title in top_results)
                )
            return f"Nenhum resultado encontrado para '{query}'"
        except Exception:
            return f"Falha ao buscar alternativas para '{query}'"

    def _run(self, query: Union[str, dict]) -> str:
        """Método principal que aceita múltiplos formatos de entrada"""
        try:
            # Handle both string and dict inputs
            if isinstance(query, dict):
                if 'query' in query:
                    clean_query = self._normalize_query(query['query'])
                elif 'description' in query:
                    clean_query = self._normalize_query(query['description'])
                else:
                    return "Formato de entrada inválido - deve conter 'query' ou 'description'"
            else:
                clean_query = self._normalize_query(query)
                
            # Verifica cache
            if clean_query in self._cache:
                return self._cache[clean_query]
            
            # Executa a pesquisa com fallbacks
            result = self._search_with_fallbacks(clean_query)
            
            # Atualiza cache
            if len(self._cache) >= self._MAX_CACHE_SIZE:
                self._cache.pop(next(iter(self._cache)))
            self._cache[clean_query] = result
            
            return result
            
        except Exception as e:
            logger.exception("Erro inesperado")
            return f"Erro durante a pesquisa: {str(e)}"