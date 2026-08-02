from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class LLMModel(StrEnum):
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_REASONER = "deepseek-reasoner"


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class workflow:
    owner_id: UUID
    name: str
    system_prompt: str
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    llm_model: LLMModel = LLMModel.DEEPSEEK_CHAT
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_executable(self) -> bool:
        return self.status == WorkflowStatus.ACTIVE

    def belongs_to_user(self, user_id: UUID) -> bool:
        return self.owner_id == user_id
