from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import WorkflowNotFoundError
from app.domain.workflow import Workflow
from app.models.workflow import WorkflowModel


class WorkflowRepositoryProtocol(Protocol):
    async def create(self, workflow: Workflow) -> Workflow: ...

    async def get_by_id(self, workflow_id: UUID) -> Workflow | None: ...

    async def list_by_owner_id(self, owner_id: UUID) -> list[Workflow]: ...

    async def update(self, workflow: Workflow) -> Workflow: ...

    async def delete(self, workflow_id: UUID) -> None: ...


class SQLAlchemyWorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, workflow: Workflow) -> Workflow:
        model = self._to_model(workflow)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, workflow_id: UUID) -> Workflow | None:
        model = await self._session.get(WorkflowModel, workflow_id)
        return self._to_domain(model) if model else None

    async def list_by_owner_id(self, owner_id: UUID) -> list[Workflow]:
        stmt = select(WorkflowModel).where(WorkflowModel.owner_id == owner_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def update(self, workflow: Workflow) -> Workflow:
        model = await self._session.get(WorkflowModel, workflow.id)

        if not model:
            raise WorkflowNotFoundError(workflow.id)

        model.name = workflow.name
        model.description = workflow.description
        model.system_prompt = workflow.system_prompt
        model.llm_model = workflow.llm_model
        model.status = workflow.status

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, workflow_id: UUID) -> None:
        model = await self._session.get(WorkflowModel, workflow_id)

        if not model:
            raise WorkflowNotFoundError(workflow_id)

        await self._session.delete(model)
        await self._session.flush()

    @staticmethod
    def _to_domain(model: WorkflowModel) -> Workflow:
        return Workflow(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            description=model.description,
            system_prompt=model.system_prompt,
            llm_model=model.llm_model,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(workflow: Workflow) -> WorkflowModel:
        return WorkflowModel(
            id=workflow.id,
            owner_id=workflow.owner_id,
            name=workflow.name,
            description=workflow.description,
            system_prompt=workflow.system_prompt,
            llm_model=workflow.llm_model,
            status=workflow.status,
        )
