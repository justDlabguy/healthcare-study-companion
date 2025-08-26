#!/usr/bin/env python3
"""
Environment Setup Script

Interactive script to help users set up their environment configuration.

Usage:
    python scripts/setup_environment.py [--environment ENV] [--non-interactive]
"""

import os
import sys
import argparse
import secrets
import string
from pathlib import Path
from typing import Dict, Any, Optional

def generate_jwt_secret(length: int = 64) -> str:
    """Generate a secure JWT secret."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_user_input(prompt: str, default: str = "", required: bool = False, secret: bool = False) -> str:
    """Get user input with validation."""
    while True:
        if secret:
            import getpass
            value = getpass.getpass(f"{prompt}: ")
        else:
            display_default = f" [{default}]" if default else ""
            value = input(f"{prompt}{display_default}: ").strip()
        
        if not value and default:
            return default
        elif not value and required:
            print("This field is required. Please enter a value.")
            continue
        else:
            return value

def setup_development_config() -> Dict[str, str]:
    """Set up development configuration."""
    print("\n🔧 Setting up DEVELOPMENT environment")
    print("=" * 50)
    
    config = {
        "ENVIRONMENT": "development",
        "APP_NAME": "Healthcare Study Companion API (Dev)"
    }
    
    # Database configuration
    print("\n📊 Database Configuration")
    print("For development, you can use a local database or TiDB Cloud.")
    
    use_tidb = get_user_input("Use TiDB Cloud? (y/n)", "n").lower().startswith('y')
    
    if use_tidb:
        config["DATABASE_URL"] = get_user_input(
            "TiDB connection string",
            required=True
        )
    else:
        config["DATABASE_HOST"] = get_user_input("Database host", "localhost")
        config["DATABASE_PORT"] = get_user_input("Database port", "4000")
        config["DATABASE_USER"] = get_user_input("Database user", "root")
        config["DATABASE_PASSWORD"] = get_user_input("Database password", "", secret=True)
        config["DATABASE_NAME"] = get_user_input("Database name", "healthcare_study_dev")
    
    # Security configuration
    print("\n🔐 Security Configuration")
    config["JWT_SECRET"] = generate_jwt_secret()
    print("Generated secure JWT secret ✅")
    
    # CORS configuration
    config["CORS_ORIGINS"] = get_user_input(
        "CORS origins (comma-separated)",
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    
    # LLM configuration
    print("\n🤖 AI/LLM Configuration")
    providers = ["mistral", "openai", "anthropic", "huggingface", "together"]
    print(f"Available providers: {', '.join(providers)}")
    
    config["LLM_PROVIDER"] = get_user_input("LLM provider", "mistral")
    
    if config["LLM_PROVIDER"] == "mistral":
        config["MISTRAL_API_KEY"] = get_user_input("Mistral API key", required=True, secret=True)
        config["DEFAULT_LLM_MODEL"] = "mistral-small"
        config["EMBEDDING_MODEL"] = "mistral-embed"
    elif config["LLM_PROVIDER"] == "openai":
        config["OPENAI_API_KEY"] = get_user_input("OpenAI API key", required=True, secret=True)
        config["DEFAULT_LLM_MODEL"] = "gpt-4"
        config["EMBEDDING_MODEL"] = "text-embedding-3-small"
    # Add other providers as needed
    
    # Development-specific settings
    config["LOG_LEVEL"] = "DEBUG"
    config["STRUCTURED_LOGGING"] = "false"
    config["EMAIL_ENABLED"] = "false"
    
    return config

def setup_staging_config() -> Dict[str, str]:
    """Set up staging configuration."""
    print("\n🔧 Setting up STAGING environment")
    print("=" * 50)
    print("Note: Sensitive values should be set via your deployment platform")
    
    config = {
        "ENVIRONMENT": "staging",
        "APP_NAME": "Healthcare Study Companion API (Staging)",
        "LOG_LEVEL": "INFO",
        "STRUCTURED_LOGGING": "true",
        "EMAIL_ENABLED": "true",
        "AUTO_ROLLBACK_ON_FAILURE": "true"
    }
    
    # Get staging-specific values
    config["CORS_ORIGINS"] = get_user_input(
        "Staging frontend URL",
        "https://staging-yourdomain.vercel.app"
    )
    
    config["LLM_PROVIDER"] = get_user_input("LLM provider", "mistral")
    
    return config

def setup_production_config() -> Dict[str, str]:
    """Set up production configuration."""
    print("\n🔧 Setting up PRODUCTION environment")
    print("=" * 50)
    print("⚠️  WARNING: All sensitive values MUST be set via secure deployment platform!")
    print("This script will create a template with placeholders.")
    
    config = {
        "ENVIRONMENT": "production",
        "APP_NAME": "Healthcare Study Companion API",
        "LOG_LEVEL": "INFO",
        "STRUCTURED_LOGGING": "true",
        "EMAIL_ENABLED": "true",
        "AUTO_ROLLBACK_ON_FAILURE": "true"
    }
    
    # Get production-specific values
    config["CORS_ORIGINS"] = get_user_input(
        "Production frontend URLs (comma-separated)",
        "https://yourdomain.com,https://www.yourdomain.com"
    )
    
    config["LLM_PROVIDER"] = get_user_input("LLM provider", "mistral")
    
    # Add placeholders for sensitive values
    config["# DATABASE_URL"] = "# Set via deployment platform"
    config["# JWT_SECRET"] = "# Set via deployment platform"
    config[f"# {config['LLM_PROVIDER'].upper()}_API_KEY"] = "# Set via deployment platform"
    
    return config

def write_env_file(config: Dict[str, str], filename: str) -> None:
    """Write configuration to environment file."""
    filepath = Path(filename)
    
    # Backup existing file
    if filepath.exists():
        backup_path = filepath.with_suffix(f"{filepath.suffix}.backup")
        filepath.rename(backup_path)
        print(f"📁 Backed up existing {filename} to {backup_path}")
    
    # Write new configuration
    with open(filepath, 'w') as f:
        f.write(f"# Healthcare Study Companion Environment Configuration\n")
        f.write(f"# Generated by setup script\n\n")
        
        for key, value in config.items():
            if key.startswith("#"):
                f.write(f"{key}={value}\n")
            else:
                f.write(f"{key}={value}\n")
    
    print(f"✅ Configuration written to {filename}")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Set up environment configuration")
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to set up"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Use defaults without prompting"
    )
    
    args = parser.parse_args()
    
    print("🚀 Healthcare Study Companion - Environment Setup")
    print("=" * 60)
    
    if args.non_interactive:
        print("Running in non-interactive mode with defaults")
    
    # Set up configuration based on environment
    if args.environment == "development":
        config = setup_development_config() if not args.non_interactive else {
            "ENVIRONMENT": "development",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "4000",
            "DATABASE_USER": "root",
            "DATABASE_PASSWORD": "",
            "DATABASE_NAME": "healthcare_study_dev",
            "JWT_SECRET": generate_jwt_secret(),
            "CORS_ORIGINS": "http://localhost:3000",
            "LLM_PROVIDER": "mistral",
            "LOG_LEVEL": "DEBUG"
        }
        filename = "local.env"
    elif args.environment == "staging":
        config = setup_staging_config()
        filename = ".env.staging"
    else:  # production
        config = setup_production_config()
        filename = ".env.production"
    
    # Write configuration file
    write_env_file(config, filename)
    
    # Provide next steps
    print("\n" + "=" * 60)
    print("✅ Environment setup complete!")
    print("\nNext steps:")
    
    if args.environment == "development":
        print("1. Review and update the generated local.env file")
        print("2. Add your API keys for the LLM provider")
        print("3. Set up your database connection")
        print("4. Run: python check_config.py")
        print("5. Start the application: uvicorn app.main:app --reload")
    else:
        print(f"1. Review the generated {filename} file")
        print("2. Set sensitive environment variables via your deployment platform")
        print("3. Deploy to your target environment")
    
    print(f"\nFor comprehensive validation, run:")
    print(f"   python scripts/validate_config.py --environment {args.environment}")

if __name__ == "__main__":
    main()