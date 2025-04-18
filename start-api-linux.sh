#!/bin/bash

echo "🔧 Criando o ambiente virtual..."
python3 -m venv .venv

echo "⚙️ Ativando o ambiente virtual..."
source .venv/bin/activate

echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt



echo "🚀 Executando aplicação..."
python src/crewai_artigo_wiki_generator/main.py

# Mantém o terminal aberto após execução (só necessário em alguns terminais interativos)
$SHELL
