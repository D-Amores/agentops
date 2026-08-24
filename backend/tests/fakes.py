from uuid import UUID

from app.core.exceptions import WorkflowNotFoundError
from app.domain.user import User
from app.domain.workflow import Workflow


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None


class FakeWorkflowRepository:
    def __init__(self) -> None:
        self._workflows: dict[UUID, Workflow] = {}

    async def create(self, workflow: Workflow) -> Workflow:
        self._workflows[workflow.id] = workflow
        return workflow

    async def get_by_id(self, workflow_id: UUID) -> Workflow | None:
        return self._workflows.get(workflow_id)

    async def list_by_owner_id(self, owner_id: UUID) -> list[Workflow]:
        return [workflow for workflow in self._workflows.values() if workflow.owner_id == owner_id]

    async def update(self, workflow: Workflow) -> Workflow:
        if workflow.id not in self._workflows:
            raise WorkflowNotFoundError(workflow.id)
        self._workflows[workflow.id] = workflow
        return workflow

    async def delete(self, workflow_id: UUID) -> None:
        if workflow_id not in self._workflows:
            raise WorkflowNotFoundError(workflow_id)
        del self._workflows[workflow_id]


class FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0
