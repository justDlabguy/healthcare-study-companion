# Healthcare Study Companion - Railway Deployment Guide

This guide provides step-by-step instructions for deploying the Healthcare Study Companion application to Railway.

## Prerequisites

- [Railway Account](https://railway.app/)
- [GitHub Account](https://github.com/)
- [Node.js](https://nodejs.org/) (for local development)
- [Python 3.8+](https://www.python.org/downloads/) (for local development)
- [Docker](https://www.docker.com/) (optional, for local testing)

## 1. Backend Deployment

### 1.1 Create New Railway Project

1. Log in to your [Railway dashboard](https://railway.app/dashboard)
2. Click "New Project" and select "Deploy from GitHub repo"
3. Select your repository and choose the `backend` directory
4. Railway will automatically detect the `railway.json` configuration

### 1.2 Configure Environment Variables

Add the following required environment variables in Railway dashboard:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# CORS (replace with your frontend URL)
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:3000

# Optional: Sentry for error tracking
SENTRY_DSN=your-sentry-dsn
```

### 1.3 Add PostgreSQL Database

1. In your Railway project, go to "New" → "Database"
2. Select "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` environment variable

## 2. Frontend Deployment

### 2.1 Create New Railway Project

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Select your repository and choose the `frontend` directory
4. Railway will automatically detect the `railway.json` configuration

### 2.2 Configure Environment Variables

Add the following required environment variables:

```env
# Backend API URL (update with your backend URL)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Next.js Auth
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=https://your-frontend.railway.app

# Optional: Sentry for error tracking
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

## 3. Networking Configuration

### 3.1 Set Up Custom Domains (Optional)

1. In each Railway project, go to "Settings" → "Domains"
2. Add your custom domain (e.g., api.yourdomain.com, app.yourdomain.com)
3. Follow the instructions to verify domain ownership

### 3.2 Configure CORS

Ensure your backend's `CORS_ORIGINS` environment variable includes:
- Your production frontend URL
- Any development/staging URLs
- `http://localhost:3000` for local development

## 4. Monitoring and Alerts

### 4.1 Railway Built-in Monitoring

1. Go to your project in Railway
2. Navigate to "Metrics" to view:
   - CPU/Memory usage
   - Request rates
   - Error rates

### 4.2 Set Up Alerts

1. In Railway, go to "Settings" → "Alerts"
2. Set up alerts for:
   - High CPU/Memory usage
   - Failed deployments
   - Service restarts

## 5. CI/CD Pipeline

### 5.1 Automatic Deployments

1. Connect your GitHub repository to Railway
2. Enable automatic deployments for the `main` branch
3. Set up preview deployments for pull requests (optional)

### 5.2 Deployment Hooks

Add the following scripts to your `package.json` (frontend) and `setup.py` (backend) for better CI/CD integration:

```json
// frontend/package.json
{
  "scripts": {
    "test": "next test",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

## 6. Database Migrations

Migrations are automatically run during deployment via the `buildCommand` in `backend/railway.json`:

```json
"buildCommand": "pip install -r requirements.txt && alembic upgrade head"
```

## 7. Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify `CORS_ORIGINS` includes all necessary domains
   - Check browser console for specific CORS errors

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correctly set
   - Check if the database is accessible from Railway's network

3. **Build Failures**
   - Check the build logs in Railway
   - Verify all dependencies are in `requirements.txt`

## 8. Maintenance

### 8.1 Database Backups

1. In Railway, go to your database
2. Navigate to "Backups"
3. Configure automatic backups
4. Test restoration process

### 8.2 Scaling

1. Monitor resource usage in Railway dashboard
2. Scale vertically (CPU/Memory) as needed
3. Consider horizontal scaling for high-traffic applications

## Support

For additional help, refer to:
- [Railway Documentation](https://docs.railway.app/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
