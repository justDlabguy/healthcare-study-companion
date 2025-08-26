#!/usr/bin/env python3
"""
Migration rollback script for the Healthcare Study Companion application.

This script provides safe rollback procedures for failed migrations with
comprehensive logging and verification.
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

def log_rollback_event(event_type, message, success=True, details=None):
    """Log rollback events for monitoring and debugging."""
    log_dir = backend_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "rollback_log.json"
    
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
        "details": details or {}
    }
    
    log_entries.append(log_entry)
    
    # Keep only last 50 rollback entries
    log_entries = log_entries[-50:]
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log_entries, f, indent=2)
    
    # Also print to stdout
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

def get_migration_history():
    """Get migration history to find valid rollback targets."""
    success, stdout, stderr = run_command_with_timeout("alembic history")
    if success and stdout:
        revisions = []
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('INFO') and '->' in line:
                # Parse revision from history line
                parts = line.split()
                if parts:
                    revision = parts[0]
                    revisions.append(revision)
        return revisions
    return []

def find_last_known_good_revision():
    """Find the last known good revision from deployment logs."""
    log_file = backend_dir / "logs" / "deployment_log.json"
    
    if not log_file.exists():
        print("⚠️  No deployment log found - cannot determine last known good revision")
        return None
    
    try:
        with open(log_file, 'r') as f:
            log_entries = json.load(f)
        
        # Find the last successful deployment
        for entry in reversed(log_entries):
            if (entry.get("event_type") == "deployment_complete" and 
                entry.get("success") and 
                "details" in entry):
                
                # Try to extract the "from" revision from the message
                message = entry.get("message", "")
                if " -> " in message:
                    parts = message.split(" -> ")
                    if len(parts) >= 2:
                        from_revision = parts[0].split()[-1]  # Get last word before ->
                        return from_revision
        
        print("⚠️  No successful deployment found in logs")
        return None
    
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️  Could not read deployment log")
        return None

def validate_rollback_target(target_revision):
    """Validate that the target revision exists and is safe to rollback to."""
    print(f"🔍 Validating rollback target: {target_revision}")
    
    # Get migration history
    history = get_migration_history()
    
    if target_revision not in history:
        log_rollback_event("validation_failed", f"Target revision {target_revision} not found in history", False)
        return False
    
    # Check if target is not too far back (safety check)
    current_rev = get_current_revision()
    if current_rev in history and target_revision in history:
        current_index = history.index(current_rev)
        target_index = history.index(target_revision)
        
        steps_back = current_index - target_index
        if steps_back > 10:  # More than 10 migrations back
            print(f"⚠️  Warning: Rolling back {steps_back} migrations")
            response = input("This is a large rollback. Are you sure? (yes/no): ")
            if response.lower() != "yes":
                log_rollback_event("validation_cancelled", "Large rollback cancelled by user", False)
                return False
    
    log_rollback_event("validation_success", f"Target revision {target_revision} validated", True)
    return True

def create_pre_rollback_backup():
    """Create a backup before rollback (placeholder for actual implementation)."""
    print("💾 Creating pre-rollback backup...")
    
    current_rev = get_current_revision()
    backup_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "revision": current_rev,
        "backup_type": "pre_rollback",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }
    
    backup_dir = backend_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f"pre_rollback_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(backup_file, 'w') as f:
        json.dump(backup_info, f, indent=2)
    
    log_rollback_event("backup_created", f"Pre-rollback backup created: {backup_file}", True)
    print(f"✅ Backup info saved to: {backup_file}")
    return str(backup_file)

def perform_rollback(target_revision):
    """Perform the actual rollback operation."""
    print(f"🔄 Rolling back to revision: {target_revision}")
    
    current_rev = get_current_revision()
    start_time = time.time()
    
    success, stdout, stderr = run_command_with_timeout(f"alembic downgrade {target_revision}", timeout=600)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if success:
        log_rollback_event(
            "rollback_success", 
            f"Rollback successful: {current_rev} -> {target_revision}", 
            True,
            {"duration_seconds": duration, "from_revision": current_rev, "to_revision": target_revision}
        )
        print(f"✅ Rollback completed successfully in {duration:.2f} seconds")
        return True
    else:
        log_rollback_event(
            "rollback_failed", 
            f"Rollback failed: {current_rev} -> {target_revision}", 
            False,
            {"duration_seconds": duration, "error": stderr}
        )
        print(f"❌ Rollback failed after {duration:.2f} seconds")
        print(f"Error: {stderr}")
        return False

def verify_rollback_success(target_revision):
    """Verify that rollback was successful."""
    print("🔍 Verifying rollback success...")
    
    try:
        # Check current revision matches target
        current_rev = get_current_revision()
        if current_rev != target_revision:
            log_rollback_event("verification_failed", f"Current revision {current_rev} does not match target {target_revision}", False)
            return False
        
        # Check database connectivity
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        log_rollback_event("verification_success", f"Rollback verification successful - at revision {current_rev}", True)
        print(f"✅ Rollback verification successful - at revision {current_rev}")
        return True
    
    except Exception as e:
        log_rollback_event("verification_failed", f"Rollback verification failed: {e}", False)
        print(f"❌ Rollback verification failed: {e}")
        return False

def emergency_rollback():
    """Perform emergency rollback to last known good state."""
    print("🚨 EMERGENCY ROLLBACK PROCEDURE")
    print("=" * 50)
    
    # Find last known good revision
    target_revision = find_last_known_good_revision()
    
    if not target_revision:
        print("❌ Cannot determine last known good revision")
        print("Please specify a target revision manually")
        return False
    
    print(f"🎯 Target revision: {target_revision}")
    
    # Confirm emergency rollback
    response = input("This is an EMERGENCY ROLLBACK. Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Emergency rollback cancelled")
        return False
    
    # Skip some safety checks in emergency mode
    log_rollback_event("emergency_start", f"Emergency rollback started to {target_revision}", True)
    
    # Create backup
    create_pre_rollback_backup()
    
    # Perform rollback
    if perform_rollback(target_revision):
        if verify_rollback_success(target_revision):
            log_rollback_event("emergency_success", f"Emergency rollback completed successfully", True)
            print("🎉 Emergency rollback completed successfully!")
            return True
    
    log_rollback_event("emergency_failed", "Emergency rollback failed", False)
    print("❌ Emergency rollback failed!")
    return False

def main():
    """Main rollback function."""
    if len(sys.argv) < 2:
        print("Migration Rollback Script")
        print("=" * 30)
        print("Usage: python rollback_migrations.py <command> [revision]")
        print("\nCommands:")
        print("  rollback <revision>  - Rollback to specific revision")
        print("  emergency           - Emergency rollback to last known good state")
        print("  status              - Show current rollback status")
        print("\nExamples:")
        print("  python rollback_migrations.py rollback abc123")
        print("  python rollback_migrations.py emergency")
        return
    
    command = sys.argv[1].lower()
    
    print("🔄 Healthcare Study Companion - Migration Rollback Script")
    print("=" * 60)
    
    environment = os.getenv("ENVIRONMENT", "unknown")
    print(f"Environment: {environment}")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        if command == "rollback":
            if len(sys.argv) < 3:
                print("❌ Error: Target revision required")
                return
            
            target_revision = sys.argv[2]
            
            log_rollback_event("rollback_start", f"Starting rollback to {target_revision}")
            
            # Validate target
            if not validate_rollback_target(target_revision):
                return
            
            # Create backup
            create_pre_rollback_backup()
            
            # Perform rollback
            if perform_rollback(target_revision):
                if verify_rollback_success(target_revision):
                    print("🎉 Rollback completed successfully!")
                else:
                    print("❌ Rollback verification failed!")
            else:
                print("❌ Rollback failed!")
        
        elif command == "emergency":
            emergency_rollback()
        
        elif command == "status":
            current_rev = get_current_revision()
            print(f"Current revision: {current_rev}")
            
            last_good = find_last_known_good_revision()
            print(f"Last known good: {last_good}")
            
            history = get_migration_history()
            print(f"Available revisions: {len(history)}")
        
        else:
            print(f"Unknown command: {command}")
    
    except KeyboardInterrupt:
        log_rollback_event("rollback_cancelled", "Rollback cancelled by user", False)
        print("\n❌ Rollback cancelled by user")
    
    except Exception as e:
        log_rollback_event("rollback_error", f"Unexpected error during rollback: {e}", False)
        print(f"❌ Unexpected error during rollback: {e}")

if __name__ == "__main__":
    main()