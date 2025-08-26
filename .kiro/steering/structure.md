# Project Structure

## Monorepo Organization
```
/healthcare-study-companion
├─ /frontend          # Next.js application
├─ /backend           # FastAPI application
├─ /.github           # GitHub Actions workflows
├─ /.kiro             # Kiro configuration and specs
└─ docs/              # Project documentation
```

## Frontend Structure (`/frontend`)
```
/frontend
├─ /app               # Next.js App Router pages
│   ├─ /auth          # Authentication pages
│   ├─ /dashboard     # Main dashboard
│   └─ /[topicId]     # Dynamic topic pages
├─ /components        # Reusable UI components (Shadcn)
├─ /contexts          # React contexts
├─ /hooks             # Custom React hooks
├─ /lib               # Utilities and API client
├─ package.json       # Dependencies and scripts
├─ tailwind.config.ts # Tailwind configuration
└─ tsconfig.json      # TypeScript configuration
```

## Backend Structure (`/backend`)
```
/backend
├─ /app
│   ├─ main.py        # FastAPI application entry point
│   ├─ config.py      # Settings and configuration
│   ├─ database.py    # Database connection and session
│   ├─ models.py      # SQLAlchemy models
│   ├─ auth.py        # Authentication router
│   ├─ /routers       # API route handlers
│   │   ├─ topics.py
│   │   ├─ documents.py
│   │   ├─ flashcards.py
│   │   ├─ qa.py
│   │   ├─ study_sessions.py
│   │   └─ progress.py
│   └─ /services      # Business logic services
├─ /alembic           # Database migrations
├─ /scripts           # Utility scripts
├─ /uploads           # File upload storage
├─ requirements.txt   # Python dependencies
├─ alembic.ini        # Alembic configuration
└─ Procfile          # Railway deployment configuration
```

## Key Conventions

### File Naming
- **Frontend**: PascalCase for components (`UserProfile.tsx`), camelCase for utilities
- **Backend**: snake_case for Python files and functions
- **Database**: snake_case for table and column names

### Import Organization
- **Frontend**: Group imports (React, libraries, local components, types)
- **Backend**: Standard library, third-party, local imports

### API Routes
- RESTful conventions with consistent patterns
- Prefix all routes with appropriate resource names
- Use HTTP status codes appropriately

### Database Models
- Use SQLAlchemy declarative models
- Include created_at/updated_at timestamps
- Foreign key relationships with proper constraints

### Component Structure
- Shadcn UI components in `/components/ui`
- Feature-specific components in `/components/features`
- Shared utilities in `/lib`

### Environment Configuration
- Separate `.env` files for each environment
- Use Pydantic Settings for backend configuration
- Prefix public frontend env vars with `NEXT_PUBLIC_`