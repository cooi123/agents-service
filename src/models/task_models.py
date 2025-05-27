from enum import Enum
from typing import Optional, List, Dict, Any, Union, Generic, TypeVar
from pydantic import BaseModel, Field
from src.models.base_models import BaseServiceRequest

T = TypeVar('T', bound=BaseModel)

class TaskStatus(str, Enum):
    """Enum for task status values"""
    RECEIVED = "received"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceType(str, Enum):
    """Enum for resource types"""
    LLM = "llm"
    EMBEDDING = "embedding"
    STORAGE = "storage"
    PROCESSING = "processing"

class TaskType(str, Enum):
    """Enum for task types"""
    TASK = "task"
    SUBTASK = "subtask"


class CeleryTaskRequest(BaseModel):
    """Base model for all Celery task requests"""
    # Base service request fields
    userId: str
    projectId: str
    serviceId: str
    inputData: dict
    documentUrls: Optional[List[str]] = None
    serviceUrl: Optional[str] = None
    
    # Task specific fields
    parent_transaction_id:str
    task_type: TaskType = TaskType.TASK
    
    # Additional metadata 
    metadata: Dict[str, Any] = Field(default_factory=dict)

    callback_url: str 
    

class TokenUsage(BaseModel):
    tokens_total: int
    prompt_tokens: int
    completion_tokens: int
    model_name: str
    
class ComputationalUsage(BaseModel):
    runtime_ms: int
    resources_used: dict
    
    
class TaskResult(BaseModel):
    """Model for task results"""
    # Result data
    result_payload: dict =None
    result_document_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    token_usage: Optional[TokenUsage] = None
    computational_usage: Optional[ComputationalUsage] = None
    task_status: TaskStatus = TaskStatus.COMPLETED
    parent_transaction_id: str
    

