from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DocumentNotFoundError
from app.domain.document import Document
from app.models.document import DocumentModel


class DocumentRepositoryProtocol(Protocol):
    async def create(self, document: Document) -> Document: ...

    async def get_by_id(self, document_id: UUID) -> Document | None: ...

    async def list_by_owner_id(self, owner_id: UUID) -> list[Document]: ...

    async def delete(self, document_id: UUID) -> None: ...


class SQLAlchemyDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, document: Document) -> Document:
        model = self._to_model(document)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, document_id: UUID) -> Document | None:
        model = await self._session.get(DocumentModel, document_id)
        return self._to_domain(model) if model else None

    async def list_by_owner_id(self, owner_id: UUID) -> list[Document]:
        stmt = select(DocumentModel).where(DocumentModel.owner_id == owner_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def delete(self, document_id: UUID) -> None:
        model = await self._session.get(DocumentModel, document_id)
        if not model:
            raise DocumentNotFoundError(document_id)
        await self._session.delete(model)
        await self._session.flush()

    @staticmethod
    def _to_domain(model: DocumentModel) -> Document:
        return Document(
            owner_id=model.owner_id,
            filename=model.filename,
            content=model.content,
            id=model.id,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(document: Document) -> DocumentModel:
        return DocumentModel(
            id=document.id,
            owner_id=document.owner_id,
            filename=document.filename,
            content=document.content,
        )
