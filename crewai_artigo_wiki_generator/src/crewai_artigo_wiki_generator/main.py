#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crewai_artigo_wiki_generator.crew import CrewaiArtigoWikiGenerator

from fastapi import FastAPI




warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")



# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    while True:
        topic = input("Digite o tópico do artigo: ").strip()

        if topic:
            # Se o tópico for válido, inicia o processo
            inputs = {
                'topic': topic,
                'current_year': str(datetime.now().year)
            }

            try:
                CrewaiArtigoWikiGenerator().crew().kickoff(inputs=inputs)
            except Exception as e:
                raise Exception(f"An error occurred while running the crew: {e}")
            break  # Sai do loop depois de executar com sucesso

        else:
            print("⚠️ Você deixou o campo em branco. Deseja tentar novamente?")
            opcao = input("Digite 's' para tentar novamente ou qualquer outra tecla para sair: ").strip().lower()
            if opcao != 's':
                print("🚪 Processo encerrado.")
                break  # Sai do loop e encerra o programa


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CrewaiArtigoWikiGenerator().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CrewaiArtigoWikiGenerator().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "Games",
        "current_year": str(datetime.now().year)
    }
    try:
        CrewaiArtigoWikiGenerator().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
