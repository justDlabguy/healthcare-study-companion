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

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the [LICENSE](LICENSE) file for full license text.

## 📧 Contact

For support or questions, please open an issue in the [GitHub repository](https://github.com/yourusername/healthcare-study-companion/issues).
