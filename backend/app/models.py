from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Float,
    Boolean,
    UniqueConstraint,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
import enum

from .database import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    
class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    topics = relationship("Topic", back_populates="owner", cascade="all,delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all,delete-orphan")
    llm_usage = relationship("LLMUsage", back_populates="user", cascade="all,delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="topics")
    documents = relationship("Document", back_populates="topic", cascade="all,delete-orphan")
    qa_history = relationship("QAHistory", back_populates="topic", cascade="all,delete-orphan")
    flashcards = relationship("Flashcard", back_populates="topic", cascade="all,delete-orphan")

    __table_args__ = (
        UniqueConstraint("owner_id", "title", name="uq_topic_owner_title"),
    )
    
    def __repr__(self):
        return f"<Topic {self.title}>"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    text = Column(Text, nullable=True)  # Extracted text content
    file_metadata = Column(JSON, nullable=True)  # File metadata
    vector_dim = Column(Integer, nullable=True)  # Dimension of the vector embeddings
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    topic = relationship("Topic", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all,delete-orphan")
    
    __table_args__ = (
        Index("idx_document_topic_status", "topic_id", "status"),
    )
    
    def __repr__(self):
        return f"<Document {self.filename}>"


class DocumentChunk(Base):
    """Represents a chunk of text from a document with its vector embedding."""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order of the chunk in the document
    text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)  # Can store page number, section, etc.
    embedding = Column(JSON, nullable=True)  # Store the vector embedding as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_document_index"),
    )
    
    def __repr__(self):
        return f"<DocumentChunk {self.document_id}.{self.chunk_index}>"


class QAHistory(Base):
    __tablename__ = "qa_history"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    qa_metadata = Column(JSON, nullable=True)  # Can store model used, parameters, etc.
    score = Column(Float, nullable=True)  # Confidence score of the answer
    feedback = Column(Text, nullable=True)  # User feedback on the answer
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="qa_history")
    user = relationship("User")
    
    # Index for faster lookups
    __table_args__ = (
        Index("idx_qa_topic_user", "topic_id", "user_id"),
    )
    
    def __repr__(self):
        return f"<QAHistory {self.id}: {self.question[:50]}...>"


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    flashcard_metadata = Column(JSON, nullable=True)  # Can store tags, difficulty, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5, nullable=False)  # For spaced repetition
    interval = Column(Integer, default=1, nullable=False)  # Days until next review
    review_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="flashcards")
    reviews = relationship("FlashcardReview", back_populates="flashcard", cascade="all,delete-orphan")
    
    def __repr__(self):
        return f"<Flashcard {self.id}: {self.front[:50]}...>"


class LLMUsage(Base):
    """Tracks usage of LLM API calls for billing and monitoring."""
    __tablename__ = "llm_usage"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # e.g., 'openai', 'anthropic', 'mistral'
    model = Column(String(100), nullable=False)  # e.g., 'gpt-4', 'claude-2', 'mistral-7b'
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    cost = Column(Float, nullable=True)  # Estimated cost in USD
    usage_metadata = Column('metadata', JSON, nullable=True)  # Additional metadata like request/response info
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="llm_usage")
    
    def __repr__(self):
        return f"<LLMUsage(id={self.id}, user_id={self.user_id}, model={self.model}, tokens={self.total_tokens})>"


class FlashcardReview(Base):
    """Tracks user reviews of flashcards for spaced repetition.
    
    This model records each review of a flashcard and implements the SM-2 spaced repetition algorithm.
    """
    __tablename__ = "flashcard_reviews"
    
    id = Column(Integer, primary_key=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Review information
    quality = Column(Integer, nullable=False)  # User's rating of the review (0-5)
    review_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Spaced repetition parameters
    ease_factor = Column(Float, nullable=False, default=2.5)  # Current ease factor
    interval = Column(Integer, nullable=False, default=1)  # Days until next review
    review_count = Column(Integer, nullable=False, default=0)  # Number of times reviewed
    
    # Calculated fields
    next_review = Column(DateTime, nullable=False)  # When to review next
    
    # Relationships
    flashcard = relationship("Flashcard", back_populates="reviews")
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_flashcard_review_user", "flashcard_id", "user_id"),
        Index("idx_next_review", "user_id", "next_review"),  # For finding due reviews
    )
    
    def __repr__(self):
        return f"<FlashcardReview {self.id}: flashcard={self.flashcard_id}, quality={self.quality}, next_review={self.next_review}>"


class StudySession(Base):
    """Tracks a user's study session."""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Session details
    session_type = Column(String(50), nullable=False)  # e.g., 'flashcard', 'qa', 'mixed'
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Calculated in seconds
    
    # Performance metrics
    total_items = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    incorrect_answers = Column(Integer, default=0, nullable=False)
    skipped_answers = Column(Integer, default=0, nullable=False)
    
    # Additional metadata
    session_metadata = Column(JSON, nullable=True)  # Can store device info, browser, etc.
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    topic = relationship("Topic")
    items = relationship("StudySessionItem", back_populates="session", cascade="all,delete-orphan")
    
    __table_args__ = (
        Index("idx_study_session_user", "user_id", "start_time"),
    )
    
    def __repr__(self):
        return f"<StudySession {self.id}: user={self.user_id}, type={self.session_type}, duration={self.duration_seconds}s>"


class StudySessionItem(Base):
    """Tracks individual items within a study session."""
    __tablename__ = "study_session_items"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Item details
    item_type = Column(String(50), nullable=False)  # e.g., 'flashcard', 'qa', 'document'
    item_id = Column(Integer, nullable=False)  # ID of the flashcard, QA, etc.
    
    # User interaction
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # User response
    user_response = Column(Text, nullable=True)  # User's answer or response
    is_correct = Column(Boolean, nullable=True)  # Whether the response was correct
    confidence = Column(Float, nullable=True)  # User's confidence in their answer (0-1)
    
    # Additional metadata
    item_metadata = Column(JSON, nullable=True)  # Can store question, correct answer, etc.
    
    # Relationships
    session = relationship("StudySession", back_populates="items")
    
    __table_args__ = (
        Index("idx_study_session_item", "session_id", "item_type", "item_id"),
        Index("idx_study_item_type", "item_type", "item_id"),
    )
    
    def __repr__(self):
        return f"<StudySessionItem {self.id}: session={self.session_id}, type={self.item_type}, correct={self.is_correct}>"

