# tests/guardrails/test_validate_artigo_json.py
from crewai.tasks.task_output import TaskOutput

from crewai_generator_wiki_article.crew import validate_artigo_json


def _output(raw: str) -> TaskOutput:
    return TaskOutput(
        raw=raw,
        description="review",
        expected_output="JSON",
        agent="reviewer",
    )


def test_guardrail_aceita_json_valido():
    raw = '{"titulo": "X", "paragrafos": [{"titulo": "a", "conteudo": "b"}]}'
    ok, valor = validate_artigo_json(_output(raw))
    assert ok is True
    assert valor["titulo"] == "X"


def test_guardrail_rejeita_json_sem_titulo():
    ok, motivo = validate_artigo_json(_output('{"paragrafos": []}'))
    assert ok is False
    assert "titulo" in motivo


def test_guardrail_rejeita_json_malformado():
    ok, motivo = validate_artigo_json(_output("não é json"))
    assert ok is False
    assert "JSON inválido" in motivo