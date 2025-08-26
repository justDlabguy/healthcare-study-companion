# Environment Variables Documentation

This document provides comprehensive documentation for all environment variables used in the Healthcare Study Companion application.

## Table of Contents

- [Overview](#overview)
- [Backend Environment Variables](#backend-environment-variables)
- [Frontend Environment Variables](#frontend-environment-variables)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Validation](#validation)
- [Security Best Practices](#security-best-practices)
- [Deployment Configuration](#deployment-configuration)

## Overview

The Healthcare Study Companion uses environment variables for configuration across different deployment environments (development, staging, production). This approach ensures:

- **Security**: Sensitive data like API keys and database credentials are not stored in code
- **Flexibility**: Different configurations for different environments
- **Maintainability**: Centralized configuration management

## Backend Environment Variables

### Application Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `ENVIRONMENT` | No | `development` | Application environment | `production` |
| `APP_NAME` | No | `Healthcare Study Companion API` | Application name | `Healthcare Study Companion API` |

### Database Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `DATABASE_URL` | Yes* | None | Complete database connection URL | `mysql+pymysql://user:pass@host:port/db?ssl_ca=...` |
| `DATABASE_HOST` | Yes** | `localhost` | Database host | `gateway01.us-east-1.prod.aws.tidbcloud.com` |
| `DATABASE_PORT` | Yes** | `4000` | Database port | `4000` |
| `DATABASE_USER` | Yes** | `root` | Database username | `your_username` |
| `DATABASE_PASSWORD` | Yes** | Empty | Database password | `your_password` |
| `DATABASE_NAME` | Yes** | `healthcare_study` | Database name | `healthcare_study` |

*Required if individual database parameters are not provided  
**Required if DATABASE_URL is not provided

### Security Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `JWT_SECRET` | Yes | `change-me` | JWT token signing secret (must be changed in production) | `your-super-secret-jwt-key-256-bits-long` |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins (comma-separated) | `https://yourdomain.com,https://www.yourdomain.com` |

### AI/LLM Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `LLM_PROVIDER` | No | `mistral` | AI provider (openai, anthropic, huggingface, together, mistral) | `mistral` |
| `DEFAULT_LLM_MODEL` | No | `mistral-small` | Default model for text generation | `mistral-small` |
| `EMBEDDING_MODEL` | No | `mistral-embed` | Model for embeddings | `mistral-embed` |
| `LLM_MODEL_ID` | No | `mistral-small` | LLM model identifier | `mistral-small` |
| `EMBEDDING_MODEL_ID` | No | `mistral-embed` | Embedding model identifier | `mistral-embed` |
| `OPENAI_API_KEY` | Conditional | None | OpenAI API key (required if LLM_PROVIDER=openai) | `sk-...` |
| `ANTHROPIC_API_KEY` | Conditional | None | Anthropic API key (required if LLM_PROVIDER=anthropic) | `sk-ant-...` |
| `HUGGINGFACE_API_KEY` | Conditional | None | Hugging Face API key (required if LLM_PROVIDER=huggingface) | `hf_...` |
| `TOGETHER_API_KEY` | Conditional | None | Together AI API key (required if LLM_PROVIDER=together) | `...` |
| `MISTRAL_API_KEY` | Conditional | None | Mistral API key (required if LLM_PROVIDER=mistral) | `...` |
| `LLM_RATE_LIMIT_PER_MINUTE` | No | `60` | Rate limit for LLM requests per minute | `100` |
| `LLM_MAX_TOKENS` | No | `4096` | Maximum tokens for LLM responses | `4096` |
| `LLM_TEMPERATURE` | No | `0.7` | Temperature for LLM generation (0.0-2.0) | `0.7` |

### Email Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `EMAIL_ENABLED` | No | `false` | Enable email functionality | `true` |
| `SMTP_SERVER` | Conditional | `smtp.gmail.com` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | Conditional | `587` | SMTP server port | `587` |
| `SMTP_USERNAME` | Conditional | None | SMTP username (required if EMAIL_ENABLED=true) | `your_email@gmail.com` |
| `SMTP_PASSWORD` | Conditional | None | SMTP password (required if EMAIL_ENABLED=true) | `your_app_password` |
| `SMTP_FROM_EMAIL` | Conditional | `noreply@example.com` | From email address | `noreply@yourdomain.com` |

### Performance Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `DB_POOL_SIZE` | No | `20` | Database connection pool size | `20` |
| `DB_MAX_OVERFLOW` | No | `30` | Maximum overflow connections | `30` |
| `DB_POOL_TIMEOUT` | No | `30` | Connection pool timeout (seconds) | `30` |
| `MAX_CONCURRENT_AI_REQUESTS` | No | `10` | Maximum concurrent AI requests | `10` |
| `MAX_CONCURRENT_DOCUMENT_PROCESSING` | No | `5` | Maximum concurrent document processing | `5` |
| `MAX_FILE_SIZE_MB` | No | `50` | Maximum file upload size (MB) | `50` |
| `ALLOWED_FILE_TYPES` | No | `pdf,txt,docx,md` | Allowed file types (comma-separated) | `pdf,txt,docx,md` |

### Logging Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `STRUCTURED_LOGGING` | No | `true` | Enable structured logging | `true` |

### Deployment Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `AUTO_ROLLBACK_ON_FAILURE` | No | `true` | Auto-rollback on deployment failure | `true` |
| `RAILWAY_DEPLOYMENT_ID` | No | None | Railway deployment ID (set automatically) | `...` |
| `RAILWAY_GIT_COMMIT_SHA` | No | None | Git commit SHA (set automatically) | `...` |

## Frontend Environment Variables

### API Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | None | Backend API base URL | `https://your-backend.railway.app` |

### Application Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NEXT_PUBLIC_ENVIRONMENT` | No | `development` | Application environment | `production` |
| `NEXT_PUBLIC_APP_NAME` | No | `Healthcare Study Companion` | Application name | `Healthcare Study Companion` |

### Feature Flags

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NEXT_PUBLIC_ENABLE_DEBUG_MODE` | No | `false` | Enable debug mode | `false` |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | No | `false` | Enable analytics tracking | `true` |

### Analytics Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `NEXT_PUBLIC_GOOGLE_ANALYTICS_ID` | Conditional | None | Google Analytics tracking ID | `GA-XXXXXXXXX-X` |
| `NEXT_PUBLIC_MIXPANEL_TOKEN` | Conditional | None | Mixpanel project token | `your_mixpanel_token` |
| `NEXT_PUBLIC_SENTRY_DSN` | No | None | Sentry error tracking DSN | `https://xxx@sentry.io/xxx` |

### Deployment Configuration

| Variable | Required | Default | Description | Example |
|----------|----------|---------|-------------|---------|
| `VERCEL_URL` | No | None | Vercel deployment URL (set automatically) | `...` |
| `VERCEL_GIT_COMMIT_SHA` | No | None | Git commit SHA (set automatically) | `...` |

## Environment-Specific Configuration

### Development Environment

**Backend (.env.development):**
- Lower resource limits for local development
- Debug logging enabled
- Local database connection
- Relaxed security settings
- CORS allows localhost

**Frontend (.env.development):**
- API URL points to localhost:8000
- Debug mode enabled
- Analytics disabled

### Staging Environment

**Backend (.env.staging):**
- Production-like settings
- Structured logging
- Staging database
- Email enabled for testing
- CORS restricted to staging domain

**Frontend (.env.staging):**
- API URL points to staging backend
- Debug mode disabled
- Analytics enabled for testing

### Production Environment

**Backend (.env.production):**
- Maximum security settings
- Structured logging
- Production database with SSL
- Email enabled
- CORS restricted to production domains
- Optimized performance settings

**Frontend (.env.production):**
- API URL points to production backend
- Debug mode disabled
- Analytics enabled
- Error tracking enabled

## Validation

The application includes validation scripts to ensure environment variables are properly configured:

### Backend Validation

```bash
# Validate current environment
python scripts/validate_environment.py

# Validate specific environment
python scripts/validate_environment.py --environment production

# Strict validation (fail on warnings)
python scripts/validate_environment.py --strict

# Verbose output
python scripts/validate_environment.py --verbose

# JSON output for CI/CD
python scripts/validate_environment.py --json
```

### Frontend Validation

```bash
# Validate current environment
node scripts/validate-environment.js

# Validate specific environment
node scripts/validate-environment.js --environment production

# Strict validation (fail on warnings)
node scripts/validate-environment.js --strict

# Verbose output
node scripts/validate-environment.js --verbose

# JSON output for CI/CD
node scripts/validate-environment.js --json
```

## Security Best Practices

### 1. Secret Management

- **Never commit secrets to version control**
- Use secure environment variable management in deployment platforms
- Rotate secrets regularly
- Use strong, randomly generated values for JWT secrets

### 2. Database Security

- Use SSL/TLS for database connections in production
- Restrict database access to application servers only
- Use strong database passwords
- Enable database audit logging

### 3. API Keys

- Store API keys securely in deployment platform
- Use least-privilege API keys when possible
- Monitor API key usage
- Rotate API keys regularly

### 4. CORS Configuration

- Never use `*` for CORS origins in production
- Specify exact domains that should have access
- Include both www and non-www versions if needed
- Use HTTPS URLs in production

### 5. Logging Security

- Don't log sensitive information (passwords, API keys, tokens)
- Use structured logging for better security monitoring
- Implement log rotation and retention policies
- Monitor logs for security events

## Deployment Configuration

### Railway (Backend)

Set environment variables in Railway dashboard:

```bash
# Required for production
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?ssl_ca=...
JWT_SECRET=your-super-secret-jwt-key-256-bits-long
MISTRAL_API_KEY=your_mistral_api_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional email configuration
EMAIL_ENABLED=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Vercel (Frontend)

Set environment variables in Vercel dashboard:

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Optional analytics
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX-X
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### CI/CD Integration

Add validation to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Validate Backend Environment
  run: |
    cd backend
    python scripts/validate_environment.py --environment production --strict --json

- name: Validate Frontend Environment
  run: |
    cd frontend
    node scripts/validate-environment.js --environment production --strict --json
```

## Troubleshooting

### Common Issues

1. **Configuration validation failed**
   - Check that all required variables are set
   - Verify variable names are correct (case-sensitive)
   - Ensure values are not placeholder text

2. **Database connection failed**
   - Verify DATABASE_URL format
   - Check SSL configuration for production
   - Ensure database server is accessible

3. **AI API errors**
   - Verify API key is correct and active
   - Check rate limits and quotas
   - Ensure LLM_PROVIDER matches the API key

4. **CORS errors**
   - Check CORS_ORIGINS includes your frontend domain
   - Verify protocol (http vs https) matches
   - Include both www and non-www versions if needed

### Getting Help

- Run validation scripts with `--verbose` flag for detailed information
- Check application logs for specific error messages
- Verify environment variable values in deployment platform
- Test configuration in staging before production deployment