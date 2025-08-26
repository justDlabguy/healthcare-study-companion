from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/topics", tags=["topics"])

@router.post("/", response_model=schemas.TopicOut, status_code=status.HTTP_201_CREATED)
async def create_topic(
    request: Request,
    topic: schemas.TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new topic (requires authentication)."""
    logger.info(f"Received topic creation request: {topic.dict()}")
    logger.info(f"Headers: {request.headers}")
    
    try:
        db_topic = models.Topic(
            title=topic.title,
            description=topic.description,
            owner_id=current_user.id
        )
        db.add(db_topic)
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except Exception as e:
        logger.error(f"Error creating topic: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create topic: {str(e)}"
        )

@router.get("/", response_model=List[schemas.TopicOut])
def list_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List topics for the current user."""
    return (
        db.query(models.Topic)
        .filter(models.Topic.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/{topic_id}", response_model=schemas.TopicOut)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a topic by ID if owned by the current user."""
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/{topic_id}", response_model=schemas.TopicOut)
def update_topic(
    topic_id: int,
    topic_update: schemas.TopicCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update a topic (must be the owner)."""
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic.title = topic_update.title
    topic.description = topic_update.description
    db.commit()
    db.refresh(topic)
    return topic

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a topic (must be the owner)."""
    topic = db.query(models.Topic).filter(
        models.Topic.id == topic_id,
        models.Topic.owner_id == current_user.id
    ).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    db.delete(topic)
    db.commit()
    return None
