import subprocess
import sys
import os
import shlex

def create_virtualenv(project_path):
    venv_path = os.path.join(project_path, '.venv')
    if not os.path.exists(venv_path):
        print("Criando o ambiente virtual...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    else:
        print("Ambiente virtual já existe.")

def install_requirements(project_path):
    requirements_path = os.path.join(project_path, 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        print("O arquivo requirements.txt não foi encontrado!")
        return

    print("Instalando dependências a partir do requirements.txt...")

    python_path = os.path.join(project_path, '.venv', 'Scripts', 'python.exe')
    subprocess.check_call([
        python_path, "-m", "pip", "install", "-r", requirements_path
    ])

def main():
    project_path = os.path.abspath(os.path.dirname(__file__))
    create_virtualenv(project_path)
    install_requirements(project_path)
    print("Tudo pronto! Ambiente configurado com sucesso.")

if __name__ == "__main__":
    main()
