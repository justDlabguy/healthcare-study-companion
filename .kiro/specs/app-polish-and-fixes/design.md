# Design Document

## Overview

This design addresses critical issues and polishing needs for the Healthcare Study Companion application after deployment to Vercel (frontend) and Render (backend). The design focuses on fixing API authentication issues, updating deployment configurations, enhancing error handling, optimizing performance, and improving the overall user experience.

## Architecture

### Current Architecture

- **Frontend**: Next.js 14 deployed on Vercel
- **Backend**: FastAPI deployed on Render (previously configured for Railway)
- **Database**: TiDB Serverless (MySQL-compatible)
- **AI Services**: Multiple LLM providers (OpenAI, Mistral, Anthropic, Kiwi AI)
- **Authentication**: JWT-based with secure token management

### Key Issues Identified

1. **API Authentication**: Mistral API key expired/invalid causing flashcard generation failures
2. **Deployment Mismatch**: Configuration still references Railway instead of Render
3. **Error Handling**: Insufficient user feedback and error recovery mechanisms
4. **Performance**: Missing optimization for production deployment
5. **Monitoring**: Limited observability and health checking

## Components and Interfaces

### 1. API Authentication Service Enhancement

#### Current Implementation Issues

- Single API key dependency without fallback
- No retry logic for authentication failures
- Limited error context for debugging

#### Enhanced Design

```typescript
interface LLMProviderConfig {
  provider: "openai" | "mistral" | "anthropic" | "kiwi";
  apiKey: string;
  fallbackProvider?: string;
  retryConfig: {
    maxRetries: number;
    backoffMultiplier: number;
    maxBackoffMs: number;
  };
}

interface LLMService {
  generateFlashcards(
    content: string,
    options: FlashcardOptions
  ): Promise<Flashcard[]>;
  validateApiKey(provider: string): Promise<boolean>;
  switchProvider(newProvider: string): Promise<void>;
}
```

#### Implementation Strategy

- **Provider Fallback Chain**: OpenAI → Mistral → Anthropic → Kiwi AI
- **Circuit Breaker Pattern**: Temporarily disable failing providers
- **API Key Validation**: Periodic health checks for all configured providers
- **Graceful Degradation**: Mock responses when all providers fail

### 2. Render Deployment Configuration

#### Configuration Updates Needed

```python
# backend/app/config.py - Render-specific settings
class RenderSettings:
    # Render uses different environment variable patterns
    port: int = int(os.getenv("PORT", 8000))
    host: str = "0.0.0.0"

    # Render-specific database URL format
    database_url: str = os.getenv("DATABASE_URL", "")

    # CORS origins for Vercel deployment
    cors_origins: List[str] = [
        "https://*.vercel.app",
        "https://healthcare-study-companion.vercel.app"
    ]
```

#### Deployment Pipeline

```yaml
# render.yaml
services:
  - type: web
    name: healthcare-study-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: healthcare-study-db
          property: connectionString
```

### 3. Enhanced Error Handling System

#### Frontend Error Boundary Enhancement

```typescript
interface ErrorState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
  retryCount: number;
}

interface ErrorRecoveryStrategy {
  canRecover: boolean;
  recoveryAction: () => Promise<void>;
  fallbackComponent?: React.ComponentType;
}
```

#### Backend Error Response Standardization

```python
class APIError(BaseModel):
    error_id: str
    error_type: str
    message: str
    details: Optional[Dict[str, Any]]
    retry_after: Optional[int]
    recovery_suggestions: List[str]

class ErrorHandler:
    def handle_llm_error(self, error: Exception) -> APIError
    def handle_database_error(self, error: Exception) -> APIError
    def handle_validation_error(self, error: Exception) -> APIError
```

### 4. Performance Optimization Components

#### Frontend Optimizations

```typescript
// Lazy loading for heavy components
const FlashcardInterface = lazy(() => import("./flashcard-interface"));
const DocumentUpload = lazy(() => import("./document-upload"));

// API response caching
interface CacheConfig {
  ttl: number;
  maxSize: number;
  strategy: "lru" | "fifo";
}

// Progressive loading for large datasets
interface PaginationConfig {
  pageSize: number;
  prefetchPages: number;
  virtualScrolling: boolean;
}
```

#### Backend Performance Enhancements

```python
# Connection pooling optimization
class DatabaseConfig:
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600

# Background task processing
class TaskQueue:
    def process_document_async(self, document_id: str) -> str
    def generate_flashcards_async(self, content: str) -> str
    def cleanup_expired_sessions(self) -> None
```

### 5. Monitoring and Health Check System

#### Health Check Endpoints

```python
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, ServiceHealth]

class ServiceHealth(BaseModel):
    status: str
    response_time_ms: float
    last_check: datetime
    error_count: int
```

#### Monitoring Dashboard

```typescript
interface MonitoringMetrics {
  apiResponseTimes: TimeSeriesData;
  errorRates: ErrorRateData;
  userSessions: SessionData;
  systemHealth: HealthStatus;
}
```

## Data Models

### Enhanced Configuration Model

```python
class AppConfig(BaseSettings):
    # Deployment-specific settings
    deployment_platform: Literal["render", "railway", "local"]

    # LLM provider configuration with fallbacks
    primary_llm_provider: str
    fallback_llm_providers: List[str]

    # Performance settings
    cache_ttl_seconds: int = 3600
    max_concurrent_requests: int = 100

    # Monitoring settings
    health_check_interval: int = 60
    error_reporting_enabled: bool = True
```

### Error Tracking Model

```python
class ErrorLog(Base):
    __tablename__ = "error_logs"

    id: int = Column(Integer, primary_key=True)
    error_id: str = Column(String(36), unique=True)
    error_type: str = Column(String(100))
    message: str = Column(Text)
    stack_trace: str = Column(Text)
    user_id: Optional[int] = Column(Integer, ForeignKey("users.id"))
    request_path: str = Column(String(500))
    timestamp: datetime = Column(DateTime, default=datetime.utcnow)
    resolved: bool = Column(Boolean, default=False)
```

## Error Handling

### Comprehensive Error Strategy

#### 1. API Authentication Errors

```python
class LLMAuthenticationError(Exception):
    def __init__(self, provider: str, status_code: int):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"Authentication failed for {provider}: {status_code}")

# Recovery strategy
async def handle_auth_error(error: LLMAuthenticationError):
    if error.status_code == 401:
        # Try fallback provider
        await switch_to_fallback_provider()
    elif error.status_code == 429:
        # Rate limited - implement backoff
        await implement_exponential_backoff()
```

#### 2. Frontend Error Recovery

```typescript
class ErrorRecoveryService {
  async recoverFromApiError(error: ApiError): Promise<void> {
    switch (error.type) {
      case "AUTHENTICATION_ERROR":
        await this.refreshAuthToken();
        break;
      case "NETWORK_ERROR":
        await this.retryWithBackoff();
        break;
      case "VALIDATION_ERROR":
        this.showValidationFeedback(error.details);
        break;
    }
  }
}
```

#### 3. Database Connection Resilience

```python
class DatabaseResilience:
    async def execute_with_retry(self, query, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await self.execute(query)
            except ConnectionError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
```

## Testing Strategy

### 1. API Integration Testing

```python
class TestLLMIntegration:
    async def test_provider_fallback(self):
        # Test automatic fallback when primary provider fails
        pass

    async def test_authentication_recovery(self):
        # Test recovery from authentication failures
        pass

    async def test_rate_limit_handling(self):
        # Test proper handling of rate limits
        pass
```

### 2. Frontend Error Boundary Testing

```typescript
describe("Error Boundary", () => {
  it("should recover from API errors gracefully", () => {
    // Test error recovery mechanisms
  });

  it("should display user-friendly error messages", () => {
    // Test error message display
  });

  it("should provide retry functionality", () => {
    // Test retry mechanisms
  });
});
```

### 3. Performance Testing

```python
class TestPerformance:
    async def test_concurrent_requests(self):
        # Test system under concurrent load
        pass

    async def test_database_connection_pooling(self):
        # Test connection pool efficiency
        pass

    async def test_response_times(self):
        # Test API response time requirements
        pass
```

## Security Considerations

### 1. API Key Management

- Store API keys in environment variables only
- Implement key rotation mechanism
- Use different keys for different environments
- Monitor API key usage and quotas

### 2. CORS Configuration

```python
# Render-specific CORS setup
CORS_ORIGINS = [
    "https://healthcare-study-companion.vercel.app",
    "https://*.vercel.app",  # For preview deployments
]

# Development origins (only in non-production)
if settings.environment != "production":
    CORS_ORIGINS.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ])
```

### 3. Rate Limiting

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def check_rate_limit(self, user_id: str) -> bool:
        # Implement sliding window rate limiting
        pass
```

## Deployment Architecture

### Vercel Frontend Configuration

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://healthcare-study-backend.onrender.com",
    "NEXT_PUBLIC_ENVIRONMENT": "production"
  }
}
```

### Render Backend Configuration

```yaml
services:
  - type: web
    name: healthcare-study-backend
    env: python
    plan: starter
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
    healthCheckPath: "/healthz"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: healthcare-study-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: JWT_SECRET
        generateValue: true
```

This design provides a comprehensive approach to fixing the identified issues while enhancing the overall robustness and user experience of the Healthcare Study Companion application.
