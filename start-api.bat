@echo off
REM Criar ambiente virtual
python -m venv .venv

REM Ativar o ambiente virtual
call .venv\Scripts\activate

REM Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

REM Rodar a aplicação principal
python crewai_artigo_wiki_generator/src/crewai_artigo_wiki_generator/main.py

REM Manter o terminal aberto
cmd /k
