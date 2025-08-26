"""
LLM Service for handling interactions with different LLM providers.
"""
from typing import Optional, Dict, Any, List
import logging
from enum import Enum
import json

import httpx
from pydantic import BaseModel, Field

from ..config import settings
from ..core.exceptions import LLMError, InvalidAPIKey, ModelUnavailable

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    MISTRAL = "mistral"

class LLMRequest(BaseModel):
    """Standardized request model for LLM calls."""
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    n: int = 1
    stream: bool = False
    
    class Config:
        extra = "ignore"

class LLMResponse(BaseModel):
    """Standardized response model for LLM calls."""
    text: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LLMService:
    """Service for interacting with different LLM providers."""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.llm_provider
        self.client = None
        self.headers = None
        # Don't validate config on startup - do it when actually making requests
    
    def _validate_config(self):
        """Validate that the required API keys are present."""
        api_keys = {
            LLMProvider.OPENAI: settings.openai_api_key,
            LLMProvider.ANTHROPIC: settings.anthropic_api_key,
            LLMProvider.HUGGINGFACE: settings.huggingface_api_key,
            LLMProvider.TOGETHER: settings.together_api_key,
            LLMProvider.MISTRAL: settings.mistral_api_key,
        }
        
        api_key = api_keys.get(self.provider)
        if not api_key:
            raise InvalidAPIKey(f"No API key found for provider: {self.provider}")
            
        if not api_key.strip():
            raise InvalidAPIKey(f"Empty API key for provider: {self.provider}")
        
        # Set the API key in the environment for libraries that use it
        if self.provider == LLMProvider.OPENAI:
            import os
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    def _setup_client(self):
        """Initialize the HTTP client with appropriate headers for the provider."""
        if self.client is None:
            self._validate_config()  # Only validate when actually setting up
            self.client = httpx.AsyncClient(timeout=60.0)
            self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the HTTP client based on the provider."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.provider == LLMProvider.OPENAI:
            headers["Authorization"] = f"Bearer {settings.openai_api_key}"
        elif self.provider == LLMProvider.ANTHROPIC:
            headers["x-api-key"] = settings.anthropic_api_key
            headers["anthropic-version"] = "2023-06-01"
        elif self.provider == LLMProvider.TOGETHER:
            headers["Authorization"] = f"Bearer {settings.together_api_key}"
        elif self.provider == LLMProvider.MISTRAL:
            headers["Authorization"] = f"Bearer {settings.mistral_api_key}"
        elif self.provider == LLMProvider.HUGGINGFACE:
            headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"
        
        return headers
    
    def _get_api_url(self) -> str:
        """Get the API URL for the provider."""
        urls = {
            LLMProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
            LLMProvider.TOGETHER: "https://api.together.xyz/v1/chat/completions",
            LLMProvider.MISTRAL: "https://api.mistral.ai/v1/chat/completions",
        }
        return urls.get(self.provider, urls[LLMProvider.OPENAI])
    
    def _format_request(self, request: LLMRequest) -> Dict[str, Any]:
        """Format the request for the provider's API."""
        model = request.model or settings.default_llm_model
        
        if self.provider == LLMProvider.ANTHROPIC:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_tokens or 4000,
                "temperature": request.temperature or 0.7,
                "stream": request.stream,
            }
            if request.top_p is not None:
                payload["top_p"] = request.top_p
            if request.stop:
                payload["stop_sequences"] = request.stop
            return payload
        else:  # OpenAI, Together, Mistral, etc.
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": request.prompt}],
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 4000,
                "n": request.n,
                "stream": request.stream,
            }
            # Only include optional parameters if they have values
            if request.top_p is not None:
                payload["top_p"] = request.top_p
            if request.frequency_penalty is not None:
                payload["frequency_penalty"] = request.frequency_penalty
            if request.presence_penalty is not None:
                payload["presence_penalty"] = request.presence_penalty
            if request.stop:
                payload["stop"] = request.stop
            return payload
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using the configured LLM provider."""
        # Setup client if not already done
        if self.client is None:
            self._setup_client()
            
        url = self._get_api_url()
        payload = self._format_request(request)
        
        try:
            response = await self.client.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            if self.provider == LLMProvider.ANTHROPIC:
                return LLMResponse(
                    text=result["content"][0]["text"],
                    model=result["model"],
                    usage={
                        "prompt_tokens": result["usage"]["input_tokens"],
                        "completion_tokens": result["usage"]["output_tokens"],
                        "total_tokens": result["usage"]["input_tokens"] + result["usage"]["output_tokens"],
                    }
                )
            else:  # OpenAI, Together, Mistral, etc.
                return LLMResponse(
                    text=result["choices"][0]["message"]["content"],
                    model=result["model"],
                    usage=result.get("usage", {})
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from {self.provider} API: {str(e)}"
            logger.error(f"{error_msg}. Response: {e.response.text}")
            raise LLMError(error_msg) from e
            
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Error parsing response from {self.provider} API: {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Error calling {self.provider} API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise LLMError(error_msg) from e
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Create a singleton instance
llm_service = LLMService()
