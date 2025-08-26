#!/usr/bin/env python3
"""
Complete migration workflow script for the Healthcare Study Companion application.

This script provides a unified interface for all migration operations including:
- Generating new migrations
- Applying migrations
- Rolling back migrations
- Deployment workflows
- Status checking and validation
"""

import os
import sys
import subprocess
import json
import datetime
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_script(script_name, args=None):
    """Run a migration script with proper error handling."""
    if args is None:
        args = []
    
    script_path = backend_dir / "scripts" / script_name
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False
    
    command = ["python", str(script_path)] + args
    
    try:
        result = subprocess.run(command, cwd=backend_dir, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def show_migration_status():
    """Show comprehensive migration status."""
    print_section("Migration Status")
    return run_script("manage_migrations.py", ["status"])

def create_new_migration():
    """Interactive migration creation workflow."""
    print_section("Create New Migration")
    
    print("This will guide you through creating a new database migration.")
    print("\nTips for good migration messages:")
    print("- Use descriptive, action-oriented messages")
    print("- Examples: 'add user preferences table', 'update flashcard model'")
    print("- Avoid: 'fix', 'update', 'change' without context")
    
    message = input("\nEnter migration message: ").strip()
    if not message:
        print("❌ Migration message is required")
        return False
    
    print(f"\nCreating migration: '{message}'")
    
    # Ask for options
    auto_generate = input("Auto-generate from model changes? (Y/n): ").strip().lower()
    auto_generate = auto_generate != 'n'
    
    force = input("Force creation even if no changes detected? (y/N): ").strip().lower()
    force = force == 'y'
    
    # Build arguments
    args = [message]
    if not auto_generate:
        args.append("--no-autogenerate")
    if force:
        args.append("--force")
    
    return run_script("generate_migration.py", args)

def apply_migrations():
    """Apply pending migrations with safety checks."""
    print_section("Apply Migrations")
    
    print("This will apply all pending migrations to the database.")
    
    # Show current status first
    if not run_script("manage_migrations.py", ["current"]):
        print("❌ Could not determine current migration status")
        return False
    
    # Ask for confirmation
    response = input("\nProceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled")
        return False
    
    # Use safe upgrade
    return run_script("manage_migrations.py", ["safe-upgrade"])

def rollback_migrations():
    """Interactive migration rollback."""
    print_section("Rollback Migrations")
    
    print("This will rollback the database to a previous migration.")
    print("⚠️  WARNING: This operation may result in data loss!")
    
    # Show migration history
    print("\nCurrent migration history:")
    if not run_script("manage_migrations.py", ["history"]):
        print("❌ Could not retrieve migration history")
        return False
    
    print("\nRollback options:")
    print("1. Rollback to specific revision")
    print("2. Emergency rollback to last known good state")
    print("3. Cancel")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        revision = input("Enter target revision: ").strip()
        if not revision:
            print("❌ Revision is required")
            return False
        
        return run_script("rollback_migrations.py", ["rollback", revision])
    
    elif choice == "2":
        print("⚠️  This will attempt to rollback to the last known good state")
        confirm = input("Are you sure? Type 'yes' to confirm: ").strip()
        if confirm.lower() == "yes":
            return run_script("rollback_migrations.py", ["emergency"])
        else:
            print("Emergency rollback cancelled")
            return False
    
    else:
        print("Rollback cancelled")
        return False

def deployment_workflow():
    """Run deployment migration workflow."""
    print_section("Deployment Workflow")
    
    environment = os.getenv("ENVIRONMENT", "development")
    print(f"Current environment: {environment}")
    
    if environment == "production":
        print("⚠️  PRODUCTION DEPLOYMENT DETECTED")
        print("This will run migrations in production with extra safety checks.")
        
        confirm = input("Continue with production deployment? Type 'yes' to confirm: ").strip()
        if confirm.lower() != "yes":
            print("Production deployment cancelled")
            return False
    
    return run_script("deploy.py")

def validate_migrations():
    """Validate migration state and consistency."""
    print_section("Validate Migrations")
    
    print("Checking migration consistency and database state...")
    
    # Use the validation from manage_migrations
    return run_script("manage_migrations.py", ["validate"])

def migration_history():
    """Show detailed migration history."""
    print_section("Migration History")
    
    return run_script("manage_migrations.py", ["history"])

def backup_database():
    """Create database backup."""
    print_section("Database Backup")
    
    print("Creating database backup...")
    return run_script("manage_migrations.py", ["backup"])

def show_help():
    """Show help information."""
    print_header("Migration Workflow Help")
    
    print("""
This script provides a unified interface for all database migration operations.

Available Commands:
  status      - Show current migration status and health
  create      - Create a new migration (interactive)
  apply       - Apply pending migrations with safety checks
  rollback    - Rollback migrations (interactive)
  deploy      - Run deployment migration workflow
  validate    - Validate migration state and consistency
  history     - Show migration history
  backup      - Create database backup
  help        - Show this help message

Examples:
  python migration_workflow.py status
  python migration_workflow.py create
  python migration_workflow.py apply
  python migration_workflow.py rollback
  python migration_workflow.py deploy

Environment Variables:
  ENVIRONMENT          - Set to 'production' for production safety checks
  AUTO_ROLLBACK_ON_FAILURE - Set to 'true' to enable automatic rollback on failure

Safety Features:
- Pre-migration validation and conflict detection
- Automatic backups before major operations
- Rollback procedures for failed migrations
- Environment-specific safety checks
- Comprehensive logging and audit trails

For more detailed options, use the individual scripts:
- manage_migrations.py     - Core migration management
- generate_migration.py    - Advanced migration generation
- deploy_migrations.py     - Deployment-specific migrations
- rollback_migrations.py   - Advanced rollback procedures
- deploy.py               - Full deployment workflow
""")

def main():
    """Main workflow function."""
    if len(sys.argv) < 2:
        print_header("Healthcare Study Companion - Migration Workflow")
        print("""
Welcome to the Migration Workflow Manager!

Usage: python migration_workflow.py <command>

Quick Commands:
  status      - Check migration status
  create      - Create new migration
  apply       - Apply migrations
  rollback    - Rollback migrations
  deploy      - Deploy migrations
  help        - Show detailed help

Run 'python migration_workflow.py help' for more information.
""")
        return
    
    command = sys.argv[1].lower()
    
    print_header("Healthcare Study Companion - Migration Workflow")
    
    try:
        if command == "status":
            show_migration_status()
        
        elif command == "create":
            create_new_migration()
        
        elif command == "apply":
            apply_migrations()
        
        elif command == "rollback":
            rollback_migrations()
        
        elif command == "deploy":
            deployment_workflow()
        
        elif command == "validate":
            validate_migrations()
        
        elif command == "history":
            migration_history()
        
        elif command == "backup":
            backup_database()
        
        elif command == "help":
            show_help()
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python migration_workflow.py help' for available commands.")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()