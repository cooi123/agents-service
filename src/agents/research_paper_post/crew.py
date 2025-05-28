from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from src.agent_tools.astra_db_ragging_tool import AstradbVectorSearchTool
from crewai_tools import SerperDevTool

@CrewBase
class ResearchPaperToPostCrew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, document_collection_name: str):
        self.astra_rag_tool = AstradbVectorSearchTool( collection_name=document_collection_name)
        self.serper_dev_tool = SerperDevTool()
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
        )

 
    @agent
    def research_paper_summariser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Research_paper_summarize_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )
    
    @agent
    def analogy_explainer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Analogy_explainer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )
    
    @agent
    def linkedin_post_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Linkedin_post_writer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )
    
    @task
    def research_paper_summariser_task(self) -> Task:
        return Task(
            config=self.tasks_config["Research_paper_summariser_task"],
            agent=self.research_paper_summariser_agent(),
            tools=[self.astra_rag_tool],
            llm=self.llm,
        )
    
    @task
    def analogy_explainer_task(self) -> Task:
        return Task(
            config=self.tasks_config["Analogy_explainer_task"],
            agent=self.analogy_explainer_agent(),
            tools=[self.astra_rag_tool],
            llm=self.llm,
        )
    
    @task
    def linkedin_post_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config["Linkedin_post_writer_task"],
            agent=self.linkedin_post_writer_agent(),
            tools=[self.astra_rag_tool, self.serper_dev_tool],
            llm=self.llm,
        )
    
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        ) 
    
    
    
    