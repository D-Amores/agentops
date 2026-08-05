from uuid import uuid4

import pytest

from app.core.exceptions import WorkflowNotFoundError
from app.domain.user import User, UserRole
from app.domain.workflow import WorkflowStatus
from app.schemas.workflow import CreateWorkflowRequest, UpdateWorkflowRequest
from app.services.workflow_service import WorkflowPermissionError, WorkflowService
from tests.fakes import FakeWorkflowRepository


@pytest.fixture
def workflow_service() -> WorkflowService:
    return WorkflowService(FakeWorkflowRepository())


@pytest.fixture
def owner() -> User:
    return User(email="owner@example.com", hashed_password="hashed")


@pytest.fixture
def other_user() -> User:
    return User(email="other@example.com", hashed_password="hashed")


@pytest.fixture
def admin() -> User:
    return User(email="admin@example.com", hashed_password="hashed", role=UserRole.ADMIN)


async def test_owner_can_create_and_retrieve_workflow(
    workflow_service: WorkflowService, owner: User
) -> None:
    data = CreateWorkflowRequest(name="Test Workflow", system_prompt="You are helpful.")

    created = await workflow_service.create(owner, data)
    fetched = await workflow_service.get_by_id(owner, created.id)

    assert fetched.id == created.id
    assert fetched.name == "Test Workflow"
    assert fetched.owner_id == owner.id
    assert fetched.status == WorkflowStatus.DRAFT


async def test_other_user_cannot_access_workflow(
    workflow_service: WorkflowService, owner: User, other_user: User
) -> None:
    data = CreateWorkflowRequest(name="Private Workflow", system_prompt="Secret prompt.")
    created = await workflow_service.create(owner, data)

    with pytest.raises(WorkflowPermissionError):
        await workflow_service.get_by_id(other_user, created.id)


async def test_admin_can_access_any_workflow(
    workflow_service: WorkflowService, owner: User, admin: User
) -> None:
    data = CreateWorkflowRequest(name="Owned Workflow", system_prompt="Prompt.")
    created = await workflow_service.create(owner, data)

    fetched = await workflow_service.get_by_id(admin, created.id)

    assert fetched.id == created.id


async def test_owner_can_update_own_workflow(
    workflow_service: WorkflowService, owner: User
) -> None:
    data = CreateWorkflowRequest(name="Draft Workflow", system_prompt="Prompt.")
    created = await workflow_service.create(owner, data)

    update_data = UpdateWorkflowRequest(
        name="Updated Name",
        system_prompt="Updated prompt.",
        llm_model=created.llm_model,
        status=WorkflowStatus.ACTIVE,
    )
    updated = await workflow_service.update(owner, created.id, update_data)

    assert updated.name == "Updated Name"
    assert updated.system_prompt == "Updated prompt."
    assert updated.status == WorkflowStatus.ACTIVE
    assert updated.id == created.id


async def test_other_user_cannot_delete_workflow(
    workflow_service: WorkflowService, owner: User, other_user: User
) -> None:
    data = CreateWorkflowRequest(name="Protected Workflow", system_prompt="Prompt.")
    created = await workflow_service.create(owner, data)

    with pytest.raises(WorkflowPermissionError):
        await workflow_service.delete(other_user, created.id)


async def test_get_nonexistent_workflow_raises_not_found(
    workflow_service: WorkflowService, owner: User
) -> None:
    with pytest.raises(WorkflowNotFoundError):
        await workflow_service.get_by_id(owner, uuid4())
