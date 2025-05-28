from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from src.agent_tools.astra_db_ragging_tool import AstradbVectorSearchTool
from crewai_tools import SerperDevTool
from src.utils.shared import generate_collection_name


@CrewBase
class ResearchPaperToScriptCrew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    collection_name = "research_paper_script"

    def __init__(self, document_collection_name: str):
        self.astra_rag_tool = AstradbVectorSearchTool( collection_name=document_collection_name)
        self.serper_dev_tool = SerperDevTool()
#         self.website_search_tool = WebsiteSearchTool(
#     config=dict(
#         llm=dict(
#             provider="ollama",
#             config=dict(
#                 model="ollama/gemma3:4b-it-qat",
#                 # temperature=0.5,
#                 # top_p=1,
#                 # stream=true,
#             ),
#         ),
#         embedder=dict(
#             provider="google", # or openai, ollama, ...
#             config=dict(
#                 model="models/embedding-001",
#                 task_type="retrieval_document",
#                 # title="Embeddings",
#             ),
#         ),
#     )
# )
 
    @agent
    def research_paper_summariser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Research_paper_summarize_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )
    
    @agent
    def analogy_explainer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Analogy_explainer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )
    
    @agent
    def narrative_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Narrative_writer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )
    
    @agent
    def script_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Script_writer_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )
    
    @task
    def research_paper_summariser_task(self) -> Task:
        return Task(
            config=self.tasks_config["Research_paper_summariser_task"],
            agent=self.research_paper_summariser_agent(),
            tools=[self.astra_rag_tool],
        )
    
    @task
    def analogy_explainer_task(self) -> Task:
        return Task(
            config=self.tasks_config["Analogy_explainer_task"],
            agent=self.analogy_explainer_agent(),
            tools=[self.astra_rag_tool],
        )
    
    @task
    def narrative_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config["Narrative_writer_task"],
            agent=self.narrative_writer_agent(),
            tools=[self.astra_rag_tool],
        )
    
    @task
    def script_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config["Script_writer_task"],
            agent=self.script_writer_agent(),
            tools=[self.astra_rag_tool, self.serper_dev_tool],
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        ) 
    
    
    
    