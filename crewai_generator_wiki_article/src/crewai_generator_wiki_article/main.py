#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crewai_generator_wiki_article.crew import CrewaiGeneratorWikiArticle

import json
from pydantic import ValidationError
from crewai_generator_wiki_article.models.article_model import Artigo

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def parse_artigo(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json").strip()
    try:
        data = json.loads(raw)
        return Artigo(**data).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Saída do revisor não é JSON válido: {e}")

def artigo_to_markdown(artigo: dict) -> str:
    """Converte o artigo validado em Markdown formatado (estilo ABNT básico)."""
    from datetime import datetime as _dt

    titulo = artigo.get("titulo", "Artigo sem título")
    autor = artigo.get("autor", "MultiAgente AI")
    topico = artigo.get("topico", "")

    # Data: usa data_criacao se preenchida; senão, usa hoje
    data_str = artigo.get("data_criacao")
    if data_str:
        try:
            dt = _dt.fromisoformat(data_str.split("T")[0])
        except (ValueError, AttributeError):
            dt = _dt.now()
    else:
        dt = _dt.now()
    data_fmt = dt.strftime("%d/%m/%Y")

    # Autor em formato ABNT: SOBRENOME, Nome
    partes = autor.split()
    autor_abnt = (
        f"{partes[-1].upper()}, {' '.join(partes[:-1])}"
        if len(partes) > 1
        else autor.upper()
    )

    # Mapeamento de títulos de seção para o padrão ABNT
    secoes_abnt = {
        "introdução": "1 INTRODUÇÃO",
        "desenvolvimento": "2 DESENVOLVIMENTO",
        "conclusão": "3 CONSIDERAÇÕES FINAIS",
        "resumo": "RESUMO",
    }

    linhas = [
        f"# {titulo.upper()}\n",
        f"**Autor:** {autor_abnt}  ",
        f"**Tópico:** {topico}  ",
        f"**Data:** {data_fmt}\n",
        "---\n",
    ]

    for p in artigo.get("paragrafos", []):
        titulo_sec = p.get("titulo", "").strip()
        conteudo = p.get("conteudo", "").strip()
        cabecalho = secoes_abnt.get(titulo_sec.lower(), titulo_sec.upper())
        linhas.append(f"## {cabecalho}\n")
        linhas.append(f"{conteudo}\n")

    referencias = artigo.get("referencias", [])
    if referencias:
        linhas.append("---\n")
        linhas.append("## REFERÊNCIAS\n")
        for ref in referencias:
            linhas.append(f"- {ref}")
        linhas.append("")

    return "\n".join(linhas)


# def run():
#     topic = sys.argv[1] if len(sys.argv) > 1 else "Brasil"
#     inputs = {
#         'topic': topic,
#         'current_year': str(datetime.now().year)
#     }

#     try:
#         result = CrewaiGeneratorWikiArticle().crew().kickoff(inputs=inputs)
#         artigo = parse_artigo(result.raw)
#         print(json.dumps(artigo, ensure_ascii=False, indent=2))
#         return artigo
#     except ValueError as e:
#         raise Exception(f"Saída do revisor inválida: {e}")
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")

def run():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Gera artigo a partir da Wikipedia.")
    parser.add_argument("topic", nargs="?", default="Brasil", help="Tópico do artigo")
    parser.add_argument("--output", "-o", help="Arquivo JSON de saída")
    parser.add_argument("--output-md", help="Arquivo Markdown de saída")
    args = parser.parse_args()

    inputs = {
        'topic': args.topic,
        'current_year': str(datetime.now().year)
    }

    try:
        result = CrewaiGeneratorWikiArticle().crew().kickoff(inputs=inputs)
        artigo = parse_artigo(result.raw)

        # JSON
        json_str = json.dumps(artigo, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(json_str, encoding="utf-8")
            print(f"\nArtigo (JSON) salvo em: {args.output}", file=sys.stderr)
        else:
            print(json_str)

        # Markdown (opcional)
        if args.output_md:
            Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output_md).write_text(
                artigo_to_markdown(artigo), encoding="utf-8"
            )
            print(f"Artigo (Markdown) salvo em: {args.output_md}", file=sys.stderr)

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
    import json as _json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = _json.loads(sys.argv[1])
    except _json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = CrewaiGeneratorWikiArticle().crew().kickoff(inputs=inputs)
        return parse_artigo(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")


if __name__ == "__main__":
    run()