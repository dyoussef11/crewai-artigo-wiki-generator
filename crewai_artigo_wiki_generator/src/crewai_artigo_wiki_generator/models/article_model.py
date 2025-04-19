from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Paragrafo(BaseModel):
    """
    Representa um parágrafo de um artigo, com um título opcional e conteúdo obrigatório.
    """
    titulo: Optional[str] = Field(default=None, description="Título opcional do parágrafo.")
    conteudo: str  # Conteúdo textual do parágrafo


class Artigo(BaseModel):
    """
    Representa um artigo gerado pelo sistema multiagente.

    Atributos:
        titulo (str): Título principal do artigo.
        topico (str): Tópico que originou a geração do artigo.
        data_criacao (datetime): Data e hora em que o artigo foi criado.
        autor (Optional[str]): Autor do artigo (por padrão, 'Sistema Multiagente').
        paragrafos (List[Paragrafo]): Lista de parágrafos que compõem o corpo do artigo.
        referencias (List[str]): Lista de URLs ou fontes utilizadas na criação do artigo.
    """
    titulo: str
    topico: str
    data_criacao: datetime = Field(default_factory=datetime.now, description="Data de criação do artigo.")
    autor: Optional[str] = "Sistema Multiagente"
    paragrafos: List[Paragrafo]
    referencias: List[str] = []

