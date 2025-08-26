# Healthcare Study Companion – Plan

## 1) Overview

- Build a web-based study companion to manage multiple study topics, upload PDFs/text, perform topic-scoped Q&A/search, and generate flashcards.
- Stack: Next.js (App Router) + Shadcn UI, FastAPI backend, TiDB Serverless (relational + vector), LLM API (OpenAI/Together/Kimi), Railway for backend hosting and Vercel for frontend hosting.

## 2) Architecture

- Frontend (`/frontend`): Next.js + Shadcn UI, manages UI for study topics, uploads, and Q&A, calls backend API endpoints.
- Backend (`/backend`): FastAPI, handles auth, topic management, file ingestion, embedding generation, vector search, and LLM response orchestration.
- Database: TiDB Serverless, tables: users, topics, documents, qa_history, flashcards, vector storage for embeddings.
- LLM API: Kimi / OpenAI / Together, for summarization, flashcard generation, and quizzes.
- Observability: structured logs, request IDs, OpenTelemetry (optional), APM in production.

## 3) File/Repo Structure (Monorepo)

```
/healthcare-study-companion
 ├─ /frontend (Next.js)
 │   ├─ /app
 │   │   ├─ /auth
 │   │   │   ├─ login.tsx
 │   │   │   └─ signup.tsx
 │   │   ├─ /dashboard
 │   │   │   ├─ page.tsx
 │   │   │   └─ [topicId]/
 │   │   │       ├─ page.tsx
 │   │   │       └─ flashcards.tsx
 │   │   ├─ /components
 │   │   │   ├─ Navbar.tsx
 │   │   │   ├─ Sidebar.tsx
 │   │   │   ├─ FileUploader.tsx
 │   │   │   └─ ChatBox.tsx
 │   │   └─ layout.tsx
 │   ├─ /lib/api.ts
 │   └─ tailwind.config.ts
 ├─ /backend
 │   ├─ app/
 │   │   ├─ main.py
 │   │   ├─ config.py
 │   │   ├─ db.py
 │   │   ├─ models.py
 │   │   ├─ auth.py
 │   │   ├─ routers/
 │   │   │   ├─ topics.py
 │   │   │   ├─ files.py
 │   │   │   ├─ qa.py
 │   │   │   └─ flashcards.py
 │   │   ├─ services/
 │   │   │   ├─ embeddings.py
 │   │   │   ├─ llm.py
 │   │   │   └─ search.py
 │   │   └─ schemas.py
 │   └─ requirements.txt
 ├─ .github/workflows/ (CI)
 ├─ vercel.json (if needed)
 ├─ railway.yml (if needed)
 ├─ README.md
 └─ PLAN.md
```

## 4) Database Schema (TiDB)

- users: id (PK), email (unique), password_hash, created_at
- topics: id (PK), user_id (FK), name, created_at
- documents: id (PK), topic_id (FK), file_name, content, embedding_vector
- qa_history: id (PK), topic_id (FK), question, answer, created_at
- flashcards: id (PK), topic_id (FK), question, answer, created_at

Notes:

- Create composite index on `(topic_id, created_at)` for history.
- Vector index on `documents.embedding_vector` for semantic search.

## 5) API Endpoints (FastAPI)

- POST /auth/signup – User registration
- POST /auth/login – User login
- POST /topics/ – Create new topic
- GET /topics/ – List user’s topics
- POST /topics/{id}/upload – Upload PDFs/text
- POST /topics/{id}/query – Topic-scoped Q&A
- GET /topics/{id}/flashcards – Topic flashcards
- GET /topics/{id}/history – Q&A history

## 6) To-Do (Execution Plan)

- Repo & Env
  - Initialize monorepo: `/frontend`, `/backend`
  - Set up `.editorconfig`, `.gitignore`, pre-commit hooks
  - Create `.env.local` (frontend) and `.env` (backend) templates
- Backend
  - TiDB Serverless provision; SQLAlchemy models, Alembic migrations
  - Auth: signup/login, JWT, RBAC
  - Ingestion: PDF/text extract → chunk → embed → store
  - Search: topic-scoped vector search + rerank (optional)
  - Q&A orchestration: retrieve→prompt→LLM; store `qa_history`
  - Flashcards generation and retrieval
  - Tests: unit + integration (DB + routers); rate limiting
- Frontend
  - Next.js + Shadcn + Tailwind setup; auth pages
  - Dashboard (topics list, CRUD), Topic Detail (upload, chat/Q&A, search), Flashcards
  - API client with auth headers, error handling, optimistic UI
  - Basic e2e flows (Playwright) for auth + topic + Q&A
- Observability & Security
  - Structured logs, request IDs
  - OpenTelemetry tracing (optional), health checks
  - CORS, HTTPS, secrets via env, dependency scanning
- Performance
  - Async ingestion, background tasks for embedding
  - Batch embeddings; streaming responses for Q&A

## 7) DevOps Plan

- Environments: `dev` (PR previews), `staging`, `prod`
- Config via env vars:
  - Backend: `DATABASE_URL`, `JWT_SECRET`, `LLM_API_KEY`, `EMBEDDING_MODEL`, `ALLOWED_ORIGINS`
  - Frontend: `NEXT_PUBLIC_API_BASE_URL`
- Migrations: Alembic migrations auto-run on backend deploy; manual guard for destructive changes
- Secrets management: GitHub Actions encrypted secrets; Vercel Project Environment Variables (Development/Preview/Production)
- Observability: Log to stdout (JSON). Optional: OTLP exporter to vendor (Datadog/Tempo)
- Backups: TiDB automated backups; retention policy aligned with compliance
- Access: least privilege DB user per environment; rotated keys

## 8) CI/CD Plan (Git + Vercel + Railway)

- Git Strategy
  - Default branch: `main`
  - Feature branches: `feat/*`, bugfix: `fix/*`, ops: `ops/*`
  - Conventional commits (e.g., `feat:`, `fix:`)
- CI (GitHub Actions)
  - Workflow 1: `frontend-ci.yml`
    - Steps: checkout → setup Node → install (pnpm/npm) → lint (eslint) → type-check (tsc) → build → artifact
  - Workflow 2: `backend-ci.yml`
    - Steps: checkout → setup Python → install deps → lint (ruff/flake8) → type-check (mypy) → test (pytest) → package artifact
  - Optional: `e2e.yml` for Playwright against preview URL
- CD
  - Frontend: Vercel auto previews on PR; auto deploy `main` to Production
  - Backend (Railway):
    - Service root: `/backend`
    - Procfile: `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --app-dir backend`
    - Add environment variables in Railway: `DATABASE_URL`, `JWT_SECRET`, `MISTRAL_API_KEY`, `LLM_MODEL_ID`, `EMBEDDING_MODEL_ID`, `ALLOWED_ORIGINS`
    - Expose generated public URL; set it as `NEXT_PUBLIC_API_BASE_URL` in Vercel
  - Migrations: run `alembic upgrade head` as a Railway deploy hook (after we add Alembic)

## 9) Environment Variables (examples)

- Frontend
  - `NEXT_PUBLIC_API_BASE_URL=https://api.example.com`
- Backend
  - `DATABASE_URL=mysql+pymysql://user:pass@host:4000/db?ssl=true` (TiDB)
  - `JWT_SECRET=...`
  - `MISTRAL_API_KEY=...`
  - `LLM_MODEL_ID=mistral-small` (or preferred)
  - `EMBEDDING_MODEL_ID=mistral-embed`
  - `ALLOWED_ORIGINS=https://app.example.com,https://*.vercel.app`

## 10) Milestones

- M1: Repo scaffold, CI running, TiDB connected
- M2: Auth + Topics CRUD
- M3: Ingestion pipeline with embeddings
- M4: Topic Q&A + flashcards endpoints
- M5: Frontend UI complete (auth, dashboard, topic, flashcards)
- M6: Staging hardening: security, logs, metrics, load tests
- M7: Production launch

## 11) Testing Strategy

- Backend: pytest (routers/services), factory fixtures, DB test container
- Frontend: unit (Vitest) + e2e (Playwright)
- Contract tests: simple endpoint schema checks

## 12) Runbooks

- Deploy: merge to `main` → CI passes → Vercel auto-deploy frontend; backend deploy via GitHub Actions or host’s auto deploy
- Rollback: revert commit or redeploy previous Vercel build; for backend, redeploy previous image/artifact; run `alembic downgrade` if needed
- Oncall basics: check logs, health endpoints `/healthz`, DB connectivity, LLM quota/errors

## 13) Risks & Mitigations

- LLM latency/cost: cache answers, smaller models, stream responses
- Vector DB performance: batch inserts, correct index, chunk sizes
- Cold starts (serverless): provisioned concurrency or move backend to container host
- Vendor limits: abstract embedding/LLM providers behind service interface

---

Short version: Monorepo with Next.js+Shadcn and FastAPI on TiDB. CI on GitHub Actions; Vercel previews and prod for frontend; backend deploy via Vercel Python or Railway. Secure with JWT/CORS, run Alembic migrations on deploy, and add structured logs and basic tracing.
