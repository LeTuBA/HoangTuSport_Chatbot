from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from typing import List
from ..core.config import settings

class EmbeddingProvider:
    """
    Provider cho các embedding models
    """
    def __init__(self):
        # Sử dụng OPENAI_EMBEDDING_MODEL thay vì EMBEDDING_MODEL
        self.model_name = settings.OPENAI_EMBEDDING_MODEL
        self._init_model()
    
    def _init_model(self):
        """
        Khởi tạo embedding model OpenAI text-embedding-3-large
        """
        # Luôn sử dụng OpenAI embedding model
        self.model = OpenAIEmbeddings(
            model=self.model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            dimensions=3072 if 'large' in self.model_name.lower() else 1536
        )
        print(f"[EMBEDDING] Đã khởi tạo OpenAI Embedding Model: {self.model_name}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Lấy embedding vectors cho một danh sách văn bản
        """
        return self.model.embed_documents(texts)
    
    def get_query_embedding(self, text: str) -> List[float]:
        """
        Lấy embedding vector cho một câu truy vấn
        """
        return self.model.embed_query(text)

# Singleton instance
embedding_provider = EmbeddingProvider() 