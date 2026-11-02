from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, llm, task, tool

# --- Workaround para o bug do cache_breakpoint com Groq (crewAI#5886) ---
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
# ----------------------------------------------------------------------

from crewai_generator_wiki_article.models.article_model import Artigo
from crewai_generator_wiki_article.tools.wikipedia_tool import WikipediaTool


@CrewBase
class CrewaiGeneratorWikiArticle:
    """Crew de geração de artigos a partir da Wikipedia."""

    @llm
    def groq_llm(self) -> LLM:
        return LLM(
            model="groq/openai/gpt-oss-120b",  # Modelo ativo no free tier
            temperature=0.3,
        )
    @tool
    def wikipedia_tool(self):
        return WikipediaTool()

    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            allow_delegation=False,
            max_iter=15,   # era 10 — reduz o loop e a queima de RPM
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["reviewer"],  # type: ignore[index]
            verbose=False,
            allow_delegation=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])  # type: ignore[index]

    @task
    def reporting_task(self) -> Task:
        return Task(config=self.tasks_config["reporting_task"])  # type: ignore[index]

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10,  # Limite conservador para o free tier do Groq  
        )