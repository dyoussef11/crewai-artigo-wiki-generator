
# 🧠 crewAI Artigo Wiki Generator

Um sistema multiagente de geração de artigos em português baseado na Wikipedia, utilizando a poderosa orquestração da biblioteca [CrewAI](https://www.crewai.com/).  
O projeto foi desenvolvido com foco em modularidade, automação e fácil execução, sendo ideal para estudo e demonstração de uso prático de agentes LLM em tarefas colaborativas.

---

## ✨ Funcionalidades

- ✅ Geração de artigos em português com base em tópicos da Wikipedia
- 🤖 Arquitetura multiagente com:
  - **Pesquisador**: busca conteúdo
  - **Redator**: gera os parágrafos
  - **Revisor**: melhora e valida o texto
- 🌐 API em Flask com endpoint simples
- 🧠 Integração com LLMs via Groq
- 📦 Instalação e execução automáticas por script (`.bat` ou `.sh`)
- 📝 Retorno formatado em JSON com título, tópicos, conteúdo e referências

---

## 🛠️ Pré-requisitos

- Python 3.10 ou superior instalado  
- Git (opcional, mas recomendado)

---

## 🚀 Instalação e Execução

### 🔁 Método Automático (Recomendado)

#### 🪟 **Windows**

1. **Clique duas vezes no `start.bat`**  
   ou execute no terminal:

   ```bash
   start.bat
   ```

#### 🐧 **Linux / MacOS**

1. Dê permissão de execução:

   ```bash
   chmod +x start.sh
   ```

2. Execute:

   ```bash
   ./start.sh
   ```

---

### 🧩 O que os scripts fazem?

- Criam ambiente virtual `.venv`
- Ativam o ambiente
- Instalam todas as dependências (`requirements.txt`)
- Executam o `main.py` com a API Flask

---

### 🔧 Instalação Manual (Alternativa)

```bash
# Clone o repositório (se aplicável)
git clone https://github.com/dyoussef11/crewai-artigo-wiki-generator.git
cd crewai-artigo-wiki-generator

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
.venv\Scripts\activate        # Windows
cd crewai_artigo_wiki_generator/src/crewai_artigo_wiki_generator
# Instale as dependências
pip install -r requirements.txt


### 🔧 Instalação Manual (Alternativa)

```bash
# Clone o repositório (se aplicável)
git clone https://github.com/dyoussef11/crewai-artigo-wiki-generator.git
cd crewai-artigo-wiki-generator

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
.venv\Scripts\activate        # Windows
cd crewai_artigo_wiki_generator
# Instale as dependências
pip install -r requirements.txt


# Execute o projeto
python src/crewai_artigo_wiki_generator/main.py
```

---

## 🧪 Como usar a API

O servidor Flask ficará disponível em:

```
http://localhost:5000
```

### 🔍 Endpoint

```
GET /generate_article
```

#### Parâmetro necessário:

- `topic`: Nome do tópico desejado

#### Exemplo de requisição:

```
http://localhost:5000/generate_article?topic=Inteligência%20Artificial
```

#### Resposta (JSON):

```json
{
  "titulo": "A Ascensão da Inteligência Artificial",
  "topico": "Inteligência Artificial",
  "data_criacao": "2025-04-18",
  "autor": "Agente IA",
  "paragrafos": [
    "Parágrafo 1...",
    "Parágrafo 2..."
  ],
  "referencias": [
    "https://pt.wikipedia.org/wiki/Intelig%C3%AAncia_artificial"
  ]
}
```

---

## 🗂️ Estrutura do Projeto

```
crewai-artigo-wiki-generator/
├── start.bat                      # Script de inicialização para Windows
├── start.sh                       # Script de inicialização para Linux/macOS
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação
└── src/
    └── crewai_artigo_wiki_generator/
        ├── config/                # Configurações gerais
        ├── models/                # Modelos de dados com Pydantic
        ├── tools/                 # Ferramentas de manipulação e scraping
        ├── crew.py                # Definição dos agentes e fluxo
        └── main.py                # Execução da aplicação Flask
```

---

## 🧰 Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Flask](https://flask.palletsprojects.com/)
- [spaCy](https://spacy.io/)
- [Wikipedia API](https://pypi.org/project/wikipedia/)
- [Pydantic](https://docs.pydantic.dev/)

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

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

