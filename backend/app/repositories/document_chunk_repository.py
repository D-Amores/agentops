from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.document import DocumentChunk
from app.models.document import DocumentChunkModel, DocumentModel


class DocumentChunkRepositoryProtocol(Protocol):
    async def create_batch(self, chunks: list[DocumentChunk]) -> None: ...

    async def search_similar(
        self, owner_id: UUID, query_embedding: list[float], limit: int = 5
    ) -> list[DocumentChunk]: ...


class SQLAlchemyDocumentChunkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_batch(self, chunks: list[DocumentChunk]) -> None:
        models = [self._to_model(chunk) for chunk in chunks]
        self._session.add_all(models)
        await self._session.flush()

    async def search_similar(
        self, owner_id: UUID, query_embedding: list[float], limit: int = 5
    ) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunkModel)
            .join(DocumentModel, DocumentChunkModel.document_id == DocumentModel.id)
            .where(DocumentModel.owner_id == owner_id)
            .order_by(DocumentChunkModel.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_model(chunk: DocumentChunk) -> DocumentChunkModel:
        return DocumentChunkModel(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            embedding=chunk.embedding,
        )

    @staticmethod
    def _to_domain(model: DocumentChunkModel) -> DocumentChunk:
        return DocumentChunk(
            id=model.id,
            document_id=model.document_id,
            content=model.content,
            chunk_index=model.chunk_index,
            embedding=model.embedding,
        )
