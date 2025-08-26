---
trigger: always_on
---

# General Code Style & Formatting
- Follow PEP 8 for Python code formatting in the backend.
- Follow the Airbnb JavaScript Style Guide for frontend code formatting.
- Use PascalCase for React component file names (e.g., StudyTopicCard.tsx, not study-topic-card.tsx).
- Prefer named exports for components and functions across frontend and backend.
- Use consistent naming conventions: snake_case for Python variables and functions, camelCase for JavaScript variables and functions.
- Enforce type hints in Python using mypy for backend code.
- Use ESLint with Airbnb config for frontend linting.

# Project Structure & Architecture
- Follow Next.js patterns and use the App Router for the frontend.
- Correctly determine when to use server vs. client components in Next.js: Use server components for data fetching and initial renders, client components for interactive elements like forms and chat boxes.
- Organize the backend following FastAPI best practices: Separate routers for different features (e.g., auth, topics, qa), services for business logic (e.g., embeddings, llm, search), and schemas for data validation.
- Use modular architecture: Break down features into reusable components, such as a FileUploader component for uploads and a ChatBox for Q&A interactions.
- Ensure separation of concerns: Frontend handles UI and API calls, backend manages auth, data processing, and LLM orchestration, database handles storage and queries.
- Implement async processing in FastAPI for file ingestion and embedding generation to handle scalability.

# Styling & UI
- Use Tailwind CSS for styling throughout the frontend.
- Use Shadcn UI for all UI components to ensure consistency and responsiveness.
- Maintain a responsive layout: Ensure mobile-friendly design for study topics, uploads, and Q&A views.
- Use consistent theming: Apply light/dark mode support if feasible, aligning with healthcare user needs for reduced eye strain.

# Data Fetching & Forms
- Use TanStack Query (react-query) for frontend data fetching from API endpoints.
- Use React Hook Form for handling forms in uploads, topic creation, and Q&A inputs.
- Use Zod for schema validation on the frontend, and Pydantic for request/response validation in FastAPI schemas.
- For file uploads, handle multipart forms asynchronously in FastAPI.

# State Management & Logic
- Use React Context for managing global state, such as user authentication and current study topic.
- Avoid overusing global state: Keep topic-specific data (e.g., documents, history) local to components where possible.
- Implement error handling and loading states in all API interactions using TanStack Query.

# Backend & Database
- Use SQLAlchemy ORM for database access with TiDB Serverless.
- Define models in models.py using SQLAlchemy declarative base for tables like users, topics, documents, qa_history, and flashcards.
- Use TiDB's vector storage capabilities for embedding_vector fields to support semantic search.
- Implement authentication middleware in FastAPI for role-based access (e.g., user owns topics and documents).
- For embedding generation, use PyTorch-based libraries like sentence-transformers in services/embeddings.py.
- Integrate LLM APIs (e.g., OpenAI or Together) in services/llm.py for summarization, flashcard generation, and quizzes.

# AI & Machine Learning Integration
- Use Python 3 as the primary language for backend AI features.
- Use PyTorch for any custom deep learning models related to embeddings or LLM fine-tuning if needed.
- Use NumPy for numerical operations in embedding handling.
- Use Pandas for any data analysis or processing of qa_history or flashcards if reporting features are added.
- Test AI components in Jupyter notebooks for interactive development before integrating into FastAPI.
- Use Conda for managing backend environments and packages.
- Use Matplotlib for visualizing embedding distributions or performance metrics during development.

# Security & Non-Functional Best Practices
- Implement secure authentication: Use JWT or session-based auth in FastAPI, with password hashing (e.g., bcrypt).
- Ensure data privacy: Store sensitive healthcare-related notes securely, with encryption for embeddings if required.
- Scalability: Leverage TiDB's distributed storage for handling growing user data and vector searches.
- Performance: Optimize vector searches with indexes in TiDB; use async endpoints in FastAPI.
- Testing: Write unit tests for backend services using pytest; integration tests for API endpoints; frontend tests with Jest and React Testing Library.
- Logging & Monitoring: Use structured logging in FastAPI (e.g., loguru) and integrate error tracking (e.g., Sentry) for enterprise reliability.
- Accessibility: Follow WCAG guidelines in UI components for healthcare users who may have disabilities.

# Deployment & Environment Management
- Use Docker for containerizing backend and frontend for consistent deployments.
- Manage environments with Conda for development and production dependencies.
- Deploy to cloud platforms supporting TiDB Serverless (e.g., AWS or GCP) for enterprise scalability.