from uuid import UUID

from app.core.exceptions import DomainError, WorkflowNotFoundError
from app.domain.user import User
from app.domain.workflow import Workflow
from app.repositories.workflow_repository import WorkflowRepositoryProtocol
from app.schemas.workflow import CreateWorkflowRequest, UpdateWorkflowRequest


class WorkflowPermissionError(DomainError):
    def __init__(self) -> None:
        super().__init__("You don't have permission to access this workflow")


class WorkflowService:
    def __init__(self, workflow_repository: WorkflowRepositoryProtocol) -> None:
        self._workflow_repository = workflow_repository

    async def create(self, owner: User, data: CreateWorkflowRequest) -> Workflow:
        workflow = Workflow(
            owner_id=owner.id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            llm_model=data.llm_model,
        )
        return await self._workflow_repository.create(workflow)

    async def get_by_id(self, requester: User, workflow_id: UUID) -> Workflow:
        workflow = await self._workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            raise WorkflowNotFoundError(workflow_id)

        self._ensure_access(requester, workflow)
        return workflow

    async def list_mine(self, owner: User) -> list[Workflow]:
        return await self._workflow_repository.list_by_owner_id(owner.id)

    async def update(
        self, requester: User, workflow_id: UUID, data: UpdateWorkflowRequest
    ) -> Workflow:
        workflow = await self.get_by_id(requester, workflow_id)

        workflow.name = data.name
        workflow.description = data.description
        workflow.system_prompt = data.system_prompt
        workflow.llm_model = data.llm_model
        workflow.status = data.status

        return await self._workflow_repository.update(workflow)

    async def delete(self, requester: User, workflow_id: UUID) -> None:
        workflow = await self.get_by_id(requester, workflow_id)
        await self._workflow_repository.delete(workflow.id)

    @staticmethod
    def _ensure_access(requester: User, workflow: Workflow) -> None:
        if requester.is_admin() or workflow.belongs_to_user(requester.id):
            return

        raise WorkflowPermissionError()
