import pytest
from flask import Flask, jsonify, request
from crewai_artigo_wiki_generator.crew import CrewaiArtigoWikiGenerator
from unittest.mock import patch

app = Flask(__name__)

@app.route('/generate_article', methods=['GET'])
def generate_article():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "O parâmetro 'topic' é obrigatório"}), 400

    # Chamada da crew
    artigo = CrewaiArtigoWikiGenerator().crew().kickoff(inputs={"topic": topic})

    # Verificação da estrutura
    if not hasattr(artigo, 'titulo'):  # Para garantir que é um Pydantic model
        return jsonify({"error": "Erro ao gerar o artigo"}), 500

    return jsonify(artigo.model_dump()), 200  # .model_dump() para serializar Pydantic


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch.object(CrewaiArtigoWikiGenerator, 'crew')
def test_generate_article_success(mocked_crew, client):
    # Simulando retorno de um modelo Pydantic (como seria com output_pydantic=Artigo)
    class MockArtigo:
        def model_dump(self):
            return {
                "titulo": "A Ascensão da Inteligência Artificial",
                "topico": "Inteligência Artificial",
                "data_criacao": "2025-04-18",
                "autor": "Autor Teste",
                "paragrafos": ["Parágrafo 1", "Parágrafo 2"],
                "referencias": ["Referência 1"]
            }
    
    mocked_crew.return_value.kickoff.return_value = MockArtigo()

    response = client.get('/generate_article?topic=Inteligência%20Artificial')

    assert response.status_code == 200
    data = response.json

    assert data["titulo"] == "A Ascensão da Inteligência Artificial"
    assert data["topico"] == "Inteligência Artificial"
    assert isinstance(data["paragrafos"], list)
    assert isinstance(data["referencias"], list)

@patch.object(CrewaiArtigoWikiGenerator, 'crew')
def test_generate_article_failure(mocked_crew, client):
    mocked_crew.return_value.kickoff.return_value = {}

    response = client.get('/generate_article?topic=Inteligência%20Artificial')
    assert response.status_code == 500
    assert response.json["error"] == "Erro ao gerar o artigo"

def test_generate_article_missing_topic(client):
    response = client.get('/generate_article')
    assert response.status_code == 400
    assert response.json["error"] == "O parâmetro 'topic' é obrigatório"
