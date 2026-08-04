from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_workflow_service
from app.domain.user import User
from app.domain.workflow import Workflow
from app.schemas.workflow import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    WorkflowResponse,
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: CreateWorkflowRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_service: Annotated[WorkflowService, Depends(get_workflow_service)],
) -> Workflow:
    return await workflow_service.create(current_user, data)


@router.get("/", response_model=list[WorkflowResponse])
async def list_my_workflows(
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_service: Annotated[WorkflowService, Depends(get_workflow_service)],
) -> list[Workflow]:
    return await workflow_service.list_mine(current_user)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_service: Annotated[WorkflowService, Depends(get_workflow_service)],
) -> Workflow:
    return await workflow_service.get_by_id(current_user, workflow_id)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    data: UpdateWorkflowRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_service: Annotated[WorkflowService, Depends(get_workflow_service)],
) -> Workflow:
    return await workflow_service.update(current_user, workflow_id, data)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    workflow_service: Annotated[WorkflowService, Depends(get_workflow_service)],
) -> None:
    await workflow_service.delete(current_user, workflow_id)
