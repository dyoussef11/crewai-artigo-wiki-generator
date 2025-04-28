from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from tools.wikipedia_tool import WikipediaTool
from models.article_model import Artigo
from crewai.tasks import TaskOutput

import re

def validate_topic_and_interrupt(topic: str) -> None:
    """
    Valida o tópico e interrompe o processo se for considerado inválido.
    
    Args:
        topic: O tópico a ser validado
        
    Raises:
        ValueError: Se o tópico for considerado inválido
    
    Validações incluídas:
    - Não vazio e é string
    - Tamanho mínimo (3 caracteres)
    - Não apenas números
    - Padrões repetitivos (como "awdawdawd")
    - Não apenas caracteres especiais
    - Permite siglas (mais de 1 letra em maiúsculas)
    """
    # Validação básica
    if not topic or not isinstance(topic, str):
        raise ValueError("Tópico não pode ser vazio ou não-string")
    
    stripped_topic = topic.strip()
    
    if len(stripped_topic) < 2:
        raise ValueError("Tópico muito curto (mínimo 2 caracteres)")
    
    if stripped_topic.isdigit():
        raise ValueError("Tópico não pode conter apenas números")
    
    # Verifica se é apenas caracteres especiais/repetitivos
    if re.fullmatch(r'[\W_]+', stripped_topic):
        raise ValueError("Tópico não pode conter apenas caracteres especiais")
    
    # Detecta padrões repetitivos (como "abcabcabc" ou "aaaaaa")
    if len(stripped_topic) > 5:  # Só aplica para tópicos maiores
        # Verifica sequências repetidas
        if re.search(r'(.+)\1+', stripped_topic.lower()):
            raise ValueError("Tópico contém padrões repetitivos sem sentido")
        
        # Verifica muitas letras repetidas
        if any(char * 4 in stripped_topic.lower() for char in stripped_topic.lower()):
            raise ValueError("Tópico contém muitas repetições de caracteres")
    
    # Verifica se é uma sigla válida (mais de 1 letra maiúscula, sem números)
    if stripped_topic.isupper() and len(stripped_topic) > 1 and stripped_topic.isalpha():
        return  # Siglas válidas são aceitas
    
    # Verifica se tem pelo menos 2 letras diferentes
    unique_chars = set(stripped_topic.lower())
    if len(unique_chars) < 2 and len(stripped_topic) >= 5:
        raise ValueError("Tópico contém pouca variação de caracteres")


@CrewBase
class CrewaiArtigoWikiGenerator:
    """
    Classe principal que configura e executa a crew de geração de artigos a partir da Wikipedia
    utilizando agentes definidos com CrewAI.

    Esta classe define os agentes, tarefas e ferramentas envolvidas no processo, com base em arquivos de configuração YAML.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        self.topico = None  # Inicializa como None

    def set_topic(self, topic:str):
        
        """Define e valida o tópico antes de usar"""
        validate_topic_and_interrupt(topic)
        self.topico = topic
    @tool
    def wikipedia_tool(self):
        """
        Inicializa a ferramenta personalizada de busca na Wikipedia.

        Returns:
            WikipediaTool: Instância da ferramenta personalizada.
        """
        print("Initializing Wikipedia Tool")
        return WikipediaTool()

    @agent
    def researcher(self) -> Agent:
        """
        Agente responsável por pesquisar informações no tópico desejado.

        Returns:
            Agent: Agente configurado com acesso à Wikipedia.
        """
        return Agent(
            config=self.agents_config['researcher'],
            tools=[WikipediaTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=10,
            memory=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        """
        Agente responsável por redigir um rascunho do artigo com base nas informações pesquisadas.

        Returns:
            Agent: Agente configurado sem ferramentas externas.
        """
        return Agent(
            config=self.agents_config['reporting_analyst'],
            allow_delegation=False,
            verbose=True
        )

    @agent
    def reviewer(self) -> Agent:
        """
        Agente responsável por revisar o artigo preliminar e gerar o conteúdo final estruturado.

        Returns:
            Agent: Agente configurado para revisão.
        """
        return Agent(
            config=self.agents_config['reviewer'],
            allow_delegation=False,
            verbose=False
        )

    @task
    def research_task(self) -> Task:
        def validate_result(result: str) -> TaskOutput:
            if "não encontrado" in result.lower() or "falha" in result.lower() or "erro" in result.lower():
                raise f"Pesquisa falhou: {result}"
            return TaskOutput(output=result)

        return Task(
            config=self.tasks_config['research_task'],
            tools=[WikipediaTool()],
            allow_delegation=False,
            output_parser=validate_result,  # aqui está o pulo do gato!
        )

    @task
    def reporting_task(self) -> Task:
        """
        Tarefa de criação do rascunho do artigo.

        Returns:
            Task: Tarefa configurada com arquivo de saída preliminar.
        """
        return Task(
            config=self.tasks_config['reporting_task'],
            
        )

    @task
    def review_task(self) -> Task:
        """
        Tarefa de revisão e estruturação do artigo final.

        Returns:
            Task: Tarefa configurada com modelo Pydantic e arquivo final.
        """
        return Task(
            config=self.tasks_config['review_task'],
            output_pydantic=Artigo,
           
        )

    @crew
    def crew(self) -> Crew:
        """
        Instancia e retorna a crew composta pelos agentes e tarefas definidos.

        Returns:
            Crew: A crew completa pronta para execução.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            output_pydantic=Artigo,
            verbose=True,
        )

    
   
