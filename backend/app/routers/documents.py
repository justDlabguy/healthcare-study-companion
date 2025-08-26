from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import asyncio
import logging
from datetime import datetime

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..models import User, DocumentStatus
from ..services.document_processor import document_processor

router = APIRouter(prefix="/topics/{topic_id}/documents", tags=["documents"])

# Configure upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


async def process_document_background(document_id: int):
    """Background task to process document asynchronously."""
    try:
        # Get a new database session for the background task
        from ..database import SessionLocal
        db = SessionLocal()
        
        try:
            await document_processor.process_document_with_embeddings(document_id, db)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {str(e)}")

@router.post("/", response_model=schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    topic_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document to a topic.
    
    - **topic_id**: ID of the topic to add the document to
    - **file**: The document file to upload (PDF, DOCX, or TXT)
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
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported"
        )
    
    # Create document record first to get the ID
    db_document = models.Document(
        topic_id=topic_id,
        filename=file.filename,
        content_type=file.content_type,
        file_size=0,  # Will be updated after saving
        status=DocumentStatus.UPLOADED,
        file_metadata={"original_filename": file.filename}
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Use document ID for filename to ensure uniqueness
    filename = f"{db_document.id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Update document with file size
        db_document.file_size = len(contents)
        db.commit()
        
    except Exception as e:
        # Clean up document record if file save fails
        db.delete(db_document)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Start async processing of document in background
    background_tasks.add_task(process_document_background, db_document.id)
    
    logger.info(f"Document {db_document.id} uploaded and queued for processing")
    
    return db_document

@router.get("/", response_model=List[schemas.DocumentOut])
def list_documents(
    topic_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all documents for a topic."""
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
    
    return db.query(models.Document)\
        .filter(models.Document.topic_id == topic_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

@router.get("/{document_id}", response_model=schemas.DocumentOut)
def get_document(
    topic_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document details."""
    document = db.query(models.Document)\
        .join(models.Topic)\
        .filter(
            models.Document.id == document_id,
            models.Topic.owner_id == current_user.id
        )\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    return document


@router.post("/{document_id}/reprocess", response_model=schemas.DocumentOut)
async def reprocess_document(
    topic_id: int,
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprocess a document (re-extract text, re-chunk, and regenerate embeddings)."""
    # Verify document exists and user has access
    document = db.query(models.Document)\
        .join(models.Topic)\
        .filter(
            models.Document.id == document_id,
            models.Topic.owner_id == current_user.id
        )\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    # Reset document status
    document.status = DocumentStatus.UPLOADED
    document.error_message = None
    db.commit()
    
    # Start reprocessing in background
    background_tasks.add_task(process_document_background, document_id)
    
    logger.info(f"Document {document_id} queued for reprocessing")
    
    return document


@router.get("/{document_id}/chunks", response_model=List[schemas.DocumentChunkOut])
def get_document_chunks(
    topic_id: int,
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chunks for a document."""
    # Verify document exists and user has access
    document = db.query(models.Document)\
        .join(models.Topic)\
        .filter(
            models.Document.id == document_id,
            models.Topic.owner_id == current_user.id
        )\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    chunks = db.query(models.DocumentChunk)\
        .filter(models.DocumentChunk.document_id == document_id)\
        .order_by(models.DocumentChunk.chunk_index)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return chunks


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    topic_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document and its associated chunks."""
    # Verify document exists and user has access
    document = db.query(models.Document)\
        .join(models.Topic)\
        .filter(
            models.Document.id == document_id,
            models.Topic.owner_id == current_user.id
        )\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    # Delete associated file
    try:
        file_ext = os.path.splitext(document.filename)[1].lower()
        file_path = os.path.join(UPLOAD_DIR, f"{document_id}{file_ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Could not delete file for document {document_id}: {str(e)}")
    
    # Delete document (chunks will be deleted via cascade)
    db.delete(document)
    db.commit()
    
    logger.info(f"Document {document_id} deleted")
    
    return None
