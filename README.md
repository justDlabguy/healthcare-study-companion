# Healthcare Study Companion

A comprehensive study companion application designed for healthcare students and professionals, featuring AI-powered learning tools, flashcard generation, and document management.

## ✨ Features

- **AI-Powered Q&A**: Get instant answers to medical study questions
- **Document Management**: Upload and organize study materials (PDFs, notes, etc.)
- **Flashcard Generation**: Automatically create study flashcards from your content
- **Topic Organization**: Categorize and manage study materials by topic
- **Spaced Repetition**: Optimized learning with spaced repetition algorithms
- **Responsive Design**: Study on any device with a mobile-friendly interface

## 🚀 Tech Stack

- **Frontend**: Next.js 14 with TypeScript, Shadcn UI, Tailwind CSS
- **Backend**: FastAPI (Python 3.11+)
- **Database**: TiDB Serverless (MySQL-compatible)
- **AI/ML**: Integration with various LLM providers (OpenAI, Anthropic, Hugging Face)
- **Authentication**: JWT-based authentication
- **Hosting**: Vercel (Frontend), Railway (Backend)

## 🛠️ Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- MySQL/MariaDB (for local development)
- Git

## 🚀 Getting Started

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/healthcare-study-companion.git
   cd healthcare-study-companion
   ```

2. **Set up Python environment**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac

   # Install dependencies
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `backend` directory with the following variables:
   ```env
   DATABASE_URL=mysql+pymysql://user:password@localhost/healthcare_study
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   LLM_PROVIDER=openai  # or anthropic, huggingface
   OPENAI_API_KEY=your-openai-api-key
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at: http://localhost:8000
   
   Check the API documentation at: http://localhost:8000/docs

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables**
   Create a `.env.local` file in the `frontend` directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME="Healthcare Study Companion"
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at: http://localhost:3000

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🌐 Deployment

The application is configured for deployment on Railway for both frontend and backend services. This provides a seamless, integrated deployment experience with automatic HTTPS, custom domains, and zero-downtime deployments.

### Railway Deployment

1. **Backend Deployment**
   - The backend is configured for Railway deployment with the `railway.json` file
   - Required environment variables are automatically pulled from Railway's environment
   - Database migrations run automatically on deployment

2. **Frontend Deployment**
   - The frontend is configured as a static Next.js application
   - Build command: `npm run build`
   - Output directory: `.next`
   - Environment variables should be set in Railway's dashboard

3. **Environment Variables**
   - Backend:
     - `DATABASE_URL`: Railway's PostgreSQL/TiDB connection string
     - `JWT_SECRET`: Secret key for JWT token generation
     - `MISTRAL_API_KEY`: API key for Mistral AI services
     - `LLM_PROVIDER`: Set to 'mistral' for Mistral AI
     - `NODE_ENV`: Set to 'production' in production
   - Frontend:
     - `NEXT_PUBLIC_API_URL`: URL of your deployed backend API
     - `NEXT_PUBLIC_APP_NAME`: Display name of your application

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT), an OSI Approved License. See the [LICENSE](LICENSE) file for full license text.

**Key Points:**
- **Permissive**: Free to use, modify, and distribute
- **Commercial Use**: Allowed for both open and closed source projects
- **Liability**: No liability or warranty provided
- **Trademark Use**: Does not grant permission to use project trademarks

## 📧 Contact

For support or questions, please open an issue in the [GitHub repository](https://github.com/yourusername/healthcare-study-companion/issues).

## Frontend Configuration

The frontend is configured to use Next.js with the App Router. Key configuration points:
- API base URL is set via `NEXT_PUBLIC_API_URL` environment variable
- Styling uses Tailwind CSS with Shadcn UI components
- Environment-specific configuration is handled through `.env.local`

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
