# tests/unit/test_parse_artigo.py
import json

import pytest

from crewai_generator_wiki_article.main import parse_artigo


def test_parse_artigo_json_limpo():
    raw = json.dumps(
        {
            "titulo": "Cerrado",
            "topico": "Bioma",
            "autor": "MultiAgente AI",
            "paragrafos": [{"titulo": "Introdução", "conteudo": "O Cerrado..."}],
            "referencias": ["WIKIPÉDIA. Cerrado..."],
        }
    )
    resultado = parse_artigo(raw)
    assert resultado["titulo"] == "Cerrado"
    assert len(resultado["paragrafos"]) == 1


def test_parse_artigo_remove_code_fence():
    raw = '```json\n{"titulo": "X", "topico": "Y", "autor": "Z", "paragrafos": [], "referencias": []}\n```'
    resultado = parse_artigo(raw)
    assert resultado["titulo"] == "X"


def test_parse_artigo_json_invalido_levanta_value_error():
    with pytest.raises(ValueError, match="não é JSON válido"):
        parse_artigo("isto não é json")


def test_parse_artigo_campo_obrigatorio_ausente():
    with pytest.raises(ValueError, match="não é JSON válido"):
        parse_artigo('{"topico": "Y"}')  # falta titulo, paragrafos