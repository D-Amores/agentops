from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_workflow_execution_service
from app.domain.user import User
from app.domain.workflow_run import WorkflowRun
from app.schemas.workflow_run import RunWorkflowRequest, WorkflowRunResponse
from app.services.workflow_execution_service import WorkflowExecutionService

router = APIRouter(prefix="/workflows", tags=["Workflow Runs"])


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: UUID,
    data: RunWorkflowRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    execution_service: Annotated[WorkflowExecutionService, Depends(get_workflow_execution_service)],
) -> WorkflowRun:
    return await execution_service.execute(current_user, workflow_id, data.message)
