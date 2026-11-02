# tests/integration/test_crew_flow.py
import json

import pytest

from crewai_generator_wiki_article.crew import CrewaiGeneratorWikiArticle
from stub_llm import StubLLM


def _crew_com_stub(llm):
    """Injeta o stub em todos os agentes da crew."""
    crew = CrewaiGeneratorWikiArticle().crew()
    for agent in crew.agents:
        agent.llm = llm
    return crew


def test_fluxo_completo_com_stub():
    artigo_final = {
        "titulo": "Cerrado",
        "topico": "Bioma",
        "autor": "MultiAgente AI",
        "paragrafos": [
            {"titulo": "Introdução", "conteudo": "O Cerrado..."},
            {"titulo": "Conclusão", "conteudo": "Fim."},
        ],
        "referencias": ["WIKIPÉDIA. Cerrado..."],
    }

    llm = StubLLM(
        responses=[
            # research_task: texto com a fonte no formato esperado
            "[FONTE: Cerrado | URL: https://pt.wikipedia.org/wiki/Cerrado]\n\nCerrado é bioma brasileiro...",
            # reporting_task: rascunho do artigo
            "# Cerrado\n\nO Cerrado é...",
            # review_task: JSON final
            json.dumps(artigo_final),
        ]
    )

    crew = _crew_com_stub(llm)
    resultado = crew.kickoff(inputs={"topic": "Cerrado", "current_year": "2026"})

    # 1. O LLM foi chamado exatamente 3 vezes (uma por task)
    assert len(llm.calls) == 3

    # 2. A primeira chamada foi do researcher, com a tool disponível
    assert llm.calls[0]["from_agent"] is not None

    # 3. O resultado final é parseável
    from crewai_generator_wiki_article.main import parse_artigo
    artigo = parse_artigo(resultado.raw)
    assert artigo["titulo"] == "Cerrado"
    assert len(artigo["referencias"]) == 1
    assert "wikipedia.org/wiki/Cerrado" in artigo["referencias"][0]