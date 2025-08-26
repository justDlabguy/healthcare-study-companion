import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.orm import Session, joinedload
import traceback

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..models import User, Topic, StudySession, StudySessionItem
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])
logger = logging.getLogger(__name__)

@router.post("/start", response_model=schemas.StudySessionOut)
async def start_study_session(
    request: Request,
    session_data: schemas.StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new study session.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting new study session for user {current_user.id}")
    logger.debug(f"Request data: {session_data.dict()}")
    
    try:
        # Verify topic exists and user has access if topic_id is provided
        if session_data.topic_id is not None:
            logger.debug(f"Verifying topic access for topic_id: {session_data.topic_id}")
            topic = db.query(Topic).filter(
                Topic.id == session_data.topic_id,
                Topic.owner_id == current_user.id  # Only owner can create sessions for their topics
            ).first()
            
            if not topic:
                error_msg = f"Topic {session_data.topic_id} not found or access denied for user {current_user.id}"
                logger.warning(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg
                )
        
        # Create the study session
        logger.debug("Creating new study session record")
        db_session = StudySession(
            user_id=current_user.id,
            topic_id=session_data.topic_id,
            session_type=session_data.session_type,
            start_time=datetime.utcnow(),
            session_metadata=session_data.session_metadata or {}
        )
        
        logger.debug(f"Adding session to database: {db_session}")
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Successfully created study session {db_session.id}")
        return db_session
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        error_msg = f"Failed to create study session: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@router.post("/{session_id}/items", response_model=schemas.StudySessionItemOut)
async def add_study_session_item(
    session_id: int,
    item_data: schemas.StudySessionItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an item to a study session.
    """
    # Verify session exists and belongs to the user
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
    
    # Create the study session item
    db_item = StudySessionItem(
        session_id=session_id,
        item_type=item_data.item_type,
        item_id=item_data.item_id,
        user_response=item_data.user_response,
        is_correct=item_data.is_correct,
        confidence=item_data.confidence,
        item_metadata=item_data.item_metadata,
        start_time=datetime.utcnow()
    )
    
    # Update session stats based on the item
    session.total_items += 1
    if item_data.is_correct is True:
        session.correct_answers += 1
    elif item_data.is_correct is False:
        session.incorrect_answers += 1
    else:
        session.skipped_answers += 1
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.patch("/{session_id}/items/{item_id}", response_model=schemas.StudySessionItemOut)
async def update_study_session_item(
    session_id: int,
    item_id: int,
    item_data: schemas.StudySessionItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a study session item.
    """
    # Verify session exists and belongs to the user
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
    
    # Get the item
    db_item = db.query(StudySessionItem).filter(
        StudySessionItem.id == item_id,
        StudySessionItem.session_id == session_id
    ).first()
    
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session item not found"
        )
    
    # Update the item
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    # If this is the first time setting is_correct, update session stats
    if item_data.is_correct is not None and db_item.is_correct != item_data.is_correct:
        # Decrement old count if it was set
        if db_item.is_correct is True:
            session.correct_answers -= 1
        elif db_item.is_correct is False:
            session.incorrect_answers -= 1
        
        # Increment new count
        if item_data.is_correct is True:
            session.correct_answers += 1
        elif item_data.is_correct is False:
            session.incorrect_answers += 1
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.patch("/{session_id}/complete", response_model=schemas.StudySessionOut)
async def complete_study_session(
    session_id: int,
    session_data: schemas.StudySessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a study session as complete.
    """
    # Get the session
    db_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
    
    # Update the session
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    # If end time is not provided, set it to now
    if db_session.end_time is None:
        db_session.end_time = datetime.utcnow()
    
    # Calculate duration if not provided
    if db_session.duration_seconds is None and db_session.end_time is not None:
        db_session.duration_seconds = int((db_session.end_time - db_session.start_time).total_seconds())
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/{session_id}", response_model=schemas.StudySessionOut)
async def get_study_session(
    session_id: int,
    include_items: bool = Query(True, description="Include session items in the response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a study session by ID.
    """
    query = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    )
    
    if include_items:
        query = query.options(joinedload(StudySession.items))
    
    db_session = query.first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
    
    return db_session

@router.get("/", response_model=schemas.StudySessionListResponse)
async def list_study_sessions(
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (inclusive)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    include_items: bool = Query(False, description="Include session items in the response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List study sessions with optional filtering.
    """
    # Build the base query
    query = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    )
    
    # Apply filters
    if topic_id is not None:
        query = query.filter(StudySession.topic_id == topic_id)
    
    if session_type is not None:
        query = query.filter(StudySession.session_type == session_type)
    
    if start_date is not None:
        query = query.filter(StudySession.start_time >= start_date)
    
    if end_date is not None:
        # Include the entire end date
        end_date = end_date.replace(hour=23, minute=59, second=59)
        query = query.filter(StudySession.start_time <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(StudySession.start_time.desc())
    query = query.offset(offset).limit(page_size)
    
    # Eager load items if requested
    if include_items:
        query = query.options(joinedload(StudySession.items))
    
    # Execute the query
    sessions = query.all()
    
    return {
        "items": sessions,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/stats/summary", response_model=schemas.StudySessionStats)
async def get_study_session_stats(
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    days: int = Query(30, ge=1, description="Number of days to include in the stats"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get study session statistics.
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build the base query
    query = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.start_time >= start_date,
        StudySession.start_time <= end_date
    )
    
    # Apply filters
    if topic_id is not None:
        query = query.filter(StudySession.topic_id == topic_id)
    
    if session_type is not None:
        query = query.filter(StudySession.session_type == session_type)
    
    # Get all sessions
    sessions = query.all()
    
    # Calculate basic stats
    total_sessions = len(sessions)
    total_duration = sum(s.duration_seconds or 0 for s in sessions)
    total_items = sum(s.total_items or 0 for s in sessions)
    total_correct = sum(s.correct_answers or 0 for s in sessions)
    total_incorrect = sum(s.incorrect_answers or 0 for s in sessions)
    total_skipped = sum(s.skipped_answers or 0 for s in sessions)
    
    # Calculate accuracy (avoid division by zero)
    total_attempted = total_correct + total_incorrect
    accuracy = (total_correct / total_attempted) * 100 if total_attempted > 0 else 0
    
    # Calculate average duration
    avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
    
    # Group by session type
    by_session_type: Dict[str, Dict[str, Any]] = {}
    for s in sessions:
        if s.session_type not in by_session_type:
            by_session_type[s.session_type] = {
                "count": 0,
                "total_duration": 0,
                "total_items": 0,
                "total_correct": 0,
                "total_incorrect": 0,
                "total_skipped": 0
            }
        
        by_session_type[s.session_type]["count"] += 1
        by_session_type[s.session_type]["total_duration"] += s.duration_seconds or 0
        by_session_type[s.session_type]["total_items"] += s.total_items or 0
        by_session_type[s.session_type]["total_correct"] += s.correct_answers or 0
        by_session_type[s.session_type]["total_incorrect"] += s.incorrect_answers or 0
        by_session_type[s.session_type]["total_skipped"] += s.skipped_answers or 0
    
    # Calculate accuracy for each session type
    for session_type, data in by_session_type.items():
        attempted = data["total_correct"] + data["total_incorrect"]
        data["accuracy"] = (data["total_correct"] / attempted * 100) if attempted > 0 else 0
        data["avg_duration"] = data["total_duration"] / data["count"] if data["count"] > 0 else 0
    
    # Group by date
    by_date: Dict[str, Dict[str, Any]] = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        by_date[date_str] = {
            "date": date_str,
            "count": 0,
            "total_duration": 0,
            "total_items": 0,
            "total_correct": 0,
            "total_incorrect": 0,
            "total_skipped": 0
        }
        current_date += timedelta(days=1)
    
    # Fill in the actual data
    for s in sessions:
        date_str = s.start_time.strftime("%Y-%m-%d")
        if date_str in by_date:
            by_date[date_str]["count"] += 1
            by_date[date_str]["total_duration"] += s.duration_seconds or 0
            by_date[date_str]["total_items"] += s.total_items or 0
            by_date[date_str]["total_correct"] += s.correct_answers or 0
            by_date[date_str]["total_incorrect"] += s.incorrect_answers or 0
            by_date[date_str]["total_skipped"] += s.skipped_answers or 0
    
    # Convert to list and calculate averages
    by_date_list = []
    for date_str, data in by_date.items():
        attempted = data["total_correct"] + data["total_incorrect"]
        data["accuracy"] = (data["total_correct"] / attempted * 100) if attempted > 0 else 0
        by_date_list.append(data)
    
    # Sort by date
    by_date_list.sort(key=lambda x: x["date"])
    
    # Convert back to dict for response
    by_date_dict = {item["date"]: item for item in by_date_list}
    
    return {
        "total_sessions": total_sessions,
        "total_duration_seconds": total_duration,
        "total_items": total_items,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_skipped": total_skipped,
        "accuracy": accuracy,
        "avg_duration_seconds": avg_duration,
        "by_session_type": by_session_type,
        "by_date": by_date_dict
    }

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_session_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific study session item.
    
    This operation is permanent and cannot be undone.
    """
    logger.info(f"Deleting study session item {item_id} for user {current_user.id}")
    
    # Get the item with its parent session for ownership verification
    db_item = db.query(StudySessionItem).join(
        StudySession,
        StudySessionItem.session_id == StudySession.id
    ).filter(
        StudySessionItem.id == item_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not db_item:
        logger.warning(f"Study session item {item_id} not found or access denied for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session item not found or access denied"
        )
    
    try:
        # Delete the item
        db.delete(db_item)
        db.commit()
        logger.info(f"Successfully deleted study session item {item_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to delete study session item {item_id}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete study session item"
        )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a study session and all its items.
    
    This operation is permanent and cannot be undone.
    """
    logger.info(f"Deleting study session {session_id} for user {current_user.id}")
    
    # Verify session exists and belongs to the user
    db_session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not db_session:
        logger.warning(f"Study session {session_id} not found or access denied for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
    
    try:
        # Delete the session (cascades to items due to delete-orphan)
        db.delete(db_session)
        db.commit()
        logger.info(f"Successfully deleted study session {session_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to delete study session {session_id}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete study session"
        )
