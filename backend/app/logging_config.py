"""
Structured logging configuration with request IDs and monitoring support.
"""
import logging
import logging.config
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
import structlog
from pythonjsonlogger import jsonlogger
from fastapi import Request
import traceback

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar('user_id', default=None)

class RequestIDFilter(logging.Filter):
    """Add request ID and user ID to log records."""
    
    def filter(self, record):
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True

class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add request context if available
        if hasattr(record, 'request_id') and record.request_id:
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id') and record.user_id:
            log_record['user_id'] = record.user_id
        
        # Add file and line info for errors
        if record.levelno >= logging.ERROR:
            log_record['file'] = record.filename
            log_record['line'] = record.lineno
            log_record['function'] = record.funcName
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

def setup_logging(
    log_level: str = "INFO",
    structured: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Set up structured logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Whether to use structured JSON logging
        log_file: Optional log file path
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer() if structured else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if structured:
        console_handler.setFormatter(StructuredFormatter(
            fmt='%(timestamp)s %(level)s %(logger)s %(message)s'
        ))
    else:
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
        ))
    console_handler.addFilter(RequestIDFilter())
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter(
            fmt='%(timestamp)s %(level)s %(logger)s %(message)s'
        ))
        file_handler.addFilter(RequestIDFilter())
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

def set_request_context(request_id: str, user_id: Optional[int] = None) -> None:
    """Set request context for logging."""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)

def clear_request_context() -> None:
    """Clear request context."""
    request_id_var.set(None)
    user_id_var.set(None)

def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())

class LoggingMiddleware:
    """Middleware to add request IDs and logging to all requests."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID
        request_id = generate_request_id()
        
        # Extract basic request info
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        # Set request context
        set_request_context(request_id)
        
        # Log request start
        start_time = datetime.utcnow()
        self.logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            path=path,
            start_time=start_time.isoformat()
        )
        
        # Process request
        try:
            await self.app(scope, receive, send)
            
            # Log successful completion
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(
                "Request completed",
                request_id=request_id,
                method=method,
                path=path,
                duration_seconds=duration,
                status="success"
            )
            
        except Exception as e:
            # Log error
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                duration_seconds=duration,
                error=str(e),
                status="error",
                exc_info=True
            )
            raise
        
        finally:
            # Clear request context
            clear_request_context()

# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._metrics = {}
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric."""
        self.logger.info(
            "Performance metric",
            metric_name=name,
            metric_value=value,
            metric_tags=tags or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    def record_database_query(self, query_type: str, duration: float, success: bool = True):
        """Record database query performance."""
        self.record_metric(
            "database_query_duration",
            duration,
            {
                "query_type": query_type,
                "success": str(success)
            }
        )
    
    def record_ai_request(self, provider: str, model: str, duration: float, success: bool = True):
        """Record AI API request performance."""
        self.record_metric(
            "ai_request_duration",
            duration,
            {
                "provider": provider,
                "model": model,
                "success": str(success)
            }
        )
    
    def record_document_processing(self, file_type: str, file_size: int, duration: float, success: bool = True):
        """Record document processing performance."""
        self.record_metric(
            "document_processing_duration",
            duration,
            {
                "file_type": file_type,
                "file_size_mb": str(round(file_size / (1024 * 1024), 2)),
                "success": str(success)
            }
        )

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Error tracking utilities
class ErrorTracker:
    """Track and categorize application errors."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
        user_id: Optional[int] = None
    ):
        """Track an application error with context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if user_id:
            error_data["user_id"] = user_id
        
        self.logger.error(
            "Application error tracked",
            **error_data,
            exc_info=True
        )
    
    def track_validation_error(self, field: str, value: Any, error_message: str):
        """Track validation errors."""
        self.track_error(
            ValueError(error_message),
            context={
                "field": field,
                "value": str(value),
                "error_type": "validation"
            },
            severity="warning"
        )
    
    def track_external_service_error(self, service: str, operation: str, error: Exception):
        """Track errors from external services."""
        self.track_error(
            error,
            context={
                "service": service,
                "operation": operation,
                "error_type": "external_service"
            },
            severity="error"
        )

# Global error tracker instance
error_tracker = ErrorTracker()