# tests/integration/test_event_bus.py
import json

from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.tool_usage_events import ToolUsageStartedEvent

from crewai_generator_wiki_article.crew import CrewaiGeneratorWikiArticle
from stub_llm import StubLLM


def test_tool_wikipedia_foi_chamada():
    eventos = []

    with crewai_event_bus.scoped_handlers():
        @crewai_event_bus.on(ToolUsageStartedEvent)
        def capturar(evento):
            eventos.append(evento.tool_name)

        llm = StubLLM(
            responses=[
                "[FONTE: Cerrado | URL: https://pt.wikipedia.org/wiki/Cerrado]\n\nCerrado...",
                "# Cerrado\n\nTexto.",
                json.dumps({
                    "titulo": "X",
                    "topico": "Y",
                    "autor": "Z",
                    "paragrafos": [],
                    "referencias": [],
                }),
            ]
        )
        crew = CrewaiGeneratorWikiArticle().crew()
        for agent in crew.agents:
            agent.llm = llm
        crew.kickoff(inputs={"topic": "Cerrado", "current_year": "2026"})

    assert "wikipedia_tool" in eventos