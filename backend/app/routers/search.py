"""
Search API endpoints for vector similarity search across documents.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_db, get_current_user
from ..models import User, Topic
from ..services.vector_search import VectorSearchService

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)

# Initialize vector search service
vector_search_service = VectorSearchService()


class SearchQuery(schemas.BaseModel):
    """Schema for search query parameters."""
    query: str = schemas.Field(..., min_length=1, max_length=500, description="Search query text")
    min_score: float = schemas.Field(0.1, ge=0.0, le=1.0, description="Minimum similarity score threshold")
    document_ids: Optional[List[int]] = schemas.Field(None, description="Optional list of document IDs to search within")


class SearchResultSchema(schemas.BaseModel):
    """Schema for individual search result."""
    chunk_id: int
    document_id: int
    document_filename: str
    score: float
    snippet: str
    text: str
    chunk_index: int
    chunk_metadata: Dict[str, Any] = {}


class SearchResponse(schemas.BaseModel):
    """Schema for search response."""
    results: List[SearchResultSchema]
    total: int
    query: str
    topic_id: Optional[int] = None
    execution_time_ms: Optional[float] = None


class CrossTopicSearchResponse(schemas.BaseModel):
    """Schema for cross-topic search response."""
    results_by_topic: Dict[int, List[SearchResultSchema]]
    total_results: int
    query: str
    execution_time_ms: Optional[float] = None


@router.post("/topics/{topic_id}", response_model=SearchResponse)
async def search_within_topic(
    topic_id: int,
    search_query: SearchQuery,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform vector similarity search within a specific topic.
    
    This endpoint searches through all document chunks within a topic using
    semantic similarity to find the most relevant content for the given query.
    """
    import time
    start_time = time.time()
    
    try:
        # Verify topic exists and user has access
        topic = db.query(Topic).filter(
            Topic.id == topic_id,
            Topic.owner_id == current_user.id
        ).first()
        
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found or access denied"
            )
        
        # Perform the search
        search_results = await vector_search_service.search(
            db=db,
            query=search_query.query,
            topic_id=topic_id,
            limit=limit,
            min_score=search_query.min_score,
            document_ids=search_query.document_ids
        )
        
        # Convert results to response schema
        result_schemas = [
            SearchResultSchema(**result.to_dict())
            for result in search_results
        ]
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        logger.info(f"Search in topic {topic_id} returned {len(result_schemas)} results in {execution_time:.2f}ms")
        
        return SearchResponse(
            results=result_schemas,
            total=len(result_schemas),
            query=search_query.query,
            topic_id=topic_id,
            execution_time_ms=execution_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing search in topic {topic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while performing the search"
        )


@router.post("/", response_model=CrossTopicSearchResponse)
async def search_across_topics(
    search_query: SearchQuery,
    limit_per_topic: int = Query(5, ge=1, le=20, description="Maximum number of results per topic"),
    topic_ids: Optional[List[int]] = Query(None, description="Optional list of topic IDs to search within"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform vector similarity search across multiple topics owned by the user.
    
    This endpoint searches through all accessible topics (or a specified subset)
    and returns results grouped by topic.
    """
    import time
    start_time = time.time()
    
    try:
        # Perform cross-topic search
        results_by_topic = await vector_search_service.search_across_topics(
            db=db,
            query=search_query.query,
            user_id=current_user.id,
            limit=limit_per_topic,
            min_score=search_query.min_score,
            topic_ids=topic_ids
        )
        
        # Convert results to response schema
        response_results = {}
        total_results = 0
        
        for topic_id, search_results in results_by_topic.items():
            result_schemas = [
                SearchResultSchema(**result.to_dict())
                for result in search_results
            ]
            response_results[topic_id] = result_schemas
            total_results += len(result_schemas)
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        logger.info(f"Cross-topic search returned {total_results} results across {len(response_results)} topics in {execution_time:.2f}ms")
        
        return CrossTopicSearchResponse(
            results_by_topic=response_results,
            total_results=total_results,
            query=search_query.query,
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        logger.error(f"Error performing cross-topic search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while performing the search"
        )


@router.get("/topics/{topic_id}/context", response_model=Dict[str, Any])
async def get_search_context(
    topic_id: int,
    query: str = Query(..., min_length=1, max_length=500, description="Query to find relevant context for"),
    max_chunks: int = Query(5, ge=1, le=10, description="Maximum number of chunks to include in context"),
    max_length: int = Query(2000, ge=500, le=5000, description="Maximum total context length"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get relevant context for a query, optimized for Q&A systems.
    
    This endpoint is designed to provide context for AI question-answering
    by finding the most relevant document chunks and combining them into
    a coherent context string.
    """
    try:
        # Verify topic exists and user has access
        topic = db.query(Topic).filter(
            Topic.id == topic_id,
            Topic.owner_id == current_user.id
        ).first()
        
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found or access denied"
            )
        
        # Get relevant context
        search_results, combined_context = await vector_search_service.get_relevant_context(
            db=db,
            query=query,
            topic_id=topic_id,
            max_chunks=max_chunks,
            max_context_length=max_length
        )
        
        # Convert search results to response format
        result_schemas = [
            SearchResultSchema(**result.to_dict())
            for result in search_results
        ]
        
        return {
            "query": query,
            "context": combined_context,
            "sources": result_schemas,
            "context_length": len(combined_context),
            "num_sources": len(result_schemas)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search context for topic {topic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting search context"
        )