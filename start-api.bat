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
    pip install -r requirements.txt || (
        echo %RED%Failed to install dependencies%RESET%
        pause
        exit /b 1
    )
)

:GET_TOPIC
echo.
set /p "TOPIC=Digite o tópico para o artigo: "
python -c "import sys; t=sys.argv[1].strip(); exit(1) if not t or len(t)<3 or t.isdigit() or all(not c.isalnum() for c in t) else exit(0)" "!TOPIC!" || (
    echo %RED%Tópico inválido! Por favor, insira um tópico significativo.%RESET%
    goto GET_TOPIC
)




:: Normalizar o tópico para URL e nome de arquivo
echo %YELLOW%Normalizando tópico...%RESET%
set "ENCODED_TOPIC="
set "CLEAN_FILENAME="

:: Usar Python para processamento mais robusto
for /f "tokens=*" %%i in ('python -c "import urllib.parse, re; topic=r'!TOPIC!'; encoded=urllib.parse.quote(topic); clean=re.sub(r'[^\w\-_]', '_', topic); print(f'{encoded}|{clean[:50]}')"') do (
    for /f "tokens=1,2 delims=|" %%a in ("%%i") do (
        set "ENCODED_TOPIC=%%a"
        set "CLEAN_FILENAME=%%b"
    )
)

:: Verificar se a normalização funcionou
if "!ENCODED_TOPIC!"=="" (
    echo %RED%Falha ao normalizar o tópico!%RESET%
    goto GET_TOPIC
)

:: Iniciar servidor Flask (mantido igual)
echo %YELLOW%Iniciando servidor Flask...%RESET%
start "Flask Server" cmd /c python crewai_artigo_wiki_generator\src\crewai_artigo_wiki_generator\main.py

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

echo %GREEN%Gerando artigo...%RESET%

:: Mostrar o comando curl que será executado
echo Comando curl que será executado:
echo curl -X GET "http://127.0.0.1:5000/generate_article?topic=!ENCODED_TOPIC!" ^
     -H "Accept: application/json; charset=utf-8" ^
     -o "artigos-gerados/!BASE_FILENAME!.json"
echo.

:: Executar o comando curl
curl -X GET "http://127.0.0.1:5000/generate_article?topic=!ENCODED_TOPIC!" ^
     -H "Accept: application/json; charset=utf-8" ^
     -o "artigos-gerados/json/!BASE_FILENAME!.json" || (
    echo %RED%Falha ao gerar artigo%RESET%
    pause
    exit /b 1
)

:: Verificar se o JSON foi criado
if not exist "artigos-gerados/json/!BASE_FILENAME!.json" (
    echo %RED%Arquivo JSON não foi criado corretamente%RESET%
    pause
    exit /b 1
)




echo - artigos-gerados/json/!BASE_FILENAME!.json (dados estruturados)

:: Abrir ambos arquivos
start "" "artigos-gerados/json/!BASE_FILENAME!.json"


echo.
pause