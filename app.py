from fastapi import FastAPI
from src.tasks.celery_tasks import create_consultant_primer, create_research_paper_summary, create_research_paper_script, create_research_paper_post, create_linkedin_lead_email_generator
from src.models.task_models import CeleryTaskRequest, TaskStatus, TaskResult
from src.configs.celery_config import celery_app
from src.utils.shared import send_update_to_broker

app = FastAPI()

@app.post("/primer")
def run_priemer_task(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    # Start the task
    task = create_consultant_primer.delay(request.model_dump())
    # Return task ID and status
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }

def linkedin_lead_email_generator(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    task = create_linkedin_lead_email_generator.delay(request.model_dump())
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }

@app.post("/research-summarizer")
def run_research_paper_task(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    # Start the task
    task = create_research_paper_summary.delay(request.model_dump())
    # Return task ID and status
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)


## add research paper to podcast 
@app.post("/research-paper-script")
def run_research_paper_script_task(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    task = create_research_paper_script.delay(request.model_dump())
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }


@app.post("/research-paper-post")
def run_research_paper_post_task(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    task = create_research_paper_post.delay(request.model_dump())
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }

@app.post("/linkedin-lead-email-generator")
def run_linkedin_lead_email_generator(request: CeleryTaskRequest):
    print("received request", request)
    # Send initial pending status
    send_update_to_broker(request, TaskResult(
        task_status=TaskStatus.PENDING,
        parent_transaction_id=request.parent_transaction_id
    ))
    task = create_linkedin_lead_email_generator.delay(request.model_dump())
    return {
        "task_id": task.id,
        "status": TaskStatus.PENDING,
        "parent_transaction_id": request.parent_transaction_id
    }