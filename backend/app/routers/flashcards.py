from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..models import User, Flashcard, FlashcardReview, Document
from ..services.spaced_repetition import calculate_next_review
from ..services.flashcard_generator import flashcard_generator, FlashcardType

router = APIRouter(prefix="/topics/{topic_id}/flashcards", tags=["flashcards"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.FlashcardOut])
def list_flashcards(
    topic_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all flashcards for a topic.
    
    - **active_only**: If True, only return active flashcards (default: True)
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return (for pagination)
    """
    # Verify topic exists and user has access
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    query = db.query(Flashcard).filter(Flashcard.topic_id == topic_id)
    
    if active_only:
        query = query.filter(Flashcard.is_active == True)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.FlashcardOut, status_code=status.HTTP_201_CREATED)
def create_flashcard(
    topic_id: int,
    flashcard: schemas.FlashcardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new flashcard for a topic.
    """
    # Verify topic exists and user has access
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    db_flashcard = Flashcard(
        topic_id=topic_id,
        front=flashcard.front,
        back=flashcard.back,
        flashcard_metadata=flashcard.flashcard_metadata,
        is_active=flashcard.is_active
    )
    
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    
    return db_flashcard

@router.post("/generate", response_model=List[schemas.FlashcardOut])
async def generate_flashcards(
    topic_id: int,
    request: schemas.FlashcardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate flashcards from topic content using AI.
    
    - **content**: The content to generate flashcards from (optional, will use documents if not provided)
    - **num_cards**: Number of flashcards to generate (default: 5)
    - **style**: Generation style (basic, cloze, multiple_choice)
    """
    # Verify topic exists and user has access
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    try:
        # Determine flashcard type from style
        card_type_mapping = {
            "basic": FlashcardType.BASIC,
            "cloze": FlashcardType.CLOZE,
            "multiple_choice": FlashcardType.MULTIPLE_CHOICE,
            "detailed": FlashcardType.BASIC,  # Fallback to basic
            "qa": FlashcardType.BASIC  # Fallback to basic
        }
        card_type = card_type_mapping.get(request.style, FlashcardType.BASIC)
        
        # Generate flashcards
        if hasattr(request, 'content') and request.content and request.content.strip():
            # Generate from provided content
            generated_flashcards = await flashcard_generator.generate_flashcards_from_content(
                content=request.content,
                num_cards=request.num_cards,
                card_type=card_type,
                topic_context=f"Topic: {topic.title}. {topic.description or ''}"
            )
        else:
            # Generate from topic documents
            documents = db.query(Document).filter(
                Document.topic_id == topic_id,
                Document.status == "processed"
            ).all()
            
            if not documents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No processed documents found in topic. Please upload and process documents first, or provide content directly."
                )
            
            generated_flashcards = await flashcard_generator.generate_flashcards_from_documents(
                documents=documents,
                num_cards=request.num_cards,
                card_type=card_type,
                topic_context=f"Topic: {topic.title}. {topic.description or ''}"
            )
        
        # Save generated flashcards to database
        db_flashcards = []
        for gen_card in generated_flashcards:
            db_flashcard = Flashcard(
                topic_id=topic_id,
                front=gen_card.front,
                back=gen_card.back,
                flashcard_metadata=gen_card.metadata,
                is_active=True
            )
            db.add(db_flashcard)
            db_flashcards.append(db_flashcard)
        
        db.commit()
        
        # Refresh all flashcards to get their IDs
        for flashcard in db_flashcards:
            db.refresh(flashcard)
        
        logger.info(f"Generated {len(db_flashcards)} flashcards for topic {topic_id}")
        return db_flashcards
        
    except Exception as e:
        logger.error(f"Error generating flashcards for topic {topic_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )

@router.post("/generate-from-documents", response_model=List[schemas.FlashcardOut])
async def generate_flashcards_from_documents(
    topic_id: int,
    num_cards: int = 5,
    card_type: str = "basic",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate flashcards from all processed documents in the topic.
    
    - **num_cards**: Number of flashcards to generate (default: 5)
    - **card_type**: Type of flashcards (basic, cloze, multiple_choice)
    """
    # Verify topic exists and user has access
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    # Get processed documents
    documents = db.query(Document).filter(
        Document.topic_id == topic_id,
        Document.status == "processed"
    ).all()
    
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processed documents found in topic. Please upload and process documents first."
        )
    
    try:
        # Map card type string to enum
        card_type_mapping = {
            "basic": FlashcardType.BASIC,
            "cloze": FlashcardType.CLOZE,
            "multiple_choice": FlashcardType.MULTIPLE_CHOICE
        }
        flashcard_type = card_type_mapping.get(card_type, FlashcardType.BASIC)
        
        # Generate flashcards from documents
        generated_flashcards = await flashcard_generator.generate_flashcards_from_documents(
            documents=documents,
            num_cards=num_cards,
            card_type=flashcard_type,
            topic_context=f"Topic: {topic.title}. {topic.description or ''}"
        )
        
        # Save to database
        db_flashcards = []
        for gen_card in generated_flashcards:
            db_flashcard = Flashcard(
                topic_id=topic_id,
                front=gen_card.front,
                back=gen_card.back,
                flashcard_metadata=gen_card.metadata,
                is_active=True
            )
            db.add(db_flashcard)
            db_flashcards.append(db_flashcard)
        
        db.commit()
        
        # Refresh to get IDs
        for flashcard in db_flashcards:
            db.refresh(flashcard)
        
        logger.info(f"Generated {len(db_flashcards)} {card_type} flashcards from documents for topic {topic_id}")
        return db_flashcards
        
    except Exception as e:
        logger.error(f"Error generating flashcards from documents for topic {topic_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )

@router.get("/review", response_model=List[schemas.FlashcardOut])
def get_flashcards_for_review(
    topic_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get flashcards that are due for review.
    
    - **limit**: Maximum number of cards to return (default: 20)
    """
    # Verify topic exists and user has access
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    # Get flashcards that are either:
    # 1. Never reviewed (next_review is NULL) OR
    # 2. Due for review (next_review <= now)
    now = datetime.utcnow()
    flashcards = db.query(Flashcard).filter(
        Flashcard.topic_id == topic_id,
        Flashcard.is_active == True,
        (Flashcard.next_review <= now) | (Flashcard.next_review.is_(None))
    ).order_by(Flashcard.next_review.asc()).limit(limit).all()
    
    return flashcards

@router.post("/{flashcard_id}/review", response_model=schemas.FlashcardReviewOut, status_code=status.HTTP_201_CREATED)
def review_flashcard(
    topic_id: int,
    flashcard_id: int,
    review: schemas.FlashcardReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a flashcard review.
    
    - **quality**: Review quality (0-5 scale)
    """
    # Verify flashcard exists and belongs to user's topic
    flashcard = db.query(Flashcard).join(models.Topic).filter(
        Flashcard.id == flashcard_id,
        Flashcard.topic_id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found or access denied"
        )
    
    # Calculate next review using the spaced repetition service
    now = datetime.utcnow()
    review_quality = min(max(review.quality, 0), 5)  # Clamp to 0-5 range
    
    # Calculate new parameters using the spaced repetition algorithm
    ease_factor, interval, next_review = calculate_next_review(
        ease_factor=flashcard.ease_factor,
        interval=flashcard.interval,
        review_quality=review_quality,
        review_count=flashcard.review_count
    )
    
    # Update flashcard stats
    flashcard.last_reviewed = now
    flashcard.next_review = next_review
    flashcard.ease_factor = ease_factor
    flashcard.interval = interval
    flashcard.review_count = flashcard.review_count + 1
    flashcard.updated_at = now
    
    # Create review record
    db_review = models.FlashcardReview(
        flashcard_id=flashcard.id,
        user_id=current_user.id,
        quality=review_quality,
        review_time=now,
        ease_factor=ease_factor,
        interval=interval,
        review_count=flashcard.review_count,
        next_review=next_review
    )
    
    db.add(db_review)
    db.add(flashcard)
    db.commit()
    db.refresh(db_review)
    db.refresh(flashcard)
    
    # Return the review using the Pydantic model for proper serialization
    return schemas.FlashcardReviewOut.from_orm(db_review)
