@echo off
REM Verificar se o ambiente virtual já existe
IF NOT EXIST .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
) ELSE (
    echo Ambiente virtual já existe.
)

REM Ativar o ambiente virtual
call .venv\Scripts\activate

REM Verificar se o ambiente virtual foi ativado corretamente
IF NOT DEFINED VIRTUAL_ENV (
    echo Falha ao ativar o ambiente virtual.
    pause
    exit /b 1
)

REM Instalar dependências
IF EXIST requirements.txt (
    echo Instalando dependências...
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    echo Arquivo requirements.txt não encontrado.
    pause
    exit /b 1
)

REM Solicitar ao usuário o tópico
set /p TOPICO=Digite o tópico para o artigo:

REM Verificar se o tópico foi fornecido
IF "%TOPICO%"=="" (
    echo Tópico não fornecido. Encerrando o processo.
    pause
    exit /b 1
)

REM Rodar a aplicação principal em segundo plano
echo Iniciando a aplicação Flask com o tópico: "%TOPICO%"
python crewai_artigo_wiki_generator/src/crewai_artigo_wiki_generator/main.py "%TOPICO%" &

REM Esperar alguns segundos para garantir que o Flask esteja rodando
echo Aguardando 5 segundos para o Flask iniciar...
timeout /t 5

REM URL do servidor Flask
set URL=http://127.0.0.1:5000/generate_article?topic=%TOPICO%

REM Testar se o Flask está acessível
echo Verificando se o servidor Flask está acessível...
curl -s --head "%URL%" | find "200 OK" > nul

IF %ERRORLEVEL% NEQ 0 (
    echo Erro ao conectar ao servidor Flask. Certifique-se de que o Flask está em execução na porta 5000.
    pause
    exit /b 1
)

REM Fazer a requisição GET para o servidor Flask
echo Enviando requisição GET para gerar o artigo...
curl -X GET "%URL%"

REM Manter o terminal aberto para visualização
pause