"""
Health check and monitoring endpoints for the Healthcare Study Companion API.
"""
import os
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import httpx

from .database import SessionLocal
from .config import settings
from .logging_config import get_logger, performance_monitor, error_tracker
from .services.llm_service import LLMService

logger = get_logger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])

class HealthChecker:
    """Comprehensive health checking for all system components."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def check_database(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            result = db.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            # Test a more complex query
            db.execute(text("SELECT COUNT(*) FROM users"))
            
            duration = time.time() - start_time
            performance_monitor.record_database_query("health_check", duration, True)
            
            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "test_query_result": test_value,
                "connection_pool_size": getattr(db.bind.pool, 'size', 'unknown'),
                "connection_pool_checked_out": getattr(db.bind.pool, 'checkedout', 'unknown')
            }
            
        except Exception as e:
            duration = time.time() - start_time
            performance_monitor.record_database_query("health_check", duration, False)
            error_tracker.track_external_service_error("database", "health_check", e)
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round(duration * 1000, 2)
            }
    
    async def check_llm_service(self) -> Dict[str, Any]:
        """Check LLM service connectivity."""
        start_time = time.time()
        
        try:
            llm_service = LLMService()
            
            # Test with a simple prompt
            test_response = await llm_service.generate_answer(
                question="What is 2+2?",
                context_chunks=["Basic math: 2+2=4"],
                temperature=0.1
            )
            
            duration = time.time() - start_time
            performance_monitor.record_ai_request(
                settings.llm_provider, 
                settings.llm_model_id, 
                duration, 
                True
            )
            
            return {
                "status": "healthy",
                "provider": settings.llm_provider,
                "model": settings.llm_model_id,
                "response_time_ms": round(duration * 1000, 2),
                "test_response_length": len(test_response) if test_response else 0
            }
            
        except Exception as e:
            duration = time.time() - start_time
            performance_monitor.record_ai_request(
                settings.llm_provider, 
                settings.llm_model_id, 
                duration, 
                False
            )
            error_tracker.track_external_service_error("llm_service", "health_check", e)
            
            return {
                "status": "unhealthy",
                "provider": settings.llm_provider,
                "model": settings.llm_model_id,
                "error": str(e),
                "response_time_ms": round(duration * 1000, 2)
            }
    
    async def check_external_dependencies(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        checks = {}
        
        # Check internet connectivity
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://httpbin.org/status/200")
                checks["internet"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_code": response.status_code
                }
        except Exception as e:
            checks["internet"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check LLM API endpoint
        api_key = settings.get_api_key_for_provider()
        if api_key and settings.llm_provider == "mistral":
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://api.mistral.ai/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    checks["mistral_api"] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "response_code": response.status_code
                    }
            except Exception as e:
                checks["mistral_api"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return checks
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                }
            }
        except Exception as e:
            error_tracker.track_error(e, {"component": "system_metrics"})
            return {"error": str(e)}

# Global health checker instance
health_checker = HealthChecker()

def get_db():
    """Database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Returns detailed status of all system components.
    """
    start_time = time.time()
    
    try:
        # Check all components
        database_health = await health_checker.check_database(db)
        llm_health = await health_checker.check_llm_service()
        external_deps = await health_checker.check_external_dependencies()
        system_metrics = health_checker.get_system_metrics()
        
        # Determine overall status
        overall_status = "healthy"
        if (database_health.get("status") != "healthy" or 
            llm_health.get("status") != "healthy"):
            overall_status = "degraded"
        
        # Check for critical issues
        if database_health.get("status") == "unhealthy":
            overall_status = "unhealthy"
        
        response_time = time.time() - start_time
        
        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(response_time * 1000, 2),
            "environment": settings.environment,
            "version": "0.1.0",
            "components": {
                "database": database_health,
                "llm_service": llm_health,
                "external_dependencies": external_deps
            },
            "system_metrics": system_metrics,
            "deployment_info": {
                "railway_deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID"),
                "git_commit": os.getenv("RAILWAY_GIT_COMMIT_SHA"),
                "service_name": os.getenv("RAILWAY_SERVICE_NAME"),
            }
        }
        
        # Log health check
        logger.info(
            "Health check completed",
            overall_status=overall_status,
            response_time_ms=health_data["response_time_ms"],
            database_status=database_health.get("status"),
            llm_status=llm_health.get("status")
        )
        
        # Return appropriate HTTP status
        if overall_status == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_data
            )
        elif overall_status == "degraded":
            return health_data  # 200 but with degraded status
        else:
            return health_data
            
    except HTTPException:
        raise
    except Exception as e:
        error_tracker.track_error(e, {"endpoint": "health_check"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint for basic monitoring.
    Returns minimal response for load balancers.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Database-specific health check."""
    result = await health_checker.check_database(db)
    
    if result.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )
    
    return result

@router.get("/health/llm")
async def llm_health_check():
    """LLM service-specific health check."""
    result = await health_checker.check_llm_service()
    
    if result.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )
    
    return result

@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics for monitoring.
    """
    try:
        system_metrics = health_checker.get_system_metrics()
        
        # Add application-specific metrics
        app_metrics = {
            "uptime_seconds": time.time() - getattr(get_metrics, '_start_time', time.time()),
            "environment": settings.environment,
            "configuration": {
                "max_concurrent_ai_requests": settings.max_concurrent_ai_requests,
                "max_concurrent_document_processing": settings.max_concurrent_document_processing,
                "db_pool_size": settings.db_pool_size,
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model_id
            }
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_metrics,
            "application": app_metrics
        }
        
    except Exception as e:
        error_tracker.track_error(e, {"endpoint": "metrics"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)}
        )

# Initialize start time for uptime calculation
get_metrics._start_time = time.time()

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = 100,
    level: Optional[str] = None,
    component: Optional[str] = None
):
    """
    Get recent log entries (if log aggregation is set up).
    This is a placeholder for integration with log aggregation systems.
    """
    # In a real implementation, this would query your log aggregation system
    # (e.g., ELK stack, Splunk, CloudWatch, etc.)
    
    return {
        "message": "Log aggregation not implemented",
        "suggestion": "Integrate with log aggregation system like ELK, Splunk, or CloudWatch",
        "parameters": {
            "limit": limit,
            "level": level,
            "component": component
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/alerts/test")
async def test_alert_system():
    """
    Test the alerting system by generating a test alert.
    """
    try:
        # Generate a test error for alerting
        test_error = Exception("Test alert - system is functioning normally")
        error_tracker.track_error(
            test_error,
            context={
                "alert_type": "test",
                "component": "monitoring",
                "severity": "info"
            },
            severity="info"
        )
        
        logger.info(
            "Test alert generated",
            alert_type="test",
            component="monitoring",
            message="This is a test alert to verify the alerting system"
        )
        
        return {
            "status": "success",
            "message": "Test alert generated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_tracker.track_error(e, {"endpoint": "test_alert"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)}
        )

# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """Decorator to monitor operation performance."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record_metric(
                    f"{operation_name}_duration",
                    duration,
                    {"success": "true"}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record_metric(
                    f"{operation_name}_duration",
                    duration,
                    {"success": "false"}
                )
                error_tracker.track_error(e, {"operation": operation_name})
                raise
        return wrapper
    return decorator