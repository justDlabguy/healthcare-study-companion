# Migration Workflow Scripts

This directory contains comprehensive database migration management scripts for the Healthcare Study Companion application.

## Overview

The migration workflow provides:
- ✅ Safe migration generation with validation
- ✅ Automated deployment with rollback capabilities
- ✅ Comprehensive error handling and logging
- ✅ Environment-specific safety checks
- ✅ Audit trails and monitoring

## Quick Start

### 1. Setup (First Time)
```bash
cd backend
python scripts/setup_migration_scripts.py
```

### 2. Check Migration Status
```bash
python scripts/migration_workflow.py status
```

### 3. Create New Migration
```bash
python scripts/migration_workflow.py create
```

### 4. Apply Migrations
```bash
python scripts/migration_workflow.py apply
```

## Scripts Overview

### 🎯 Main Workflow Script
- **`migration_workflow.py`** - Unified interface for all migration operations
  - Interactive commands for common tasks
  - Safety checks and validation
  - Environment-aware operations

### 🔧 Core Migration Scripts
- **`manage_migrations.py`** - Core migration management
  - Create, apply, rollback migrations
  - Validation and status checking
  - Backup and restore capabilities

- **`generate_migration.py`** - Advanced migration generation
  - Model change detection
  - Conflict resolution
  - Migration validation and review

- **`deploy_migrations.py`** - Deployment-specific migrations
  - Production-safe deployment
  - Health checks and verification
  - Rollback on failure

- **`rollback_migrations.py`** - Migration rollback procedures
  - Safe rollback with validation
  - Emergency rollback procedures
  - Backup before rollback

- **`deploy.py`** - Complete deployment workflow
  - Environment validation
  - Migration orchestration
  - Health checks and monitoring

### 🛠️ Utility Scripts
- **`setup_migration_scripts.py`** - Initial setup and configuration

## Command Reference

### Migration Workflow Commands
```bash
# Check status
python scripts/migration_workflow.py status

# Create new migration (interactive)
python scripts/migration_workflow.py create

# Apply pending migrations
python scripts/migration_workflow.py apply

# Rollback migrations (interactive)
python scripts/migration_workflow.py rollback

# Run deployment workflow
python scripts/migration_workflow.py deploy

# Validate migration state
python scripts/migration_workflow.py validate

# Show migration history
python scripts/migration_workflow.py history

# Create database backup
python scripts/migration_workflow.py backup

# Show help
python scripts/migration_workflow.py help
```

### Direct Script Usage

#### Core Management
```bash
# Check current revision
python scripts/manage_migrations.py current

# Show migration history
python scripts/manage_migrations.py history

# Create migration
python scripts/manage_migrations.py create "add user preferences"

# Safe upgrade with backup
python scripts/manage_migrations.py safe-upgrade

# Rollback to specific revision
python scripts/manage_migrations.py rollback abc123

# Show comprehensive status
python scripts/manage_migrations.py status
```

#### Advanced Generation
```bash
# Generate migration with validation
python scripts/generate_migration.py "add user preferences table"

# Create empty migration (manual)
python scripts/generate_migration.py "custom changes" --no-autogenerate

# Force creation without change detection
python scripts/generate_migration.py "fix issue" --force

# Skip migration review
python scripts/generate_migration.py "quick fix" --no-review
```

#### Deployment
```bash
# Run deployment migrations
python scripts/deploy_migrations.py

# Full deployment workflow
python scripts/deploy.py
```

#### Rollback Procedures
```bash
# Rollback to specific revision
python scripts/rollback_migrations.py rollback abc123

# Emergency rollback to last known good
python scripts/rollback_migrations.py emergency

# Check rollback status
python scripts/rollback_migrations.py status
```

## Environment Configuration

### Required Environment Variables
```bash
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
JWT_SECRET=your_jwt_secret
MISTRAL_API_KEY=your_mistral_api_key
```

### Optional Environment Variables
```bash
ENVIRONMENT=production                    # Enable production safety checks
AUTO_ROLLBACK_ON_FAILURE=true           # Auto-rollback on deployment failure
RAILWAY_DEPLOYMENT_ID=deployment_id     # Deployment tracking
RAILWAY_GIT_COMMIT_SHA=commit_sha       # Commit tracking
```

## Safety Features

### 🛡️ Production Safety
- Environment-specific validation
- Automatic backups before major operations
- Rollback procedures for failed migrations
- Health checks and verification
- Comprehensive logging and audit trails

### 🔍 Validation Checks
- Model consistency validation
- Migration conflict detection
- Database connectivity verification
- Environment variable validation
- Migration file review and analysis

### 📊 Monitoring & Logging
- Structured JSON logging
- Deployment event tracking
- Performance metrics
- Error tracking and alerting
- Audit trail maintenance

## File Structure

```
backend/scripts/
├── README.md                    # This documentation
├── setup_migration_scripts.py  # Initial setup
├── migration_workflow.py       # Main workflow interface
├── manage_migrations.py        # Core migration management
├── generate_migration.py       # Advanced migration generation
├── deploy_migrations.py        # Deployment migrations
├── rollback_migrations.py      # Rollback procedures
└── deploy.py                   # Full deployment workflow

backend/logs/                    # Generated logs
├── migration_log.json          # Migration events
├── deployment_log.json         # Deployment events
├── rollback_log.json          # Rollback events
└── migration_generation_log.json # Generation events

backend/backups/                 # Generated backups
└── *.json                      # Backup metadata files
```

## Integration with CI/CD

### GitHub Actions
The migration workflow integrates with GitHub Actions:

- **Backend CI** (`.github/workflows/backend-ci.yml`)
  - Tests migration generation
  - Validates migration state
  - Runs migration tests

- **Production Deployment** (`.github/workflows/deploy-production.yml`)
  - Validates migration state
  - Creates pre-deployment backups
  - Runs deployment with migrations
  - Handles rollback on failure

### Railway Deployment
The `Procfile` includes automatic migration running:
```
release: python scripts/deploy_migrations.py
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --app-dir backend
```

## Best Practices

### 📝 Migration Messages
- Use descriptive, action-oriented messages
- Good: "add user preferences table", "update flashcard model indexes"
- Avoid: "fix", "update", "change" without context

### 🔄 Development Workflow
1. Make model changes
2. Generate migration: `python scripts/migration_workflow.py create`
3. Review generated migration file
4. Test migration on development database
5. Apply migration: `python scripts/migration_workflow.py apply`
6. Commit both model changes and migration file

### 🚀 Deployment Workflow
1. Validate migration state: `python scripts/migration_workflow.py validate`
2. Create backup: `python scripts/migration_workflow.py backup`
3. Deploy: `python scripts/migration_workflow.py deploy`
4. Verify: `python scripts/migration_workflow.py status`

### 🚨 Emergency Procedures
If deployment fails:
1. Check logs: `backend/logs/deployment_log.json`
2. Assess damage: `python scripts/migration_workflow.py status`
3. Emergency rollback: `python scripts/rollback_migrations.py emergency`
4. Investigate and fix issues
5. Redeploy when ready

## Troubleshooting

### Common Issues

#### Migration Conflicts
```bash
# Check for conflicts
python scripts/migration_workflow.py validate

# Resolve conflicts manually, then
python scripts/manage_migrations.py stamp head
```

#### Failed Deployment
```bash
# Check deployment logs
cat backend/logs/deployment_log.json

# Emergency rollback
python scripts/rollback_migrations.py emergency

# Check status
python scripts/migration_workflow.py status
```

#### Database Connectivity Issues
```bash
# Test connectivity
python scripts/migration_workflow.py validate

# Check environment variables
echo $DATABASE_URL
```

### Getting Help
- Run `python scripts/migration_workflow.py help` for detailed help
- Check log files in `backend/logs/` for error details
- Review migration files in `backend/alembic/versions/`

## Contributing

When adding new migration functionality:
1. Follow the existing logging patterns
2. Add comprehensive error handling
3. Include safety checks for production
4. Update this documentation
5. Add tests for new functionality

## Support

For issues with the migration workflow:
1. Check the logs in `backend/logs/`
2. Run validation: `python scripts/migration_workflow.py validate`
3. Review the migration history: `python scripts/migration_workflow.py history`
4. Consult this documentation
5. Check the individual script help: `python scripts/<script_name>.py --help`