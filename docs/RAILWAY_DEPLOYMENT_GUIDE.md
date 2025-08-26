# Railway Deployment Guide

This guide provides step-by-step instructions for deploying the Healthcare Study Companion backend to Railway.

## Prerequisites

1. Railway account (sign up at [railway.app](https://railway.app))
2. GitHub repository connected to Railway
3. TiDB Serverless database set up
4. Mistral AI API key

## Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Healthcare Study Companion repository
5. Railway will automatically detect the backend service

## Step 2: Configure Environment Variables

In the Railway dashboard, go to your project → Variables tab and set the following environment variables:

### Required Environment Variables

```bash
# Application Environment
ENVIRONMENT=production
APP_NAME=Healthcare Study Companion API

# Database Configuration (TiDB Serverless)
DATABASE_URL=mysql+pymysql://username:password@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/healthcare_study?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true

# Security
JWT_SECRET=your-super-secret-jwt-key-256-bits-long-randomly-generated

# CORS (replace with your actual frontend domain)
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://www.your-frontend-domain.vercel.app

# AI Configuration
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_mistral_api_key_here
DEFAULT_LLM_MODEL=mistral-small
EMBEDDING_MODEL=mistral-embed
LLM_MODEL_ID=mistral-small
EMBEDDING_MODEL_ID=mistral-embed
```

### Optional Environment Variables

```bash
# Email Configuration (if you want email functionality)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Performance Tuning
LLM_RATE_LIMIT_PER_MINUTE=100
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
MAX_CONCURRENT_AI_REQUESTS=10
MAX_CONCURRENT_DOCUMENT_PROCESSING=5

# File Upload Limits
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,txt,docx,md

# Logging
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Deployment
AUTO_ROLLBACK_ON_FAILURE=true
```

## Step 3: Database Setup (TiDB Serverless)

### 3.1 Create TiDB Serverless Cluster

1. Go to [TiDB Cloud](https://tidbcloud.com/)
2. Sign up/sign in
3. Create a new Serverless cluster
4. Choose your preferred region (us-east-1 recommended for Railway)
5. Set cluster name (e.g., "healthcare-study-prod")

### 3.2 Get Connection Details

1. In TiDB Cloud dashboard, go to your cluster
2. Click "Connect"
3. Choose "General" connection type
4. Copy the connection string
5. The format should be: `mysql://username:password@host:port/database`

### 3.3 Configure SSL (Important for Production)

TiDB Serverless requires SSL. Your DATABASE_URL should include SSL parameters:

```bash
DATABASE_URL=mysql+pymysql://username:password@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/healthcare_study?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true
```

## Step 4: Configure Build Settings

Railway should automatically detect your Python application. Verify these settings:

### Build Configuration
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: Automatically detected from Procfile

### Root Directory
- Set to `/` (repository root) since we have a monorepo structure

## Step 5: Deploy

1. Push your code to the main branch
2. Railway will automatically trigger a deployment
3. Monitor the build logs in Railway dashboard
4. The deployment includes:
   - Installing dependencies
   - Running database migrations (release command)
   - Starting the web server

## Step 6: Verify Deployment

### 6.1 Check Health Endpoint

Once deployed, test the health endpoint:

```bash
curl https://your-app-name.railway.app/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

### 6.2 Test API Endpoints

Test a few key endpoints:

```bash
# Root endpoint
curl https://your-app-name.railway.app/

# API documentation
# Visit: https://your-app-name.railway.app/docs
```

### 6.3 Check Database Connection

The health endpoint will verify database connectivity. If there are issues:

1. Check DATABASE_URL format
2. Verify TiDB cluster is running
3. Check SSL configuration
4. Review Railway logs for specific errors

## Step 7: Configure Custom Domain (Optional)

1. In Railway dashboard, go to Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. Update CORS_ORIGINS to include your custom domain

## Step 8: Set Up Monitoring

### 8.1 Railway Monitoring

Railway provides built-in monitoring:
- CPU and memory usage
- Request metrics
- Error rates
- Deployment history

### 8.2 Application Logs

View logs in Railway dashboard:
- Build logs
- Application logs
- Error logs

### 8.3 Health Checks

Railway automatically monitors your `/healthz` endpoint for health checks.

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms**: Health check fails, "database connection failed" error

**Solutions**:
- Verify DATABASE_URL format
- Check TiDB cluster status
- Ensure SSL parameters are correct
- Verify database credentials

#### 2. Migration Errors

**Symptoms**: Deployment fails during release phase

**Solutions**:
- Check Alembic configuration
- Verify database schema
- Review migration scripts
- Check database permissions

#### 3. Environment Variable Issues

**Symptoms**: Configuration validation errors

**Solutions**:
- Run validation script locally: `python backend/scripts/validate_environment.py --environment production --strict`
- Check all required variables are set
- Verify no placeholder values remain

#### 4. CORS Errors

**Symptoms**: Frontend cannot connect to API

**Solutions**:
- Update CORS_ORIGINS with correct frontend domain
- Include both www and non-www versions
- Ensure HTTPS is used in production

#### 5. AI API Errors

**Symptoms**: Q&A and flashcard generation fail

**Solutions**:
- Verify MISTRAL_API_KEY is correct
- Check API key quotas and limits
- Test API key with direct API calls

### Getting Help

1. **Railway Logs**: Check deployment and runtime logs in Railway dashboard
2. **Health Endpoint**: Use `/healthz` to diagnose issues
3. **Validation Script**: Run environment validation locally
4. **Railway Support**: Use Railway's support channels for platform issues

## Security Checklist

Before going live:

- [ ] Strong JWT_SECRET (32+ characters, randomly generated)
- [ ] Database uses SSL/TLS
- [ ] CORS_ORIGINS restricted to your domains only
- [ ] API keys are production-grade
- [ ] No development/localhost references
- [ ] Environment variables stored securely in Railway
- [ ] No secrets committed to version control

## Performance Optimization

For production workloads:

- [ ] Database connection pool configured appropriately
- [ ] Rate limiting configured for AI endpoints
- [ ] File upload limits set
- [ ] Logging level set to INFO or WARNING
- [ ] Structured logging enabled
- [ ] Health checks configured

## Maintenance

### Regular Tasks

- Monitor application performance and error rates
- Review and rotate API keys quarterly
- Update dependencies regularly
- Monitor database performance
- Review logs for security events

### Scaling

Railway automatically handles scaling, but monitor:
- Response times
- Error rates
- Database connection usage
- Memory and CPU usage

If you need more resources, Railway offers various plan upgrades.

## Next Steps

After successful Railway deployment:

1. Deploy frontend to Vercel (see Vercel deployment guide)
2. Configure custom domains
3. Set up monitoring and alerting
4. Configure backup strategies
5. Document operational procedures

## Environment Variables Reference

For a complete list of all environment variables, see [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md).

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- TiDB Documentation: [docs.tidb.io](https://docs.tidb.io)
- Application Issues: Check repository issues or create new ones