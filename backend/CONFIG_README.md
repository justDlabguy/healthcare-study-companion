# Configuration Management

This document explains how to configure the Healthcare Study Companion backend application.

## Quick Start

### 1. Automated Setup (Recommended)

Run the interactive setup script:

```bash
cd backend
python scripts/setup_environment.py
```

This will guide you through setting up your environment configuration.

### 2. Manual Setup

Copy the example file and fill in your values:

```bash
cp .env.example local.env
# Edit local.env with your configuration
```

### 3. Validate Configuration

Check your configuration:

```bash
# Quick check
python check_config.py

# Comprehensive validation
python scripts/validate_config.py --check-connections
```

## Environment Files

| File | Purpose | Committed to Git |
|------|---------|------------------|
| `.env.example` | Template with all variables | ✅ Yes |
| `local.env` | Your local development config | ❌ No |
| `.env.development` | Development defaults | ✅ Yes |
| `.env.staging` | Staging defaults | ✅ Yes |
| `.env.production` | Production template | ✅ Yes |

## Required Variables

These variables **must** be set for the application to work:

```bash
# Database connection
DATABASE_URL=mysql+pymysql://user:pass@host:port/database

# Security
JWT_SECRET=your-super-secret-jwt-key

# AI Provider (choose one)
MISTRAL_API_KEY=your-mistral-api-key
# OR
OPENAI_API_KEY=your-openai-api-key
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## Configuration Loading Order

The application loads configuration in this order (later files override earlier ones):

1. `.env.production` (if ENVIRONMENT=production)
2. `.env.staging` (if ENVIRONMENT=staging)  
3. `.env.development` (if ENVIRONMENT=development)
4. `local.env` (your local overrides)
5. System environment variables (highest priority)

## Environment-Specific Setup

### Development

```bash
# Use the setup script
python scripts/setup_environment.py --environment development

# Or copy the development template
cp .env.development local.env
# Then edit local.env with your API keys
```

### Staging/Production

For staging and production, set sensitive variables via your deployment platform (Railway, Heroku, etc.) rather than in files:

```bash
# Railway example
railway variables set DATABASE_URL="mysql+pymysql://..."
railway variables set JWT_SECRET="your-secret"
railway variables set MISTRAL_API_KEY="your-key"
```

## Validation and Troubleshooting

### Quick Health Check

```bash
python check_config.py
```

### Comprehensive Validation

```bash
# Validate configuration only
python scripts/validate_config.py

# Validate and test connections
python scripts/validate_config.py --check-connections

# Strict mode (warnings become errors)
python scripts/validate_config.py --strict
```

### Common Issues

1. **"Configuration validation failed"**
   - Run `python check_config.py` to see what's missing
   - Check that all required variables are set

2. **"Database connection failed"**
   - Verify your `DATABASE_URL` format
   - Check that the database server is running
   - For TiDB Cloud, ensure SSL certificates are correct

3. **"LLM API errors"**
   - Verify your API key is correct
   - Check that you haven't exceeded rate limits
   - Ensure the model names are valid for your provider

## Security Best Practices

1. **Never commit secrets to Git**
   - Use `local.env` for development secrets
   - Use deployment platform variables for production

2. **Use strong JWT secrets**
   - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
   - Or use the setup script which generates them automatically

3. **Restrict CORS origins in production**
   - Don't use `CORS_ORIGINS=*` in production
   - Set specific domains: `CORS_ORIGINS=https://yourdomain.com`

4. **Enable structured logging in production**
   - Set `STRUCTURED_LOGGING=true`
   - Set `LOG_LEVEL=INFO` (not DEBUG)

## Configuration Reference

See [docs/ENVIRONMENT_VARIABLES.md](../docs/ENVIRONMENT_VARIABLES.md) for complete documentation of all available configuration options.

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `check_config.py` | Quick configuration validation |
| `scripts/setup_environment.py` | Interactive environment setup |
| `scripts/validate_config.py` | Comprehensive configuration validation |

## Getting Help

1. Check the logs for detailed error messages
2. Run the validation scripts to identify issues
3. Review the environment variables documentation
4. Ensure all required variables are set for your environment