from pydantic import BaseModel, Field

class AgentInputModel(BaseModel):
    info: str = Field(
        ..., 
        description="Information about the prospect"
    )
