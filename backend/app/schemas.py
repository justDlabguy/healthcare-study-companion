from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# User
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


# Topic
class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicOut(TopicBase):
    id: int
    owner_id: int
    created_at: datetime
    is_public: bool = False

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    filename: str
    content_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentOut(DocumentBase):
    id: int
    topic_id: int
    file_size: Optional[int] = None
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    file_metadata: Optional[dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# Document Chunk schemas
class DocumentChunkBase(BaseModel):
    text: str
    chunk_index: int
    chunk_metadata: Optional[Dict[str, Any]] = None


class DocumentChunkOut(DocumentChunkBase):
    id: int
    document_id: int
    created_at: datetime
    embedding: Optional[List[float]] = None

    class Config:
        from_attributes = True


# Flashcard schemas
class FlashcardBase(BaseModel):
    front: str
    back: str
    flashcard_metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True


class FlashcardCreate(FlashcardBase):
    pass


class FlashcardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    flashcard_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FlashcardOut(FlashcardBase):
    id: int
    topic_id: int
    created_at: datetime
    updated_at: datetime
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    ease_factor: float = 2.5
    interval: int = 1
    review_count: int = 0

    class Config:
        from_attributes = True


class FlashcardGenerateRequest(BaseModel):
    content: Optional[str] = None  # Optional - will use documents if not provided
    num_cards: int = 5
    style: Optional[str] = "basic"  # basic, cloze, multiple_choice, detailed, qa


class FlashcardReviewRequest(BaseModel):
    quality: int  # 0-5 scale


class FlashcardReviewOut(BaseModel):
    id: int
    flashcard_id: int
    quality: int
    ease_factor: float
    interval: int
    review_count: int
    review_time: datetime
    next_review: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Create a dictionary with all the fields
        data = {
            'id': obj.id,
            'flashcard_id': obj.flashcard_id,
            'quality': obj.quality,
            'ease_factor': float(obj.ease_factor) if obj.ease_factor is not None else 2.5,
            'interval': int(obj.interval) if obj.interval is not None else 0,
            'review_count': int(obj.review_count) if obj.review_count is not None else 0,
            'review_time': obj.review_time if obj.review_time is not None else datetime.utcnow(),
            'next_review': obj.next_review if obj.next_review is not None else datetime.utcnow()
        }
        return cls(**data)


# Q&A Schemas
class QAQuestion(BaseModel):
    """Schema for asking a question about a topic"""
    question: str = Field(..., min_length=3, max_length=500, description="The question to ask about the topic")
    context: Optional[str] = Field(None, max_length=2000, description="Additional context for the question")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Controls randomness in the AI's response")


class QAAnswer(BaseModel):
    """Schema for an answer to a question"""
    answer: str = Field(..., description="The generated answer to the question")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="List of sources used to generate the answer")
    model: str = Field(..., description="The AI model used to generate the answer")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used to generate the answer")


class QAHistoryItem(BaseModel):
    """Schema for a Q&A history item"""
    id: int
    topic_id: int
    question: str
    answer: str
    confidence: float
    created_at: datetime
    tokens_used: int
    model: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class QAHistoryResponse(BaseModel):
    """Response model for Q&A history"""
    items: List[QAHistoryItem]
    total: int
    page: int
    page_size: int


# Study Session Schemas
class StudySessionBase(BaseModel):
    """Base schema for study session"""
    topic_id: Optional[int] = Field(
        None, 
        description="ID of the topic this session is associated with"
    )
    session_type: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Type of study session (e.g., 'flashcard', 'qa', 'mixed')"
    )
    session_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the session",
        example={"device": "web", "app_version": "1.0.0"}
    )


class StudySessionCreate(StudySessionBase):
    """Schema for creating a new study session"""
    topic_id: Optional[int] = Field(None, description="ID of the topic this session is associated with")
    session_type: str = Field(..., min_length=1, max_length=50, description="Type of study session (e.g., 'flashcard', 'qa', 'mixed')")
    session_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the session",
        example={"device": "web", "app_version": "1.0.0"}
    )


class StudySessionItemBase(BaseModel):
    """Base schema for study session item"""
    item_type: str = Field(..., min_length=1, max_length=50, description="Type of item (e.g., 'flashcard', 'qa')")
    item_id: int = Field(..., gt=0, description="ID of the item in its respective table")
    user_response: Optional[str] = Field(None, description="User's response to the item")
    is_correct: Optional[bool] = Field(None, description="Whether the response was correct")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="User's confidence in their answer (0-1)")
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the item")


class StudySessionItemCreate(StudySessionItemBase):
    """Schema for creating a new study session item"""
    item_type: str = Field(..., min_length=1, max_length=50, description="Type of item (e.g., 'flashcard', 'qa')")
    item_id: int = Field(..., gt=0, description="ID of the item in its respective table")
    user_response: Optional[str] = Field(None, description="User's response to the item")
    is_correct: Optional[bool] = Field(None, description="Whether the response was correct")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="User's confidence in their answer (0-1)")
    item_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata for the item",
        example={"difficulty": "medium", "time_spent_seconds": 30}
    )


class StudySessionItemUpdate(StudySessionItemBase):
    """Schema for updating a study session item"""
    end_time: Optional[datetime] = Field(None, description="When the user completed the item")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Time spent on the item in seconds")


class StudySessionItemOut(StudySessionItemBase):
    """Schema for returning a study session item"""
    id: int
    session_id: int
    item_type: str
    item_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    user_response: Optional[str] = None
    is_correct: Optional[bool] = None
    confidence: Optional[float] = None
    item_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StudySessionOut(StudySessionBase):
    """Schema for returning a study session with its items"""
    id: int
    user_id: int
    topic_id: Optional[int] = None
    session_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_items: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_answers: int = 0
    created_at: Optional[datetime] = None
    session_metadata: Optional[Dict[str, Any]] = None
    items: List[StudySessionItemOut] = []
    
    class Config:
        from_attributes = True


class StudySessionUpdate(BaseModel):
    """Schema for updating a study session"""
    end_time: Optional[datetime] = Field(None, description="When the session ended")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Total duration of the session in seconds")
    total_items: Optional[int] = Field(None, ge=0, description="Total number of items in the session")
    correct_answers: Optional[int] = Field(None, ge=0, description="Number of correct answers")
    incorrect_answers: Optional[int] = Field(None, ge=0, description="Number of incorrect answers")
    skipped_answers: Optional[int] = Field(None, ge=0, description="Number of skipped answers")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the session")


class StudySessionStats(BaseModel):
    """Schema for study session statistics"""
    total_sessions: int = 0
    total_duration_seconds: int = 0
    total_items: int = 0
    total_correct: int = 0
    total_incorrect: int = 0
    total_skipped: int = 0
    accuracy: float = 0.0
    avg_duration_seconds: float = 0.0
    by_session_type: Dict[str, Dict[str, Any]] = {}
    by_date: Dict[str, Dict[str, Any]] = {}


class StudySessionListResponse(BaseModel):
    """Response model for listing study sessions"""
    items: List[StudySessionOut]
    total: int
    page: int
    page_size: int


# Progress Tracking Schemas
class ProgressStats(BaseModel):
    """Schema for progress statistics"""
    total_sessions: int = 0
    total_study_time_minutes: int = 0
    total_questions_answered: int = 0
    correct_answers: int = 0
    accuracy: float = 0.0
    average_score: float = 0.0
    weak_areas: List[Dict[str, Any]] = []
    recent_activity: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class RecentSession(BaseModel):
    """Schema for recent study sessions in progress overview"""
    id: int
    session_type: str
    start_time: datetime
    duration_seconds: Optional[int] = None
    correct_answers: int
    total_items: int
    
    class Config:
        from_attributes = True


class UserProgressOverview(BaseModel):
    """Schema for user progress overview"""
    total_sessions: int
    total_study_time_seconds: int
    total_answers: int
    correct_answers: int
    accuracy: float
    current_streak_days: int
    recent_sessions: List[RecentSession]


class WeakArea(BaseModel):
    """Schema for weak area identification"""
    topic_id: int
    topic_name: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    last_studied: datetime
