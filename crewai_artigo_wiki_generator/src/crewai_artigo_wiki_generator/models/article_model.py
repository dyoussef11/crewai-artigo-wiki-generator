from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Paragrafo(BaseModel):
    titulo: Optional[str] = Field(default=None)
    conteudo: str

class Artigo(BaseModel):
    titulo: str
    topico: str
    data_criacao: datetime = Field(default_factory=datetime.now)
    autor: Optional[str] = "Sistema Multiagente"
    paragrafos: List[Paragrafo]
    referencias: List[str] = []
