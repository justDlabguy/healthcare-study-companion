# Railway Deployment - Healthcare Study Companion Backend

This directory contains the backend API for the Healthcare Study Companion application, configured for deployment on Railway.

## Quick Start

1. **Connect to Railway**: Connect your GitHub repository to Railway
2. **Set Environment Variables**: Configure required environment variables in Railway dashboard
3. **Deploy**: Push to main branch to trigger automatic deployment

## Required Environment Variables

Set these in your Railway dashboard (Variables tab):

```bash
# Database (TiDB Serverless)
DATABASE_URL=mysql+pymysql://username:password@host:port/database?ssl_params

# Security
JWT_SECRET=your-super-secret-jwt-key-256-bits-long

# AI Service
MISTRAL_API_KEY=your_mistral_api_key

# CORS (replace with your frontend domain)
CORS_ORIGINS=https://your-frontend.vercel.app

# Environment
ENVIRONMENT=production
```

## Deployment Process

Railway automatically:
1. Installs Python dependencies from `requirements.txt`
2. Runs database migrations via the `release` command in `Procfile`
3. Starts the web server via the `web` command in `Procfile`

## Health Check

Once deployed, verify your deployment:

```bash
curl https://your-app.railway.app/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

## Testing Scripts

Use these scripts to validate your deployment:

```bash
# Test database connectivity
python scripts/test_railway_db_connection.py

# Validate deployment
python scripts/validate_railway_deployment.py https://your-app.railway.app

# Run full test suite
python scripts/railway_deploy_test.py https://your-app.railway.app
```

## API Documentation

Once deployed, access the interactive API documentation at:
- Swagger UI: `https://your-app.railway.app/docs`
- ReDoc: `https://your-app.railway.app/redoc`

## Monitoring

Railway provides built-in monitoring for:
- CPU and memory usage
- Request metrics
- Error rates
- Deployment logs

Access these in your Railway dashboard.

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify TiDB cluster is running
   - Ensure SSL parameters are correct

2. **Migration Errors**
   - Check Alembic configuration
   - Verify database permissions
   - Review migration scripts

3. **Environment Variable Issues**
   - Run validation: `python scripts/validate_environment.py --environment production --strict`
   - Check all required variables are set
   - Verify no placeholder values

### Getting Help

- Check Railway logs in the dashboard
- Use the health endpoint: `/healthz`
- Run validation scripts locally
- Review the deployment guide: `docs/RAILWAY_DEPLOYMENT_GUIDE.md`

## File Structure

```
backend/
├── app/                    # FastAPI application
├── scripts/               # Deployment and testing scripts
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
├── Procfile             # Railway deployment configuration
└── .env.railway         # Environment variable template
```

## Support

For deployment issues:
1. Check the comprehensive deployment guide: `docs/RAILWAY_DEPLOYMENT_GUIDE.md`
2. Review environment variables: `docs/ENVIRONMENT_VARIABLES.md`
3. Use the deployment checklist: `docs/DEPLOYMENT_CHECKLIST.md`