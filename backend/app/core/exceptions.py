"""Custom exceptions for the application."""
from fastapi import status
from fastapi.exceptions import HTTPException
from typing import Any, Dict, Optional

class LLMError(HTTPException):
    """Exception raised for errors in LLM operations."""
    
    def __init__(
        self,
        detail: str = "An error occurred while processing your request with the LLM service",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers or {},
        )

class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

class InvalidAPIKey(HTTPException):
    """Exception raised when an invalid API key is provided."""
    
    def __init__(self, service: str = "LLM") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key for {service} service",
        )

class ModelUnavailable(HTTPException):
    """Exception raised when the requested model is not available."""
    
    def __init__(self, model: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The model '{model}' is not available or not supported.",
        )

class ContextWindowExceeded(HTTPException):
    """Exception raised when the context window is exceeded."""
    
    def __init__(self, max_tokens: int) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The request exceeds the context window. Maximum tokens allowed: {max_tokens}",
        )
