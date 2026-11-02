

# 🧠 crewAI Artigo Wiki Generator

Sistema multiagente de geração de artigos em português a partir da Wikipedia, construído com [CrewAI](https://www.crewai.com/) e LLMs do [Groq](https://groq.com/). O projeto orquestra três agentes especializados — pesquisador, redator e revisor — para produzir artigos estruturados, com referências no padrão ABNT, em dois formatos de saída: **JSON estruturado** e **Markdown formatado**.

---

## ✨ Funcionalidades

- ✅ Geração de artigos em português baseados em tópicos da Wikipedia
- 🤖 Arquitetura multiagente com três papéis especializados:
  - **Pesquisador** — busca e extrai conteúdo da Wikipedia
  - **Redator** — transforma o material em artigo coeso
  - **Revisor** — corrige, estrutura e devolve o JSON final
- 📚 Referências no padrão **ABNT** (verbete da Wikipédia citado com URL e data de acesso)
- 📦 Gerenciamento de dependências com [`uv`](https://docs.astral.sh/uv/) (substitui `pip` + `requirements.txt`)
- 🧠 Integração com **Groq** via LiteLLM (`groq/openai/gpt-oss-120b`)
- 📝 Saída dupla: **JSON** (dados estruturados) e **Markdown** (pronto para publicação)
- 🚀 Execução por linha de comando (CLI) ou por scripts prontos para Windows e Linux/macOS
- 🔒 Validação Pydantic no Python — o LLM não é forçado a emitir tool calls para estruturar a saída

---

## 🛠️ Pré-requisitos

- **[uv](https://docs.astral.sh/uv/)** instalado:
  ```bash
  # Linux/macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  irm https://astral.sh/uv/install.ps1 | iex
  ```
- **Python 3.10 a 3.13** (o `uv` instala automaticamente se necessário)
- **Chave de API do Groq** — gratuita em [console.groq.com](https://console.groq.com/)

---

## 🚀 Instalação e Execução

### 🔑 Configuração da chave do Groq

Crie o arquivo `crewai_generator_wiki_article/.env` com:

```env
GROQ_API_KEY=gsk_...sua_chave_aqui...
```

> A chave é carregada automaticamente pelo `main.py` via `python-dotenv`. O `.env` já está no `.gitignore`.

### 🔁 Método Automático (Recomendado)

#### 🪟 Windows

Clique duas vezes em `start-api.bat` ou execute no terminal:

```cmd
start-api.bat
```

#### 🐧 Linux / macOS

```bash
chmod +x start-api-linux.sh
./start-api-linux.sh
```

**O que os scripts fazem:**

1. Verificam se o `uv` está instalado
2. Executam `uv sync --extra dev` no diretório do projeto
3. Solicitam o tópico do artigo
4. Chamam o `main.py` com `--output` e `--output-md`
5. Abrem automaticamente os dois arquivos gerados

### 🔧 Instalação Manual (Alternativa)

```bash
# Clone o repositório
git clone https://github.com/dyoussef11/crewai-artigo-wiki-generator.git
cd crewai-artigo-wiki-generator/crewai_generator_wiki_article

# Sincronize as dependências (cria .venv e instala tudo)
uv sync --extra dev

# Configure a chave do Groq
echo "GROQ_API_KEY=gsk_..." > .env

# Execute com um tópico
uv run python src/crewai_generator_wiki_article/main.py "Cerrado" \
    --output ../artigos-gerados/json/artigo_Cerrado.json \
    --output-md ../artigos-gerados/edicao-final/artigo_Cerrado.md
```

---

## 🧪 Como usar

### CLI direto

```bash
cd crewai_generator_wiki_article
uv run python src/crewai_generator_wiki_article/main.py "Tópico" \
    --output ../artigos-gerados/json/artigo_Topico.json \
    --output-md ../artigos-gerados/edicao-final/artigo_Topico.md
```

**Argumentos:**

| Argumento | Obrigatório | Descrição |
| :--- | :--- | :--- |
| `topic` | Não | Tópico do artigo (padrão: `Brasil`) |
| `--output`, `-o` | Não | Caminho do JSON de saída (se omitido, imprime no stdout) |
| `--output-md` | Não | Caminho do Markdown de saída (formato ABNT) |

### Saída JSON

```json
{
  "titulo": "Cerrado",
  "topico": "Bioma brasileiro",
  "autor": "MultiAgente AI",
  "data_criacao": "2026-11-02T14:30:00",
  "paragrafos": [
    {"titulo": "Introdução", "conteudo": "O Cerrado..."},
    {"titulo": "Desenvolvimento", "conteudo": "A vegetação..."},
    {"titulo": "Conclusão", "conteudo": "Para mitigar..."}
  ],
  "referencias": [
    "WIKIPÉDIA. Cerrado. Disponível em: <https://pt.wikipedia.org/wiki/Cerrado>. Acesso em: 02 nov. 2026."
  ]
}
```

### Saída Markdown (ABNT básico)

```markdown
# CERRADO

**Autor:** AI, MULTIAGENTE  
**Tópico:** Bioma brasileiro  
**Data:** 02/11/2026

---

## 1 INTRODUÇÃO
O Cerrado...

## 2 DESENVOLVIMENTO
A vegetação...

## 3 CONSIDERAÇÕES FINAIS
Para mitigar...

---

## REFERÊNCIAS
- WIKIPÉDIA. Cerrado. Disponível em: <https://pt.wikipedia.org/wiki/Cerrado>. Acesso em: 02 nov. 2026.
```

---

## 🗂️ Estrutura do Projeto

```
crewai-artigo-wiki-generator/
├── artigos-gerados/                    # Saídas geradas (ignoradas pelo git)
│   ├── json/                           # JSON estruturado
│   └── edicao-final/                   # Markdown formatado (ABNT)
├── crewai_generator_wiki_article/      # Projeto CrewAI (raiz do pacote)
│   ├── .env                            # GROQ_API_KEY (não versionado)
│   ├── pyproject.toml                  # Dependências e metadados
│   ├── uv.lock                         # Lock file (reprodutibilidade)
│   └── src/crewai_generator_wiki_article/
│       ├── __init__.py
│       ├── main.py                     # Entrypoint CLI (argparse + parse_artigo + artigo_to_markdown)
│       ├── crew.py                     # @CrewBase, @llm, @tool, 3 agentes, 3 tarefas
│       ├── config/
│       │   ├── agents.yaml             # Definição dos agentes (role, goal, backstory)
│       │   └── tasks.yaml              # Definição das tarefas + contexto
│       ├── models/
│       │   └── article_model.py        # Modelos Pydantic (Artigo, Paragrafo)
│       └── tools/
│           └── wikipedia_tool.py       # Ferramenta customizada de pesquisa
├── sanitize.py                         # Normaliza o tópico para nome de arquivo
├── start-api.bat                       # Script de inicialização (Windows)
├── start-api-linux.sh                  # Script de inicialização (Linux/macOS)
├── .gitignore
├── README.md
└── deptry_report.json                  # Relatório do deptry (opcional)
```

---

## 🧰 Tecnologias Utilizadas

- [Python](https://www.python.org/) 3.10–3.13
- [CrewAI](https://www.crewai.com/) — orquestração multiagente
- [LiteLLM](https://github.com/BerriAI/litellm) — camada de abstração dos LLMs (via `crewai[litellm]`)
- [Groq](https://groq.com/) — provedor dos modelos (`groq/openai/gpt-oss-120b`)
- [uv](https://docs.astral.sh/uv/) — gerenciador de dependências e ambiente
- [Pydantic](https://docs.pydantic.dev/) — validação da saída
- [python-dotenv](https://github.com/theskumar/python-dotenv) — carregamento do `.env`
- [requests](https://requests.readthedocs.io/) — chamadas à API do MediaWiki

---

## ⚠️ Solução de Problemas

### `429 Too Many Requests`

O plano gratuito do Groq impõe limites de **8.000 TPM** para o `gpt-oss-120b`. Se ocorrer:

- Reduza `exchars` na `WikipediaTool` (atualmente 900) para **600**
- Reduza o `expected_output` da `reporting_task` de 250 para **200 palavras**
- O `max_rpm=10` na `Crew` já segura a execução entre requisições

### `Tool choice is none, but model called a tool`

Bug conhecido do CrewAI ao forçar resposta final após `max_iter`. Mitigado com:

- `max_iter=15` no agente pesquisador
- Instrução explícita no `research_task` para parar após a primeira busca bem-sucedida
- Se persistir, troque o modelo para `groq/llama-3.3-70b-versatile`

### `model has been decommissioned`

O Groq descontinua modelos com frequência. Consulte [console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations) e ajuste o `model=` no método `@llm` do `crew.py`.

### `Missing GROQ_API_KEY`

Verifique se o arquivo `.env` existe em `crewai_generator_wiki_article/` e se a chave começa com `gsk_`.

---

## 🤝 Contribuindo

1. Faça um fork
2. Crie uma branch com sua feature (`git checkout -b minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Daniel Youssef** — [LinkedIn](https://www.linkedin.com/in/daniel-youssef-603867285/) • [GitHub](https://github.com/dyoussef11)


