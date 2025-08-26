# Technology Stack

## Architecture
Monorepo with separate frontend and backend applications.

## Frontend Stack
- **Framework**: Next.js 14 with App Router
- **UI Library**: Shadcn UI components with Radix UI primitives
- **Styling**: Tailwind CSS with custom design tokens
- **Language**: TypeScript
- **HTTP Client**: Axios for API communication
- **Icons**: Lucide React

## Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: TiDB Serverless (MySQL-compatible with vector support)
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **Authentication**: JWT with passlib for password hashing
- **LLM Integration**: OpenAI, Anthropic, Hugging Face Hub APIs
- **Vector Operations**: Built-in TiDB vector capabilities
- **Logging**: Structlog for structured logging

## Development Commands

### Backend
```bash
# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend

# Database migrations
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration

# Testing
pytest  # Run tests
flake8  # Linting
```

### Frontend
```bash
# Install dependencies
npm install  # or pnpm install

# Development server
npm run dev  # Runs on port 3000

# Build and deployment
npm run build
npm run start
npm run lint
npm run type-check
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: TiDB connection string with SSL
- `JWT_SECRET`: Secret for JWT token signing
- `MISTRAL_API_KEY`: LLM API key
- `LLM_MODEL_ID`: Model identifier (e.g., mistral-small)
- `EMBEDDING_MODEL_ID`: Embedding model (e.g., mistral-embed)
- `ALLOWED_ORIGINS`: CORS origins (comma-separated)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL

## Deployment
- **Frontend**: Vercel (auto-deploy from main branch)
- **Backend**: Railway (using Procfile configuration)
- **Database**: TiDB Serverless (managed)