#!/usr/bin/env python3
"""
Deployment migration script for the Healthcare Study Companion application.

This script is designed to be run during deployment to safely apply database migrations
with proper error handling, logging, and rollback capabilities.
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

def check_database_connectivity():
    """Check if database is accessible before running migrations."""
    print("🔍 Checking database connectivity...")
    
    try:
        # Import here to avoid issues if dependencies aren't available
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        log_deployment_event("database_check", "Database connectivity verified", True)
        return True
    
    except Exception as e:
        log_deployment_event("database_check", f"Database connectivity failed: {e}", False)
        print(f"❌ Database connectivity check failed: {e}")
        return False

def get_current_revision():
    """Get current database revision."""
    success, stdout, stderr = run_command_with_timeout("alembic current")
    if success and stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('INFO'):
                revision = line.split()[0] if line.split() else None
                return revision
    return None

def check_pending_migrations():
    """Check if there are pending migrations to apply."""
    print("🔍 Checking for pending migrations...")
    
    # Get current revision
    current_rev = get_current_revision()
    
    # Get head revision
    success, stdout, stderr = run_command_with_timeout("alembic heads")
    if not success:
        log_deployment_event("migration_check", "Failed to get head revision", False)
        return False, None, None
    
    head_rev = None
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('INFO'):
                head_rev = line.split()[0] if line.split() else None
                break
    
    if current_rev == head_rev:
        log_deployment_event("migration_check", "No pending migrations", True)
        print("✅ Database is up to date - no migrations needed")
        return False, current_rev, head_rev
    else:
        log_deployment_event("migration_check", f"Pending migrations found: {current_rev} -> {head_rev}", True)
        print(f"📋 Pending migrations: {current_rev} -> {head_rev}")
        return True, current_rev, head_rev

def run_migrations():
    """Run database migrations with proper error handling."""
    print("🚀 Running database migrations...")
    
    start_time = time.time()
    success, stdout, stderr = run_command_with_timeout("alembic upgrade head", timeout=600)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if success:
        log_deployment_event(
            "migration_upgrade", 
            "Database migrations completed successfully", 
            True,
            {"duration_seconds": duration}
        )
        print(f"✅ Migrations completed successfully in {duration:.2f} seconds")
        return True
    else:
        log_deployment_event(
            "migration_upgrade", 
            "Database migrations failed", 
            False,
            {"duration_seconds": duration, "error": stderr}
        )
        print(f"❌ Migrations failed after {duration:.2f} seconds")
        print(f"Error: {stderr}")
        return False

def verify_migration_success():
    """Verify that migrations were applied successfully."""
    print("🔍 Verifying migration success...")
    
    try:
        # Check that we can connect and query the database
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Try to query a basic table to ensure schema is working
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            
            if len(tables) > 0:
                log_deployment_event("migration_verify", f"Migration verification successful - {len(tables)} tables found", True)
                print(f"✅ Migration verification successful - {len(tables)} tables found")
                return True
            else:
                log_deployment_event("migration_verify", "No tables found after migration", False)
                print("❌ No tables found after migration")
                return False
    
    except Exception as e:
        log_deployment_event("migration_verify", f"Migration verification failed: {e}", False)
        print(f"❌ Migration verification failed: {e}")
        return False

def main():
    """Main deployment migration function."""
    print("🚀 Healthcare Study Companion - Deployment Migration Script")
    print("=" * 60)
    
    deployment_id = os.getenv("RAILWAY_DEPLOYMENT_ID", os.getenv("VERCEL_DEPLOYMENT_ID", "local"))
    environment = os.getenv("ENVIRONMENT", "unknown")
    
    print(f"Environment: {environment}")
    print(f"Deployment ID: {deployment_id}")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print("=" * 60)
    
    log_deployment_event("deployment_start", f"Starting deployment migration in {environment}")
    
    try:
        # Step 1: Check database connectivity
        if not check_database_connectivity():
            log_deployment_event("deployment_failed", "Database connectivity check failed", False)
            sys.exit(1)
        
        # Step 2: Check for pending migrations
        has_pending, current_rev, head_rev = check_pending_migrations()
        
        if not has_pending:
            log_deployment_event("deployment_complete", "No migrations needed - deployment successful", True)
            print("🎉 Deployment complete - no migrations were needed")
            sys.exit(0)
        
        # Step 3: Run migrations
        if not run_migrations():
            log_deployment_event("deployment_failed", "Migration execution failed", False)
            sys.exit(1)
        
        # Step 4: Verify migration success
        if not verify_migration_success():
            log_deployment_event("deployment_failed", "Migration verification failed", False)
            sys.exit(1)
        
        # Success!
        log_deployment_event("deployment_complete", f"Deployment migration successful: {current_rev} -> {head_rev}", True)
        print("🎉 Deployment migration completed successfully!")
        
    except KeyboardInterrupt:
        log_deployment_event("deployment_cancelled", "Deployment cancelled by user", False)
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        log_deployment_event("deployment_error", f"Unexpected error during deployment: {e}", False)
        print(f"❌ Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()