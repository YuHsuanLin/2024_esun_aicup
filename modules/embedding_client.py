from openai import AzureOpenAI
from typing import List
import config

class EmbeddingClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT
        )
        
    def get_embedding(self, text: str) -> List[float]:
        """獲取文本嵌入向量"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"獲取嵌入向量時出錯: {e}")
            raise 