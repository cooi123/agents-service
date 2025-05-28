from pydantic import BaseModel, Field

class ResearchPaperToScriptInputModel(BaseModel):
    """Input schema for the Document Summariser."""
    document_url: str = Field(
        ..., description="The document URL or the path to be summarised, This can usually be find on the document url field of the request") 
    area_of_research: str = Field(
        None, description="The area of research to be used for vector search. This can usually be find on the area of research field of the request")
    paper_title: str = Field(
        None, description="The title of the research paper")
    # abstract: str = Field(
    #     None, description="The abstract of the research paper")
    paper_content: str = Field(
        None, description="The content of the research paper")
    