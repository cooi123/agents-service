import sys
from src.agents.research_paper_post.crew import ResearchPaperToPostCrew
from src.agents.research_paper_post.models.research_post_input import ResearchPaperToPostInputModel



def runResearchPaperToPostAgent(inputs:ResearchPaperToPostInputModel, collection_name:str, **kwargs):
    result = ResearchPaperToPostCrew(document_collection_name=collection_name).crew().kickoff(inputs=inputs.model_dump())   
    return result


##tldr format for linked ( summarizing linked)
## podcast with speech 

if __name__ == "__main__":
    print("Starting")
    print("creating collection")
    # Example usage
    from dotenv import load_dotenv
    from src.utils.astradb_utils import initialize_astra_client, create_astra_collection, search_astra_collection, upload_documents_to_astra
    from src.utils.shared import generate_collection_name
    from src.utils.file_processsing import extract_metadata_from_docs
    import os
    load_dotenv()
    astra_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    astra_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    database = initialize_astra_client(
        astra_api_endpoint=astra_api_endpoint,
        astra_token=astra_token,
        astra_namespace="test"  # Replace with your namespace
    )
    collection_name = "temp2"  # Replace with your collection name
    collection = create_astra_collection(
        collection_name=collection_name,
        database=database
    )
    from src.utils.file_processsing import get_file_from_url, chuncker
    loaded_docs = get_file_from_url("https://lzmyefwwdwxaophnzjgf.supabase.co/storage/v1/object/sign/documents/71764662-e421-4c10-aeff-34bf432d657a/1748413699106-2505.20397v1.pdf?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InN0b3JhZ2UtdXJsLXNpZ25pbmcta2V5XzIyNTJjNTBhLTJlYzgtNGM4ZS04NzdhLTJhN2RlMThiODQ0NyJ9.eyJ1cmwiOiJkb2N1bWVudHMvNzE3NjQ2NjItZTQyMS00YzEwLWFlZmYtMzRiZjQzMmQ2NTdhLzE3NDg0MTM2OTkxMDYtMjUwNS4yMDM5N3YxLnBkZiIsImlhdCI6MTc0ODQxNjY3OSwiZXhwIjoxNzc5OTUyNjc5fQ.u_NKcc4PO0khJScrIivXeCfHxCIK4JBWw-_Qn_o7p6k")
    # Extract metadata from the document
    metadata = extract_metadata_from_docs(loaded_docs)
    print("Extracted metadata:", metadata)
    
    # Combine all page content
    docs = "\n".join([doc.page_content for doc in loaded_docs])
    print(docs[:10000])
    
    # chunks = chuncker(loaded_docs, chunk_size=500, chunk_overlap=100)
    # upload_documents_to_astra(
    #     documents=chunks,
    #     collection=collection
    # )

    # inputs = ResearchPaperToPostInputModel(
    #     document_url="https://arxiv.org/pdf/2505.20397",
    #     area_of_research="AI",
    #     paper_title=metadata.get('title', 'Attention is all you need'),
    #     paper_content=docs[:500],
    #     abstract=metadata.get('abstract', '')
    # )
    # runResearchPaperToPostAgent(inputs, collection_name)