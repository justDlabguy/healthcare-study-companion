# Healthcare Study Companion – Actionable TODO

Use this checklist to drive implementation. Mark items as you complete them.

## 0) Repo & Project Setup
- [ ] Create Git repo; set default branch to `main`
- [ ] Add `.gitignore`, `.editorconfig`, and commit hooks (pre-commit)
- [x] Create monorepo folders: `/frontend`, `/backend`
- [x] Create `README.md`, update with setup instructions

## 1) Environments & Secrets
- [ ] Provision TiDB Serverless (dev/staging/prod)
- [ ] Create DB users with least privilege per env
- [ ] Store secrets:
  - [ ] GitHub Actions: `DATABASE_URL`, `JWT_SECRET`, `LLM_API_KEY`
  - [ ] Vercel Project Env: `NEXT_PUBLIC_API_BASE_URL`

## 2) Backend (FastAPI)
- [x] Scaffold FastAPI app structure under `/backend/app`
- [x] Dependencies in `/backend/requirements.txt` (fastapi, uvicorn, sqlalchemy, pydantic, alembic, pymysql, httpx, pypdf, python-multipart, jose/pyjwt, passlib, structlog, slowapi)
- [x] Implement `config.py` and `db.py` (SQLAlchemy engine to TiDB)
- [ ] Define models in `models.py` for users, topics, documents, qa_history, flashcards
- [ ] Alembic setup + initial migration
- [ ] Auth (`auth.py`): signup/login, JWT access tokens, password hashing
- [ ] Routers: `topics.py`, `files.py`, `qa.py`, `flashcards.py`
- [ ] Services:
  - [x] `embeddings.py` (OpenAI/Together/Kimi client abstraction)
  - [ ] `search.py` (topic-scoped vector search)
  - [x] `llm.py` (Q&A + flashcard generation orchestration)
- [ ] File ingestion: PDF/text extract → chunk → embed → store
- [ ] Rate limiting (slowapi) + CORS config
- [x] Health check `/healthz`
- [ ] Tests (pytest): unit + integration (DB)

## 3) Frontend (Next.js + Shadcn)
- [x] Initialize Next.js App Router project in `/frontend`
- [x] Tailwind + Shadcn setup
- [ ] Auth pages: `/app/auth/login.tsx`, `/app/auth/signup.tsx`
- [ ] Dashboard `/app/dashboard/page.tsx` (list topics, create/edit/delete)
- [ ] Topic detail `/app/dashboard/[topicId]/page.tsx` (uploads, Q&A, search)
- [ ] Flashcards `/app/dashboard/[topicId]/flashcards.tsx`
- [ ] Components: `Navbar.tsx`, `Sidebar.tsx`, `FileUploader.tsx`, `ChatBox.tsx`
- [ ] API client `/lib/api.ts` with auth header handling
- [ ] Basic e2e (Playwright): auth → create topic → upload → ask → flashcards

## 4) Observability & Security
- [ ] Structured logging (structlog) with request IDs
- [ ] Optional OpenTelemetry tracing
- [ ] HTTPS, CORS allowed origins, secure cookies (frontend)
- [ ] Dependency scanning (pip audit / npm audit) in CI

## 5) Performance
- [ ] Async ingestion + background tasks
- [ ] Batch embeddings and DB inserts
- [ ] Streaming responses for Q&A (SSE)

## 6) CI/CD (Git + Vercel)
- [ ] Git strategy: feature branches `feat/*`, conventional commits
- [x] GitHub Actions: `frontend-ci.yml`
  - [x] Setup Node → install → lint → type-check → build
- [x] GitHub Actions: `backend-ci.yml`
  - [x] Setup Python → install → lint → type-check → test → package
- [ ] Vercel project connected to Git repo (frontend)
  - [ ] Preview deployments for PRs
  - [ ] Auto deploy `main` to Production
- [ ] Backend deployment
  - [ ] Choose: Vercel Python or Railway/Render/Fly.io
  - [ ] Add deploy step to run `alembic upgrade head`
  - [ ] Expose `BACKEND_URL` to frontend via Vercel env

## 7) Milestones (Tracking)
- [ ] M1: Repo scaffold, CI green, TiDB connected
- [ ] M2: Auth + Topics CRUD
- [ ] M3: Ingestion + embeddings
- [ ] M4: Q&A + flashcards
- [ ] M5: Frontend polished
- [ ] M6: Staging hardening
- [ ] M7: Production launch

