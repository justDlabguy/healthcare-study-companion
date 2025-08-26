#!/usr/bin/env python3
"""
Environment Configuration Validation Script

This script validates that all required environment variables are properly configured
for the Healthcare Study Companion application.

Usage:
    python scripts/validate_environment.py [--environment ENV] [--strict]
    
Arguments:
    --environment: Target environment (development, staging, production)
    --strict: Fail on warnings (useful for CI/CD)
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum

# Add the app directory to the path so we can import our config
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.config import Settings, ConfigurationError
except ImportError as e:
    print(f"Error importing configuration: {e}")
    print("Make sure you're running this script from the backend directory")
    sys.exit(1)


class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationResult:
    level: ValidationLevel
    category: str
    message: str
    variable: Optional[str] = None
    suggestion: Optional[str] = None


class EnvironmentValidator:
    """Validates environment configuration for different deployment environments."""
    
    def __init__(self, environment: str = "development", strict: bool = False):
        self.environment = environment
        self.strict = strict
        self.results: List[ValidationResult] = []
        
    def validate(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation checks and return success status and results."""
        self.results = []
        
        # Load settings and catch configuration errors
        try:
            settings = Settings()
        except ConfigurationError as e:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Configuration",
                message=f"Configuration validation failed: {e}",
                suggestion="Check your environment variables and fix the reported issues"
            ))
            return False, self.results
        except Exception as e:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Configuration",
                message=f"Failed to load configuration: {e}",
                suggestion="Check that all required environment variables are set"
            ))
            return False, self.results
        
        # Run validation checks
        self._validate_database_config(settings)
        self._validate_security_config(settings)
        self._validate_llm_config(settings)
        self._validate_email_config(settings)
        self._validate_performance_config(settings)
        self._validate_deployment_config(settings)
        self._validate_environment_specific(settings)
        
        # Check if validation passed
        has_errors = any(r.level == ValidationLevel.ERROR for r in self.results)
        has_warnings = any(r.level == ValidationLevel.WARNING for r in self.results)
        
        success = not has_errors and (not self.strict or not has_warnings)
        return success, self.results
    
    def _validate_database_config(self, settings: Settings) -> None:
        """Validate database configuration."""
        if not settings.database_url:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Database",
                message="DATABASE_URL is not configured",
                variable="DATABASE_URL",
                suggestion="Set DATABASE_URL or individual database connection parameters"
            ))
            return
        
        # Check database URL format
        if not settings.database_url.startswith(("mysql+", "mysql://")):
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="Database",
                message="Database URL should use mysql+ driver for better compatibility",
                variable="DATABASE_URL",
                suggestion="Use mysql+pymysql:// instead of mysql://"
            ))
        
        # Check SSL configuration for production
        if self.environment == "production":
            if "ssl" not in settings.database_url.lower():
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Database",
                    message="SSL not configured for production database",
                    variable="DATABASE_URL",
                    suggestion="Add SSL parameters to DATABASE_URL for production security"
                ))
        
        # Validate connection pool settings
        if settings.db_pool_size < 1:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Database",
                message="Database pool size must be at least 1",
                variable="DB_POOL_SIZE"
            ))
        
        if settings.db_pool_size > 100:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="Database",
                message="Database pool size is very high, may cause resource issues",
                variable="DB_POOL_SIZE",
                suggestion="Consider reducing DB_POOL_SIZE to 20-50 for most applications"
            ))
    
    def _validate_security_config(self, settings: Settings) -> None:
        """Validate security configuration."""
        # JWT Secret validation
        weak_secrets = ["change-me", "dev-secret-key-change-me-in-production", "secret", "password"]
        if settings.jwt_secret.lower() in weak_secrets:
            level = ValidationLevel.ERROR if self.environment == "production" else ValidationLevel.WARNING
            self.results.append(ValidationResult(
                level=level,
                category="Security",
                message="JWT secret is using a default/weak value",
                variable="JWT_SECRET",
                suggestion="Generate a strong, random JWT secret key"
            ))
        
        if len(settings.jwt_secret) < 32:
            level = ValidationLevel.ERROR if self.environment == "production" else ValidationLevel.WARNING
            self.results.append(ValidationResult(
                level=level,
                category="Security",
                message="JWT secret is too short (should be at least 32 characters)",
                variable="JWT_SECRET",
                suggestion="Use a longer, more secure JWT secret"
            ))
        
        # CORS validation
        if self.environment == "production" and settings.cors_origins == "*":
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="Security",
                message="CORS allows all origins in production",
                variable="CORS_ORIGINS",
                suggestion="Restrict CORS_ORIGINS to specific domains in production"
            ))
        
        # Check for localhost in production CORS
        if self.environment == "production" and "localhost" in settings.cors_origins:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="Security",
                message="CORS includes localhost in production",
                variable="CORS_ORIGINS",
                suggestion="Remove localhost from CORS_ORIGINS in production"
            ))
    
    def _validate_llm_config(self, settings: Settings) -> None:
        """Validate LLM/AI configuration."""
        # Check if API key is set for the selected provider
        api_key = settings.get_api_key_for_provider()
        if not api_key:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="LLM",
                message=f"API key not configured for LLM provider '{settings.llm_provider}'",
                variable=f"{settings.llm_provider.upper()}_API_KEY",
                suggestion=f"Set the API key for {settings.llm_provider}"
            ))
        elif api_key.startswith("your_") or api_key.endswith("_here"):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="LLM",
                message="API key appears to be a placeholder value",
                variable=f"{settings.llm_provider.upper()}_API_KEY",
                suggestion="Replace with your actual API key"
            ))
        
        # Validate rate limiting
        if settings.llm_rate_limit_per_minute < 1:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="LLM",
                message="LLM rate limit must be at least 1 request per minute",
                variable="LLM_RATE_LIMIT_PER_MINUTE"
            ))
        
        if settings.llm_rate_limit_per_minute > 1000:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="LLM",
                message="LLM rate limit is very high, may exceed API limits",
                variable="LLM_RATE_LIMIT_PER_MINUTE",
                suggestion="Check your API provider's rate limits"
            ))
        
        # Validate model parameters
        if settings.llm_temperature < 0 or settings.llm_temperature > 2:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="LLM",
                message="LLM temperature should be between 0 and 2",
                variable="LLM_TEMPERATURE",
                suggestion="Use a temperature between 0.1 and 1.0 for most applications"
            ))
    
    def _validate_email_config(self, settings: Settings) -> None:
        """Validate email configuration."""
        if settings.email_enabled:
            if not settings.smtp_username or not settings.smtp_password:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="Email",
                    message="Email is enabled but SMTP credentials are missing",
                    variable="SMTP_USERNAME, SMTP_PASSWORD",
                    suggestion="Set SMTP credentials or disable email functionality"
                ))
            
            if not settings.smtp_from_email or "@" not in settings.smtp_from_email:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    category="Email",
                    message="Invalid or missing SMTP from email address",
                    variable="SMTP_FROM_EMAIL",
                    suggestion="Set a valid email address for SMTP_FROM_EMAIL"
                ))
        else:
            if self.environment == "production":
                self.results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    category="Email",
                    message="Email functionality is disabled in production",
                    suggestion="Consider enabling email for password resets and notifications"
                ))
    
    def _validate_performance_config(self, settings: Settings) -> None:
        """Validate performance configuration."""
        # Validate concurrent request limits
        if settings.max_concurrent_ai_requests < 1:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Performance",
                message="Max concurrent AI requests must be at least 1",
                variable="MAX_CONCURRENT_AI_REQUESTS"
            ))
        
        if settings.max_concurrent_document_processing < 1:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Performance",
                message="Max concurrent document processing must be at least 1",
                variable="MAX_CONCURRENT_DOCUMENT_PROCESSING"
            ))
        
        # Check for reasonable limits based on environment
        if self.environment == "production":
            if settings.max_concurrent_ai_requests > 50:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Performance",
                    message="Very high concurrent AI request limit may cause resource issues",
                    variable="MAX_CONCURRENT_AI_REQUESTS",
                    suggestion="Consider a lower limit (10-20) unless you have high-capacity infrastructure"
                ))
        
        # File upload validation
        if settings.max_file_size_mb < 1:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                category="Performance",
                message="Max file size must be at least 1 MB",
                variable="MAX_FILE_SIZE_MB"
            ))
        
        if settings.max_file_size_mb > 500:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                category="Performance",
                message="Very large file size limit may cause memory issues",
                variable="MAX_FILE_SIZE_MB",
                suggestion="Consider a smaller limit (50-100 MB) for better performance"
            ))
    
    def _validate_deployment_config(self, settings: Settings) -> None:
        """Validate deployment-specific configuration."""
        if self.environment in ["staging", "production"]:
            # Check for development-specific values in non-dev environments
            if "dev" in settings.app_name.lower() and self.environment == "production":
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Deployment",
                    message="App name contains 'dev' in production environment",
                    variable="APP_NAME",
                    suggestion="Use a production-appropriate app name"
                ))
            
            # Check logging configuration
            if settings.log_level == "DEBUG" and self.environment == "production":
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Deployment",
                    message="Debug logging enabled in production",
                    variable="LOG_LEVEL",
                    suggestion="Use INFO or WARNING log level in production"
                ))
            
            if not settings.structured_logging and self.environment == "production":
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Deployment",
                    message="Structured logging disabled in production",
                    variable="STRUCTURED_LOGGING",
                    suggestion="Enable structured logging for better monitoring in production"
                ))
    
    def _validate_environment_specific(self, settings: Settings) -> None:
        """Validate environment-specific requirements."""
        if self.environment == "development":
            # Development-specific validations
            if settings.db_pool_size > 10:
                self.results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    category="Development",
                    message="Database pool size is high for development",
                    variable="DB_POOL_SIZE",
                    suggestion="Consider using a smaller pool size (5-10) for development"
                ))
        
        elif self.environment == "staging":
            # Staging should be similar to production
            if settings.log_level == "DEBUG":
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    category="Staging",
                    message="Debug logging in staging environment",
                    variable="LOG_LEVEL",
                    suggestion="Use INFO log level in staging to match production"
                ))
        
        elif self.environment == "production":
            # Production-specific validations
            required_for_production = [
                ("DATABASE_URL", settings.database_url),
                ("JWT_SECRET", settings.jwt_secret),
            ]
            
            for var_name, value in required_for_production:
                if not value:
                    self.results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        category="Production",
                        message=f"{var_name} is required for production",
                        variable=var_name,
                        suggestion=f"Set {var_name} via secure environment variables"
                    ))


def print_results(results: List[ValidationResult], verbose: bool = False) -> None:
    """Print validation results in a formatted way."""
    if not results:
        print("✅ All validation checks passed!")
        return
    
    # Group results by level
    errors = [r for r in results if r.level == ValidationLevel.ERROR]
    warnings = [r for r in results if r.level == ValidationLevel.WARNING]
    info = [r for r in results if r.level == ValidationLevel.INFO]
    
    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Errors: {len(errors)}")
    print(f"   Warnings: {len(warnings)}")
    print(f"   Info: {len(info)}")
    
    # Print errors
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for result in errors:
            print(f"   [{result.category}] {result.message}")
            if result.variable:
                print(f"      Variable: {result.variable}")
            if result.suggestion:
                print(f"      Suggestion: {result.suggestion}")
            print()
    
    # Print warnings
    if warnings and verbose:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for result in warnings:
            print(f"   [{result.category}] {result.message}")
            if result.variable:
                print(f"      Variable: {result.variable}")
            if result.suggestion:
                print(f"      Suggestion: {result.suggestion}")
            print()
    
    # Print info
    if info and verbose:
        print(f"\nℹ️  Information ({len(info)}):")
        for result in info:
            print(f"   [{result.category}] {result.message}")
            if result.suggestion:
                print(f"      Suggestion: {result.suggestion}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Validate environment configuration for Healthcare Study Companion"
    )
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "staging", "production"],
        default=os.getenv("ENVIRONMENT", "development"),
        help="Target environment to validate"
    )
    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Fail on warnings (useful for CI/CD)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including warnings and info"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Validating environment configuration for: {args.environment}")
    print(f"   Strict mode: {'enabled' if args.strict else 'disabled'}")
    
    # Run validation
    validator = EnvironmentValidator(args.environment, args.strict)
    success, results = validator.validate()
    
    if args.json:
        # Output JSON for programmatic use
        output = {
            "success": success,
            "environment": args.environment,
            "strict": args.strict,
            "results": [
                {
                    "level": r.level.value,
                    "category": r.category,
                    "message": r.message,
                    "variable": r.variable,
                    "suggestion": r.suggestion
                }
                for r in results
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print_results(results, args.verbose)
        
        if success:
            print("\n✅ Environment configuration is valid!")
        else:
            print("\n❌ Environment configuration validation failed!")
            print("   Please fix the errors above before deploying.")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()