from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from tools.wikipedia_tool import WikipediaTool
from models.article_model import Artigo

@CrewBase
class CrewaiArtigoWikiGenerator:
    """
    Classe principal que configura e executa a crew de geração de artigos a partir da Wikipedia
    utilizando agentes definidos com CrewAI.

    Esta classe define os agentes, tarefas e ferramentas envolvidas no processo, com base em arquivos de configuração YAML.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

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
            max_iter=3,
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
            verbose=False
        )

    @task
    def research_task(self) -> Task:
        """
        Tarefa de pesquisa, utilizando o WikipediaTool.

        Returns:
            Task: Tarefa configurada para pesquisa inicial.
        """
        return Task(
            config=self.tasks_config['research_task'],
            tools=[WikipediaTool()],
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
            output_file='artigos-gerados/Versão_preliminar.md'
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
            output_file='artigos-gerados/Artigo_Final.md',
            additional_output_file='artigos-gerados/Artigo_ABNT.md'
        )

    @crew
    def crew(self) -> Crew:
        """
        Instancia e retorna a crew composta pelos agentes e tarefas definidos.

        Returns:
            Crew: A crew completa pronta para execução.
        """
        if self._is_valid_topic(" "):
            raise Exception("Tópico inválido, interrompendo o processo.")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            output_pydantic=Artigo,
            verbose=True,
        )

    def _is_valid_topic(self, topic: str) -> bool:
        """
        Verifica se o tópico fornecido é válido.

        Args:
            topic (str): Tópico a ser validado.

        Returns:
            bool: True se o tópico for válido, False caso contrário.
        """
        return topic.lower().strip() != ""
