# Deployment Configuration Checklist

This checklist ensures all environment variables and configuration are properly set before deploying the Healthcare Study Companion application.

## Pre-Deployment Validation

### 1. Run Environment Validation Scripts

**Backend Validation:**
```bash
# Development
cd backend
python scripts/validate_environment.py --environment development --verbose

# Staging
python scripts/validate_environment.py --environment staging --strict

# Production
python scripts/validate_environment.py --environment production --strict
```

**Frontend Validation:**
```bash
# Development
cd frontend
node scripts/validate-environment.js --environment development --verbose

# Staging
node scripts/validate-environment.js --environment staging --strict

# Production
node scripts/validate-environment.js --environment production --strict
```

**All Environments (Comprehensive):**
```bash
# Unix/Linux/macOS
./scripts/validate-all-environments.sh --strict

# Windows PowerShell
.\scripts\validate-all-environments.ps1 -Strict
```

## Environment-Specific Checklists

### Development Environment

#### Backend (.env.development)
- [ ] `ENVIRONMENT=development`
- [ ] `DATABASE_HOST` or `DATABASE_URL` configured for local database
- [ ] `JWT_SECRET` set (can be development value)
- [ ] `CORS_ORIGINS` includes `http://localhost:3000`
- [ ] `LLM_PROVIDER` selected
- [ ] API key for selected LLM provider set
- [ ] `LOG_LEVEL=DEBUG` for detailed logging
- [ ] `STRUCTURED_LOGGING=false` for readable logs
- [ ] Performance limits set appropriately for development

#### Frontend (.env.development)
- [ ] `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] `NEXT_PUBLIC_ENVIRONMENT=development`
- [ ] `NEXT_PUBLIC_ENABLE_DEBUG_MODE=true`
- [ ] `NEXT_PUBLIC_ENABLE_ANALYTICS=false`

### Staging Environment

#### Backend (.env.staging)
- [ ] `ENVIRONMENT=staging`
- [ ] `DATABASE_URL` configured for staging database (with SSL)
- [ ] `JWT_SECRET` set to secure value (different from production)
- [ ] `CORS_ORIGINS` restricted to staging frontend domain
- [ ] `LLM_PROVIDER` and API key configured
- [ ] `EMAIL_ENABLED=true` with staging SMTP credentials
- [ ] `LOG_LEVEL=INFO`
- [ ] `STRUCTURED_LOGGING=true`
- [ ] Performance settings similar to production
- [ ] `AUTO_ROLLBACK_ON_FAILURE=true`

#### Frontend (.env.staging)
- [ ] `NEXT_PUBLIC_API_URL` points to staging backend
- [ ] `NEXT_PUBLIC_ENVIRONMENT=staging`
- [ ] `NEXT_PUBLIC_ENABLE_DEBUG_MODE=false`
- [ ] `NEXT_PUBLIC_ENABLE_ANALYTICS=true` (for testing)
- [ ] Analytics IDs configured (optional)

### Production Environment

#### Backend (Production Environment Variables)
- [ ] `ENVIRONMENT=production`
- [ ] `DATABASE_URL` configured for production database with SSL
- [ ] `JWT_SECRET` set to strong, unique value (32+ characters)
- [ ] `CORS_ORIGINS` restricted to production domain(s) only
- [ ] `LLM_PROVIDER` and production API key configured
- [ ] `EMAIL_ENABLED=true` with production SMTP credentials
- [ ] `LOG_LEVEL=INFO` or `WARNING`
- [ ] `STRUCTURED_LOGGING=true`
- [ ] Performance settings optimized for production load
- [ ] `AUTO_ROLLBACK_ON_FAILURE=true`
- [ ] No development/localhost references
- [ ] No placeholder values (your_, _here, etc.)

#### Frontend (Production Environment Variables)
- [ ] `NEXT_PUBLIC_API_URL` points to production backend
- [ ] `NEXT_PUBLIC_ENVIRONMENT=production`
- [ ] `NEXT_PUBLIC_ENABLE_DEBUG_MODE=false`
- [ ] `NEXT_PUBLIC_ENABLE_ANALYTICS=true`
- [ ] Production analytics IDs configured
- [ ] Error tracking (Sentry) configured
- [ ] No localhost references

## Security Checklist

### Database Security
- [ ] Database uses SSL/TLS encryption
- [ ] Database credentials are strong and unique
- [ ] Database access restricted to application servers
- [ ] Database backups configured and tested
- [ ] Connection pooling configured appropriately

### API Security
- [ ] JWT secret is strong and unique (32+ characters)
- [ ] API keys are production-grade and active
- [ ] CORS origins restricted to specific domains
- [ ] Rate limiting configured
- [ ] No sensitive data in logs

### Infrastructure Security
- [ ] HTTPS enabled for all production URLs
- [ ] Environment variables stored securely in deployment platform
- [ ] No secrets committed to version control
- [ ] Access logs enabled and monitored
- [ ] Error tracking configured

## Performance Checklist

### Database Performance
- [ ] Connection pool size appropriate for expected load
- [ ] Database indexes optimized
- [ ] Query performance tested
- [ ] Connection timeout configured

### Application Performance
- [ ] Concurrent request limits set appropriately
- [ ] File upload limits configured
- [ ] Memory usage monitored
- [ ] Response time targets defined

### Monitoring
- [ ] Application logs structured and searchable
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring enabled
- [ ] Health check endpoints working
- [ ] Alerting configured for critical issues

## Deployment Platform Configuration

### Railway (Backend)

**Required Environment Variables:**
```bash
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?ssl_ca=...
JWT_SECRET=your-super-secret-jwt-key-256-bits-long
MISTRAL_API_KEY=your_mistral_api_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
```

**Optional Environment Variables:**
```bash
EMAIL_ENABLED=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true
```

**Railway Configuration:**
- [ ] Environment variables set in Railway dashboard
- [ ] Build and deploy settings configured
- [ ] Custom domain configured (if applicable)
- [ ] Health check URL configured (`/healthz`)
- [ ] Auto-deploy from main branch enabled
- [ ] Procfile configured for proper startup
- [ ] Database connectivity tested
- [ ] API endpoints responding correctly

**Railway Deployment Testing:**
```bash
# Test database connectivity
python backend/scripts/test_railway_db_connection.py

# Validate deployment
python backend/scripts/validate_railway_deployment.py https://your-app.railway.app

# Run comprehensive test suite
python backend/scripts/railway_deploy_test.py https://your-app.railway.app
```

### Vercel (Frontend)

**Required Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_ENVIRONMENT=production
```

**Optional Environment Variables:**
```bash
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX-X
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

**Vercel Configuration:**
- [ ] Environment variables set in Vercel dashboard
- [ ] Build settings configured
- [ ] Custom domain configured
- [ ] Auto-deploy from main branch enabled
- [ ] Preview deployments configured

## Testing Checklist

### Pre-Deployment Testing
- [ ] All environment validation scripts pass
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Database migrations tested
- [ ] API endpoints tested
- [ ] Frontend builds successfully
- [ ] End-to-end workflow tested

### Post-Deployment Testing
- [ ] Application starts successfully
- [ ] Database connection working
- [ ] API endpoints responding
- [ ] Frontend loads correctly
- [ ] Authentication working
- [ ] File upload working
- [ ] AI features working
- [ ] Email functionality working (if enabled)

## Rollback Plan

### Preparation
- [ ] Previous deployment version identified
- [ ] Database backup created before deployment
- [ ] Rollback procedure documented
- [ ] Rollback testing completed in staging

### Rollback Triggers
- [ ] Application fails to start
- [ ] Critical functionality broken
- [ ] Performance degradation
- [ ] Security issues identified
- [ ] Data corruption detected

### Rollback Procedure
1. [ ] Stop new deployments
2. [ ] Revert to previous application version
3. [ ] Rollback database migrations (if necessary)
4. [ ] Verify application functionality
5. [ ] Monitor for issues
6. [ ] Document incident and lessons learned

## Post-Deployment Monitoring

### Immediate Monitoring (First 24 hours)
- [ ] Application startup logs reviewed
- [ ] Error rates monitored
- [ ] Response times checked
- [ ] Database performance monitored
- [ ] User feedback collected

### Ongoing Monitoring
- [ ] Daily error rate review
- [ ] Weekly performance analysis
- [ ] Monthly security review
- [ ] Quarterly configuration audit

## Documentation Updates

### Post-Deployment Documentation
- [ ] Deployment notes updated
- [ ] Configuration changes documented
- [ ] Known issues documented
- [ ] Monitoring dashboards updated
- [ ] Runbooks updated

### Team Communication
- [ ] Deployment announcement sent
- [ ] New features communicated
- [ ] Support team briefed
- [ ] Documentation shared with stakeholders

## Compliance and Audit

### Configuration Audit
- [ ] All environment variables documented
- [ ] Security settings reviewed
- [ ] Access controls verified
- [ ] Data handling compliance checked

### Regular Reviews
- [ ] Monthly configuration review scheduled
- [ ] Quarterly security audit planned
- [ ] Annual compliance review scheduled
- [ ] Incident response plan updated

---

## Quick Reference Commands

### Validation Commands
```bash
# Validate all environments
./scripts/validate-all-environments.sh --strict --verbose

# Backend only
cd backend && python scripts/validate_environment.py --environment production --strict

# Frontend only
cd frontend && node scripts/validate-environment.js --environment production --strict
```

### Deployment Commands
```bash
# Backend deployment (Railway)
git push origin main  # Auto-deploys to Railway

# Frontend deployment (Vercel)
git push origin main  # Auto-deploys to Vercel

# Manual deployment
railway up  # Backend
vercel --prod  # Frontend
```

### Monitoring Commands
```bash
# Check application health
curl https://your-backend.railway.app/health

# View logs
railway logs  # Backend logs
vercel logs  # Frontend logs
```

This checklist should be reviewed and updated regularly to ensure it remains current with the application's requirements and deployment practices.