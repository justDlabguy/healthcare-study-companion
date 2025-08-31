"""
LLM Service for handling interactions with different LLM providers.
Enhanced with provider fallback, circuit breaker pattern, and health monitoring.
"""
from typing import Optional, Dict, Any, List, Tuple
import logging
from enum import Enum
import json
import asyncio
import time
from datetime import datetime, timedelta

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
    KIWI = "kiwi"

class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

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
    provider: str
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""
    provider: LLMProvider
    api_key: str
    default_model: str
    max_retries: int = 3
    timeout: float = 60.0
    rate_limit_per_minute: int = 60
    priority: int = 1  # Lower number = higher priority

class RetryConfig(BaseModel):
    """Configuration for exponential backoff retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True

class CircuitBreaker:
    """Enhanced circuit breaker implementation for provider resilience."""
    
    def __init__(
        self,
        provider: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.provider = provider
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        self.consecutive_failures = 0
        self.total_requests = 0
        self.failure_rate_window = []  # Track failures in a sliding window
        
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker for {self.provider} moved to HALF_OPEN state")
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        return False
    
    def record_success(self):
        """Record a successful call."""
        self.success_count += 1
        self.total_requests += 1
        self.consecutive_failures = 0
        self.last_success_time = datetime.utcnow()
        
        # Add success to sliding window (False = success)
        self.failure_rate_window.append((datetime.utcnow(), False))
        self._cleanup_window()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self._reset()
                logger.info(f"Circuit breaker for {self.provider} reset to CLOSED state after {self.half_open_calls} successful calls")
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.info(f"Circuit breaker for {self.provider} failure count reset from {self.failure_count} to 0")
                self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.total_requests += 1
        self.last_failure_time = datetime.utcnow()
        
        # Add failure to sliding window (True = failure)
        self.failure_rate_window.append((datetime.utcnow(), True))
        self._cleanup_window()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self._trip()
            logger.warning(f"Circuit breaker for {self.provider} tripped during HALF_OPEN state after {self.half_open_calls} calls")
        elif self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
            failure_rate = self.get_failure_rate()
            self._trip()
            logger.warning(f"Circuit breaker for {self.provider} tripped after {self.failure_count} failures (failure rate: {failure_rate:.2%})")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        return datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
    
    def _trip(self):
        """Trip the circuit breaker to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = datetime.utcnow()
    
    def _reset(self):
        """Reset the circuit breaker to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
        self.consecutive_failures = 0
        # Keep last_failure_time for metrics but don't reset it
        
    def _cleanup_window(self, window_minutes: int = 5):
        """Clean up old entries from the failure rate window."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        self.failure_rate_window = [
            (timestamp, is_failure) for timestamp, is_failure in self.failure_rate_window
            if timestamp > cutoff_time
        ]
    
    def get_failure_rate(self) -> float:
        """Calculate the current failure rate in the sliding window."""
        if not self.failure_rate_window:
            return 0.0
        
        failures = sum(1 for _, is_failure in self.failure_rate_window if is_failure)
        total = len(self.failure_rate_window)
        return failures / total if total > 0 else 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "provider": self.provider,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "consecutive_failures": self.consecutive_failures,
            "total_requests": self.total_requests,
            "failure_rate": self.get_failure_rate(),
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "half_open_calls": self.half_open_calls if self.state == CircuitBreakerState.HALF_OPEN else 0
        }

class ProviderHealth(BaseModel):
    """Enhanced health status for a provider."""
    provider: str
    status: ProviderStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    consecutive_failures: int = 0
    failure_rate: float = 0.0
    circuit_breaker_state: CircuitBreakerState
    last_error: Optional[str] = None
    last_success: Optional[datetime] = None
    recovery_attempts: int = 0
    is_degraded: bool = False
    degradation_reason: Optional[str] = None

class LLMService:
    """Enhanced service for interacting with multiple LLM providers with fallback support."""
    
    def __init__(self, primary_provider: Optional[str] = None):
        self.primary_provider = primary_provider or settings.llm_provider
        self.client: Optional[httpx.AsyncClient] = None
        
        # Initialize provider configurations
        self.providers = self._initialize_providers()
        
        # Initialize circuit breakers with configurable parameters
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            provider.provider.value: CircuitBreaker(
                provider.provider.value,
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout,
                half_open_max_calls=settings.circuit_breaker_half_open_max_calls
            )
            for provider in self.providers
        }
        
        # Initialize retry configuration
        self.retry_config = RetryConfig(
            max_attempts=settings.retry_max_attempts,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
            backoff_multiplier=settings.retry_backoff_multiplier
        )
        
        # Provider health tracking
        self.provider_health: Dict[str, ProviderHealth] = {
            provider.provider.value: ProviderHealth(
                provider=provider.provider.value,
                status=ProviderStatus.HEALTHY,
                last_check=datetime.utcnow(),
                circuit_breaker_state=CircuitBreakerState.CLOSED,
                success_count=0,
                consecutive_failures=0,
                failure_rate=0.0,
                recovery_attempts=0
            )
            for provider in self.providers
        }
        
        # Fallback chain (ordered by priority)
        self.fallback_chain = self._create_fallback_chain()
        
        logger.info(f"LLM Service initialized with fallback chain: {[p.provider for p in self.fallback_chain]}")
    
    def _initialize_providers(self) -> List[ProviderConfig]:
        """Initialize provider configurations based on available API keys."""
        providers = []
        
        # Define provider configurations with priorities
        provider_configs = [
            (LLMProvider.OPENAI, settings.openai_api_key, "gpt-4", 1),
            (LLMProvider.MISTRAL, settings.mistral_api_key, "mistral-small", 2),
            (LLMProvider.ANTHROPIC, settings.anthropic_api_key, "claude-3-sonnet-20240229", 3),
            (LLMProvider.KIWI, settings.kiwi_api_key, "kiwi-chat", 4),
            (LLMProvider.TOGETHER, settings.together_api_key, "meta-llama/Llama-2-7b-chat-hf", 5),
            (LLMProvider.HUGGINGFACE, settings.huggingface_api_key, "microsoft/DialoGPT-medium", 6),
        ]
        
        for provider, api_key, default_model, priority in provider_configs:
            if api_key and api_key.strip() and not api_key.startswith("your_"):
                providers.append(ProviderConfig(
                    provider=provider,
                    api_key=api_key,
                    default_model=default_model,
                    priority=priority
                ))
                logger.info(f"Configured provider: {provider} with priority {priority}")
            else:
                logger.warning(f"Skipping provider {provider}: no valid API key")
        
        if not providers:
            logger.error("No valid LLM providers configured")
            raise InvalidAPIKey("No valid API keys found for any LLM provider")
        
        return providers
    
    def _create_fallback_chain(self) -> List[ProviderConfig]:
        """Create fallback chain ordered by priority."""
        # Sort by priority (lower number = higher priority)
        chain = sorted(self.providers, key=lambda p: p.priority)
        
        # Move primary provider to front if it exists in the chain
        primary_config = next((p for p in chain if p.provider == self.primary_provider), None)
        if primary_config:
            chain.remove(primary_config)
            chain.insert(0, primary_config)
        
        return chain
    
    async def validate_api_key(self, provider: str) -> bool:
        """Validate API key for a specific provider with enhanced health tracking."""
        try:
            provider_config = next((p for p in self.providers if p.provider == provider), None)
            if not provider_config:
                return False
            
            # Make a simple test request to validate the API key
            test_request = LLMRequest(
                prompt="Test",
                max_tokens=1,
                temperature=0.1
            )
            
            start_time = time.time()
            await self._make_provider_request(provider_config, test_request)
            response_time = (time.time() - start_time) * 1000
            
            # Update comprehensive health status
            health = self.provider_health[provider]
            circuit_breaker = self.circuit_breakers[provider]
            
            health.status = ProviderStatus.HEALTHY
            health.last_check = datetime.utcnow()
            health.last_success = datetime.utcnow()
            health.response_time_ms = response_time
            health.last_error = None
            health.success_count = circuit_breaker.success_count
            health.consecutive_failures = circuit_breaker.consecutive_failures
            health.failure_rate = circuit_breaker.get_failure_rate()
            health.circuit_breaker_state = circuit_breaker.state
            health.is_degraded = response_time > 5000  # Mark as degraded if response time > 5s
            health.degradation_reason = f"Slow response time: {response_time:.2f}ms" if health.is_degraded else None
            
            logger.info(f"API key validation successful for {provider} (response time: {response_time:.2f}ms)")
            return True
            
        except Exception as e:
            # Update health status for failure
            health = self.provider_health[provider]
            circuit_breaker = self.circuit_breakers[provider]
            
            health.status = ProviderStatus.FAILED
            health.last_check = datetime.utcnow()
            health.last_error = str(e)
            health.error_count += 1
            health.consecutive_failures = circuit_breaker.consecutive_failures
            health.failure_rate = circuit_breaker.get_failure_rate()
            health.circuit_breaker_state = circuit_breaker.state
            health.recovery_attempts += 1
            
            logger.error(f"API key validation failed for {provider}: {str(e)}")
            return False
    
    async def check_provider_health(self, provider: str) -> ProviderHealth:
        """Check health status of a specific provider with automatic recovery detection."""
        circuit_breaker = self.circuit_breakers[provider]
        
        # If circuit breaker is open, check if we should attempt recovery
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if circuit_breaker._should_attempt_reset():
                logger.info(f"Attempting automatic recovery for {provider}")
                is_healthy = await self.validate_api_key(provider)
                if is_healthy:
                    logger.info(f"Automatic recovery successful for {provider}")
                else:
                    logger.warning(f"Automatic recovery failed for {provider}")
            else:
                # Don't validate if circuit breaker is still open
                is_healthy = False
        else:
            is_healthy = await self.validate_api_key(provider)
        
        health = self.provider_health[provider]
        health.circuit_breaker_state = circuit_breaker.state
        
        # Update degraded status based on circuit breaker state and failure rate
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            health.is_degraded = True
            health.degradation_reason = "Circuit breaker is OPEN"
        elif circuit_breaker.get_failure_rate() > 0.5:  # More than 50% failure rate
            health.is_degraded = True
            health.degradation_reason = f"High failure rate: {circuit_breaker.get_failure_rate():.2%}"
        elif health.response_time_ms and health.response_time_ms > 10000:  # Slow responses
            health.is_degraded = True
            health.degradation_reason = f"Slow response time: {health.response_time_ms:.2f}ms"
        
        return health
    
    def get_circuit_breaker_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed circuit breaker metrics for all providers."""
        return {
            provider: circuit_breaker.get_metrics()
            for provider, circuit_breaker in self.circuit_breakers.items()
        }
    
    async def get_all_provider_health(self) -> Dict[str, ProviderHealth]:
        """Get health status for all configured providers."""
        health_checks = []
        for provider_config in self.providers:
            health_checks.append(self.check_provider_health(provider_config.provider.value))
        
        await asyncio.gather(*health_checks, return_exceptions=True)
        return self.provider_health.copy()
    
    def get_available_providers(self) -> List[str]:
        """Get list of providers that are currently available (circuit breaker allows execution)."""
        available = []
        for provider_config in self.fallback_chain:
            provider_key = provider_config.provider.value
            if self.circuit_breakers[provider_key].can_execute():
                available.append(provider_key)
        return available
    
    def _calculate_backoff_delay(self, attempt: int, base_delay: float = None) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        if base_delay is None:
            base_delay = self.retry_config.base_delay
        
        # Calculate exponential backoff
        delay = min(
            base_delay * (self.retry_config.backoff_multiplier ** attempt),
            self.retry_config.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.retry_config.jitter:
            import random
            jitter = random.uniform(0.1, 0.3) * delay
            delay += jitter
        
        return delay
    
    def _setup_client(self):
        """Initialize the HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_headers(self, provider_config: ProviderConfig) -> Dict[str, str]:
        """Get headers for the HTTP client based on the provider."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if provider_config.provider == LLMProvider.OPENAI:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        elif provider_config.provider == LLMProvider.ANTHROPIC:
            headers["x-api-key"] = provider_config.api_key
            headers["anthropic-version"] = "2023-06-01"
        elif provider_config.provider == LLMProvider.TOGETHER:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        elif provider_config.provider == LLMProvider.MISTRAL:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        elif provider_config.provider == LLMProvider.KIWI:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        elif provider_config.provider == LLMProvider.HUGGINGFACE:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        
        return headers
    
    def _get_api_url(self, provider: LLMProvider) -> str:
        """Get the API URL for the provider."""
        urls = {
            LLMProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
            LLMProvider.TOGETHER: "https://api.together.xyz/v1/chat/completions",
            LLMProvider.MISTRAL: "https://api.mistral.ai/v1/chat/completions",
            LLMProvider.KIWI: "https://api.kiwi.ai/v1/chat/completions",  # Placeholder URL
            LLMProvider.HUGGINGFACE: "https://api-inference.huggingface.co/models/",
        }
        return urls.get(provider, urls[LLMProvider.OPENAI])
    
    def _format_request(self, provider_config: ProviderConfig, request: LLMRequest) -> Dict[str, Any]:
        """Format the request for the provider's API."""
        model = request.model or provider_config.default_model
        
        if provider_config.provider == LLMProvider.ANTHROPIC:
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
        elif provider_config.provider == LLMProvider.HUGGINGFACE:
            # Hugging Face has a different format
            payload = {
                "inputs": request.prompt,
                "parameters": {
                    "max_new_tokens": request.max_tokens or 4000,
                    "temperature": request.temperature or 0.7,
                    "return_full_text": False,
                }
            }
            if request.top_p is not None:
                payload["parameters"]["top_p"] = request.top_p
            if request.stop:
                payload["parameters"]["stop"] = request.stop
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
    
    async def _make_provider_request(self, provider_config: ProviderConfig, request: LLMRequest) -> LLMResponse:
        """Make a request to a specific provider."""
        if self.client is None:
            self._setup_client()
        
        url = self._get_api_url(provider_config.provider)
        if provider_config.provider == LLMProvider.HUGGINGFACE:
            # For Hugging Face, append the model to the URL
            model = request.model or provider_config.default_model
            url = f"{url}{model}"
        
        headers = self._get_headers(provider_config)
        payload = self._format_request(provider_config, request)
        
        start_time = time.time()
        
        try:
            response = await self.client.post(
                url,
                headers=headers,
                json=payload,
                timeout=provider_config.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse response based on provider
            if provider_config.provider == LLMProvider.ANTHROPIC:
                return LLMResponse(
                    text=result["content"][0]["text"],
                    model=result["model"],
                    provider=provider_config.provider.value,
                    usage={
                        "prompt_tokens": result["usage"]["input_tokens"],
                        "completion_tokens": result["usage"]["output_tokens"],
                        "total_tokens": result["usage"]["input_tokens"] + result["usage"]["output_tokens"],
                    },
                    metadata={"response_time_ms": response_time}
                )
            elif provider_config.provider == LLMProvider.HUGGINGFACE:
                # Hugging Face returns different format
                text = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
                return LLMResponse(
                    text=text,
                    model=request.model or provider_config.default_model,
                    provider=provider_config.provider.value,
                    usage={},  # Hugging Face doesn't provide usage info
                    metadata={"response_time_ms": response_time}
                )
            else:  # OpenAI, Together, Mistral, etc.
                return LLMResponse(
                    text=result["choices"][0]["message"]["content"],
                    model=result["model"],
                    provider=provider_config.provider.value,
                    usage=result.get("usage", {}),
                    metadata={"response_time_ms": response_time}
                )
                
        except httpx.HTTPStatusError as e:
            response_time = (time.time() - start_time) * 1000
            
            # Check for authentication errors
            if e.response.status_code in [401, 403]:
                raise InvalidAPIKey(f"{provider_config.provider.value} API")
            
            error_msg = f"HTTP error from {provider_config.provider.value} API: {str(e)}"
            logger.error(f"{error_msg}. Response: {e.response.text}")
            raise LLMError(error_msg) from e
            
        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Error parsing response from {provider_config.provider.value} API: {str(e)}"
            logger.error(error_msg)
            raise LLMError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Error calling {provider_config.provider.value} API: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise LLMError(error_msg) from e
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using provider fallback chain."""
        last_error = None
        attempted_providers = []
        
        for provider_config in self.fallback_chain:
            provider_key = provider_config.provider.value
            circuit_breaker = self.circuit_breakers[provider_key]
            
            # Check if circuit breaker allows execution
            if not circuit_breaker.can_execute():
                logger.warning(f"Circuit breaker OPEN for {provider_key}, skipping")
                continue
            
            attempted_providers.append(provider_key)
            
            try:
                logger.info(f"Attempting request with provider: {provider_key}")
                
                # Implement enhanced exponential backoff retry logic
                max_retries = min(provider_config.max_retries, self.retry_config.max_attempts)
                for attempt in range(max_retries + 1):
                    try:
                        response = await self._make_provider_request(provider_config, request)
                        
                        # Record success
                        circuit_breaker.record_success()
                        
                        # Update comprehensive health status
                        health = self.provider_health[provider_key]
                        health.status = ProviderStatus.HEALTHY
                        health.error_count = 0
                        health.success_count = circuit_breaker.success_count
                        health.consecutive_failures = 0
                        health.failure_rate = circuit_breaker.get_failure_rate()
                        health.last_success = datetime.utcnow()
                        health.is_degraded = False
                        health.degradation_reason = None
                        
                        logger.info(f"Successfully generated text using {provider_key} (attempt {attempt + 1})")
                        return response
                        
                    except (InvalidAPIKey, LLMError) as e:
                        if attempt < max_retries:
                            # Enhanced exponential backoff with jitter
                            wait_time = self._calculate_backoff_delay(attempt)
                            logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed for {provider_key}, retrying in {wait_time:.2f}s: {str(e)}")
                            await asyncio.sleep(wait_time)
                        else:
                            raise e
                
            except InvalidAPIKey as e:
                # Authentication errors should not trigger circuit breaker but should update health
                logger.error(f"Authentication failed for {provider_key}: {str(e)}")
                
                health = self.provider_health[provider_key]
                health.status = ProviderStatus.FAILED
                health.last_error = str(e)
                health.error_count += 1
                health.recovery_attempts += 1
                health.is_degraded = True
                health.degradation_reason = "Authentication failure"
                
                last_error = e
                continue
                
            except Exception as e:
                # Record failure and trigger circuit breaker
                circuit_breaker.record_failure()
                
                # Update comprehensive health status
                health = self.provider_health[provider_key]
                health.status = ProviderStatus.FAILED
                health.error_count += 1
                health.consecutive_failures = circuit_breaker.consecutive_failures
                health.failure_rate = circuit_breaker.get_failure_rate()
                health.last_error = str(e)
                health.circuit_breaker_state = circuit_breaker.state
                health.recovery_attempts += 1
                health.is_degraded = True
                health.degradation_reason = f"Request failure: {str(e)[:100]}"
                
                logger.error(f"Provider {provider_key} failed (consecutive failures: {circuit_breaker.consecutive_failures}): {str(e)}")
                last_error = e
                continue
        
        # All providers failed
        error_msg = f"All LLM providers failed. Attempted: {attempted_providers}"
        if last_error:
            error_msg += f". Last error: {str(last_error)}"
        
        logger.error(error_msg)
        raise LLMError(error_msg)
    
    async def switch_provider(self, new_provider: str) -> bool:
        """Switch to a different provider."""
        provider_config = next((p for p in self.providers if p.provider == new_provider), None)
        if not provider_config:
            logger.error(f"Provider {new_provider} not configured")
            return False
        
        # Validate the new provider
        if await self.validate_api_key(new_provider):
            # Move the provider to the front of the fallback chain
            self.fallback_chain.remove(provider_config)
            self.fallback_chain.insert(0, provider_config)
            self.primary_provider = new_provider
            
            logger.info(f"Successfully switched to provider: {new_provider}")
            return True
        else:
            logger.error(f"Failed to switch to provider {new_provider}: API key validation failed")
            return False
    
    async def force_recovery_attempt(self, provider: str) -> bool:
        """Force a recovery attempt for a failed provider."""
        if provider not in self.circuit_breakers:
            logger.error(f"Provider {provider} not found")
            return False
        
        circuit_breaker = self.circuit_breakers[provider]
        logger.info(f"Forcing recovery attempt for {provider} (current state: {circuit_breaker.state})")
        
        # Temporarily allow execution regardless of circuit breaker state
        original_state = circuit_breaker.state
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.half_open_calls = 0
        
        try:
            success = await self.validate_api_key(provider)
            if success:
                logger.info(f"Forced recovery successful for {provider}")
                return True
            else:
                # Restore original state if recovery failed
                circuit_breaker.state = original_state
                logger.warning(f"Forced recovery failed for {provider}")
                return False
        except Exception as e:
            # Restore original state if recovery failed
            circuit_breaker.state = original_state
            logger.error(f"Forced recovery failed for {provider}: {str(e)}")
            return False
    
    def reset_circuit_breaker(self, provider: str) -> bool:
        """Manually reset a circuit breaker to CLOSED state."""
        if provider not in self.circuit_breakers:
            logger.error(f"Provider {provider} not found")
            return False
        
        circuit_breaker = self.circuit_breakers[provider]
        old_state = circuit_breaker.state
        circuit_breaker._reset()
        
        # Reset health status
        health = self.provider_health[provider]
        health.status = ProviderStatus.HEALTHY
        health.circuit_breaker_state = CircuitBreakerState.CLOSED
        health.consecutive_failures = 0
        health.recovery_attempts = 0
        health.is_degraded = False
        health.degradation_reason = None
        
        logger.info(f"Circuit breaker for {provider} manually reset from {old_state} to CLOSED")
        return True
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()

# Create a singleton instance
llm_service = LLMService()
