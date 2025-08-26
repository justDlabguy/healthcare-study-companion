import axios from 'axios';

// Environment-aware API base URL configuration
const getApiBaseUrl = (): string => {
  // Use environment variable if available
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Fallback for development
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  
  // Production fallback - should be set via environment variables
  console.warn('NEXT_PUBLIC_API_URL not set, using fallback URL');
  return 'https://healthcare-study-companion-backend.railway.app';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with base URL and common headers
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 30000, // 30 second timeout
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log API calls in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Log successful responses in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    // Enhanced error logging for production debugging
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      timestamp: new Date().toISOString(),
      isCorsError: error.code === 'ERR_NETWORK' && !error.response,
    };
    
    console.error('API Error:', errorInfo);
    
    // Handle CORS errors specifically
    if (errorInfo.isCorsError) {
      console.error('CORS Error Detected:', {
        apiBaseUrl: API_BASE_URL,
        currentOrigin: typeof window !== 'undefined' ? window.location.origin : 'unknown',
        suggestion: 'Check CORS configuration on the backend server'
      });
    }
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token');
      if (typeof window !== 'undefined' && window.location.pathname !== '/auth/login') {
        window.location.href = '/auth/login';
      }
    }
    
    // Handle rate limiting
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      if (retryAfter) {
        console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
      }
    }
    
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PasswordResetRequest {
  email: string;
}

// Authentication API
export const authApi = {
  /**
   * Login user
   */
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      // Store token in localStorage
      localStorage.setItem('auth_token', response.data.access_token);
      
      // Fetch user data after successful login
      const userResponse = await api.get('/auth/me', {
        headers: {
          'Authorization': `Bearer ${response.data.access_token}`
        }
      });
      
      return {
        access_token: response.data.access_token,
        token_type: response.data.token_type,
        user: userResponse.data
      };
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  /**
   * Register new user
   */
  signup: async (userData: SignupRequest): Promise<AuthResponse> => {
    try {
      const response = await api.post('/auth/signup', userData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      // Store token in localStorage if available in response
      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        
        // Fetch user data after successful signup
        const userResponse = await api.get('/auth/me');
        return {
          ...response.data,
          user: userResponse.data
        };
      }
      
      return response.data;
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  },

  /**
   * Get current user profile
   */
  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    try {
      localStorage.removeItem('auth_token');
      // Optionally call backend logout endpoint if it exists
      // await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  },

  /**
   * Request password reset
   */
  requestPasswordReset: async (data: PasswordResetRequest): Promise<void> => {
    try {
      await api.post('/auth/password-reset', data);
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw error;
    }
  },
};

// Topic types
export interface Topic {
  id: number;
  title: string;
  description: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateTopicRequest {
  title: string;
  description: string;
}

export interface UpdateTopicRequest {
  title?: string;
  description?: string;
}

// Topics API
export const topicsApi = {
  /**
   * Get all topics for the current user
   */
  getTopics: async (): Promise<Topic[]> => {
    try {
      const response = await api.get('/topics');
      return response.data;
    } catch (error) {
      console.error('Failed to get topics:', error);
      throw error;
    }
  },

  /**
   * Get a specific topic by ID
   */
  getTopic: async (topicId: number): Promise<Topic> => {
    try {
      const response = await api.get(`/topics/${topicId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get topic:', error);
      throw error;
    }
  },

  /**
   * Create a new topic
   */
  createTopic: async (data: CreateTopicRequest): Promise<Topic> => {
    try {
      const response = await api.post('/topics/', data);
      return response.data;
    } catch (error) {
      console.error('Failed to create topic:', error);
      throw error;
    }
  },

  /**
   * Update a topic
   */
  updateTopic: async (topicId: number, data: UpdateTopicRequest): Promise<Topic> => {
    try {
      const response = await api.put(`/topics/${topicId}`, data);
      return response.data;
    } catch (error) {
      console.error('Failed to update topic:', error);
      throw error;
    }
  },

  /**
   * Delete a topic
   */
  deleteTopic: async (topicId: number): Promise<void> => {
    try {
      await api.delete(`/topics/${topicId}`);
    } catch (error) {
      console.error('Failed to delete topic:', error);
      throw error;
    }
  },
};

// Document types
export interface Document {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  status: 'PENDING' | 'PROCESSING' | 'PROCESSED' | 'ERROR';
  error_message?: string;
  topic_id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface QAResponse {
  id: number;
  question: string;
  answer: string;
  topic_id: number;
  created_at: string;
  confidence?: number;
  tokens_used?: number;
  model?: string;
  metadata?: any;
}

export interface QAHistoryResponse {
  items: QAResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateQARequest {
  question: string;
  context?: string;
  temperature?: number;
}

export interface Flashcard {
  id: number;
  topic_id: number;
  front: string;
  back: string;
  tags?: string[];
  difficulty?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_reviewed?: string;
  next_review?: string;
  ease_factor: number;
  review_count: number;
}

export interface FlashcardReviewRequest {
  quality: number; // 0-5 scale
}

// Search types
export interface SearchResult {
  chunk_id: number;
  document_id: number;
  document_filename: string;
  score: number;
  snippet: string;
  text: string;
  chunk_index: number;
  chunk_metadata: Record<string, any>;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  topic_id?: number;
  execution_time_ms?: number;
}

export interface CrossTopicSearchResponse {
  results_by_topic: Record<number, SearchResult[]>;
  total_results: number;
  query: string;
  execution_time_ms?: number;
}

export interface SearchQuery {
  query: string;
  min_score?: number;
  document_ids?: number[];
}

export interface SearchContextResponse {
  query: string;
  context: string;
  sources: SearchResult[];
  context_length: number;
  num_sources: number;
}

// Documents API
export const documentsApi = {
  /**
   * Get all documents for a topic
   */
  getDocuments: async (topicId: number): Promise<Document[]> => {
    try {
      const response = await api.get(`/topics/${topicId}/documents`);
      return response.data;
    } catch (error) {
      console.error('Failed to get documents:', error);
      throw error;
    }
  },

  /**
   * Upload a document to a topic
   */
  uploadDocument: async (topicId: number, file: File): Promise<Document> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`/topics/${topicId}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to upload document:', error);
      throw error;
    }
  },

  /**
   * Delete a document
   */
  deleteDocument: async (topicId: number, documentId: number): Promise<void> => {
    try {
      await api.delete(`/topics/${topicId}/documents/${documentId}`);
    } catch (error) {
      console.error('Failed to delete document:', error);
      throw error;
    }
  },

  /**
   * Reprocess a failed document
   */
  reprocessDocument: async (documentId: number): Promise<Document> => {
    try {
      const response = await api.post(`/documents/${documentId}/reprocess`);
      return response.data;
    } catch (error) {
      console.error('Failed to reprocess document:', error);
      throw error;
    }
  },
};

// Q&A API
export const qaApi = {
  /**
   * Get Q&A history for a topic
   */
  getQAHistory: async (topicId: number): Promise<QAHistoryResponse> => {
    try {
      const response = await api.get(`/topics/${topicId}/qa/history`);
      return response.data;
    } catch (error) {
      console.error('Failed to get Q&A history:', error);
      throw error;
    }
  },

  /**
   * Ask a question about a topic
   */
  askQuestion: async (topicId: number, question: string, context?: string): Promise<QAResponse> => {
    try {
      const response = await api.post(`/topics/${topicId}/qa/ask`, {
        question,
        context,
        temperature: 0.7
      });
      
      // Create a mock QA response since the backend returns just the answer
      const qaResponse: QAResponse = {
        id: Date.now(), // Temporary ID
        question,
        answer: response.data.answer,
        topic_id: topicId,
        created_at: new Date().toISOString(),
        confidence: response.data.confidence,
        tokens_used: response.data.tokens_used,
        model: response.data.model
      };
      
      return qaResponse;
    } catch (error) {
      console.error('Failed to ask question:', error);
      throw error;
    }
  },

  /**
   * Delete a Q&A entry
   */
  deleteQA: async (topicId: number, qaId: number): Promise<void> => {
    try {
      await api.delete(`/topics/${topicId}/qa/history/${qaId}`);
    } catch (error) {
      console.error('Failed to delete Q&A:', error);
      throw error;
    }
  },

  /**
   * Delete all Q&A history for a topic
   */
  deleteAllQA: async (topicId: number): Promise<void> => {
    try {
      await api.delete(`/topics/${topicId}/qa/history`);
    } catch (error) {
      console.error('Failed to delete all Q&A history:', error);
      throw error;
    }
  },
};

// Flashcards API
export const flashcardsApi = {
  /**
   * Get all flashcards for a topic
   */
  getFlashcards: async (topicId: number): Promise<Flashcard[]> => {
    try {
      const response = await api.get(`/topics/${topicId}/flashcards`);
      return response.data;
    } catch (error) {
      console.error('Failed to get flashcards:', error);
      throw error;
    }
  },

  /**
   * Get flashcards due for review
   */
  getFlashcardsForReview: async (topicId: number, limit: number = 20): Promise<Flashcard[]> => {
    try {
      const response = await api.get(`/topics/${topicId}/flashcards/review?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get flashcards for review:', error);
      throw error;
    }
  },

  /**
   * Create a new flashcard
   */
  createFlashcard: async (topicId: number, flashcard: { front: string; back: string; tags?: string[]; difficulty?: number }): Promise<Flashcard> => {
    try {
      const response = await api.post(`/topics/${topicId}/flashcards`, flashcard);
      return response.data;
    } catch (error) {
      console.error('Failed to create flashcard:', error);
      throw error;
    }
  },

  /**
   * Review a flashcard
   */
  reviewFlashcard: async (topicId: number, flashcardId: number, quality: number): Promise<any> => {
    try {
      const response = await api.post(`/topics/${topicId}/flashcards/${flashcardId}/review`, {
        quality
      });
      return response.data;
    } catch (error) {
      console.error('Failed to review flashcard:', error);
      throw error;
    }
  },

  /**
   * Generate flashcards from content
   */
  generateFlashcards: async (topicId: number, content: string, numCards: number = 5): Promise<Flashcard[]> => {
    try {
      const response = await api.post(`/topics/${topicId}/flashcards/generate`, {
        content,
        num_cards: numCards,
        style: 'basic'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate flashcards:', error);
      throw error;
    }
  },
};

// Study Session API
export const studySessionsApi = {
  /**
   * Delete a study session
   * @param sessionId - ID of the session to delete
   */
  deleteSession: async (sessionId: string): Promise<void> => {
    try {
      await api.delete(`/study-sessions/${sessionId}`);
    } catch (error) {
      console.error('Failed to delete study session:', error);
      throw error;
    }
  },

  // Other study session related methods can be added here
  // For example:
  // getSessions: async (): Promise<StudySession[]> => { ... },
  // createSession: async (data: CreateSessionDto): Promise<StudySession> => { ... },
};

// Search API
export const searchApi = {
  /**
   * Search within a specific topic
   */
  searchWithinTopic: async (
    topicId: number, 
    searchQuery: SearchQuery, 
    limit: number = 10
  ): Promise<SearchResponse> => {
    try {
      const response = await api.post(`/search/topics/${topicId}?limit=${limit}`, searchQuery);
      return response.data;
    } catch (error) {
      console.error('Failed to search within topic:', error);
      throw error;
    }
  },

  /**
   * Search across multiple topics
   */
  searchAcrossTopics: async (
    searchQuery: SearchQuery,
    limitPerTopic: number = 5,
    topicIds?: number[]
  ): Promise<CrossTopicSearchResponse> => {
    try {
      const params = new URLSearchParams();
      params.append('limit_per_topic', limitPerTopic.toString());
      if (topicIds) {
        topicIds.forEach(id => params.append('topic_ids', id.toString()));
      }
      
      const response = await api.post(`/search/?${params.toString()}`, searchQuery);
      return response.data;
    } catch (error) {
      console.error('Failed to search across topics:', error);
      throw error;
    }
  },

  /**
   * Get search context for Q&A
   */
  getSearchContext: async (
    topicId: number,
    query: string,
    maxChunks: number = 5,
    maxLength: number = 2000
  ): Promise<SearchContextResponse> => {
    try {
      const params = new URLSearchParams({
        query,
        max_chunks: maxChunks.toString(),
        max_length: maxLength.toString()
      });
      
      const response = await api.get(`/search/topics/${topicId}/context?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get search context:', error);
      throw error;
    }
  },
};

export default api;
