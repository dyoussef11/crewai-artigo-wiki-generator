import json
import logging
from datetime import datetime
from typing import Dict, Any
from flask import Flask, request, jsonify
from pydantic import ValidationError
from crewai import Crew
from crewai.task import TaskOutput
from models.article_model import Artigo  # Your Pydantic model
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
    required_fields = {
        "titulo": "Sem Título",
        "topico": "Tópico Desconhecido",
        "paragrafos": []
    }
    
    # Ensure all required fields exist with defaults
    for field, default in required_fields.items():
        data[field.lower()] = data.get(field.lower(), data.get(field, default))
    
    # Convert paragraphs if they're Pydantic models
    if isinstance(data["paragrafos"], list):
        data["paragrafos"] = [
            p.model_dump() if hasattr(p, 'model_dump') else 
            p.dict() if hasattr(p, 'dict') else p
            for p in data["paragrafos"]
        ]
    
    # Add metadata fields with defaults
    data["data_criacao"] = data.get("data_criacao", datetime.now().strftime("%Y-%m-%d"))
    data["autor"] = data.get("autor", "Artigo Multiagente IA")
    data["referencias"] = data.get("referencias", [])
    
    return data

def execute_crew_process(topic: str) -> Dict[str, Any]:
    """Execute the CrewAI process with robust error handling"""
    try:
        logger.info(f"Starting article generation for: {topic}")
        
        # Initialize and execute crew
        result = CrewaiArtigoWikiGenerator().crew().kickoff(inputs={"topic": topic})
        
        # Normalize and validate output
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
    """Endpoint to generate Wikipedia-style articles"""
    try:
        # Get and validate topic
        topic = request.args.get("topic", "").strip()
        if not topic:
            return jsonify({"error": "Topic cannot be empty"}), 400
        
        # Execute process
        result = execute_crew_process(topic)
        
        # Handle errors
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.after_request
def add_headers(response):
    """Ensure proper content type and encoding"""
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)