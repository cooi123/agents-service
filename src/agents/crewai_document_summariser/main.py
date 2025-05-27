import sys
from src.agents.crewai_document_summariser.crew import ResearchPaperSummariserCrew
from src.agents.crewai_document_summariser.models.document_summariser_input import DocumentSummariserInputModel

def runSummarizerAgent(inputs:DocumentSummariserInputModel, **kwargs):
    
    print("Starting")
    result = ResearchPaperSummariserCrew(inputs.document).crew().kickoff(inputs=inputs.model_dump())
    return result
