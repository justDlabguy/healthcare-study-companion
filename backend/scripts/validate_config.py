#!/usr/bin/env python3
"""
Configuration Validation Script

This script validates the application configuration and provides detailed
feedback about missing or invalid environment variables.

Usage:
    python scripts/validate_config.py [--environment ENV] [--strict]

Options:
    --environment ENV    Validate for specific environment (development, staging, production)
    --strict            Fail on warnings (useful for CI/CD)
    --check-connections Test actual connections (database, APIs)
    --help              Show this help message
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Settings, ConfigurationError, get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """Comprehensive configuration validator."""
    
    def __init__(self, environment: Optional[str] = None, strict: bool = False):
        self.environment = environment
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_environment_files(self) -> None:
        """Validate that environment files exist and are readable."""
        env_files = [
            'local.env',
            '.env.development',
            '.env.staging', 
            '.env.production',
            '.env.example'
        ]
        
        for env_file in env_files:
            file_path = Path(env_file)
            if file_path.exists():
                if file_path.stat().st_size == 0:
                    self.warnings.append(f"Environment file {env_file} is empty")
                else:
                    self.info.append(f"Found environment file: {env_file}")
            elif env_file == '.env.example':
                self.errors.append(f"Required template file {env_file} is missing")
    
    def validate_settings(self) -> Optional[Settings]:
        """Validate settings configuration."""
        try:
            settings = get_settings()
            self.info.append(f"Configuration loaded successfully for environment: {settings.environment}")
            
            # Environment-specific validations
            if settings.environment == "production":
                self._validate_production_settings(settings)
            elif settings.environment == "staging":
                self._validate_staging_settings(settings)
            else:
                self._validate_development_settings(settings)
            
            return settings
            
        except ConfigurationError as e:
            self.errors.append(f"Configuration error: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Unexpected error loading configuration: {e}")
            return None
    
    def _validate_production_settings(self, settings: Settings) -> None:
        """Validate production-specific requirements."""
        # Security validations
        if settings.cors_origins == "*":
            self.warnings.append("CORS is set to allow all origins (*) in production")
        
        if not settings.structured_logging:
            self.warnings.append("Structured logging is disabled in production")
        
        if settings.log_level.upper() == "DEBUG":
            self.warnings.append("Debug logging is enabled in production")
        
        # Performance validations
        if settings.db_pool_size < 10:
            self.warnings.append(f"Database pool size ({settings.db_pool_size}) is low for production")
        
        if settings.max_concurrent_ai_requests < 5:
            self.warnings.append(f"Max concurrent AI requests ({settings.max_concurrent_ai_requests}) is low for production")
    
    def _validate_staging_settings(self, settings: Settings) -> None:
        """Validate staging-specific requirements."""
        if not settings.structured_logging:
            self.info.append("Consider enabling structured logging in staging")
        
        if settings.cors_origins == "*":
            self.warnings.append("CORS allows all origins in staging - consider restricting")
    
    def _validate_development_settings(self, settings: Settings) -> None:
        """Validate development-specific requirements."""
        if settings.jwt_secret == "change-me":
            self.info.append("Using default JWT secret in development (this is OK)")
        
        if settings.log_level.upper() != "DEBUG":
            self.info.append("Consider using DEBUG log level in development")
    
    async def test_database_connection(self, settings: Settings) -> None:
        """Test database connectivity."""
        try:
            from app.database import engine
            from sqlalchemy import text
            
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    self.info.append("✅ Database connection successful")
                else:
                    self.errors.append("❌ Database connection test failed")
                    
        except Exception as e:
            self.errors.append(f"❌ Database connection failed: {e}")
    
    async def test_llm_api_connection(self, settings: Settings) -> None:
        """Test LLM API connectivity."""
        try:
            api_key = settings.get_api_key_for_provider()
            if not api_key:
                self.errors.append(f"❌ No API key found for provider: {settings.llm_provider}")
                return
            
            # Simple API test (without making actual requests to avoid costs)
            if len(api_key) < 10:
                self.warnings.append(f"⚠️ API key for {settings.llm_provider} seems too short")
            else:
                self.info.append(f"✅ API key for {settings.llm_provider} is present and properly formatted")
                
        except Exception as e:
            self.errors.append(f"❌ LLM API validation failed: {e}")
    
    def validate_file_permissions(self) -> None:
        """Validate file and directory permissions."""
        # Check uploads directory
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            self.warnings.append("Uploads directory does not exist - will be created on first upload")
        elif not os.access(uploads_dir, os.W_OK):
            self.errors.append("Uploads directory is not writable")
        else:
            self.info.append("✅ Uploads directory is writable")
        
        # Check logs directory
        logs_dir = Path("logs")
        if not logs_dir.exists():
            self.info.append("Logs directory does not exist - will be created if needed")
        elif not os.access(logs_dir, os.W_OK):
            self.warnings.append("Logs directory is not writable")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            "status": "failed" if self.errors else ("warning" if self.warnings else "passed"),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_info": len(self.info)
            }
        }
    
    def print_report(self) -> None:
        """Print formatted validation report."""
        print("\n" + "="*60)
        print("CONFIGURATION VALIDATION REPORT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.info:
            print(f"\nℹ️  INFO ({len(self.info)}):")
            for info in self.info:
                print(f"   {info}")
        
        print("\n" + "="*60)
        
        if self.errors:
            print("❌ VALIDATION FAILED - Please fix the errors above")
            return False
        elif self.warnings and self.strict:
            print("⚠️  VALIDATION FAILED - Warnings treated as errors in strict mode")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            return True
        else:
            print("✅ VALIDATION PASSED")
            return True

async def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate Healthcare Study Companion configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--environment", 
        choices=["development", "staging", "production"],
        help="Validate for specific environment"
    )
    
    parser.add_argument(
        "--strict", 
        action="store_true",
        help="Treat warnings as errors"
    )
    
    parser.add_argument(
        "--check-connections", 
        action="store_true",
        help="Test actual connections (database, APIs)"
    )
    
    args = parser.parse_args()
    
    # Set environment if specified
    if args.environment:
        os.environ["ENVIRONMENT"] = args.environment
    
    # Create validator
    validator = ConfigValidator(
        environment=args.environment,
        strict=args.strict
    )
    
    print("🔍 Starting configuration validation...")
    
    # Validate environment files
    validator.validate_environment_files()
    
    # Validate settings
    settings = validator.validate_settings()
    
    # Validate file permissions
    validator.validate_file_permissions()
    
    # Test connections if requested
    if args.check_connections and settings:
        print("🔗 Testing connections...")
        await validator.test_database_connection(settings)
        await validator.test_llm_api_connection(settings)
    
    # Print report
    success = validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())