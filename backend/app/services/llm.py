import os
from typing import List, Optional
import httpx

from ..config import settings

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or settings.mistral_api_key or os.getenv("MISTRAL_API_KEY", "")
        self.model = model or settings.llm_model_id
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        timeout: float = 60.0,
        stream: bool = False,
    ) -> str:
        """Simple non-streaming completion combining retrieved context and user question."""
        system = system_prompt or (
            "You are a helpful medical study assistant. Answer using only the provided context. "
            "If unsure, say you don't know. Be concise and accurate."
        )
        context_text = "\n\n".join(context_chunks)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"},
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(MISTRAL_CHAT_URL, json=payload, headers=self._headers)
            resp.raise_for_status()
            data = resp.json()
            # Expected: choices[0].message.content
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

    async def generate_flashcards(
        self,
        topic_name: str,
        context_summary: str,
        count: int = 10,
        timeout: float = 60.0,
    ) -> List[dict]:
        prompt = (
            "Create high-quality flashcards for medical study. "
            "Return a numbered list of concise Q/A pairs. Avoid ambiguous phrasing.\n\n"
            f"Topic: {topic_name}\nContext: {context_summary}\nCount: {count}"
        )
        messages = [
            {"role": "system", "content": "You generate clear, focused flashcards in Q/A format."},
            {"role": "user", "content": prompt},
        ]
        payload = {"model": self.model, "messages": messages, "temperature": 0.3, "stream": False}
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(MISTRAL_CHAT_URL, json=payload, headers=self._headers)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Minimal parser: split lines into simple Q/A dicts
        cards: List[dict] = []
        for line in text.splitlines():
            line = line.strip(" -")
            if not line:
                continue
            # Heuristic: split at '?'
            if "?" in line:
                q, _, a = line.partition("?")
                q = q.strip() + "?"
                a = a.strip(" -:")
                if q and a:
                    cards.append({"question": q, "answer": a})
        return cards[:count]
