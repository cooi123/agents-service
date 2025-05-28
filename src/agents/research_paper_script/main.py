import sys
from src.agents.research_paper_script.crew import ResearchPaperToScriptCrew
from src.agents.research_paper_script.models.research_script_input import ResearchPaperToScriptInputModel

def run(inputs:ResearchPaperToScriptInputModel,collection_name:str, **kwargs):
    
    result = ResearchPaperToScriptCrew(document_collection_name=collection_name).crew().kickoff(inputs=inputs.model_dump())   
    
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
    import os
    load_dotenv()
    # astra_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    # astra_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    # database =initialize_astra_client(
    #     astra_api_endpoint=astra_api_endpoint,
    #     astra_token=astra_token,
    #     astra_namespace="test"  # Replace with your namespace
    # )
    # collection_name = "temp2"  # Replace with your collection name
    # collection = create_astra_collection(
    #     collection_name="test_collection",
    #     database=database
    # )
    from src.utils.file_processsing import get_file_from_url, chuncker
    loaded_docs = get_file_from_url("https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf")
    print("Loaded documents:", loaded_docs)
    # Convert loaded documents to string by joining their page content
    docs = "\n".join([doc.page_content for doc in loaded_docs])
    print("Document content:", docs[:500], "...")  # Print first 500 chars to verify
    # chunks = chuncker(docs, chunk_size=500, chunk_overlap=100)
    # upload_documents_to_astra(
    #         documents=chunks,
    #         collection=collection
    #     )

    inputs = ResearchPaperToScriptInputModel(
        document_url="https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf",
        area_of_research="AI",
        paper_title="Attention is all you need",    
#         abstract = """The dominant sequence transduction models are based on complex recurrent or
# convolutional neural networks that include an encoder and a decoder. The best
# performing models also connect the encoder and decoder through an attention
# mechanism. We propose a new simple network architecture, the Transformer,
# based solely on attention mechanisms, dispensing with recurrence and convolutions
# entirely. Experiments on two machine translation tasks show these models to
# be superior in quality while being more parallelizable and requiring significantly
# less time to train. Our model achieves 28.4 BLEU on the WMT 2014 Englishto-German translation task, improving over the existing best results, including
# ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task,
# our model establishes a new single-model state-of-the-art BLEU score of 41.0 after
# training for 3.5 days on eight GPUs, a small fraction of the training costs of the
# best models from the literature. """
        paper_content = docs
        # abstract
    )
    run(inputs)