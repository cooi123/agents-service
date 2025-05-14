import hashlib
from src.models.task_models import CeleryTaskRequest, TaskResult
import httpx

def generate_collection_name(project_id: str, service_id: str) -> str:
    """
    Generate a valid collection name from project_id and service_id.
    Ensures the name is:
    - Alphanumeric with underscores only
    - Max 48 characters
    - Unique and deterministic for the same inputs
    """
    # Combine service_id and project_id for uniqueness
    combined = f"{service_id}_{project_id}"
    
    # Create a hash of the combined string
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    
    # Take first 40 chars of hash to leave room for prefix
    hash_prefix = hash_hex[:40]
    
    # Create final collection name with prefix
    collection_name = f"proj_{hash_prefix}"
    
    return collection_name


def send_update_to_broker(task_request: CeleryTaskRequest, result: TaskResult):
    """
    Send an update to the broker.
    """
    callback_url = task_request.callback_url

    print("sending update to broker", callback_url)
    print("result", result)
    #do a post request to the broker_url with the result
    client = httpx.Client()
    response = client.post(callback_url, json=result.model_dump())
    #print error
    if response.status_code != 200:
        raise Exception(f"Error sending update to broker: {response.text}")
    return response.json()
