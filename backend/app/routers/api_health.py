"""
API Health and Key Validation Router.
Provides endpoints for monitoring API key status and provider health.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel

from ..services.api_key_validator import (
    api_key_validator, 
    APIKeyValidationResult, 
    ProviderHealthCheck,
    APIKeyStatus,
    ProviderHealthStatus
)
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/health", tags=["API Health"])

class APIKeyValidationResponse(BaseModel):
    """Response model for API key validation."""
    provider: str
    status: APIKeyStatus
    is_valid: bool
    response_time_ms: float
    error_message: Optional[str] = None
    quota_info: Optional[Dict[str, Any]] = None
    rate_limit_info: Optional[Dict[str, Any]] = None
    last_validated: datetime

class ProviderHealthResponse(BaseModel):
    """Response model for provider health check."""
    provider: str
    status: ProviderHealthStatus
    api_key_status: APIKeyStatus
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    usage_metrics: Optional[Dict[str, Any]] = None
    endpoint_status: Dict[str, bool] = {}

class APIUsageSummaryResponse(BaseModel):
    """Response model for API usage summary."""
    provider: str
    requests_made: int
    tokens_used: int
    errors_count: int
    error_rate: float
    last_request_time: Optional[datetime] = None
    quota_limit: Optional[int] = None
    quota_remaining: Optional[int] = None
    quota_usage_percent: Optional[float] = None
    quota_reset_time: Optional[datetime] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_time: Optional[datetime] = None

class OverallHealthResponse(BaseModel):
    """Response model for overall API health status."""
    overall_status: str
    healthy_providers: List[str]
    degraded_providers: List[str]
    unhealthy_providers: List[str]
    total_providers: int
    last_check: datetime
    providers: Dict[str, ProviderHealthResponse]

@router.get("/validate/{provider}", response_model=APIKeyValidationResponse)
async def validate_provider_api_key(provider: str):
    """
    Validate API key for a specific provider.
    
    Args:
        provider: The LLM provider name (openai, anthropic, mistral, etc.)
    
    Returns:
        API key validation result with status and timing information
    """
    try:
        result = await api_key_validator.validate_api_key(provider)
        
        return APIKeyValidationResponse(
            provider=result.provider,
            status=result.status,
            is_valid=result.is_valid,
            response_time_ms=result.response_time_ms,
            error_message=result.error_message,
            quota_info=result.quota_info,
            rate_limit_info=result.rate_limit_info,
            last_validated=result.last_validated
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {provider}"
        )
    except Exception as e:
        logger.error(f"Error validating API key for {provider}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate API key: {str(e)}"
        )

@router.get("/validate", response_model=Dict[str, APIKeyValidationResponse])
async def validate_all_api_keys():
    """
    Validate API keys for all configured providers.
    
    Returns:
        Dictionary of validation results for each provider
    """
    try:
        results = await api_key_validator.validate_all_providers()
        
        response = {}
        for provider, result in results.items():
            response[provider] = APIKeyValidationResponse(
                provider=result.provider,
                status=result.status,
                is_valid=result.is_valid,
                response_time_ms=result.response_time_ms,
                error_message=result.error_message,
                quota_info=result.quota_info,
                rate_limit_info=result.rate_limit_info,
                last_validated=result.last_validated
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error validating all API keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate API keys: {str(e)}"
        )

@router.get("/check/{provider}", response_model=ProviderHealthResponse)
async def check_provider_health(provider: str):
    """
    Check health status for a specific provider.
    
    Args:
        provider: The LLM provider name
    
    Returns:
        Comprehensive health check result including API status and metrics
    """
    try:
        health_check = await api_key_validator.check_provider_health(provider)
        
        # Convert usage metrics to dict if present
        usage_metrics_dict = None
        if health_check.usage_metrics:
            metrics = health_check.usage_metrics
            usage_metrics_dict = {
                "requests_made": metrics.requests_made,
                "tokens_used": metrics.tokens_used,
                "errors_count": metrics.errors_count,
                "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None,
                "quota_limit": metrics.quota_limit,
                "quota_remaining": metrics.quota_remaining,
                "quota_reset_time": metrics.quota_reset_time.isoformat() if metrics.quota_reset_time else None,
                "rate_limit_remaining": metrics.rate_limit_remaining,
                "rate_limit_reset_time": metrics.rate_limit_reset_time.isoformat() if metrics.rate_limit_reset_time else None
            }
        
        return ProviderHealthResponse(
            provider=health_check.provider,
            status=health_check.status,
            api_key_status=health_check.api_key_status,
            response_time_ms=health_check.response_time_ms,
            last_check=health_check.last_check,
            error_message=health_check.error_message,
            usage_metrics=usage_metrics_dict,
            endpoint_status=health_check.endpoint_status
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {provider}"
        )
    except Exception as e:
        logger.error(f"Error checking health for {provider}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check provider health: {str(e)}"
        )

@router.get("/check", response_model=OverallHealthResponse)
async def check_all_providers_health():
    """
    Check health status for all configured providers.
    
    Returns:
        Overall health status with breakdown by provider
    """
    try:
        health_results = await api_key_validator.check_all_providers_health()
        
        if not health_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No providers configured"
            )
        
        # Categorize providers by health status
        healthy_providers = []
        degraded_providers = []
        unhealthy_providers = []
        
        providers_response = {}
        
        for provider, health_check in health_results.items():
            # Convert to response model
            usage_metrics_dict = None
            if health_check.usage_metrics:
                metrics = health_check.usage_metrics
                usage_metrics_dict = {
                    "requests_made": metrics.requests_made,
                    "tokens_used": metrics.tokens_used,
                    "errors_count": metrics.errors_count,
                    "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None,
                    "quota_limit": metrics.quota_limit,
                    "quota_remaining": metrics.quota_remaining,
                    "quota_reset_time": metrics.quota_reset_time.isoformat() if metrics.quota_reset_time else None,
                    "rate_limit_remaining": metrics.rate_limit_remaining,
                    "rate_limit_reset_time": metrics.rate_limit_reset_time.isoformat() if metrics.rate_limit_reset_time else None
                }
            
            provider_response = ProviderHealthResponse(
                provider=health_check.provider,
                status=health_check.status,
                api_key_status=health_check.api_key_status,
                response_time_ms=health_check.response_time_ms,
                last_check=health_check.last_check,
                error_message=health_check.error_message,
                usage_metrics=usage_metrics_dict,
                endpoint_status=health_check.endpoint_status
            )
            
            providers_response[provider] = provider_response
            
            # Categorize by status
            if health_check.status == ProviderHealthStatus.HEALTHY:
                healthy_providers.append(provider)
            elif health_check.status == ProviderHealthStatus.DEGRADED:
                degraded_providers.append(provider)
            else:
                unhealthy_providers.append(provider)
        
        # Determine overall status
        if len(healthy_providers) == len(health_results):
            overall_status = "healthy"
        elif len(unhealthy_providers) == len(health_results):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return OverallHealthResponse(
            overall_status=overall_status,
            healthy_providers=healthy_providers,
            degraded_providers=degraded_providers,
            unhealthy_providers=unhealthy_providers,
            total_providers=len(health_results),
            last_check=datetime.utcnow(),
            providers=providers_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking all providers health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check providers health: {str(e)}"
        )

@router.get("/usage", response_model=Dict[str, APIUsageSummaryResponse])
async def get_api_usage_summary():
    """
    Get API usage summary for all providers.
    
    Returns:
        Usage statistics including requests, tokens, quotas, and rate limits
    """
    try:
        usage_summary = api_key_validator.get_usage_summary()
        
        response = {}
        for provider, usage_data in usage_summary.items():
            response[provider] = APIUsageSummaryResponse(
                provider=provider,
                requests_made=usage_data["requests_made"],
                tokens_used=usage_data["tokens_used"],
                errors_count=usage_data["errors_count"],
                error_rate=usage_data["error_rate"],
                last_request_time=datetime.fromisoformat(usage_data["last_request_time"]) if usage_data["last_request_time"] else None,
                quota_limit=usage_data["quota_limit"],
                quota_remaining=usage_data["quota_remaining"],
                quota_usage_percent=usage_data["quota_usage_percent"],
                quota_reset_time=datetime.fromisoformat(usage_data["quota_reset_time"]) if usage_data["quota_reset_time"] else None,
                rate_limit_remaining=usage_data["rate_limit_remaining"],
                rate_limit_reset_time=datetime.fromisoformat(usage_data["rate_limit_reset_time"]) if usage_data["rate_limit_reset_time"] else None
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage summary: {str(e)}"
        )

@router.get("/usage/{provider}", response_model=APIUsageSummaryResponse)
async def get_provider_usage(provider: str):
    """
    Get API usage summary for a specific provider.
    
    Args:
        provider: The LLM provider name
    
    Returns:
        Usage statistics for the specified provider
    """
    try:
        usage_summary = api_key_validator.get_usage_summary()
        
        if provider not in usage_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider} not found or not configured"
            )
        
        usage_data = usage_summary[provider]
        
        return APIUsageSummaryResponse(
            provider=provider,
            requests_made=usage_data["requests_made"],
            tokens_used=usage_data["tokens_used"],
            errors_count=usage_data["errors_count"],
            error_rate=usage_data["error_rate"],
            last_request_time=datetime.fromisoformat(usage_data["last_request_time"]) if usage_data["last_request_time"] else None,
            quota_limit=usage_data["quota_limit"],
            quota_remaining=usage_data["quota_remaining"],
            quota_usage_percent=usage_data["quota_usage_percent"],
            quota_reset_time=datetime.fromisoformat(usage_data["quota_reset_time"]) if usage_data["quota_reset_time"] else None,
            rate_limit_remaining=usage_data["rate_limit_remaining"],
            rate_limit_reset_time=datetime.fromisoformat(usage_data["rate_limit_reset_time"]) if usage_data["rate_limit_reset_time"] else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting usage for {provider}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage for provider: {str(e)}"
        )

@router.post("/validate/refresh")
async def refresh_api_key_validation(background_tasks: BackgroundTasks):
    """
    Trigger immediate refresh of API key validation for all providers.
    
    Returns:
        Confirmation that validation refresh has been triggered
    """
    try:
        # Run validation in background
        background_tasks.add_task(api_key_validator.validate_all_providers)
        
        return {
            "message": "API key validation refresh triggered",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
    except Exception as e:
        logger.error(f"Error triggering validation refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger validation refresh: {str(e)}"
        )

@router.post("/usage/record")
async def record_api_usage(
    provider: str,
    tokens_used: int = 0,
    success: bool = True
):
    """
    Record API usage for monitoring purposes.
    
    Args:
        provider: The LLM provider name
        tokens_used: Number of tokens consumed
        success: Whether the request was successful
    
    Returns:
        Confirmation of usage recording
    """
    try:
        api_key_validator.record_api_usage(provider, tokens_used, success)
        
        return {
            "message": "API usage recorded",
            "provider": provider,
            "tokens_used": tokens_used,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording API usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record API usage: {str(e)}"
        )

@router.get("/status")
async def get_api_health_status():
    """
    Get overall API health monitoring status.
    
    Returns:
        Status of the API health monitoring system
    """
    try:
        return {
            "monitoring_enabled": settings.api_usage_monitoring_enabled,
            "validation_interval_minutes": settings.api_key_validation_interval_minutes,
            "health_check_timeout_seconds": settings.health_check_timeout_seconds,
            "quota_warning_threshold": settings.api_quota_warning_threshold,
            "configured_providers": list(api_key_validator.usage_metrics.keys()),
            "last_validation_check": datetime.utcnow().isoformat(),
            "system_status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Error getting API health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API health status: {str(e)}"
        )