
1. **Authentication**
   - `POST /auth/token` - User login to obtain JWT token
     - Uses OAuth2 password flow
     - Returns access token for authenticated requests
     - Required for most other endpoints

2. **Health Check**
   - `GET /healthz` - Service health status
     - Verifies database connectivity
     - Returns API status and version

3. **Topics** (`/topics/`)
   - `GET /topics/` - List all topics
     - Returns paginated list of topics
     - Filterable by visibility (public/private)
   - `POST /topics/` - Create new topic
     - Requires authentication
     - Creates a new study topic
   - `GET /topics/{topic_id}` - Get topic details
     - Returns full topic information
     - Includes related documents and flashcards

4. **Documents** (`/topics/{topic_id}/documents/`)
   - `POST /` - Upload document
     - Supports PDF, DOCX, TXT files
     - Triggers async processing
   - `GET /` - List documents in topic
     - Shows document status and metadata
   - `GET /{document_id}` - Get document details
     - Includes extracted text and metadata

5. **Flashcards** (`/topics/{topic_id}/flashcards/`)
   - `GET /` - List flashcards
     - Filterable by review status
   - `POST /` - Create flashcard
     - Manual card creation
   - `POST /generate` - Generate flashcards
     - AI-generated from topic content
   - `GET /review` - Get cards due for review
     - Uses spaced repetition algorithm

6. **Q&A** (`/topics/{topic_id}/qa/`)
   - `POST /ask` - Ask question about topic
     - Uses AI to generate answers
     - Context-aware responses
   - `GET /history` - View Q&A history
     - Previous questions and answers
     - Filterable by date/score

7. **Study Sessions** (`/study-sessions/`)
   - `POST /start` - Begin study session
     - Tracks study metrics
   - `POST /{session_id}/complete` - End session
     - Saves progress
     - Updates spaced repetition schedule

8. **User Progress** (`/progress/`)
   - `GET /overview` - Study statistics
     - Time spent, cards reviewed
   - `GET /weak-areas` - Identified weak areas
     - Based on review performance

**Key Features:**
- JWT-based authentication
- Role-based access control (User/Admin)
- File upload with async processing
- AI-powered Q&A
- Spaced repetition for flashcards
- Progress tracking
- RESTful API design

**Authentication Flow:**
1. Get token from `/auth/token`
2. Include in header: `Authorization: Bearer <token>`
3. Token expires after 24 hours

**Error Handling:**
- Standard HTTP status codes
- JSON error responses
- Detailed validation messages

