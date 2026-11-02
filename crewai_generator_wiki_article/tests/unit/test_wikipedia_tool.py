# tests/unit/test_wikipedia_tool.py
import pytest

from crewai_generator_wiki_article.tools.wikipedia_tool import WikipediaTool


@pytest.fixture
def tool():
    return WikipediaTool()


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("História do Brasil", "História do Brasil"),
        ("história DO brasil", "História DO brasil"),
        ("  cerrado  ", "Cerrado"),
        ("São Paulo", "São Paulo"),
        ("", ""),
    ],
)
def test_normalize_query_preserva_preposicoes(tool, entrada, esperado):
    assert tool._normalize_query(entrada) == esperado


def test_normalize_query_decodifica_url(tool):
    assert tool._normalize_query("Intelig%C3%AAncia%20Artificial") == "Inteligência Artificial"


@pytest.mark.parametrize(
    "resultado, valido",
    [
        ("Cerrado é bioma brasileiro...", True),
        ("Página não encontrada para: Xyz", False),
        ("Conteúdo não disponível para: Xyz", False),
        ("Nenhum resultado encontrado para: Xyz", True),  # mensagem de "sem resultado" é válida como texto
    ],
)
def test_is_valid_result(tool, resultado, valido):
    assert tool._is_valid_result(resultado) is valido


def test_is_relevant_rejeita_resultado_fora_do_tema(tool):
    # Query "Cerrado (bioma)" não deve aceitar um artigo sobre "Wikipédia"
    assert tool._is_relevant("Cerrado (bioma)", "Wikipédia", "Wikipédia é uma enciclopédia...") is False


def test_is_relevant_aceita_resultado_do_tema(tool):
    assert tool._is_relevant("Cerrado", "Cerrado", "Cerrado é bioma brasileiro...") is True