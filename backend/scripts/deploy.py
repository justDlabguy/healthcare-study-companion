#!/usr/bin/env python3
"""
Comprehensive deployment script for the Healthcare Study Companion application.

This script orchestrates the entire deployment process including:
- Environment validation
- Database migrations
- Health checks
- Rollback procedures if needed
"""

import os
import sys
import subprocess
import json
import datetime
import time
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def log_deployment_event(event_type, message, success=True, details=None):
    """Log deployment events for monitoring and debugging."""
    log_dir = backend_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "deployment_log.json"
    
    # Load existing log or create new
    log_entries = []
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            log_entries = []
    
    # Add new entry
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "success": success,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", os.getenv("VERCEL_DEPLOYMENT_ID", "local")),
        "commit_sha": os.getenv("RAILWAY_GIT_COMMIT_SHA", os.getenv("VERCEL_GIT_COMMIT_SHA", "unknown")),
        "details": details or {}
    }
    
    log_entries.append(log_entry)
    
    # Keep only last 100 entries
    log_entries = log_entries[-100:]
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log_entries, f, indent=2)
    
    # Also print to stdout for deployment logs
    status = "✅" if success else "❌"
    print(f"{status} [{datetime.datetime.now().isoformat()}] {event_type}: {message}")

def run_command_with_timeout(command, timeout=300, cwd=None):
    """Run a command with timeout and proper error handling."""
    if cwd is None:
        cwd = backend_dir
    
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout} seconds")
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        print(f"❌ Command failed with exception: {e}")
        return False, "", str(e)

def validate_environment():
    """Validate that all required environment variables are set."""
    print("🔍 Validating environment configuration...")
    
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET",
        "MISTRAL_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log_deployment_event(
            "environment_validation_failed", 
            f"Missing required environment variables: {', '.join(missing_vars)}", 
            False
        )
        return False
    
    log_deployment_event("environment_validation_success", "All required environment variables are set", True)
    print("✅ Environment validation passed")
    return True

def check_database_connectivity():
    """Check if database is accessible before deployment."""
    print("🔍 Checking database connectivity...")
    
    try:
        # Import here to avoid issues if dependencies aren't available
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        log_deployment_event("database_connectivity_success", "Database connectivity verified", True)
        print("✅ Database connectivity verified")
        return True
    
    except Exception as e:
        log_deployment_event("database_connectivity_failed", f"Database connectivity failed: {e}", False)
        print(f"❌ Database connectivity check failed: {e}")
        return False

def run_migrations():
    """Run database migrations using the deploy_migrations script."""
    print("🚀 Running database migrations...")
    
    # Use the existing deploy_migrations.py script
    success, stdout, stderr = run_command_with_timeout(
        "python scripts/deploy_migrations.py", 
        timeout=600
    )
    
    if success:
        log_deployment_event("migrations_success", "Database migrations completed successfully", True)
        print("✅ Database migrations completed successfully")
        return True
    else:
        log_deployment_event("migrations_failed", f"Database migrations failed: {stderr}", False)
        print(f"❌ Database migrations failed: {stderr}")
        return False

def run_health_checks():
    """Run post-deployment health checks."""
    print("🏥 Running post-deployment health checks...")
    
    try:
        # Check that we can import the main app
        from app.main import app
        
        # Check database connectivity again
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check that we can query the alembic version table
            result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            version = result.fetchone()
            
            if version:
                log_deployment_event(
                    "health_check_success", 
                    f"Health checks passed - database at version {version[0]}", 
                    True
                )
                print(f"✅ Health checks passed - database at version {version[0]}")
                return True
            else:
                log_deployment_event("health_check_failed", "No alembic version found", False)
                print("❌ Health check failed - no alembic version found")
                return False
    
    except Exception as e:
        log_deployment_event("health_check_failed", f"Health checks failed: {e}", False)
        print(f"❌ Health checks failed: {e}")
        return False

def handle_deployment_failure():
    """Handle deployment failure with potential rollback."""
    print("🚨 Deployment failed - checking rollback options...")
    
    environment = os.getenv("ENVIRONMENT", "unknown")
    
    if environment == "production":
        print("⚠️  Production deployment failed - manual intervention may be required")
        log_deployment_event("deployment_failure_production", "Production deployment failed", False)
        
        # In production, we might want to automatically rollback
        response = os.getenv("AUTO_ROLLBACK_ON_FAILURE", "false").lower()
        if response == "true":
            print("🔄 Auto-rollback enabled - attempting emergency rollback...")
            success, stdout, stderr = run_command_with_timeout(
                "python scripts/rollback_migrations.py emergency",
                timeout=300
            )
            
            if success:
                log_deployment_event("auto_rollback_success", "Emergency rollback completed", True)
                print("✅ Emergency rollback completed")
            else:
                log_deployment_event("auto_rollback_failed", f"Emergency rollback failed: {stderr}", False)
                print(f"❌ Emergency rollback failed: {stderr}")
    else:
        log_deployment_event("deployment_failure_non_production", f"Deployment failed in {environment}", False)
        print(f"⚠️  Deployment failed in {environment} environment")

def main():
    """Main deployment orchestration function."""
    print("🚀 Healthcare Study Companion - Deployment Script")
    print("=" * 60)
    
    deployment_id = os.getenv("RAILWAY_DEPLOYMENT_ID", os.getenv("VERCEL_DEPLOYMENT_ID", "local"))
    environment = os.getenv("ENVIRONMENT", "unknown")
    commit_sha = os.getenv("RAILWAY_GIT_COMMIT_SHA", os.getenv("VERCEL_GIT_COMMIT_SHA", "unknown"))
    
    print(f"Environment: {environment}")
    print(f"Deployment ID: {deployment_id}")
    print(f"Commit SHA: {commit_sha}")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print("=" * 60)
    
    log_deployment_event("deployment_start", f"Starting deployment in {environment}")
    
    deployment_start_time = time.time()
    
    try:
        # Step 1: Validate environment
        if not validate_environment():
            handle_deployment_failure()
            sys.exit(1)
        
        # Step 2: Check database connectivity
        if not check_database_connectivity():
            handle_deployment_failure()
            sys.exit(1)
        
        # Step 3: Run migrations
        if not run_migrations():
            handle_deployment_failure()
            sys.exit(1)
        
        # Step 4: Run health checks
        if not run_health_checks():
            handle_deployment_failure()
            sys.exit(1)
        
        # Success!
        deployment_duration = time.time() - deployment_start_time
        log_deployment_event(
            "deployment_success", 
            f"Deployment completed successfully in {deployment_duration:.2f} seconds", 
            True,
            {"duration_seconds": deployment_duration}
        )
        print(f"🎉 Deployment completed successfully in {deployment_duration:.2f} seconds!")
        
    except KeyboardInterrupt:
        log_deployment_event("deployment_cancelled", "Deployment cancelled by user", False)
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        log_deployment_event("deployment_error", f"Unexpected error during deployment: {e}", False)
        print(f"❌ Unexpected error during deployment: {e}")
        handle_deployment_failure()
        sys.exit(1)

if __name__ == "__main__":
    main()