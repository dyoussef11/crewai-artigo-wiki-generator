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
        
        # Handle string output (try to parse as JSON)
        if isinstance(output, str):
            try:
                output = json.loads(output)
            except json.JSONDecodeError:
                return {"raw_output": output}
        
        # Handle Pydantic models
        if hasattr(output, 'model_dump'):  # Pydantic v2
            return output.model_dump()
        elif hasattr(output, 'dict'):  # Pydantic v1
            return output.dict()
        
        # Handle dictionaries directly
        if isinstance(output, dict):
            return output
        
        # Fallback for other types
        return {"raw_output": str(output)}
    
    except Exception as e:
        logger.error(f"Normalization failed: {str(e)}")
        raise ValueError(f"Output normalization error: {str(e)}")

def validate_article_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and complete article data structure"""
    try:
        # Handle raw string if present
        if 'raw' in data and data['raw']:
            try:
                # Clean and parse the raw JSON
                raw_str = data['raw'].strip()
                
                # Remove potential JSON code block markers
                if raw_str.startswith('```json') and raw_str.endswith('```'):
                    raw_str = raw_str[7:-3].strip()
                
                # Parse the JSON
                parsed_data = json.loads(raw_str)
                
                # Merge with existing data (raw takes precedence)
                data = {**data, **parsed_data}
                
                # Remove the raw field as it's no longer needed
                data.pop('raw', None)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse raw JSON: {e}")
                # If raw is invalid but we have other data, continue
                if not all(k in data for k in ['titulo', 'topico', 'paragrafos']):
                    raise ValueError("Invalid raw JSON and missing required fields")

        # Ensure required fields with defaults
        defaults = {
            "titulo": "Sem Título",
            "topico": "Tópico Desconhecido",
            "paragrafos": [],
            "data_criacao": datetime.now().isoformat(),
            "autor": "Artigo Multiagente IA",
            "referencias": []
        }

        # Merge provided data with defaults
        merged_data = {**defaults, **data}

        # Convert paragraphs to dict if they're Pydantic models
        if isinstance(merged_data["paragrafos"], list):
            merged_data["paragrafos"] = [
                p.model_dump() if hasattr(p, 'model_dump') else 
                p.dict() if hasattr(p, 'dict') else p
                for p in merged_data["paragrafos"]
            ]

        # Validate using Pydantic model
        artigo = Artigo(**merged_data)
        
        return artigo.model_dump()
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValueError(f"Invalid article data structure: {e}")
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise ValueError(f"Article validation failed: {e}")

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