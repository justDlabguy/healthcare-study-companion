#!/usr/bin/env python3
"""
Migration generation script for the Healthcare Study Companion application.

This script provides a safe way to generate new migrations with validation,
conflict detection, and proper naming conventions.
"""

import os
import sys
import subprocess
import json
import datetime
import re
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def log_migration_event(event_type, message, success=True, details=None):
    """Log migration generation events."""
    log_dir = backend_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "migration_generation_log.json"
    
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
        "details": details or {}
    }
    
    log_entries.append(log_entry)
    
    # Keep only last 50 entries
    log_entries = log_entries[-50:]
    
    # Save updated log
    with open(log_file, 'w') as f:
        json.dump(log_entries, f, indent=2)
    
    # Also print to stdout
    status = "✅" if success else "❌"
    print(f"{status} [{datetime.datetime.now().isoformat()}] {event_type}: {message}")

def run_command_with_timeout(command, timeout=120, cwd=None):
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

def validate_migration_message(message):
    """Validate migration message follows conventions."""
    if not message:
        return False, "Migration message cannot be empty"
    
    if len(message) < 5:
        return False, "Migration message must be at least 5 characters long"
    
    if len(message) > 100:
        return False, "Migration message must be less than 100 characters"
    
    # Check for valid characters (alphanumeric, spaces, underscores, hyphens)
    if not re.match(r'^[a-zA-Z0-9\s_-]+$', message):
        return False, "Migration message contains invalid characters"
    
    # Check for common patterns that should be avoided
    forbidden_patterns = [
        r'test',
        r'temp',
        r'debug',
        r'fix.*fix',  # Multiple "fix" words
        r'update.*update'  # Multiple "update" words
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, message.lower()):
            return False, f"Migration message should not contain '{pattern}' pattern"
    
    return True, "Migration message is valid"

def check_for_model_changes():
    """Check if there are actual model changes to migrate."""
    print("🔍 Checking for model changes...")
    
    # Create a temporary migration to see if there are changes
    temp_message = "temp_check_for_changes"
    success, stdout, stderr = run_command_with_timeout(
        f'alembic revision --autogenerate -m "{temp_message}"'
    )
    
    if not success:
        log_migration_event("model_check_failed", f"Failed to check for model changes: {stderr}", False)
        return False, "Failed to check for model changes"
    
    # Find the generated migration file
    versions_dir = backend_dir / "alembic" / "versions"
    temp_files = list(versions_dir.glob(f"*{temp_message.replace(' ', '_')}*.py"))
    
    if not temp_files:
        log_migration_event("model_check_failed", "No migration file generated", False)
        return False, "No migration file was generated"
    
    temp_file = temp_files[0]
    
    try:
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Remove the temporary file
        temp_file.unlink()
        
        # Check if the migration has any actual changes
        # Look for operation calls (op.create_table, op.add_column, etc.)
        operation_patterns = [
            r'op\.create_table',
            r'op\.drop_table',
            r'op\.add_column',
            r'op\.drop_column',
            r'op\.alter_column',
            r'op\.create_index',
            r'op\.drop_index',
            r'op\.create_foreign_key',
            r'op\.drop_constraint'
        ]
        
        has_operations = any(re.search(pattern, content) for pattern in operation_patterns)
        
        if has_operations:
            log_migration_event("model_check_success", "Model changes detected", True)
            return True, "Model changes detected - migration needed"
        else:
            log_migration_event("model_check_no_changes", "No model changes detected", True)
            return False, "No model changes detected - migration not needed"
    
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file.exists():
            temp_file.unlink()
        
        log_migration_event("model_check_error", f"Error checking model changes: {e}", False)
        return False, f"Error checking model changes: {e}"

def check_for_migration_conflicts():
    """Check for potential migration conflicts."""
    print("🔍 Checking for migration conflicts...")
    
    # Get current migration history
    success, stdout, stderr = run_command_with_timeout("alembic history")
    
    if not success:
        log_migration_event("conflict_check_failed", f"Failed to get migration history: {stderr}", False)
        return False, "Failed to check migration history"
    
    # Check for multiple heads (branching)
    success, stdout, stderr = run_command_with_timeout("alembic heads")
    
    if not success:
        log_migration_event("conflict_check_failed", f"Failed to get migration heads: {stderr}", False)
        return False, "Failed to check migration heads"
    
    # Count the number of heads
    heads = [line.strip() for line in stdout.split('\n') if line.strip() and not line.startswith('INFO')]
    
    if len(heads) > 1:
        log_migration_event("conflict_detected", f"Multiple migration heads detected: {heads}", False)
        return False, f"Multiple migration heads detected: {heads}. Please merge migrations first."
    
    log_migration_event("conflict_check_success", "No migration conflicts detected", True)
    return True, "No migration conflicts detected"

def generate_migration(message, auto_generate=True):
    """Generate a new migration with the given message."""
    print(f"📝 Generating migration: {message}")
    
    # Prepare the command
    if auto_generate:
        command = f'alembic revision --autogenerate -m "{message}"'
    else:
        command = f'alembic revision -m "{message}"'
    
    success, stdout, stderr = run_command_with_timeout(command)
    
    if success:
        # Extract the migration file path from output
        migration_file = None
        for line in stdout.split('\n'):
            if 'Generating' in line and '.py' in line:
                # Extract file path
                parts = line.split()
                for part in parts:
                    if part.endswith('.py'):
                        migration_file = part
                        break
        
        log_migration_event(
            "migration_generated", 
            f"Migration generated successfully: {message}", 
            True,
            {"migration_file": migration_file}
        )
        print(f"✅ Migration generated successfully")
        if migration_file:
            print(f"📄 Migration file: {migration_file}")
        
        return True, migration_file
    else:
        log_migration_event("migration_generation_failed", f"Failed to generate migration: {stderr}", False)
        print(f"❌ Failed to generate migration: {stderr}")
        return False, None

def review_generated_migration(migration_file):
    """Review the generated migration file and provide feedback."""
    if not migration_file or not Path(migration_file).exists():
        print("⚠️  Cannot review migration file - file not found")
        return
    
    print(f"📖 Reviewing generated migration: {migration_file}")
    
    try:
        with open(migration_file, 'r') as f:
            content = f.read()
        
        # Check for common issues
        issues = []
        
        # Check for empty upgrade/downgrade functions
        if 'def upgrade():' in content and 'pass' in content:
            issues.append("Migration appears to be empty (contains 'pass')")
        
        # Check for potentially dangerous operations
        dangerous_patterns = [
            (r'op\.drop_table', "Dropping tables - ensure you have backups"),
            (r'op\.drop_column', "Dropping columns - ensure data is not needed"),
            (r'op\.drop_constraint', "Dropping constraints - may affect data integrity"),
        ]
        
        for pattern, warning in dangerous_patterns:
            if re.search(pattern, content):
                issues.append(warning)
        
        # Check for missing downgrade operations
        upgrade_ops = len(re.findall(r'op\.\w+', content.split('def downgrade():')[0]))
        downgrade_section = content.split('def downgrade():')[1] if 'def downgrade():' in content else ""
        downgrade_ops = len(re.findall(r'op\.\w+', downgrade_section))
        
        if upgrade_ops > 0 and downgrade_ops == 0:
            issues.append("Migration has upgrade operations but no downgrade operations")
        
        if issues:
            print("⚠️  Migration review found potential issues:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            print("\nPlease review the migration file carefully before applying it.")
        else:
            print("✅ Migration review passed - no obvious issues found")
        
        # Show a preview of the migration
        print("\n📋 Migration preview:")
        print("-" * 50)
        
        # Extract and show the upgrade function
        lines = content.split('\n')
        in_upgrade = False
        upgrade_lines = []
        
        for line in lines:
            if 'def upgrade():' in line:
                in_upgrade = True
                upgrade_lines.append(line)
            elif in_upgrade and line.startswith('def '):
                break
            elif in_upgrade:
                upgrade_lines.append(line)
        
        for line in upgrade_lines[:20]:  # Show first 20 lines
            print(line)
        
        if len(upgrade_lines) > 20:
            print("... (truncated)")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"⚠️  Error reviewing migration file: {e}")

def main():
    """Main function for migration generation."""
    if len(sys.argv) < 2:
        print("Migration Generation Script")
        print("=" * 30)
        print("Usage: python generate_migration.py <message> [options]")
        print("\nOptions:")
        print("  --no-autogenerate    Create empty migration (manual)")
        print("  --force             Skip model change detection")
        print("  --no-review         Skip migration review")
        print("\nExamples:")
        print("  python generate_migration.py 'add user preferences table'")
        print("  python generate_migration.py 'update user model' --no-autogenerate")
        print("  python generate_migration.py 'fix index issue' --force")
        return
    
    message = sys.argv[1]
    auto_generate = "--no-autogenerate" not in sys.argv
    force = "--force" in sys.argv
    review = "--no-review" not in sys.argv
    
    print("📝 Healthcare Study Companion - Migration Generation Script")
    print("=" * 60)
    print(f"Message: {message}")
    print(f"Auto-generate: {auto_generate}")
    print(f"Force: {force}")
    print(f"Review: {review}")
    print("=" * 60)
    
    try:
        # Step 1: Validate migration message
        valid, validation_message = validate_migration_message(message)
        if not valid:
            print(f"❌ Invalid migration message: {validation_message}")
            return
        
        print(f"✅ Migration message validated: {validation_message}")
        
        # Step 2: Check for migration conflicts
        conflict_ok, conflict_message = check_for_migration_conflicts()
        if not conflict_ok:
            print(f"❌ Migration conflict detected: {conflict_message}")
            return
        
        print(f"✅ No migration conflicts: {conflict_message}")
        
        # Step 3: Check for model changes (unless forced or manual)
        if auto_generate and not force:
            has_changes, changes_message = check_for_model_changes()
            if not has_changes:
                print(f"⚠️  {changes_message}")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    print("Migration generation cancelled")
                    return
        
        # Step 4: Generate the migration
        success, migration_file = generate_migration(message, auto_generate)
        if not success:
            return
        
        # Step 5: Review the generated migration
        if review and migration_file:
            review_generated_migration(migration_file)
        
        print("\n🎉 Migration generation completed!")
        print("\nNext steps:")
        print("1. Review the generated migration file")
        print("2. Test the migration on a development database")
        print("3. Apply the migration: alembic upgrade head")
        
    except KeyboardInterrupt:
        print("\n❌ Migration generation cancelled by user")
    
    except Exception as e:
        log_migration_event("generation_error", f"Unexpected error during migration generation: {e}", False)
        print(f"❌ Unexpected error during migration generation: {e}")

if __name__ == "__main__":
    main()