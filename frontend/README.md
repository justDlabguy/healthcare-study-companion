# Healthcare Study Companion - Frontend

This is the frontend application for the Healthcare Study Companion, built with Next.js 14 and deployed to Vercel.

## 🚀 Quick Start

### Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:3000
   ```

### Production Build

1. **Validate environment**
   ```bash
   npm run validate:env production
   ```

2. **Build application**
   ```bash
   npm run build
   ```

3. **Start production server**
   ```bash
   npm run start
   ```

## 📦 Deployment

### Vercel Deployment (Recommended)

#### Automatic Deployment

1. **Connect to Vercel**
   - Fork/clone this repository
   - Connect your GitHub account to Vercel
   - Import the project and select the `frontend` directory

2. **Configure Environment Variables**
   
   In Vercel dashboard → Settings → Environment Variables:
   
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   NEXT_PUBLIC_ENVIRONMENT=production
   NEXT_PUBLIC_APP_NAME=Healthcare Study Companion
   NEXT_PUBLIC_ENABLE_DEBUG_MODE=false
   NEXT_PUBLIC_ENABLE_ANALYTICS=true
   ```

3. **Deploy**
   - Push to main branch
   - Vercel automatically builds and deploys

#### Manual Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login and deploy**
   ```bash
   vercel login
   vercel --prod
   ```

#### Automated Deployment Script

```bash
npm run deploy:vercel
```

This script will:
- Validate environment configuration
- Test local build
- Test API connectivity
- Deploy to Vercel

### Manual Deployment

For other platforms, build the static files:

```bash
npm run build
npm run export  # If using static export
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend API URL | `https://api.example.com` |
| `NEXT_PUBLIC_ENVIRONMENT` | ✅ | Environment name | `production` |
| `NEXT_PUBLIC_APP_NAME` | ✅ | App display name | `Healthcare Study Companion` |
| `NEXT_PUBLIC_ENABLE_DEBUG_MODE` | ❌ | Enable debug mode | `false` |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | ❌ | Enable analytics | `true` |
| `NEXT_PUBLIC_VERCEL_ANALYTICS_ID` | ❌ | Vercel Analytics ID | `your-analytics-id` |
| `NEXT_PUBLIC_SENTRY_DSN` | ❌ | Sentry error tracking | `https://xxx@sentry.io/xxx` |

### Build Configuration

The application is configured for optimal Vercel deployment:

- **Framework**: Next.js 14 with App Router
- **Output**: Standalone build for serverless deployment
- **Optimization**: Bundle splitting, image optimization, CSS optimization
- **Security**: Security headers, CORS configuration
- **Performance**: CDN caching, compression, edge functions

## 🧪 Testing

### Environment Validation

```bash
npm run validate:env [environment] [--strict]
```

Examples:
```bash
npm run validate:env development
npm run validate:env production --strict
```

### Backend Connectivity

```bash
npm run test:connectivity [API_URL]
```

Examples:
```bash
npm run test:connectivity http://localhost:8000
npm run test:connectivity https://your-backend.railway.app
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── dashboard/         # Main dashboard
│   ├── topics/           # Topic management pages
│   └── layout.tsx        # Root layout
├── components/           # Reusable UI components
│   ├── ui/              # Shadcn UI components
│   ├── auth/            # Authentication components
│   ├── topics/          # Topic-related components
│   ├── documents/       # Document management
│   ├── flashcards/      # Flashcard components
│   ├── qa/              # Q&A interface
│   ├── search/          # Search components
│   └── navigation/      # Navigation components
├── contexts/            # React contexts
├── hooks/               # Custom React hooks
├── lib/                 # Utilities and API client
├── scripts/             # Deployment and utility scripts
├── public/              # Static assets
└── styles/              # Global styles
```

## 🔗 API Integration

The frontend communicates with the backend API through:

- **Authentication**: JWT-based authentication
- **API Client**: Axios with interceptors for auth and error handling
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Rate Limiting**: Automatic retry and rate limit handling

### API Client Features

- Automatic token management
- Request/response interceptors
- Error handling and logging
- Environment-aware base URL configuration
- Timeout and retry mechanisms

## 🎨 UI Components

Built with:
- **Shadcn UI**: Modern, accessible component library
- **Radix UI**: Unstyled, accessible UI primitives
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful, customizable icons

### Component Categories

- **Authentication**: Login, signup, password reset
- **Navigation**: Navbar, sidebar, breadcrumbs
- **Topics**: Topic cards, forms, management
- **Documents**: Upload, display, management
- **Flashcards**: Review interface, generation
- **Q&A**: Question interface, history
- **Search**: Search input, results, filters

## 🚨 Error Handling

### Error Boundaries

React Error Boundaries catch and handle component errors gracefully.

### API Error Handling

- Network errors with retry mechanisms
- Authentication errors with automatic redirect
- Validation errors with field-specific messages
- Server errors with user-friendly messages

### Logging

- Development: Console logging for debugging
- Production: Structured error logging (optional Sentry integration)

## 📊 Performance

### Optimization Features

- **Code Splitting**: Automatic route-based code splitting
- **Image Optimization**: Next.js automatic image optimization
- **Bundle Analysis**: Webpack optimizations for smaller bundles
- **Caching**: Aggressive caching of static assets
- **Compression**: Automatic gzip/brotli compression

### Performance Monitoring

- **Vercel Analytics**: Built-in performance monitoring
- **Web Vitals**: Core Web Vitals tracking
- **Bundle Size**: Automatic bundle size analysis

## 🔒 Security

### Security Headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)
- `Referrer-Policy: origin-when-cross-origin`

### Authentication Security

- JWT token storage in localStorage
- Automatic token refresh
- Secure API communication
- CORS configuration

## 🛠️ Development

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript type checking |
| `npm run validate:env` | Validate environment variables |
| `npm run test:connectivity` | Test backend connectivity |
| `npm run deploy:vercel` | Deploy to Vercel |

### Development Guidelines

1. **Code Style**: Follow ESLint and Prettier configurations
2. **TypeScript**: Use strict TypeScript for type safety
3. **Components**: Create reusable, accessible components
4. **Testing**: Write tests for critical functionality
5. **Performance**: Optimize for Core Web Vitals

## 🐛 Troubleshooting

### Common Issues

#### Build Failures
- Check TypeScript errors: `npm run type-check`
- Check ESLint errors: `npm run lint`
- Verify environment variables are set

#### API Connection Issues
- Test connectivity: `npm run test:connectivity [API_URL]`
- Check CORS configuration in backend
- Verify API URL is correct

#### Deployment Issues
- Validate environment: `npm run validate:env production`
- Check Vercel logs in dashboard
- Verify all environment variables are set in Vercel

### Getting Help

1. Check the [deployment guide](../docs/VERCEL_DEPLOYMENT_GUIDE.md)
2. Review Vercel logs and error messages
3. Test API connectivity with the provided scripts
4. Check environment variable configuration

## 📚 Documentation

- [Vercel Deployment Guide](../docs/VERCEL_DEPLOYMENT_GUIDE.md)
- [Environment Variables](../docs/ENVIRONMENT_VARIABLES.md)
- [API Documentation](../docs/API_DOCUMENTATION.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.