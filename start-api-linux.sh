#!/bin/bash

echo "🔧 Criando o ambiente virtual..."
python3 -m venv .venv

echo "⚙️ Ativando o ambiente virtual..."
source .venv/bin/activate

echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Solicitar o tópico do usuário
read -p "Digite o tópico para o artigo: " TOPICO

# Verificar se o tópico foi fornecido
if [ -z "$TOPICO" ]; then
    echo "O tópico não pode estar vazio. Encerrando o processo."
    exit 1
fi

# URL do servidor Flask
URL="http://127.0.0.1:5000/generate_article?topic=$TOPICO"

echo "🌐 Enviando requisição para o servidor Flask..."

# Fazer a requisição GET para o servidor Flask
curl -X GET "$URL"

# Manter o terminal aberto após execução
$SHELL
