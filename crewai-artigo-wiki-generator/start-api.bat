@echo off
SETLOCAL EnableDelayedExpansion

:: Configuração de cores (mantida igual)
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "DEL=%%a"
)
set "RED=%DEL%[91m"
set "GREEN=%DEL%[92m"
set "YELLOW=%DEL%[93m"
set "BLUE=%DEL%[94m"
set "RESET=%DEL%[0m"

:: Verificação do Python (mantida igual)
python --version >nul 2>&1 || (
    echo %RED%Python not found in PATH%RESET%
    pause
    exit /b 1
)

:: Configuração do ambiente virtual (mantida igual)
if not exist ".venv" (
    echo %GREEN%Creating virtual environment...%RESET%
    python -m venv .venv || (
        echo %RED%Failed to create virtual environment%RESET%
        pause
        exit /b 1
    )
)

echo %YELLOW%Activating virtual environment...%RESET%
call .venv\Scripts\activate || (
    echo %RED%Failed to activate virtual environment%RESET%
    pause
    exit /b 1
)

:: Instalação de dependências (mantida igual)
if exist "requirements.txt" (
    echo %GREEN%Installing dependencies...%RESET%
    pip install --upgrade pip && pip install -r requirements.txt || (
        echo %RED%Failed to install dependencies%RESET%
        pause
        exit /b 1
    )
)

:: Obter tópico do usuário (mantido igual)
:GET_TOPIC
echo.
set /p "TOPIC=Digite o tópico para o artigo: "
if "!TOPIC!"=="" (
    echo %RED%O tópico não pode estar vazio!%RESET%
    goto GET_TOPIC
)

:: Iniciar servidor Flask (mantido igual)
echo %YELLOW%Iniciando servidor Flask...%RESET%
start "Flask Server" cmd /c python crewai-artigo-wiki-generator\crewai_artigo_wiki_generator\src\crewai_artigo_wiki_generator\main.py

:: Esperar inicialização (mantido igual)
echo %YELLOW%Aguardando inicialização do servidor...%RESET%
timeout /t 10 >nul

:: Gerar nome de arquivo limpo
set "CLEAN_TOPIC=!TOPIC:/=!"
set "CLEAN_TOPIC=!CLEAN_TOPIC:\=!"
set "CLEAN_TOPIC=!CLEAN_TOPIC::=!"
set "CLEAN_TOPIC=!CLEAN_TOPIC:?=!"
set "CLEAN_TOPIC=!CLEAN_TOPIC:&=!"
set "BASE_FILENAME=artigo_!CLEAN_TOPIC:~0,50!"

:: Fazer requisição e salvar JSON
echo %GREEN%Gerando artigo...%RESET%
curl -X GET "http://127.0.0.1:5000/generate_article?topic=!TOPIC!" ^
     -H "Accept: application/json; charset=utf-8" ^
     -o "!BASE_FILENAME!.json" || (
    echo %RED%Falha ao gerar artigo%RESET%
    pause
    exit /b 1
)

:: Verificar se o JSON foi criado
if not exist "!BASE_FILENAME!.json" (
    echo %RED%Arquivo JSON não foi criado corretamente%RESET%
    pause
    exit /b 1
)

:: Criar script Python temporário para conversão
set "PY_SCRIPT=temp_md_converter.py"
(
echo import json
echo import sys
echo 
echo try:
echo     with open('!BASE_FILENAME!.json', 'r', encoding='utf-8') as f:
echo         data = json.load(f)
echo     
echo     md_content = f'# {data.get("titulo", "Artigo")}\n\n'
echo     md_content += f'**Tópico:** {data.get("topico", "")}\n'
echo     md_content += f'**Data de criação:** {data.get("data_criacao", "")}\n'
echo     md_content += f'**Autor:** {data.get("autor", "")}\n\n'
echo     
echo     for p in data.get("paragrafos", []):
echo         md_content += f'## {p.get("titulo", "")}\n\n{p.get("conteudo", "")}\n\n'
echo     
echo     md_content += '## Referências\n\n'
echo     for ref in data.get("referencias", []):
echo         md_content += f'- {ref}\n'
echo     
echo     with open('!BASE_FILENAME!.md', 'w', encoding='utf-8') as f:
echo         f.write(md_content)
echo     print("Arquivo Markdown criado com sucesso")
echo except Exception as e:
echo     print(f"Erro ao converter para Markdown: {str(e)}")
echo     sys.exit(1)
) > "!PY_SCRIPT!"

:: Executar conversão
echo %YELLOW%Convertendo para Markdown...%RESET%
python "!PY_SCRIPT!" || (
    echo %RED%Falha na conversão para Markdown%RESET%
    del "!PY_SCRIPT!"
    pause
    exit /b 1
)

:: Limpar script temporário
del "!PY_SCRIPT!"

:: Verificar se o MD foi criado
if not exist "!BASE_FILENAME!.md" (
    echo %RED%Arquivo Markdown não foi criado%RESET%
    pause
    exit /b 1
)

echo %GREEN%Artigo gerado com sucesso!%RESET%
echo %YELLOW%Arquivos salvos como:
echo - !BASE_FILENAME!.json (dados estruturados)
echo - !BASE_FILENAME!.md (formato Markdown)%RESET%

:: Abrir ambos arquivos
start "" "!BASE_FILENAME!.json"
start "" "!BASE_FILENAME!.md"

echo.
pause