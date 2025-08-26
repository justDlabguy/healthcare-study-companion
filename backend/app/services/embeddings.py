import os
from typing import List
import httpx

from ..config import settings

MISTRAL_EMBEDDINGS_URL = "https://api.mistral.ai/v1/embeddings"


class EmbeddingsClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.mistral_api_key or os.getenv("MISTRAL_API_KEY", "")
        self.model = model or settings.embedding_model_id
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def embed_texts(self, texts: List[str], timeout: float = 30.0) -> List[List[float]]:
        if not texts:
            return []
        payload = {"model": self.model, "input": texts}
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(MISTRAL_EMBEDDINGS_URL, json=payload, headers=self._headers)
            resp.raise_for_status()
            data = resp.json()
            # Expected: { data: [{ embedding: [...] }, ...] }
            return [item["embedding"] for item in data.get("data", [])]
