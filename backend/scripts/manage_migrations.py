#!/usr/bin/env python3
"""
Enhanced migration management script for the Healthcare Study Companion application.

This script provides comprehensive utilities for managing Alembic database migrations,
including rollback procedures, deployment automation, and safety checks.
"""

import os
import sys
import subprocess
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_command(command, cwd=None, capture_output=False):
    """Run a shell command and return the result."""
    if cwd is None:
        cwd = backend_dir
    
    print(f"Running: {command}")
    
    if capture_output:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            text=True, 
            capture_output=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    else:
        result = subprocess.run(command, shell=True, cwd=cwd, text=True)
        return result.returncode == 0

def check_current_revision():
    """Check the current database revision."""
    print("Checking current database revision...")
    success = run_command("alembic current")
    return success

def check_migration_history():
    """Show migration history."""
    print("Migration history:")
    success = run_command("alembic history")
    return success

def create_migration(message):
    """Create a new migration."""
    print(f"Creating new migration: {message}")
    success = run_command(f'alembic revision --autogenerate -m "{message}"')
    return success

def upgrade_database():
    """Upgrade database to the latest revision."""
    print("Upgrading database to latest revision...")
    success = run_command("alembic upgrade head")
    return success

def downgrade_database(revision="base"):
    """Downgrade database to a specific revision."""
    print(f"Downgrading database to revision: {revision}")
    success = run_command(f"alembic downgrade {revision}")
    return success

def stamp_database(revision):
    """Stamp database with a specific revision without running migrations."""
    print(f"Stamping database with revision: {revision}")
    success = run_command(f"alembic stamp {revision}")
    return success

def get_current_revision():
    """Get the current database revision."""
    success, stdout, stderr = run_command("alembic current", capture_output=True)
    if success and stdout:
        # Parse the revision from output
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('INFO'):
                # Extract revision hash (first part before space)
                revision = line.split()[0] if line.split() else None
                return revision
    return None

def get_migration_history():
    """Get the migration history as a list."""
    success, stdout, stderr = run_command("alembic history", capture_output=True)
    if success and stdout:
        return stdout.strip().split('\n')
    return []

def backup_database():
    """Create a database backup before migrations (placeholder for actual implementation)."""
    print("⚠️  Database backup functionality should be implemented based on your database provider")
    print("For TiDB Serverless, consider using their backup features or export functionality")
    
    # Create a backup record
    backup_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "revision": get_current_revision(),
        "backup_type": "pre_migration"
    }
    
    backup_file = backend_dir / "backups" / f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_file.parent.mkdir(exist_ok=True)
    
    with open(backup_file, 'w') as f:
        json.dump(backup_info, f, indent=2)
    
    print(f"Backup info saved to: {backup_file}")
    return str(backup_file)

def safe_upgrade(create_backup=True):
    """Safely upgrade database with backup and rollback capability."""
    print("🚀 Starting safe database upgrade...")
    
    # Get current revision for potential rollback
    current_revision = get_current_revision()
    print(f"Current revision: {current_revision}")
    
    # Create backup if requested
    backup_file = None
    if create_backup:
        backup_file = backup_database()
    
    # Validate migrations first
    if not validate_migrations():
        print("❌ Migration validation failed. Aborting upgrade.")
        return False
    
    # Perform the upgrade
    print("Upgrading database...")
    success = upgrade_database()
    
    if success:
        print("✅ Database upgrade completed successfully!")
        new_revision = get_current_revision()
        print(f"New revision: {new_revision}")
        
        # Log the successful migration
        log_migration_event("upgrade", current_revision, new_revision, True)
        return True
    else:
        print("❌ Database upgrade failed!")
        
        # Log the failed migration
        log_migration_event("upgrade", current_revision, None, False)
        
        # Offer rollback
        if current_revision:
            response = input(f"Would you like to rollback to {current_revision}? (y/N): ")
            if response.lower() == 'y':
                rollback_to_revision(current_revision)
        
        return False

def rollback_to_revision(revision):
    """Rollback to a specific revision with safety checks."""
    print(f"🔄 Rolling back to revision: {revision}")
    
    current_revision = get_current_revision()
    print(f"Current revision: {current_revision}")
    
    # Confirm the rollback
    response = input(f"Are you sure you want to rollback from {current_revision} to {revision}? (y/N): ")
    if response.lower() != 'y':
        print("Rollback cancelled.")
        return False
    
    # Create backup before rollback
    backup_file = backup_database()
    
    # Perform rollback
    success = downgrade_database(revision)
    
    if success:
        print("✅ Rollback completed successfully!")
        log_migration_event("rollback", current_revision, revision, True)
        return True
    else:
        print("❌ Rollback failed!")
        log_migration_event("rollback", current_revision, revision, False)
        return False

def log_migration_event(event_type, from_revision, to_revision, success):
    """Log migration events for audit trail."""
    log_dir = backend_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "migration_log.json"
    
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
        "from_revision": from_revision,
        "to_revision": to_revision,
        "success": success,
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }
    
    log_entries.append(log_entry)
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log_entries, f, indent=2)
    
    print(f"Migration event logged to: {log_file}")

def validate_migrations():
    """Validate that migrations are in sync with models."""
    print("Validating migrations against current models...")
    print("Note: This will create a temporary migration file to check for differences.")
    
    # Create a temporary migration to check for differences
    temp_message = "temp_validation_check"
    success = run_command(f'alembic revision --autogenerate -m "{temp_message}"')
    
    if success:
        # Check if the migration file is empty (no changes detected)
        versions_dir = backend_dir / "alembic" / "versions"
        temp_files = list(versions_dir.glob(f"*{temp_message.replace(' ', '_')}*.py"))
        
        if temp_files:
            temp_file = temp_files[0]
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Remove the temporary file
            temp_file.unlink()
            
            # Check if the migration has any actual changes
            if "pass" in content and content.count("op.") < 3:  # Minimal operations
                print("✅ Database is in sync with models - no significant changes detected")
                return True
            else:
                print("⚠️  Database is NOT in sync with models - changes detected")
                print("Consider creating a new migration to sync the database.")
                return False
    
    return False

def deployment_migrate():
    """Run migrations in deployment environment with safety checks."""
    print("🚀 Running deployment migrations...")
    
    # Check if we're in a production environment
    environment = os.getenv("ENVIRONMENT", "development")
    print(f"Environment: {environment}")
    
    if environment == "production":
        print("⚠️  Running in PRODUCTION environment - extra safety checks enabled")
        
        # In production, always validate first
        if not validate_migrations():
            print("❌ Migration validation failed in production. Aborting.")
            return False
        
        # Create backup in production
        backup_database()
    
    # Run the migration
    success = upgrade_database()
    
    if success:
        print("✅ Deployment migrations completed successfully!")
        return True
    else:
        print("❌ Deployment migrations failed!")
        return False

def show_migration_status():
    """Show comprehensive migration status."""
    print("📊 Migration Status Report")
    print("=" * 50)
    
    # Current revision
    current_rev = get_current_revision()
    print(f"Current Revision: {current_rev or 'None'}")
    
    # Migration history (last 5)
    print("\nRecent Migration History:")
    history = get_migration_history()
    for line in history[:5]:
        if line.strip():
            print(f"  {line}")
    
    # Check if migrations are up to date
    print("\nValidation Status:")
    if validate_migrations():
        print("  ✅ Database is in sync with models")
    else:
        print("  ⚠️  Database may need migration")
    
    # Show recent migration events
    log_file = backend_dir / "logs" / "migration_log.json"
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
            
            print("\nRecent Migration Events:")
            for entry in log_entries[-3:]:  # Last 3 events
                status = "✅" if entry["success"] else "❌"
                print(f"  {status} {entry['timestamp']}: {entry['event_type']} "
                      f"({entry.get('from_revision', 'N/A')} → {entry.get('to_revision', 'N/A')})")
        except (json.JSONDecodeError, FileNotFoundError):
            print("  No migration events logged")
    
    print("=" * 50)

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Enhanced Migration Management Script")
        print("=" * 40)
        print("Usage: python manage_migrations.py <command> [args]")
        print("\nBasic Commands:")
        print("  current          - Show current database revision")
        print("  history          - Show migration history")
        print("  create <message> - Create new migration")
        print("  upgrade          - Upgrade to latest revision")
        print("  downgrade [rev]  - Downgrade to revision (default: base)")
        print("  stamp <revision> - Stamp database with revision")
        print("  validate         - Validate migrations against models")
        print("\nEnhanced Commands:")
        print("  safe-upgrade     - Safely upgrade with backup and rollback")
        print("  rollback <rev>   - Rollback to specific revision with safety checks")
        print("  deploy           - Run migrations for deployment environment")
        print("  status           - Show comprehensive migration status")
        print("  backup           - Create database backup")
        print("\nExamples:")
        print("  python manage_migrations.py create 'add user preferences'")
        print("  python manage_migrations.py safe-upgrade")
        print("  python manage_migrations.py rollback abc123")
        print("  python manage_migrations.py deploy")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "current":
            check_current_revision()
        elif command == "history":
            check_migration_history()
        elif command == "create":
            if len(sys.argv) < 3:
                print("Error: Migration message required")
                return
            message = " ".join(sys.argv[2:])
            create_migration(message)
        elif command == "upgrade":
            upgrade_database()
        elif command == "safe-upgrade":
            safe_upgrade()
        elif command == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "base"
            downgrade_database(revision)
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Error: Revision required for rollback")
                return
            revision = sys.argv[2]
            rollback_to_revision(revision)
        elif command == "stamp":
            if len(sys.argv) < 3:
                print("Error: Revision required")
                return
            revision = sys.argv[2]
            stamp_database(revision)
        elif command == "validate":
            validate_migrations()
        elif command == "deploy":
            deployment_migrate()
        elif command == "status":
            show_migration_status()
        elif command == "backup":
            backup_database()
        else:
            print(f"Unknown command: {command}")
            print("Run without arguments to see available commands.")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error executing command '{command}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()