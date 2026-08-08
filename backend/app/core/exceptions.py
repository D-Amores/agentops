from uuid import UUID


class DomainError(Exception):
    """Base exception for business rule violations."""


class EmailAlreadyExistsError(DomainError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class WorkflowNotFoundError(DomainError):
    def __init__(self, workflow_id: UUID) -> None:
        self.workflow_id = workflow_id
        super().__init__(f"Workflow with id '{workflow_id}' not found")


class WorkflowRunNotFoundError(DomainError):
    def __init__(self, workflow_run_id: UUID) -> None:
        self.workflow_run_id = workflow_run_id
        super().__init__(f"Workflow run with id '{workflow_run_id}' not found")


class WorkflowNotExecutableError(DomainError):
    def __init__(self, workflow_id: UUID) -> None:
        self.workflow_id = workflow_id
        super().__init__(f"Workflow '{workflow_id}' is not active and cannot be executed")
