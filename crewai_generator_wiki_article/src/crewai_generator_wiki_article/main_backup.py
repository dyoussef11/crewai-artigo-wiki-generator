#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crewai_generator_wiki_article.crew import CrewaiGeneratorWikiArticle

import json
from pydantic import ValidationError
from crewai_generator_wiki_article.models.article_model import Artigo

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew and validate the final article.
    """
    inputs = {
        'topic': 'Brasil',
        'current_year': str(datetime.now().year)
    }

    try:
        result = CrewaiGeneratorWikiArticle().crew().kickoff(inputs=inputs)
        artigo = parse_artigo(result.raw)  # <-- valida e converte para dict
        print(json.dumps(artigo, ensure_ascii=False, indent=2))
        return artigo
    except ValueError as e:
        raise Exception(f"Saída do revisor inválida: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        CrewaiGeneratorWikiArticle().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CrewaiGeneratorWikiArticle().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        CrewaiGeneratorWikiArticle().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = CrewaiGeneratorWikiArticle().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")

def parse_artigo(raw: str) -> dict:
    # Remove code fences, se houver
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json").strip()
    try:
        data = json.loads(raw)
        return Artigo(**data).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Saída do revisor não é JSON válido: {e}")