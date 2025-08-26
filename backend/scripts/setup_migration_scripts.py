#!/usr/bin/env python3
"""
Setup script for migration workflow scripts.

This script ensures all migration scripts are properly configured and executable.
"""

import os
import stat
from pathlib import Path

def make_executable(file_path):
    """Make a file executable on Unix-like systems."""
    if os.name != 'nt':  # Not Windows
        current_permissions = file_path.stat().st_mode
        file_path.chmod(current_permissions | stat.S_IEXEC)
        print(f"✅ Made executable: {file_path.name}")
    else:
        print(f"ℹ️  Windows detected - {file_path.name} permissions unchanged")

def main():
    """Setup migration scripts."""
    print("🔧 Setting up migration workflow scripts...")
    print("=" * 50)
    
    scripts_dir = Path(__file__).parent
    
    # List of migration scripts to make executable
    migration_scripts = [
        "manage_migrations.py",
        "deploy_migrations.py",
        "rollback_migrations.py",
        "generate_migration.py",
        "migration_workflow.py",
        "deploy.py"
    ]
    
    for script_name in migration_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            make_executable(script_path)
        else:
            print(f"⚠️  Script not found: {script_name}")
    
    # Create necessary directories
    backend_dir = scripts_dir.parent
    directories_to_create = [
        backend_dir / "logs",
        backend_dir / "backups"
    ]
    
    for directory in directories_to_create:
        directory.mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory.name}")
    
    print("\n📋 Migration Workflow Setup Complete!")
    print("\nAvailable commands:")
    print("  python scripts/migration_workflow.py help    - Show all available commands")
    print("  python scripts/migration_workflow.py status  - Check migration status")
    print("  python scripts/migration_workflow.py create  - Create new migration")
    print("  python scripts/migration_workflow.py apply   - Apply migrations")
    print("  python scripts/migration_workflow.py deploy  - Run deployment workflow")
    
    print("\nDirect script access:")
    for script in migration_scripts:
        print(f"  python scripts/{script}")
    
    print("\n🎯 Quick Start:")
    print("1. Check current status: python scripts/migration_workflow.py status")
    print("2. Create a migration: python scripts/migration_workflow.py create")
    print("3. Apply migrations: python scripts/migration_workflow.py apply")

if __name__ == "__main__":
    main()