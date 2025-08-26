from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import StudySession, StudySessionItem, Topic, User, Flashcard, QAHistory
from ..schemas import UserProgressOverview, WeakArea, ProgressStats
from ..auth import get_current_user

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/overview", response_model=UserProgressOverview)
async def get_progress_overview(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an overview of the user's study progress
    
    Args:
        days: Number of days to look back for statistics (default: 30)
        
    Returns:
        UserProgressOverview: Overview of the user's study progress
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get study sessions in the date range
        sessions = db.query(StudySession).filter(
            StudySession.user_id == current_user.id,
            StudySession.start_time >= start_date
        ).all()
        
        # Calculate statistics
        total_sessions = len(sessions)
        total_study_time = sum(
            (s.duration_seconds or 0) 
            for s in sessions 
            if s.duration_seconds is not None
        )
        
        # Get session items for accuracy calculation
        session_items = db.query(StudySessionItem).filter(
            StudySessionItem.session_id.in_([s.id for s in sessions])
        ).all()
        
        # Calculate accuracy
        total_answers = len(session_items)
        correct_answers = sum(1 for item in session_items if item.is_correct)
        accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        # Get recent activity
        recent_sessions = db.query(StudySession).filter(
            StudySession.user_id == current_user.id
        ).order_by(StudySession.start_time.desc()).limit(5).all()
        
        # Calculate streak
        current_streak = 0
        current_date = end_date.date()
        
        # Check for consecutive days with study sessions
        while True:
            had_session = db.query(StudySession).filter(
                StudySession.user_id == current_user.id,
                StudySession.start_time >= datetime.combine(current_date, datetime.min.time()),
                StudySession.start_time < datetime.combine(current_date + timedelta(days=1), datetime.min.time())
            ).first() is not None
            
            if had_session:
                current_streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return {
            "total_sessions": total_sessions,
            "total_study_time_seconds": total_study_time,
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "accuracy": accuracy,
            "current_streak_days": current_streak,
            "recent_sessions": [
                {
                    "id": s.id,
                    "session_type": s.session_type,
                    "start_time": s.start_time,
                    "duration_seconds": s.duration_seconds,
                    "correct_answers": s.correct_answers,
                    "total_items": s.total_items
                } for s in recent_sessions
            ]
        }
        
    except Exception as e:
        logging.error(f"Error getting progress overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get progress overview"
        )

@router.get("/weak-areas", response_model=List[WeakArea])
async def get_weak_areas(
    limit: int = 5,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the user's weak areas based on study performance
    
    Args:
        limit: Maximum number of weak areas to return (default: 5)
        days: Number of days to look back for weak areas (default: 30)
        
    Returns:
        List[WeakArea]: List of weak areas with performance metrics
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all topics the user has studied
        topics = db.query(Topic).filter(
            Topic.owner_id == current_user.id
        ).all()
        
        weak_areas = []
        
        # Analyze performance by topic
        for topic in topics:
            # Get all session items for this topic
            items = db.query(StudySessionItem).join(
                StudySession,
                StudySessionItem.session_id == StudySession.id
            ).filter(
                StudySession.user_id == current_user.id,
                StudySession.topic_id == topic.id,
                StudySession.start_time >= start_date
            ).all()
            
            if not items:
                continue
                
            # Calculate performance metrics
            total = len(items)
            correct = sum(1 for i in items if i.is_correct)
            accuracy = (correct / total * 100) if total > 0 else 0
            
            # Only include areas with accuracy < 70%
            if accuracy < 70:
                weak_areas.append({
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "total_attempts": total,
                    "correct_attempts": correct,
                    "accuracy": accuracy,
                    "last_studied": max(i.session.start_time for i in items if i.session)
                })
        
        # Sort by accuracy (lowest first) and limit results
        weak_areas.sort(key=lambda x: x["accuracy"])
        return weak_areas[:limit]
        
    except Exception as e:
        logging.error(f"Error identifying weak areas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to identify weak areas"
        )
