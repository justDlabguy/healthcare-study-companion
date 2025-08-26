"""
LLM Router for handling LLM-related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, List, Dict, Any, Union
import logging
import time
import json
import httpx
from datetime import datetime, timedelta

from ..services.llm_service import LLMRequest, LLMResponse, LLMService, LLMProvider, llm_service
from ..core.exceptions import (
    LLMError, RateLimitExceeded, InvalidAPIKey, ModelUnavailable, ContextWindowExceeded
)
from ..config import settings
from ..auth import get_current_user
from ..models import User, LLMUsage
from ..database import get_db
from sqlalchemy.orm import Session
from ..core.rate_limiter import RateLimiter

# Initialize rate limiter
rate_limiter = RateLimiter(
    max_requests=settings.llm_rate_limit_per_minute,
    time_window=60  # 1 minute
)

router = APIRouter(prefix="/llm", tags=["llm"])
logger = logging.getLogger(__name__)

class ChatRequest(LLMRequest):
    """Request model for chat completion."""
    provider: Optional[LLMProvider] = None
    system_prompt: Optional[str] = None
    messages: List[Dict[str, str]] = []

async def track_llm_usage(
    db: Session,
    user_id: int,
    provider: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0
):
    """Track LLM usage in the database."""
    usage = LLMUsage(
        user_id=user_id,
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        timestamp=datetime.utcnow()
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage

@router.post("/chat", response_model=LLMResponse)
async def chat_completion(
    request: ChatRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> LLMResponse:
    """
    Generate a chat completion using the configured LLM provider.
    
    Args:
        request: The chat completion request
        response: FastAPI response object
        db: Database session
        current_user: The authenticated user
        
    Returns:
        LLMResponse: The generated response
    """
    # Check rate limiting
    if not rate_limiter.allow_request(user_id=current_user.id):
        retry_after = rate_limiter.get_retry_after(user_id=current_user.id)
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                "retry_after": retry_after
            }
        )
    
    try:
        # Override provider if specified in the request
        provider = request.provider.value if request.provider else None
        service = LLMService(provider) if provider else llm_service
        
        # Format the prompt with system message if provided
        if request.system_prompt:
            messages = [{"role": "system", "content": request.system_prompt}]
            messages.extend(request.messages)
            request.prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        # Generate the response
        start_time = time.time()
        llm_response = await service.generate_text(request)
        processing_time = time.time() - start_time
        
        # Track usage
        try:
            await track_llm_usage(
                db=db,
                user_id=current_user.id,
                provider=service.provider,
                model=llm_response.model,
                prompt_tokens=llm_response.usage.get("prompt_tokens", 0),
                completion_tokens=llm_response.usage.get("completion_tokens", 0),
                total_tokens=llm_response.usage.get("total_tokens", 0)
            )
        except Exception as e:
            logger.error(f"Failed to track LLM usage: {str(e)}", exc_info=True)
        
        # Add response headers
        response.headers["X-LLM-Provider"] = service.provider
        response.headers["X-LLM-Model"] = llm_response.model
        response.headers["X-Processing-Time"] = f"{processing_time:.4f}s"
        
        return llm_response
        
    except InvalidAPIKey as e:
        logger.error(f"Invalid API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_api_key",
                "message": str(e)
            },
        )
    except (ModelUnavailable, ContextWindowExceeded) as e:
        logger.error(f"Model error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "model_error",
                "message": str(e)
            },
        )
    except RateLimitExceeded as e:
        retry_after = 60  # Default 1 minute
        response.headers["Retry-After"] = str(retry_after)
        logger.error(f"Rate limit exceeded: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "provider_rate_limit_exceeded",
                "message": str(e),
                "retry_after": retry_after
            },
        )
    except LLMError as e:
        logger.error(f"LLM service error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "service_unavailable",
                "message": "The LLM service is currently unavailable. Please try again later."
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat completion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_server_error",
                "message": "An unexpected error occurred while processing your request."
            },
        )

@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stream chat completion responses from the LLM.
    """
    # Set up streaming
    request.stream = True
    
    async def event_generator():
        try:
            # Override provider if specified in the request
            provider = request.provider.value if request.provider else None
            service = LLMService(provider) if provider else llm_service
            
            # Format the prompt with system message if provided
            if request.system_prompt:
                messages = [{"role": "system", "content": request.system_prompt}]
                messages.extend(request.messages)
                request.prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            # Stream the response
            async with httpx.AsyncClient() as client:
                url = service._get_api_url()
                payload = service._format_request(request)
                
                async with client.stream(
                    "POST",
                    url,
                    headers=service.headers,
                    json=payload,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    
                    async for chunk in response.aiter_text():
                        if chunk.startswith("data: [DONE]"):
                            break
                            
                        if chunk.startswith("data: {"):
                            try:
                                data = json.loads(chunk[6:])  # Remove 'data: ' prefix
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield f"data: {json.dumps({'content': delta['content']})}\n\n"
                            except json.JSONDecodeError:
                                continue
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

# Exception handlers are handled globally in main.py
