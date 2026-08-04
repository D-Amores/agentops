from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.workflow import LLMModel, WorkflowStatus


class CreateWorkflowRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    system_prompt: str = Field(min_length=1)
    llm_model: LLMModel = LLMModel.DEEPSEEK_CHAT


class UpdateWorkflowRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    system_prompt: str = Field(min_length=1)
    llm_model: LLMModel
    status: WorkflowStatus


class WorkflowResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    system_prompt: str
    llm_model: LLMModel
    status: WorkflowStatus

    model_config = {"from_attributes": True}
