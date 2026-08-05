import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.workflow_run import WorkflowRunStatus


class WorkflowRunModel(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[WorkflowRunStatus] = mapped_column(
        SQLEnum(
            WorkflowRunStatus,
            name="workflow_run_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=WorkflowRunStatus.RUNNING,
        nullable=False,
    )
    input_message: Mapped[str] = mapped_column(Text, nullable=False)
    output_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
