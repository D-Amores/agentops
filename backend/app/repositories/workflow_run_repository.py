from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import WorkflowRunNotFoundError
from app.domain.workflow_run import WorkflowRun
from app.models.workflow_run import WorkflowRunModel


class WorkflowRunRepositoryProtocol(Protocol):
    async def create(self, workflow_run: WorkflowRun) -> WorkflowRun: ...

    async def update(self, workflow_run: WorkflowRun) -> WorkflowRun: ...

    async def get_by_id(self, workflow_run_id: UUID) -> WorkflowRun | None: ...


class SQLAlchemyWorkflowRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, workflow_run: WorkflowRun) -> WorkflowRun:
        model = self._to_model(workflow_run)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, workflow_run: WorkflowRun) -> WorkflowRun:
        model = await self._session.get(WorkflowRunModel, workflow_run.id)
        if not model:
            raise WorkflowRunNotFoundError(workflow_run.id)

        model.status = workflow_run.status
        model.input_message = workflow_run.input_message
        model.output_message = workflow_run.output_message
        model.error_message = workflow_run.error_message
        model.input_tokens = workflow_run.input_tokens
        model.output_tokens = workflow_run.output_tokens
        model.completed_at = workflow_run.completed_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, workflow_run_id: UUID) -> WorkflowRun | None:
        model = await self._session.get(WorkflowRunModel, workflow_run_id)
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_model(workflow_run: WorkflowRun) -> WorkflowRunModel:
        return WorkflowRunModel(
            id=workflow_run.id,
            workflow_id=workflow_run.workflow_id,
            status=workflow_run.status,
            input_message=workflow_run.input_message,
            output_message=workflow_run.output_message,
            error_message=workflow_run.error_message,
            input_tokens=workflow_run.input_tokens,
            output_tokens=workflow_run.output_tokens,
        )

    @staticmethod
    def _to_domain(workflow_run_model: WorkflowRunModel) -> WorkflowRun:
        return WorkflowRun(
            id=workflow_run_model.id,
            workflow_id=workflow_run_model.workflow_id,
            status=workflow_run_model.status,
            input_message=workflow_run_model.input_message,
            output_message=workflow_run_model.output_message,
            error_message=workflow_run_model.error_message,
            input_tokens=workflow_run_model.input_tokens,
            output_tokens=workflow_run_model.output_tokens,
            created_at=workflow_run_model.created_at,
            completed_at=workflow_run_model.completed_at,
        )
