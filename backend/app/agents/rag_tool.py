from uuid import UUID

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.core.embeddings import embeddings_client
from app.repositories.document_chunk_repository import DocumentChunkRepositoryProtocol


class _SearchDocumentsInput(BaseModel):
    query: str = Field(description="The search query to find relevant document excerpts.")


def build_search_documents_tool(
    owner_id: UUID, chunk_repository: DocumentChunkRepositoryProtocol
) -> StructuredTool:
    async def _search_documents(query: str) -> str:
        query_embeddig = await embeddings_client.aembed_query(query)
        chunks = await chunk_repository.search_similar(owner_id, query_embeddig, limit=3)

        if not chunks:
            return "No relevant documents found."

        return "\n\n---\n\n".join(chunk.content for chunk in chunks)

    return StructuredTool.from_function(
        coroutine=_search_documents,
        name="search_documents",
        description=(
            "Search the user's uploaded documents for relevant information. "
            "Use this when the user asks something that might be answered by "
            "their own documents (policies, notes, manuals, etc.)."
        ),
        args_schema=_SearchDocumentsInput,
    )
