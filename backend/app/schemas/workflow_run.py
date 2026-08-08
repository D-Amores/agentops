from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.workflow_run import WorkflowRunStatus


class RunWorkflowRequest(BaseModel):
    message: str = Field(min_length=1)


class WorkflowRunResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: WorkflowRunStatus
    input_message: str
    output_message: str | None
    error_message: str | None
    input_tokens: int
    output_tokens: int
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
