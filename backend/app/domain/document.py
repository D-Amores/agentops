from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Document:
    owner_id: UUID
    filename: str
    content: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def belongs_to(self, user_id: UUID) -> bool:
        return self.owner_id == user_id


@dataclass
class DocumentChunk:
    document_id: UUID
    content: str
    chunk_index: int
    id: UUID = field(default_factory=uuid4)
    embedding: list[float] | None = None
