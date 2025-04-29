import json
import logging
from datetime import datetime
import traceback
from typing import Dict, Any
from urllib.parse import unquote
from flask import request, jsonify
from flask import Flask
from pydantic import ValidationError
from crewai import Crew
from crewai.task import TaskOutput
from models.article_model import Artigo # Your Pydantic model
from crew import CrewaiArtigoWikiGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def normalize_output(output: Any) -> Dict[str, Any]:
    """Normalize CrewAI output to consistent dictionary format"""
    try:
        # Handle TaskOutput objects
        if isinstance(output, TaskOutput):
            output = output.raw_output
        
        # Handle string output that might be Python dict representation
        if isinstance(output, str):
            output = output.strip()
            
            # Try to detect and convert Python dict string
            if output.startswith(('{', '[', 'titulo=', 'paragrafos=')):
                try:
                    # Convert from Python dict string to actual dict
                    import ast
                    output = ast.literal_eval(output)
                except (ValueError, SyntaxError):
                    # If that fails, try as JSON
                    try:
                        output = json.loads(output)
                    except json.JSONDecodeError:
                        pass  # Keep as string
        
        # Handle Pydantic models
        if hasattr(output, 'model_dump'):  # Pydantic v2
            return output.model_dump()
        elif hasattr(output, 'dict'):  # Pydantic v1
            return output.dict()
        
        # Handle dictionaries directly
        if isinstance(output, dict):
            return output
        
        # Fallback for other types - attempt to extract structure
        return {
            "raw_output": str(output),
            "titulo": getattr(output, 'titulo', "Sem Título"),
            "topico": getattr(output, 'topico', "Tópico Desconhecido"),
            "paragrafos": getattr(output, 'paragrafos', [])
        }
    
    except Exception as e:
        logger.error(f"Normalization failed: {str(e)}")
        return {"error": f"Output normalization error: {str(e)}"}

def validate_article_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and complete article data structure"""
    try:
        # Handle cases where data might be a string representation
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                try:
                    import ast
                    data = ast.literal_eval(data)
                except (ValueError, SyntaxError):
                    raise ValueError("Invalid data format - could not parse as JSON or Python dict")

        # Ensure we have a dictionary at this point
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary or convertible to one")

        # Handle raw content if present
        if 'raw' in data and data['raw']:
            try:
                raw_content = data['raw'].strip()
                if raw_content.startswith('```json') and raw_content.endswith('```'):
                    raw_content = raw_content[7:-3].strip()
                parsed_raw = json.loads(raw_content)
                data = {**data, **parsed_raw}
                data.pop('raw', None)
            except json.JSONDecodeError:
                logger.warning("Could not parse raw content - proceeding without it")

        # Set defaults
        defaults = {
            "titulo": data.get('titulo', "Sem Título"),
            "topico": data.get('topico', "Tópico Desconhecido"),
            "paragrafos": data.get('paragrafos', []),
            "data_criacao": datetime.now().isoformat(),
            "autor": "Artigo Multiagente IA",
            "referencias": []
        }

        # Merge with existing data
        validated_data = {**defaults, **data}

        # Ensure paragraphs have proper structure
        validated_paragraphs = []
        for para in validated_data['paragrafos']:
            if isinstance(para, str):
                validated_paragraphs.append({
                    "titulo": "Parágrafo",
                    "conteudo": para
                })
            elif isinstance(para, dict):
                validated_paragraphs.append({
                    "titulo": para.get('titulo', "Parágrafo"),
                    "conteudo": para.get('conteudo', "")
                })
            else:
                # Try to convert other paragraph types
                validated_paragraphs.append({
                    "titulo": getattr(para, 'titulo', "Parágrafo"),
                    "conteudo": getattr(para, 'conteudo', "")
                })

        validated_data['paragrafos'] = validated_paragraphs

        # Validate using Pydantic model
        artigo = Artigo(**validated_data)
        return artigo.model_dump()
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise ValueError(f"Invalid article structure: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected validation error: {str(e)}")
        raise ValueError(f"Article validation failed: {str(e)}")

def execute_crew_process(topic: str) -> Dict[str, Any]:
    """Execute the CrewAI process with robust error handling"""
    try:
        logger.info(f"Starting article generation for: {topic}")
        
        
        # Initialize and execute crew
        result = CrewaiArtigoWikiGenerator().crew().kickoff(inputs={"topic": topic})
        
        # Normalize and validate output
        print(result)
        normalized = normalize_output(result)
        validated = validate_article_data(normalized)
        
        # Debug logging
        logger.debug(f"Final output structure: {json.dumps(validated, indent=2, ensure_ascii=False)}")
        
        return validated
    
    except Exception as e:
        logger.error(f"Process execution failed: {str(e)}")
        return {"error": str(e)}

@app.route("/generate_article", methods=["GET"])
def generate_article():
    try:
        topic = request.args.get('topic', '').strip()
        if not topic:
            return jsonify({"error": "O parâmetro 'topic' é obrigatório"}), 400
        
        # Initialize the generator
        result = execute_crew_process(topic)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500




@app.after_request
def add_headers(response):
    """Ensure proper content type and encoding"""
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)