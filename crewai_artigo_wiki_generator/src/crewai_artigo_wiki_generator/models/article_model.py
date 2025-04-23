from pydantic import BaseModel
from typing import List

class Paragrafo(BaseModel):
    titulo: str
    conteudo: str

class Artigo(BaseModel):
    titulo: str
    topico: str
    data_criacao: str = None
    autor: str = "Artigo Multiagente IA"
    paragrafos: List[Paragrafo]
    referencias: List[str] = []