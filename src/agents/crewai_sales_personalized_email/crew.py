from crewai_tools import ScrapeWebsiteTool, SerperDevTool, DirectoryReadTool, FileReadTool

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .models import PersonalizedEmail



@CrewBase
class SalesPersonalizedEmailCrew:
    """SalesPersonalizedEmail crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    @agent
    def information_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["information_extractor"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )

    @agent
    def prospect_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["prospect_researcher"],
            tools=[SerperDevTool(country="Australia"), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )

    @agent
    def product_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["product_expert"],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )
    
    @agent
    def content_personalizer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_personalizer"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )

    @agent
    def email_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config["email_copywriter"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )
    
    @agent
    def email_editor(self) -> Agent:
        return Agent(
            config=self.agents_config["email_editor"],
            tools=[],
            allow_delegation=False,
            verbose=True,
            memory = True,
        )
    
    @task
    def information_extractor_task(self) -> Task:
        return Task(
            config=self.tasks_config["information_extractor_task"],
            agent=self.information_extractor(),
        )

    @task
    def research_prospect_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_prospect_task"],
            agent=self.prospect_researcher(),
        )
    @task
    def research_product_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_product_task"],
            agent=self.product_expert(),
        )
    
    @task
    def personalize_content_task(self) -> Task:
        return Task(
            config=self.tasks_config["personalize_content_task"],
            agent=self.content_personalizer(),
        )

    @task
    def write_email_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_email_task"],
            agent=self.email_copywriter(),
        )
    
    @task
    def email_editor_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_email_task"],
            agent=self.email_editor(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SalesPersonalizedEmail crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_llm="gemini/gemini-2.0-flash",
            planning= True,
            planning_llm="gemini/gemini-2.0-flash",
      
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
