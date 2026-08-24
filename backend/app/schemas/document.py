from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateDocumentRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: UUID
    owner_id: UUID
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}
