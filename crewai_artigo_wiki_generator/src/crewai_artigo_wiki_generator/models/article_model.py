from pydantic import BaseModel
from typing import List

class Referencia(BaseModel):
    titulo: str
    link: str

class Secao(BaseModel):
    subtitulo: str
    conteudo: str

class Artigo(BaseModel):
    titulo: str
    secoes: List[Secao]
    conclusao: str
    referencias: List[Referencia]
