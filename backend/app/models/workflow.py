import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.workflow import LLMModel, WorkflowStatus


class WorkflowModel(Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    llm_model: Mapped[LLMModel] = mapped_column(
        SQLEnum(
            LLMModel,
            name="workflow_llm_model",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=LLMModel.DEEPSEEK_CHAT,
        nullable=False,
    )
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(
            WorkflowStatus,
            name="workflow_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=WorkflowStatus.DRAFT,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
