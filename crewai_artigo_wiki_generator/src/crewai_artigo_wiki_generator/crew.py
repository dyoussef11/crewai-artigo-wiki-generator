from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from tools.wikipedia_tool import WikipediaTool
from models.article_model import Artigo


@CrewBase
class CrewaiArtigoWikiGenerator():
    """CrewaiArtigoWikiGenerator crew"""

    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @tool
    def wikipedia_tool(self):
        print("Initializing Wikipedia Tool")
        return WikipediaTool()
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[WikipediaTool()],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )
        
    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['reviewer'],
            verbose=False
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            tools=[WikipediaTool()],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )
    
    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            output_pydantic=Artigo,
            output_file='article_final.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewaiArtigoWikiGenerator crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        if not self._is_valid_topic("" or " "):  # Exemplo de condição de interrupção
            raise Exception("Tópico inválido, interrompendo o processo.")
        
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            output_pydantic=Artigo,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
        
    def _is_valid_topic(self, topic: str) -> bool:
            # Exemplo de verificação simples
            return topic.lower() != " "