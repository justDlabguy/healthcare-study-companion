# Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the Healthcare Study Companion frontend to Vercel.

## Prerequisites

1. Vercel account (sign up at [vercel.com](https://vercel.com))
2. GitHub repository connected to Vercel
3. Backend deployed to Railway (see [Railway Deployment Guide](./RAILWAY_DEPLOYMENT_GUIDE.md))
4. Backend API URL available

## Step 1: Prepare for Deployment

### 1.1 Validate Environment Configuration

Before deploying, validate your environment configuration:

```bash
cd frontend
npm run validate:env production --strict
```

This will check that all required environment variables are properly configured.

### 1.2 Test Local Build

Ensure your application builds successfully:

```bash
cd frontend
npm run build
```

Fix any build errors before proceeding with deployment.

### 1.3 Test Backend Connectivity

Test connectivity to your backend API:

```bash
cd frontend
npm run test:connectivity https://your-backend.railway.app
```

Replace `https://your-backend.railway.app` with your actual backend URL.

## Step 2: Deploy to Vercel

### Option A: Automatic Deployment (Recommended)

1. **Connect Repository to Vercel**

   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` directory as the root directory

2. **Configure Build Settings**

   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)
   - Install Command: `npm install` (auto-detected)

3. **Set Environment Variables**

   In the Vercel dashboard, go to your project → Settings → Environment Variables and add:

   ```bash
   # Required Variables
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
   NEXT_PUBLIC_ENVIRONMENT=production
   NEXT_PUBLIC_APP_NAME=Healthcare Study Companion

   # Optional Variables
   NEXT_PUBLIC_ENABLE_DEBUG_MODE=false
   NEXT_PUBLIC_ENABLE_ANALYTICS=true
   ```

   **Important**: Replace `https://your-railway-app.railway.app` with your actual Railway backend URL. You can find this in your Railway dashboard after deploying the backend.

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy your application
   - Monitor the build logs for any issues

### Option B: Manual Deployment with CLI

1. **Install Vercel CLI**

   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**

   ```bash
   vercel login
   ```

3. **Deploy from Frontend Directory**

   ```bash
   cd frontend
   vercel --prod
   ```

4. **Configure Environment Variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   vercel env add NEXT_PUBLIC_ENVIRONMENT production
   vercel env add NEXT_PUBLIC_APP_NAME production
   ```

### Option C: Automated Deployment Script

Use the provided deployment script:

```bash
cd frontend
npm run deploy:vercel
```

This script will:

- Validate environment configuration
- Test local build
- Test API connectivity
- Deploy to Vercel

## Step 3: Configure Environment Variables

### Required Environment Variables

| Variable                  | Description              | Example                            |
| ------------------------- | ------------------------ | ---------------------------------- |
| `NEXT_PUBLIC_API_URL`     | Backend API base URL     | `https://your-backend.railway.app` |
| `NEXT_PUBLIC_ENVIRONMENT` | Application environment  | `production`                       |
| `NEXT_PUBLIC_APP_NAME`    | Application display name | `Healthcare Study Companion`       |

### Optional Environment Variables

| Variable                          | Description           | Default | Example                     |
| --------------------------------- | --------------------- | ------- | --------------------------- |
| `NEXT_PUBLIC_ENABLE_DEBUG_MODE`   | Enable debug mode     | `false` | `false`                     |
| `NEXT_PUBLIC_ENABLE_ANALYTICS`    | Enable analytics      | `false` | `true`                      |
| `NEXT_PUBLIC_VERCEL_ANALYTICS_ID` | Vercel Analytics ID   | -       | `your-analytics-id`         |
| `NEXT_PUBLIC_SENTRY_DSN`          | Sentry error tracking | -       | `https://xxx@sentry.io/xxx` |

### Setting Environment Variables in Vercel

1. Go to your project in Vercel dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable with the appropriate value
4. Select the environment (Production, Preview, Development)
5. Click "Save"

## Step 4: Configure Custom Domain (Optional)

1. **Add Domain in Vercel**

   - Go to Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update CORS Configuration**

   Update your backend's CORS configuration to include your custom domain:

   ```bash
   # In Railway, update CORS_ORIGINS environment variable
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-app.vercel.app
   ```

## Step 5: Verify Deployment

### 5.1 Check Deployment Status

1. Visit your Vercel deployment URL
2. Verify the application loads correctly
3. Check that all pages are accessible

### 5.2 Test Frontend-Backend Connectivity

```bash
# Test from your local machine
npm run test:connectivity https://your-app.vercel.app
```

Or test manually:

1. Try to sign up for a new account
2. Try to log in
3. Create a topic
4. Upload a document
5. Ask a question

### 5.3 Check Browser Console

1. Open browser developer tools
2. Check for any console errors
3. Verify API calls are successful
4. Check network tab for failed requests

## Step 6: Set Up Monitoring

### 6.1 Vercel Analytics

Enable Vercel Analytics for performance monitoring:

1. Go to your project dashboard
2. Navigate to Analytics tab
3. Enable Web Analytics
4. Add `NEXT_PUBLIC_VERCEL_ANALYTICS_ID` environment variable

### 6.2 Error Tracking (Optional)

Set up Sentry for error tracking:

1. Create a Sentry project
2. Get your DSN
3. Add `NEXT_PUBLIC_SENTRY_DSN` environment variable
4. Deploy the updated configuration

## Troubleshooting

### Common Issues

#### 1. Build Failures

**Symptoms**: Deployment fails during build phase

**Solutions**:

- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Test build locally: `npm run build`
- Check for TypeScript errors: `npm run type-check`

#### 2. Environment Variable Issues

**Symptoms**: App loads but features don't work

**Solutions**:

- Verify all environment variables are set in Vercel
- Check variable names (must start with `NEXT_PUBLIC_`)
- Redeploy after adding variables
- Check browser console for undefined variables

#### 3. API Connection Issues

**Symptoms**: Frontend loads but can't connect to backend

**Solutions**:

- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is deployed and accessible
- Verify CORS configuration in backend
- Test API directly: `curl https://your-backend.railway.app/healthz`

#### 4. CORS Errors

**Symptoms**: "CORS policy" errors in browser console

**Solutions**:

- Update backend `CORS_ORIGINS` to include Vercel domain
- Include both `https://your-app.vercel.app` and custom domain
- Redeploy backend after CORS changes
- Check backend logs for CORS-related errors

#### 5. 404 Errors on Page Refresh

**Symptoms**: Direct URLs return 404 errors

**Solutions**:

- Verify `vercel.json` configuration is correct
- Check Next.js routing configuration
- Ensure all pages are properly exported
- Check Vercel function logs

### Getting Help

1. **Vercel Logs**: Check deployment and function logs in Vercel dashboard
2. **Browser Console**: Check for JavaScript errors and network issues
3. **API Testing**: Use the connectivity test script to diagnose API issues
4. **Vercel Support**: Use Vercel's support channels for platform issues

## Performance Optimization

### Build Optimization

The deployment includes several optimizations:

- **Bundle Analysis**: Webpack optimizations for smaller bundles
- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic code splitting for better performance
- **Static Generation**: Pre-rendered pages where possible

### Runtime Optimization

- **CDN**: Vercel's global CDN for fast content delivery
- **Edge Functions**: Optimized serverless functions
- **Caching**: Automatic caching of static assets
- **Compression**: Automatic gzip/brotli compression

## Security Considerations

### Headers

The deployment includes security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)
- `Referrer-Policy: origin-when-cross-origin`

### Environment Variables

- Never commit secrets to version control
- Use Vercel's environment variable system
- Prefix public variables with `NEXT_PUBLIC_`
- Regularly rotate API keys and secrets

## Maintenance

### Regular Tasks

- Monitor application performance in Vercel Analytics
- Review error reports in Sentry (if configured)
- Update dependencies regularly
- Monitor build times and bundle sizes
- Review and update environment variables

### Scaling

Vercel automatically handles scaling, but monitor:

- Function execution times
- Bandwidth usage
- Build minutes usage
- Edge requests

## CI/CD Integration

### GitHub Actions (Optional)

Create `.github/workflows/frontend-deploy.yml`:

```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches: [main]
    paths: ["frontend/**"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: frontend

      - name: Validate environment
        run: npm run validate:env production
        working-directory: frontend
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
          NEXT_PUBLIC_ENVIRONMENT: production
          NEXT_PUBLIC_APP_NAME: Healthcare Study Companion

      - name: Build application
        run: npm run build
        working-directory: frontend
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.NEXT_PUBLIC_API_URL }}
          NEXT_PUBLIC_ENVIRONMENT: production
          NEXT_PUBLIC_APP_NAME: Healthcare Study Companion

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend
```

## Next Steps

After successful Vercel deployment:

1. **Test End-to-End Functionality**

   - Complete user registration and login flow
   - Test document upload and processing
   - Verify Q&A functionality
   - Test flashcard generation and review

2. **Set Up Monitoring**

   - Configure Vercel Analytics
   - Set up error tracking with Sentry
   - Create uptime monitoring

3. **Performance Optimization**

   - Analyze bundle size and optimize
   - Set up performance monitoring
   - Configure caching strategies

4. **Security Review**
   - Review security headers
   - Audit environment variables
   - Set up security monitoring

## Support

- Vercel Documentation: [vercel.com/docs](https://vercel.com/docs)
- Next.js Documentation: [nextjs.org/docs](https://nextjs.org/docs)
- Application Issues: Check repository issues or create new ones

## Environment Variables Reference

For a complete list of all environment variables, see [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md).
