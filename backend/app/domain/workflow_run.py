from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class WorkflowRunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowRun:
    workflow_id: UUID
    input_message: str
    id: UUID = field(default_factory=uuid4)
    status: WorkflowRunStatus = WorkflowRunStatus.RUNNING
    output_message: str | None = None
    error_message: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def mark_completed(self, output: str, input_tokens: int, output_tokens: int) -> None:
        self.status = WorkflowRunStatus.COMPLETED
        self.output_message = output
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.completed_at = datetime.now(UTC)

    def mark_failed(self, error: str) -> None:
        self.status = WorkflowRunStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now(UTC)
