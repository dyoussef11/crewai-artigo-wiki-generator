# tests/unit/test_markdown.py
from crewai_generator_wiki_article.main import artigo_to_markdown


def test_markdown_inclui_titulo_e_referencias():
    artigo = {
        "titulo": "Cerrado",
        "topico": "Bioma",
        "autor": "MultiAgente AI",
        "data_criacao": "2026-11-02T10:00:00",
        "paragrafos": [
            {"titulo": "Introdução", "conteudo": "Texto."},
            {"titulo": "Conclusão", "conteudo": "Fim."},
        ],
        "referencias": ["WIKIPÉDIA. Cerrado..."],
    }
    md = artigo_to_markdown(artigo)
    assert "# CERRADO" in md
    assert "## 1 INTRODUÇÃO" in md
    assert "## 3 CONSIDERAÇÕES FINAIS" in md
    assert "## REFERÊNCIAS" in md
    assert "WIKIPÉDIA. Cerrado..." in md