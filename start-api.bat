@echo off
SETLOCAL EnableDelayedExpansion

:: ============================================================
:: Cores ANSI
:: ============================================================
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "DEL=%%a"
)
set "RED=%DEL%[91m"
set "GREEN=%DEL%[92m"
set "YELLOW=%DEL%[93m"
set "RESET=%DEL%[0m"

:: ============================================================
:: Verificações iniciais
:: ============================================================
where uv >nul 2>&1 || (
    echo %RED%uv nao encontrado. Instale: https://docs.astral.sh/uv/%RESET%
    pause
    exit /b 1
)

if not exist "%~dp0crewai_generator_wiki_article\pyproject.toml" (
    echo %RED%Projeto nao encontrado em: %~dp0crewai_generator_wiki_article%RESET%
    pause
    exit /b 1
)

:: ============================================================
:: Sincroniza dependências
:: ============================================================
echo %GREEN%Sincronizando dependencias com uv...%RESET%
pushd "%~dp0crewai_generator_wiki_article"
uv sync --extra dev || (
    echo %RED%Falha ao sincronizar dependencias%RESET%
    popd
    pause
    exit /b 1
)

:: ============================================================
:: Solicita e valida o tópico
:: ============================================================
:GET_TOPIC
echo.
set /p "TOPIC=Digite o topico para o artigo: "
uv run --quiet python -c "import sys; t=sys.argv[1].strip(); exit(1) if not t or len(t)<3 or t.isdigit() or all(not c.isalnum() for c in t) else exit(0)" "!TOPIC!" || (
    echo %RED%Topico invalido! Use ao menos 3 caracteres alfanumericos.%RESET%
    goto GET_TOPIC
)

:: ============================================================
:: Normaliza o nome do arquivo (via sanitize.py)
:: ============================================================
set "CLEAN_TOPIC="
set "TMP_SANITIZE=%TEMP%\crewai_sanitize_%RANDOM%%RANDOM%.txt"

uv run --quiet python "%~dp0sanitize.py" "!TOPIC!" > "!TMP_SANITIZE!" 2>nul

if exist "!TMP_SANITIZE!" (
    set /p CLEAN_TOPIC=<"!TMP_SANITIZE!"
    del "!TMP_SANITIZE!" >nul 2>&1
)
if "!CLEAN_TOPIC!"=="" set "CLEAN_TOPIC=artigo"

if /i "!CLEAN_TOPIC!"=="artigo" (
    set "BASE_FILENAME=artigo"
) else (
    set "BASE_FILENAME=artigo_!CLEAN_TOPIC!"
)

:: ============================================================
:: Prepara diretórios de saída
:: ============================================================
set "OUTPUT_DIR_JSON=%~dp0artigos-gerados\json"
set "OUTPUT_DIR_MD=%~dp0artigos-gerados\edicao-final"
if not exist "!OUTPUT_DIR_JSON!" mkdir "!OUTPUT_DIR_JSON!"
if not exist "!OUTPUT_DIR_MD!"   mkdir "!OUTPUT_DIR_MD!"

set "OUTPUT_JSON=!OUTPUT_DIR_JSON!\!BASE_FILENAME!.json"
set "OUTPUT_MD=!OUTPUT_DIR_MD!\!BASE_FILENAME!.md"

:: ============================================================
:: Executa o crew
:: ============================================================
echo.
echo %GREEN%Gerando artigo sobre "!TOPIC!"...%RESET%
echo %YELLOW%JSON:     !OUTPUT_JSON!%RESET%
echo %YELLOW%Markdown: !OUTPUT_MD!%RESET%
echo.

uv run python src\crewai_generator_wiki_article\main.py "!TOPIC!" --output "!OUTPUT_JSON!" --output-md "!OUTPUT_MD!"
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
    echo.
    echo %RED%Falha ao gerar o artigo. Veja os logs acima.%RESET%
    pause
    exit /b 1
)

if not exist "!OUTPUT_JSON!" (
    echo %RED%Arquivo JSON nao foi criado: !OUTPUT_JSON!%RESET%
    pause
    exit /b 1
)

if not exist "!OUTPUT_MD!" (
    echo %RED%Arquivo Markdown nao foi criado: !OUTPUT_MD!%RESET%
    pause
    exit /b 1
)

:: ============================================================
:: Resultado
:: ============================================================
echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%  Artigo gerado com sucesso!%RESET%
echo %GREEN%============================================================%RESET%
echo   JSON:     !OUTPUT_JSON!
echo   Markdown: !OUTPUT_MD!
echo %GREEN%============================================================%RESET%
echo.

start "" "!OUTPUT_JSON!"
start "" "!OUTPUT_MD!"

echo %YELLOW%Os dois arquivos foram abertos. Pressione qualquer tecla para sair.%RESET%
pause >nul
endlocal