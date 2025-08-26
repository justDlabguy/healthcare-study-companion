# Healthcare Study Companion

Monorepo for a study companion app: Next.js + Shadcn UI frontend, FastAPI backend, TiDB Serverless, LLM APIs.

## Quickstart

1) Clone and create branches off `main` using conventional commits.

2) Backend dev server
```
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```
Open: http://localhost:8000/healthz

3) Frontend
- Initialize Next.js in `/frontend` (App Router) when ready. Configure API base URL via `NEXT_PUBLIC_API_BASE_URL`.

## Environments
- Backend env (.env):
  - `DATABASE_URL` (TiDB, e.g., `mysql+pymysql://user:pass@host:4000/db?ssl=true`)
  - `JWT_SECRET`
  - `MISTRAL_API_KEY`
  - `LLM_MODEL_ID` (e.g., `mistral-small`)
  - `EMBEDDING_MODEL_ID` (e.g., `mistral-embed`)
  - `ALLOWED_ORIGINS` (comma-separated; include your Vercel domain)
- Frontend env (.env.local): `NEXT_PUBLIC_API_BASE_URL`

## CI/CD
- GitHub Actions: backend syntax checks; frontend CI only runs if `/frontend/package.json` exists
- Vercel: connect repo for frontend previews and production on `main`

## Docs
- See `PLAN.md` and `TODO.md` for detailed plan and task list.

---

## Deployment

### Backend on Railway
1. Create a new Railway project → "Deploy from GitHub" → select this repo.
2. Set service root to `/backend` (if prompted). Railway will detect `Procfile`:
   - `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --app-dir backend`
3. Add environment variables in Railway:
   - `DATABASE_URL`, `JWT_SECRET`, `MISTRAL_API_KEY`, `LLM_MODEL_ID`, `EMBEDDING_MODEL_ID`, `ALLOWED_ORIGINS`
4. Deploy. Copy the public service URL (e.g., `https://your-api.up.railway.app`).

Notes:
- Ensure TiDB’s connection string has TLS enabled (`?ssl=true`).
- Prefer short-lived DB sessions; server stays warm on Railway.

### Frontend on Vercel
1. Import GitHub repo in Vercel → select `/frontend` as the project path once created.
2. Set Environment Variable `NEXT_PUBLIC_API_BASE_URL` to your Railway backend URL.
3. Deploy. Vercel will build previews on PRs and deploy `main` to Production.
