from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator, model_validator, Field, validator
from typing import List, Optional, Dict, Any, Literal
import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            'local.env',  # Primary env file - highest priority
            '.env.development',  # Development fallback
        ],
        env_file_encoding='utf-8',
        extra='ignore',  # Ignore extra fields in environment variables
        case_sensitive=False
    )
    
    app_name: str = "Healthcare Study Companion API"
    environment: Literal["development", "staging", "production"] = "development"

    # Database configuration
    database_url: Optional[str] = None
    database_host: str = "localhost"
    database_port: int = 4000  # TiDB default port
    database_user: str = "root"
    database_password: str = ""
    database_name: str = "healthcare_study"
    
    # JWT configuration
    jwt_secret: str = "SI1ydIUGwGo7m2MsPjtQeqGNQYnoBNX0UpVCVn2g6p8"
    
    @property
    def tidb_connection_string(self) -> str:
        """Generate database connection string."""
        if self.database_url:
            return self.database_url
        # Default to MySQL/TiDB format if no specific URL is provided
        return f"mysql+pymysql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @model_validator(mode='after')
    def validate_database_url(self) -> 'Settings':
        """Ensure database URL is properly formatted."""
        if not self.database_url:
            self.database_url = self.tidb_connection_string
        elif not self.database_url.startswith(("mysql+", "mysql://", "sqlite://", "sqlite:///")):
            # Only convert to MySQL format if it doesn't look like SQLite
            if not self.database_url.endswith(".db") and "sqlite" not in self.database_url.lower():
                self.database_url = f"mysql+pymysql://{self.database_url}" if "://" not in self.database_url else self.database_url
        return self
    
    # CORS - use a simple string for development
    # Set to "*" to allow all origins, or a specific origin like "http://localhost:3000"
    cors_origins: str = "*"
    
    # LLM Configuration
    llm_provider: str = "openai"  # Options: 'openai', 'anthropic', 'huggingface', 'together', 'mistral', 'kiwi'
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    kiwi_api_key: Optional[str] = None
    
    # Model configurations
    default_llm_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    llm_model_id: str = "mistral-small"
    embedding_model_id: str = "mistral-embed"
    
    # Rate limiting and generation parameters
    llm_rate_limit_per_minute: int = 60
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.7
    
    # Circuit breaker configuration
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_half_open_max_calls: int = 3
    
    # Exponential backoff configuration
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_backoff_multiplier: float = 2.0
    
    # API key validation and health check configuration
    api_key_validation_interval_minutes: int = 30
    health_check_timeout_seconds: int = 10
    api_usage_monitoring_enabled: bool = True
    api_quota_warning_threshold: float = 0.8  # Warn at 80% of quota
    
    # API key rotation configuration
    api_key_rotation_enabled: bool = False
    api_key_rotation_interval_hours: int = 24
    api_key_backup_count: int = 3
    
    @property
    def allowed_origins(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@example.com"
    email_enabled: bool = False  # Set to True when email is properly configured
    
    # Logging configuration
    log_level: str = "INFO"
    structured_logging: bool = True
    
    # Performance configuration
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    max_concurrent_ai_requests: int = 10
    max_concurrent_document_processing: int = 5
    
    # File upload configuration
    max_file_size_mb: int = 50
    allowed_file_types: str = "pdf,txt,docx,md"
    
    # Deployment configuration
    auto_rollback_on_failure: bool = True
    railway_deployment_id: Optional[str] = None
    railway_git_commit_sha: Optional[str] = None
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]
    
    @model_validator(mode='after')
    def validate_configuration(self) -> 'Settings':
        """Validate the complete configuration and check for required values."""
        errors = []
        warnings = []
        
        # Validate database configuration
        if not self.database_url and not all([
            self.database_host, 
            self.database_user, 
            self.database_name
        ]):
            errors.append("Database configuration incomplete: Either DATABASE_URL or individual database parameters must be provided")
        
        # Check database URL format and SSL for production
        if self.database_url:
            if not self.database_url.startswith(("mysql+", "mysql://", "sqlite://", "sqlite:///")):
                warnings.append("Database URL should use mysql+ driver for better compatibility")
            
            if (self.environment == "production" and 
                "ssl" not in self.database_url.lower() and 
                not self.database_url.startswith("sqlite")):
                warnings.append("SSL not configured for production database - consider adding SSL parameters")
        
        # Validate JWT secret
        weak_secrets = ["change-me", "dev-secret-key-change-me-in-production", "secret", "password"]
        if self.jwt_secret.lower() in weak_secrets:
            if self.environment == "production":
                errors.append("JWT_SECRET must be set to a secure value in production environment")
            else:
                warnings.append("JWT_SECRET is using a default/weak value - should be changed for security")
        
        if len(self.jwt_secret) < 32:
            if self.environment == "production":
                errors.append("JWT_SECRET is too short - must be at least 32 characters in production")
            else:
                warnings.append("JWT_SECRET is too short - should be at least 32 characters")
        
        # Validate LLM configuration
        llm_key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "huggingface": self.huggingface_api_key,
            "together": self.together_api_key,
            "mistral": self.mistral_api_key,
            "kiwi": self.kiwi_api_key
        }
        
        if self.llm_provider not in llm_key_mapping:
            errors.append(f"Invalid LLM_PROVIDER: {self.llm_provider}. Must be one of: {list(llm_key_mapping.keys())}")
        else:
            api_key = llm_key_mapping[self.llm_provider]
            if not api_key:
                errors.append(f"API key for {self.llm_provider} is required when LLM_PROVIDER is set to {self.llm_provider}")
            elif api_key.startswith("your_") or api_key.endswith("_here"):
                errors.append(f"API key for {self.llm_provider} appears to be a placeholder value")
        
        # Validate LLM parameters
        if self.llm_temperature < 0 or self.llm_temperature > 2:
            warnings.append("LLM_TEMPERATURE should be between 0 and 2")
        
        if self.llm_rate_limit_per_minute < 1:
            errors.append("LLM_RATE_LIMIT_PER_MINUTE must be at least 1")
        elif self.llm_rate_limit_per_minute > 1000:
            warnings.append("LLM_RATE_LIMIT_PER_MINUTE is very high - may exceed API provider limits")
        
        # Validate email configuration if enabled
        if self.email_enabled:
            if not all([self.smtp_username, self.smtp_password]):
                errors.append("Email is enabled but SMTP credentials are missing")
            
            if not self.smtp_from_email or "@" not in self.smtp_from_email:
                errors.append("Invalid or missing SMTP_FROM_EMAIL address")
        elif self.environment == "production":
            warnings.append("Email functionality is disabled in production - consider enabling for notifications")
        
        # Validate CORS origins
        if self.environment == "production" and self.cors_origins == "*":
            warnings.append("CORS allows all origins (*) in production - consider restricting to specific domains")
        
        if self.environment == "production" and "localhost" in self.cors_origins:
            warnings.append("CORS includes localhost in production - should be removed")
        
        # Validate performance settings
        if self.db_pool_size < 1:
            errors.append("DB_POOL_SIZE must be at least 1")
        elif self.db_pool_size > 100:
            warnings.append("DB_POOL_SIZE is very high - may cause resource issues")
        
        if self.max_concurrent_ai_requests < 1:
            errors.append("MAX_CONCURRENT_AI_REQUESTS must be at least 1")
        elif self.max_concurrent_ai_requests > 50:
            warnings.append("MAX_CONCURRENT_AI_REQUESTS is very high - may cause resource issues")
        
        if self.max_concurrent_document_processing < 1:
            errors.append("MAX_CONCURRENT_DOCUMENT_PROCESSING must be at least 1")
        
        if self.max_file_size_mb < 1:
            errors.append("MAX_FILE_SIZE_MB must be at least 1")
        elif self.max_file_size_mb > 500:
            warnings.append("MAX_FILE_SIZE_MB is very large - may cause memory issues")
        
        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid LOG_LEVEL: {self.log_level}. Must be one of: {valid_log_levels}")
        
        if self.environment == "production" and self.log_level == "DEBUG":
            warnings.append("DEBUG logging enabled in production - consider using INFO or WARNING")
        
        if self.environment == "production" and not self.structured_logging:
            warnings.append("Structured logging disabled in production - recommended for monitoring")
        
        # Environment-specific validations
        if self.environment == "production":
            # Check for development-specific values
            if "dev" in self.app_name.lower():
                warnings.append("App name contains 'dev' in production environment")
        
        # Log validation results
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_msg)
            if self.environment == "production":
                raise ConfigurationError(error_msg)
            else:
                logger.warning("Configuration errors detected but continuing in non-production environment")
        
        if warnings:
            warning_msg = "Configuration warnings:\n" + "\n".join(f"  - {warning}" for warning in warnings)
            logger.warning(warning_msg)
        
        if not errors and not warnings:
            logger.info(f"Configuration validation passed for environment: {self.environment}")
        
        return self
    
    def get_api_key_for_provider(self, provider: Optional[str] = None) -> Optional[str]:
        """Get the API key for the specified provider (or current provider)."""
        target_provider = provider or self.llm_provider
        key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "huggingface": self.huggingface_api_key,
            "together": self.together_api_key,
            "mistral": self.mistral_api_key,
            "kiwi": self.kiwi_api_key
        }
        return key_mapping.get(target_provider)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        return {
            "level": self.log_level.upper(),
            "structured": self.structured_logging,
            "format": "json" if self.structured_logging else "text"
        }


def get_settings() -> Settings:
    """Get validated settings instance with environment-aware loading."""
    try:
        # Determine which environment files to load based on ENVIRONMENT variable
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        env_files = ['local.env']  # Always load local.env first
        
        if env == "development":
            env_files.append('.env.development')
        elif env == "staging":
            env_files.append('.env.staging')
        elif env == "production":
            env_files.append('.env.production')
        else:
            # Default to development
            env_files.append('.env.development')
        
        # Create settings with dynamic env_file list
        class DynamicSettings(Settings):
            model_config = SettingsConfigDict(
                env_file=env_files,
                env_file_encoding='utf-8',
                extra='ignore',
                case_sensitive=False
            )
        
        return DynamicSettings()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        if os.getenv("ENVIRONMENT") == "production":
            sys.exit(1)
        raise

settings = get_settings()
