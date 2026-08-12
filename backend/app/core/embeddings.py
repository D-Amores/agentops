from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.core.config import get_settings
from app.models.document import EMBEDDING_DIMENSIONS

settings = get_settings()

embeddings_client = OpenAIEmbeddings(
    model="text-embeddig-3-small",
    api_key=SecretStr(settings.OPENAI_API_KEY),
    dimensions=EMBEDDING_DIMENSIONS,
)
