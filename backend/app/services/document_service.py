from uuid import UUID

from app.core.chunking import split_text
from app.core.embeddings import embeddings_client
from app.core.exceptions import (
    DocumentNotFoundError,
    ResourcePermissionError,
)
from app.domain.document import Document, DocumentChunk
from app.domain.user import User
from app.repositories.document_chunk_repository import DocumentChunkRepositoryProtocol
from app.repositories.document_repository import DocumentRepositoryProtocol
from app.schemas.document import CreateDocumentRequest


class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepositoryProtocol,
        document_chunk_repository: DocumentChunkRepositoryProtocol,
    ) -> None:
        self._document_repository = document_repository
        self._document_chunk_repository = document_chunk_repository

    async def ingest(self, owner: User, data: CreateDocumentRequest) -> Document:
        document = Document(owner_id=owner.id, filename=data.filename, content=data.content)
        document = await self._document_repository.create(document)

        text_chunks = split_text(data.content)
        embedded_vectors = await embeddings_client.aembed_documents(text_chunks)

        chunks = [
            DocumentChunk(
                document_id=document.id,
                content=text,
                chunk_index=index,
                embedding=vector,
            )
            for index, (text, vector) in enumerate(zip(text_chunks, embedded_vectors, strict=True))
        ]
        await self._document_chunk_repository.create_batch(chunks)
        return document

    async def list_mine(self, owner: User) -> list[Document]:
        return await self._document_repository.list_by_owner_id(owner.id)

    async def delete(self, requester: User, document_id: UUID) -> None:
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        if not (requester.is_admin() or document.belongs_to(requester.id)):
            raise ResourcePermissionError()

        await self._document_repository.delete(document_id)
