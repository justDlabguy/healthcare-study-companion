# Database Migrations with Alembic

This document explains how to use Alembic for database migrations in the Healthcare Study Companion application.

## Overview

Alembic is configured to manage database schema changes for the application. The configuration is set up to:

- Connect to TiDB Serverless database
- Track only application-specific tables (filters out system tables)
- Support both online and offline migration modes
- Handle MySQL-specific features and constraints

## Configuration Files

- `alembic.ini` - Main Alembic configuration
- `alembic/env.py` - Environment configuration and connection setup
- `alembic/versions/` - Directory containing migration files

## Common Commands

### Check Current Database State

```bash
# Show current database revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration file
alembic revision -m "Description of changes"
```

### Applying Migrations

```bash
# Upgrade to latest revision
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Upgrade by relative number
alembic upgrade +2
```

### Downgrading Migrations

```bash
# Downgrade to previous revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
alembic downgrade base
```

### Stamping Database

```bash
# Mark database as being at a specific revision without running migrations
alembic stamp head
alembic stamp <revision_id>
```

## Migration Management Script

A helper script is available at `scripts/manage_migrations.py`:

```bash
# Check current state
python scripts/manage_migrations.py current

# Create new migration
python scripts/manage_migrations.py create "Add new feature"

# Upgrade database
python scripts/manage_migrations.py upgrade

# Validate migrations
python scripts/manage_migrations.py validate
```

## Best Practices

### 1. Always Review Generated Migrations

Auto-generated migrations should be reviewed before applying:

- Check that only intended changes are included
- Verify data migration logic if needed
- Ensure proper handling of constraints and indexes

### 2. Test Migrations

- Test migrations on a copy of production data
- Verify both upgrade and downgrade paths
- Check for data loss or corruption

### 3. Backup Before Major Changes

Always backup the database before applying migrations in production.

### 4. Migration Naming

Use descriptive names for migrations:

```bash
alembic revision --autogenerate -m "Add user preferences table"
alembic revision --autogenerate -m "Add index on document.created_at"
```

### 5. Handle Data Migrations

For complex data transformations, create custom migration functions:

```python
def upgrade():
    # Schema changes
    op.add_column('users', sa.Column('full_name', sa.String(255)))

    # Data migration
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = CONCAT(first_name, ' ', last_name)"
    )

    # Remove old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

## Troubleshooting

### Migration Conflicts

If multiple developers create migrations simultaneously:

```bash
# Merge migration heads
alembic merge -m "Merge migration heads" <rev1> <rev2>
```

### Database Out of Sync

If the database schema doesn't match the models:

```bash
# Create a migration to sync
alembic revision --autogenerate -m "Sync database with models"

# Or stamp the database if schema is correct
alembic stamp head
```

### System Table Interference

The configuration filters out TiDB system tables, but if you encounter issues:

1. Check the `include_object` function in `alembic/env.py`
2. Ensure system tables are properly filtered
3. Clean up any migrations that include system table changes

## Environment Variables

The migration system uses these environment variables:

- `DATABASE_URL` - Full database connection string
- `DATABASE_HOST` - Database host (fallback)
- `DATABASE_PORT` - Database port (fallback)
- `DATABASE_USER` - Database user (fallback)
- `DATABASE_PASSWORD` - Database password (fallback)
- `DATABASE_NAME` - Database name (fallback)

## Production Deployment

For production deployments:

1. **Backup the database**
2. **Test migrations on staging**
3. **Apply migrations during maintenance window**
4. **Verify application functionality**

```bash
# Production migration workflow
alembic current                    # Check current state
alembic history                    # Review pending migrations
alembic upgrade head              # Apply migrations
alembic current                    # Verify final state
```

## Integration with Application

The application automatically creates tables on startup if they don't exist, but for production:

1. Use migrations for all schema changes
2. Disable auto-table creation in production
3. Apply migrations before starting the application

## Monitoring

Monitor migration performance and impact:

- Track migration execution time
- Monitor database locks during migrations
- Verify data integrity after migrations
- Check application performance after schema changes
