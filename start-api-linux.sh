#!/bin/bash
set -e

# ============================================================
# Cores
# ============================================================
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
RESET='\033[0m'

# ============================================================
# Diretórios
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/crewai_generator_wiki_article"

# ============================================================
# Verificações iniciais
# ============================================================
if ! command -v uv &> /dev/null; then
    echo -e "${RED}uv nao encontrado. Instale: https://docs.astral.sh/uv/${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
fi

if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    echo -e "${RED}Projeto nao encontrado em: $PROJECT_DIR${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
fi

# ============================================================
# Sincroniza dependências
# ============================================================
echo -e "${GREEN}Sincronizando dependencias com uv...${RESET}"
cd "$PROJECT_DIR"
uv sync --extra dev || {
    echo -e "${RED}Falha ao sincronizar dependencias${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
}

# ============================================================
# Solicita e valida o tópico
# ============================================================
get_topic() {
    while true; do
        echo
        read -p "Digite o topico para o artigo: " TOPIC

        uv run --quiet python -c "
import sys
t = sys.argv[1].strip()
if not t or len(t) < 3 or t.isdigit() or all(not c.isalnum() for c in t):
    sys.exit(1)
sys.exit(0)
" "$TOPIC" && break

        echo -e "${RED}Topico invalido! Use ao menos 3 caracteres alfanumericos.${RESET}"
    done
}

get_topic

# ============================================================
# Normaliza o nome do arquivo
# ============================================================
CLEAN_TOPIC=$(uv run --quiet python "$SCRIPT_DIR/sanitize.py" "$TOPIC" | tr -d '\r\n')
[ -z "$CLEAN_TOPIC" ] && CLEAN_TOPIC="artigo"

if [ "$CLEAN_TOPIC" = "artigo" ]; then
    BASE_FILENAME="artigo"
else
    BASE_FILENAME="artigo_${CLEAN_TOPIC}"
fi

# ============================================================
# Prepara diretórios de saída
# ============================================================
OUTPUT_DIR_JSON="$SCRIPT_DIR/artigos-gerados/json"
OUTPUT_DIR_MD="$SCRIPT_DIR/artigos-gerados/edicao-final"
mkdir -p "$OUTPUT_DIR_JSON" "$OUTPUT_DIR_MD"

OUTPUT_JSON="$OUTPUT_DIR_JSON/$BASE_FILENAME.json"
OUTPUT_MD="$OUTPUT_DIR_MD/$BASE_FILENAME.md"

# ============================================================
# Executa o crew
# ============================================================
echo
echo -e "${GREEN}Gerando artigo sobre \"$TOPIC\"...${RESET}"
echo -e "${YELLOW}JSON:     $OUTPUT_JSON${RESET}"
echo -e "${YELLOW}Markdown: $OUTPUT_MD${RESET}"
echo

if ! uv run python src/crewai_generator_wiki_article/main.py "$TOPIC" \
        --output "$OUTPUT_JSON" \
        --output-md "$OUTPUT_MD"; then
    echo
    echo -e "${RED}Falha ao gerar o artigo. Veja os logs acima.${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
fi

if [ ! -f "$OUTPUT_JSON" ]; then
    echo -e "${RED}Arquivo JSON nao foi criado: $OUTPUT_JSON${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
fi

if [ ! -f "$OUTPUT_MD" ]; then
    echo -e "${RED}Arquivo Markdown nao foi criado: $OUTPUT_MD${RESET}"
    read -p "Pressione Enter para sair..."
    exit 1
fi

# ============================================================
# Resultado
# ============================================================
echo
echo -e "${GREEN}============================================================${RESET}"
echo -e "${GREEN}  Artigo gerado com sucesso!${RESET}"
echo -e "${GREEN}============================================================${RESET}"
echo "  JSON:     $OUTPUT_JSON"
echo "  Markdown: $OUTPUT_MD"
echo -e "${GREEN}============================================================${RESET}"
echo

# Abre os dois arquivos com o handler padrão
if command -v xdg-open &> /dev/null; then
    xdg-open "$OUTPUT_JSON" >/dev/null 2>&1 &
    xdg-open "$OUTPUT_MD"   >/dev/null 2>&1 &
elif command -v open &> /dev/null; then
    open "$OUTPUT_JSON"
    open "$OUTPUT_MD"
else
    echo -e "${YELLOW}Nao foi possivel abrir automaticamente. Abra manualmente.${RESET}"
fi

read -p "Pressione Enter para sair..."