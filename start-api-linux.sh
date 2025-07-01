#!/bin/bash

# Color configuration
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
RESET='\033[0m'

# Python check
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python not found in PATH${RESET}"
    read -p "Press any key to continue..."
    exit 1
fi

# Virtual environment setup
if [ ! -d ".venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${RESET}"
    python -m venv .venv || {
        echo -e "${RED}Failed to create virtual environment${RESET}"
        read -p "Press any key to continue..."
        exit 1
    }
fi

echo -e "${YELLOW}Activating virtual environment...${RESET}"
source .venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment${RESET}"
    read -p "Press any key to continue..."
    exit 1
}

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}Installing dependencies...${RESET}"
    pip install -r requirements.txt || {
        echo -e "${RED}Failed to install dependencies${RESET}"
        read -p "Press any key to continue..."
        exit 1
    }
fi

# Get and validate topic
get_topic() {
    while true; do
        echo
        read -p "Digite o tópico para o artigo: " TOPIC
        
        # Python validation
        python -c "
import sys, re
t = sys.argv[1].strip()
exit(1) if (not t or len(t)<3 or t.isdigit() or all(not c.isalnum() for c in t)) else exit(0)
" "$TOPIC" && break
        
        echo -e "${RED}Tópico inválido! Por favor, insira um tópico significativo.${RESET}"
    done
}

get_topic

# Normalize topic for URL and filename
echo -e "${YELLOW}Normalizando tópico...${RESET}"

ENCODED_TOPIC=$(python -c "
import urllib.parse, re
topic = r'''$TOPIC'''
encoded = urllib.parse.quote(topic)
clean = re.sub(r'[^\w\-_]', '_', topic)
print(f'{encoded}|{clean[:50]}')
")

IFS='|' read -r ENCODED_TOPIC CLEAN_FILENAME <<< "$ENCODED_TOPIC"

if [ -z "$ENCODED_TOPIC" ]; then
    echo -e "${RED}Falha ao normalizar o tópico!${RESET}"
    get_topic
fi

# Start Flask server
echo -e "${YELLOW}Iniciando servidor Flask...${RESET}"
gnome-terminal -- python crewai-artigo-wiki-generator/crewai_artigo_wiki_generator/src/crewai_artigo_wiki_generator/main.py &
FLASK_PID=$!

# Wait for initialization
echo -e "${YELLOW}Aguardando inicialização do servidor...${RESET}"
sleep 10

# Generate clean filename
CLEAN_TOPIC=$(echo "$TOPIC" | tr -d '/\:?&')
BASE_FILENAME="artigo_${CLEAN_TOPIC:0:50}"

# Create output directory if it doesn't exist
mkdir -p "artigos-gerados-exemplo/json"

echo -e "${GREEN}Gerando artigo...${RESET}"

# Show curl command
echo "Comando curl que será executado:"
echo "curl -X GET \"http://127.0.0.1:5000/generate_article?topic=$ENCODED_TOPIC\" \\"
echo "     -H \"Accept: application/json; charset=utf-8\" \\"
echo "     -o \"artigos-gerados-exemplo/json/$BASE_FILENAME.json\""
echo

# Execute curl
curl -X GET "http://127.0.0.1:5000/generate_article?topic=$ENCODED_TOPIC" \
     -H "Accept: application/json; charset=utf-8" \
     -o "artigos-gerados-exemplo/json/$BASE_FILENAME.json" || {
    echo -e "${RED}Falha ao gerar artigo${RESET}"
    read -p "Press any key to continue..."
    kill $FLASK_PID
    exit 1
}

# Verify JSON was created
if [ ! -f "artigos-gerados-exemplo/json/$BASE_FILENAME.json" ]; then
    echo -e "${RED}Arquivo JSON não foi criado corretamente${RESET}"
    read -p "Press any key to continue..."
    kill $FLASK_PID
    exit 1
fi

echo -e "- artigos-gerados-exemplo/json/$BASE_FILENAME.json (dados estruturados)"

# Open the file
xdg-open "artigos-gerados-exemplo/json/$BASE_FILENAME.json"

echo
read -p "Press any key to continue..."
kill $FLASK_PID