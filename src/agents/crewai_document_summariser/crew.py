from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
# from crewai_tools import RagTool
from src.agent_tools.astra_db_ragging_tool import AstradbVectorSearchTool
from crewai_tools import WebsiteSearchTool



@CrewBase
class ResearchPaperSummariserCrew():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, document_url):
        # self.rag_tool = RagTool()
        # self.rag_tool.add(data_type="web_page",url=document_url)
        self.astra_rag_tool = AstradbVectorSearchTool( collection_name="document_summariser")
        self.website_search_tool = WebsiteSearchTool(
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="ollama/gemma3:4b-it-qat",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google", # or openai, ollama, ...
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
 
    @agent
    def summariser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Research_paper_summariser_agent"],
            tools=[],
            allow_delegation=False,
            verbose=True,
        )
    
    @task
    def summariser_task(self) -> Task:
        """
        Create a task for the schema agent
        """
        return Task(
            config=self.tasks_config["Research_paper_summariser_task"],
            agent=self.summariser_agent(),
            tools= [self.astra_rag_tool, self.website_search_tool],
        )
    
    @crew
    def crew(self) -> Crew:
        """

        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )   
    
    