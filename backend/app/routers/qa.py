import logging
import traceback
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..models import User, Topic, QAHistory
from ..services.vector_search import VectorSearchService
from ..services.llm_service import LLMService, LLMRequest

router = APIRouter(prefix="/topics/{topic_id}/qa", tags=["qa"])
logger = logging.getLogger(__name__)

# Initialize services
vector_search_service = VectorSearchService()
llm_service = LLMService()

@router.post("/ask", response_model=schemas.QAAnswer)
async def ask_question(
    topic_id: int,
    question: schemas.QAQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question about a topic and get an AI-generated answer.
    
    This endpoint uses vector search to find relevant context from uploaded documents
    and then generates an answer using an LLM with that context.
    """
    # Verify topic exists and user has access
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.owner_id == current_user.id  # Only topic owner can ask questions
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    try:
        # Get relevant context using vector search
        logger.info(f"Retrieving context for question: {question.question[:100]}...")
        search_results, context = await vector_search_service.get_relevant_context(
            db=db,
            query=question.question,
            topic_id=topic_id,
            max_chunks=5,
            max_context_length=2000
        )
        
        # Prepare the prompt with context
        if context:
            prompt = f"""Based on the following context from the user's study materials, please answer the question.

Context:
{context}

Question: {question.question}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing."""
        else:
            prompt = f"""The user has asked a question about their study topic "{topic.title}", but no relevant context was found in their uploaded documents.

Question: {question.question}

Please provide a helpful response indicating that no relevant information was found in their documents and suggest they might need to upload more relevant materials or rephrase their question."""
        
        # Add user-provided context if available
        if question.context:
            prompt += f"\n\nAdditional context from user: {question.context}"
        
        # Generate answer using LLM
        logger.info("Generating answer using LLM...")
        llm_request = LLMRequest(
            prompt=prompt,
            temperature=question.temperature,
            max_tokens=1000
        )
        
        llm_response = await llm_service.generate_text(llm_request)
        
        # Calculate confidence based on context availability and search results
        confidence = 0.9 if context else 0.3
        if search_results:
            # Adjust confidence based on search result scores
            avg_score = sum(result.score for result in search_results) / len(search_results)
            confidence = min(0.95, confidence * (0.5 + avg_score))
        
        # Prepare sources information
        sources = []
        for result in search_results:
            sources.append({
                "document_id": result.document.id,
                "document_filename": result.document.filename,
                "chunk_id": result.chunk.id,
                "relevance_score": result.score,
                "snippet": result.snippet
            })
        
        # Create QA history record
        qa_history = models.QAHistory(
            topic_id=topic_id,
            user_id=current_user.id,
            question=question.question,
            answer=llm_response.text,
            qa_metadata={
                "model": llm_response.model,
                "temperature": question.temperature,
                "context_length": len(context),
                "num_sources": len(sources),
                "tokens_used": llm_response.usage.get("total_tokens", 0),
                "sources": sources
            },
            score=confidence
        )
        
        db.add(qa_history)
        db.commit()
        db.refresh(qa_history)
        
        logger.info(f"Generated answer with {len(sources)} sources and confidence {confidence:.2f}")
        
        # Return the answer
        return schemas.QAAnswer(
            answer=llm_response.text,
            confidence=confidence,
            sources=sources,
            model=llm_response.model,
            tokens_used=llm_response.usage.get("total_tokens", 0)
        )
    
    except Exception as e:
        logger.error(f"Error generating answer for question: {str(e)}")
        
        # Fallback response
        fallback_answer = f"I apologize, but I encountered an error while processing your question. Please try again or rephrase your question."
        
        # Still create a history record for the attempt
        qa_history = models.QAHistory(
            topic_id=topic_id,
            user_id=current_user.id,
            question=question.question,
            answer=fallback_answer,
            qa_metadata={
                "error": str(e),
                "model": "error-fallback",
                "temperature": question.temperature
            },
            score=0.0
        )
        
        db.add(qa_history)
        db.commit()
        
        return schemas.QAAnswer(
            answer=fallback_answer,
            confidence=0.0,
            sources=[],
            model="error-fallback",
            tokens_used=0
        )

@router.get("/history", response_model=schemas.QAHistoryResponse)
async def get_qa_history(
    topic_id: int,
    skip: int = 0,
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the Q&A history for a topic.
    """
    # Verify topic exists and user has access
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.owner_id == current_user.id  # Only topic owner can view history
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    # Get total count and paginated results
    total = db.query(QAHistory).filter(QAHistory.topic_id == topic_id).count()
    history = db.query(QAHistory)\
        .filter(QAHistory.topic_id == topic_id)\
        .order_by(QAHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Convert to response model
    items = []
    for item in history:
        items.append(
            schemas.QAHistoryItem(
                id=item.id,
                topic_id=item.topic_id,
                question=item.question,
                answer=item.answer,
                confidence=item.score or 0.0,
                created_at=item.created_at,
                tokens_used=item.qa_metadata.get("tokens_used", 0) if item.qa_metadata else 0,
                model=item.qa_metadata.get("model", "unknown") if item.qa_metadata else "unknown",
                metadata=item.qa_metadata
            )
        )
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@router.delete("/history/{qa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qa_history_item(
    topic_id: int,
    qa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific Q&A history item.
    
    This operation is permanent and cannot be undone.
    """
    logger.info(f"Deleting Q&A history item {qa_id} for topic {topic_id} and user {current_user.id}")
    
    # Verify topic exists and user has access
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        logger.warning(f"Topic {topic_id} not found or access denied for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    # Find the Q&A history item
    qa_item = db.query(QAHistory).filter(
        QAHistory.id == qa_id,
        QAHistory.topic_id == topic_id
    ).first()
    
    if not qa_item:
        logger.warning(f"Q&A history item {qa_id} not found for topic {topic_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Q&A history item not found"
        )
    
    try:
        # Delete the Q&A history item
        db.delete(qa_item)
        db.commit()
        logger.info(f"Successfully deleted Q&A history item {qa_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to delete Q&A history item {qa_id}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Q&A history item"
        )

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_qa_history(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all Q&A history for a topic.
    
    This operation is permanent and cannot be undone.
    """
    logger.info(f"Deleting all Q&A history for topic {topic_id} by user {current_user.id}")
    
    # Verify topic exists and user has access
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.owner_id == current_user.id
    ).first()
    
    if not topic:
        logger.warning(f"Topic {topic_id} not found or access denied for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
    
    try:
        # Delete all Q&A history for the topic
        deleted_count = db.query(QAHistory).filter(
            QAHistory.topic_id == topic_id
        ).delete(synchronize_session=False)
        
        db.commit()
        logger.info(f"Successfully deleted {deleted_count} Q&A history items for topic {topic_id}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to delete Q&A history for topic {topic_id}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Q&A history"
        )
