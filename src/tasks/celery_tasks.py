from celery import shared_task
from typing import Dict, Any, Optional, List, Callable, TypeVar, Generic, Type
import time
import psutil
from functools import wraps
from src.agents.crewai_document_summariser.models.document_summariser_input import DocumentSummariserInputModel
from src.agents.research_paper_script.main import runResearchPaperToScripAgent
from src.agents.research_paper_script.models.research_script_input import ResearchPaperToScriptInputModel  
from src.agents.research_paper_post.main import runResearchPaperToPostAgent
from src.agents.research_paper_post.models.research_post_input import ResearchPaperToPostInputModel
from src.utils.astradb_utils import initialize_astra_client, create_astra_collection, upload_documents_to_astra, delete_astra_collection
from src.utils.file_processsing import extract_metadata_from_docs
import os
from dotenv import load_dotenv
from src.utils.shared import generate_collection_name
load_dotenv()

from src.models.task_models import (
    TaskStatus, ResourceType, TaskType, TaskResult,
    CeleryTaskRequest, TokenUsage, ComputationalUsage
)
from src.models.base_models import TextInput
from src.agents import runAgentPrimer
from src.utils.shared import send_update_to_broker
from src.agents.crewai_document_summariser.main import runSummarizerAgent
from src.agents.crewai_document_summariser.models.document_summariser_input import DocumentSummariserInputModel
from src.agents.crewai_text_to_schema.main import runAgentTextToSchema
from src.utils.file_processsing import get_file_from_url, chuncker
from src.utils.astradb_utils import create_astra_collection, upload_documents_to_astra, astra_client
from src.utils.text_to_speech import text_to_speech

def track_usage_metrics(start_time: float, resource_type: ResourceType = ResourceType.LLM) -> ComputationalUsage:
    """Track usage metrics for a task"""
    end_time = time.time()
    runtime_ms = int((end_time - start_time) * 1000)
    
    # Get memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return ComputationalUsage(
        runtime_ms=runtime_ms,
        resources_used={
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "cpu_percent": process.cpu_percent()
        }
    )

def with_transaction_tracking(task_func: Callable[..., TaskResult]) -> Callable[..., TaskResult]:
    """
    Higher-order function to wrap agent tasks with consistent transaction handling.
    
    This wrapper ensures:
    1. Proper transaction creation
    2. Status updates at each stage
    3. Usage metrics tracking
    4. Error handling
    5. Parent task status synchronization
    6. Proper type handling for chaining
    """
    @wraps(task_func)
    def wrapper(self, request: Dict[str, Any], *args, **kwargs) -> TaskResult:
        start_time = time.time()
        task_id = None
        print("received request", request)
        try:
            # Parse and validate request
            task_request = CeleryTaskRequest(**request)
                        
            # Execute the actual task
            try:
                print("running task")
                send_update_to_broker(task_request=task_request, result=TaskResult(
                    task_status=TaskStatus.RUNNING,
                    parent_transaction_id=task_request.parent_transaction_id
                ))
                result: TaskResult = task_func(self, task_request, *args, **kwargs)
                print("result", result)
            except Exception as e:
                result = TaskResult(
                    task_status=TaskStatus.FAILED,
                    error_message=str(e),
                    parent_transaction_id=task_request.parent_transaction_id
                )
                send_update_to_broker(task_request=task_request, result=result)
                raise e
            
            # Track usage metrics
            computational_usage = track_usage_metrics(start_time)
            result.computational_usage = computational_usage
            send_update_to_broker(task_request=task_request, result=result)
            return result.model_dump()
            
        except Exception as e:
            if task_id:
                result = TaskResult(
                    task_status=TaskStatus.FAILED,
                    error_message=str(e),
                    parent_transaction_id=task_request.parent_transaction_id
                )
                send_update_to_broker(task_request=task_request, result=result)
                return result.model_dump()
            raise
            
    return wrapper

@shared_task(bind=True)
@with_transaction_tracking
def create_consultant_primer(self, task_request: CeleryTaskRequest) -> TaskResult:
    """Generate a comprehensive consultant primer based on the given topic.
    This task analyzes the topic and creates a detailed primer document with key insights,
    market analysis, and strategic recommendations.
    """
    print("task id", self.request.id)
    print("task request", task_request)
    
    # Run the primer agent
    agentOutput = runAgentPrimer(inputs={"topic": task_request.inputData.get("text","")})
    
    # Process output
    agentOutputDict = agentOutput.model_dump()
    raw_token_usage = agentOutputDict.get("token_usage", {})
    
    # Convert raw token usage to TokenUsage model
    token_usage = TokenUsage(
        tokens_total=raw_token_usage.get("total_tokens", 0),
        prompt_tokens=raw_token_usage.get("prompt_tokens", 0),
        completion_tokens=raw_token_usage.get("completion_tokens", 0),
        model_name="ollama/gemma3:4b-it-qat"  # Hardcoded since we know the model
    )
    
    result = agentOutputDict.get("raw", {})
    
    return TaskResult(
        task_status=TaskStatus.COMPLETED,
        result_payload={"unstructured_text": result},
        token_usage=token_usage,
        parent_transaction_id=task_request.parent_transaction_id
    )


@shared_task(bind=True)
@with_transaction_tracking
def create_research_paper_summary(self, task_request: CeleryTaskRequest) -> TaskResult:
    """Create a summary of a research paper"""
    print("task id", self.request.id)
    print("task request", task_request)
    
    # strcuted_input = runAgentTextToSchema(task_request.inputData.get("text", ""),DocumentSummariserInputModel )

    batch_size = 10
    results = []
    # print("strcuted_input", strcuted_input)
    # Generate a valid collection name
    print(f"Creating collection: {"document_summariser"}")
    collection = create_astra_collection(
        collection_name="document_summariser",
        database=astra_client)

    for i in range(0, len(task_request.documentUrls), batch_size):
        batch_urls = task_request.documentUrls[i:i + batch_size]
        batch_results = []
        for url in batch_urls:
            file = get_file_from_url(url)
            chunks = chuncker(file, chunk_size=500, chunk_overlap=100)
            batch_results.extend(chunks)   
        upload_documents_to_astra(
            documents=batch_results,
            collection = collection
        )

    insight = task_request.inputData.get("text", "provide a summary of the document")
    # Run the research paper summary agent
    agentOutput = runSummarizerAgent(DocumentSummariserInputModel(insight=insight, collection_name="document_summariser", document="document"))
    print("agentOutput", agentOutput.model_dump())
    return TaskResult(
        task_status=TaskStatus.COMPLETED,
        result_payload={"unstructured_text": agentOutput.model_dump().get("raw", "")},
        parent_transaction_id=task_request.parent_transaction_id
    )

@shared_task(bind=True)
@with_transaction_tracking
def create_research_paper_script(self, task_request: CeleryTaskRequest) -> TaskResult:
    """Create a script for a research paper"""
    if (len(task_request.documentUrls) == 0):
        return TaskResult(
            task_status=TaskStatus.FAILED,
            error_message="No document URLs provided",
            parent_transaction_id=task_request.parent_transaction_id
        )
    ##upload document to astra db
    loaded_doc = get_file_from_url(task_request.documentUrls[0])
    metadata = extract_metadata_from_docs(loaded_doc)
    doc = "\n".join([doc.page_content for doc in loaded_doc])
    astradb = initialize_astra_client(
        astra_api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        astra_token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        astra_namespace="test"
    )
    collection_name = generate_collection_name(project_id=task_request.projectId, service_id=task_request.serviceId, transaction_id=task_request.parent_transaction_id)  
    collection = create_astra_collection(
        collection_name=collection_name,
        database=astradb
    )
    chunks = chuncker(loaded_doc, chunk_size=500, chunk_overlap=100)
    upload_documents_to_astra(
        documents=chunks,
        collection=collection
    )
    inputs = ResearchPaperToScriptInputModel(
        document_url=task_request.documentUrls[0],
        area_of_research=task_request.inputData.get("text", ""),
        paper_title=metadata.get("title") or task_request.inputData.get("text", ""),
        paper_content=doc[:10000],
        abstract=metadata.get("abstract", "")
    )
    agentOutput = runResearchPaperToScripAgent(inputs,collection_name=collection_name)
    agentOutputDict = agentOutput.model_dump()
    raw_token_usage = agentOutputDict.get("token_usage", {})
    
    # Convert raw token usage to TokenUsage model
    token_usage = TokenUsage(
        tokens_total=raw_token_usage.get("total_tokens", 0),
        prompt_tokens=raw_token_usage.get("prompt_tokens", 0),
        completion_tokens=raw_token_usage.get("completion_tokens", 0),
        model_name="gemini-2.0-flash" 
    )
    
    result = agentOutputDict.get("raw", {})

    ##clean up the collection
    delete_astra_collection(collection_name=collection_name, database=astradb)
    #text to speech
    audio_url = text_to_speech(result, bucket_name="podcast-audio")

    return TaskResult(
        task_status=TaskStatus.COMPLETED,
        result_payload={"unstructured_text": result},
        result_document_urls=[audio_url],
        token_usage=token_usage,
        parent_transaction_id=task_request.parent_transaction_id
    )

@shared_task(bind=True)
@with_transaction_tracking
def create_research_paper_post(self, task_request: CeleryTaskRequest) -> TaskResult:
    """Create a post for a research paper"""
    print("task id", self.request.id)
    print("task request", task_request)

    ##upload document to astra db
    loaded_doc = get_file_from_url(task_request.documentUrls[0])
    metadata = extract_metadata_from_docs(loaded_doc)

    doc = "\n".join([doc.page_content for doc in loaded_doc])

    astradb = initialize_astra_client(
        astra_api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        astra_token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        astra_namespace="test"
    )
    collection_name = generate_collection_name(project_id=task_request.projectId, service_id=task_request.serviceId, transaction_id=task_request.parent_transaction_id)  
    collection = create_astra_collection(
        collection_name=collection_name,
        database=astradb
    )
    chunks = chuncker(loaded_doc, chunk_size=500, chunk_overlap=100)
    upload_documents_to_astra(
        documents=chunks,
        collection=collection
    )
    inputs = ResearchPaperToPostInputModel(
        document_url=task_request.documentUrls[0],
        area_of_research=task_request.inputData.get("text", ""),
        paper_title=metadata.get("title") or task_request.inputData.get("text", ""),     
        abstract=metadata.get("abstract", ""),
        paper_content=doc[:10000]
    )
    agentOutput = runResearchPaperToPostAgent(inputs,collection_name=collection_name)
    agentOutputDict = agentOutput.model_dump()
    raw_token_usage = agentOutputDict.get("token_usage", {})

    result = agentOutputDict.get("raw", {})

    token_usage = TokenUsage(
        tokens_total=raw_token_usage.get("total_tokens", 0),
        prompt_tokens=raw_token_usage.get("prompt_tokens", 0),
        completion_tokens=raw_token_usage.get("completion_tokens", 0),
        model_name="gemini/gemini-2.0-flash"
    )


    ##clean up the collection
    delete_astra_collection(collection_name=collection_name, database=astradb)
    return TaskResult(
        task_status=TaskStatus.COMPLETED,
        result_payload={"unstructured_text": result},
        parent_transaction_id=task_request.parent_transaction_id,
        token_usage=token_usage
    )

    
    
    
