"""
Vector search service for semantic search across document chunks.

This service provides similarity search functionality using document chunk embeddings
to find relevant content based on semantic similarity rather than keyword matching.
"""

import logging
import math
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text

from ..models import DocumentChunk, Document, Topic
from ..services.embeddings import EmbeddingsClient

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result with relevance score and metadata."""
    chunk: DocumentChunk
    document: Document
    score: float
    snippet: str  # Highlighted text snippet
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary for API responses."""
        return {
            "chunk_id": self.chunk.id,
            "document_id": self.document.id,
            "document_filename": self.document.filename,
            "score": self.score,
            "snippet": self.snippet,
            "text": self.chunk.text,
            "chunk_index": self.chunk.chunk_index,
            "chunk_metadata": self.chunk.chunk_metadata or {}
        }


class VectorSearchService:
    """Service for performing vector similarity search on document chunks."""
    
    def __init__(self, embeddings_client: Optional[EmbeddingsClient] = None):
        self.embeddings_client = embeddings_client or EmbeddingsClient()
    
    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        # Avoid division by zero
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def create_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """
        Create a text snippet highlighting relevant parts.
        
        Args:
            text: Full text content
            query: Search query for context
            max_length: Maximum snippet length
            
        Returns:
            Text snippet with ellipsis if truncated
        """
        if len(text) <= max_length:
            return text
        
        # Try to find query terms in the text for better snippets
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # Find the best position to start the snippet
        best_pos = 0
        max_matches = 0
        
        for i in range(0, len(text) - max_length + 1, 50):
            snippet_text = text_lower[i:i + max_length]
            matches = sum(1 for word in query_words if word in snippet_text)
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        # Create snippet
        snippet = text[best_pos:best_pos + max_length]
        
        # Add ellipsis if needed
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_length < len(text):
            snippet = snippet + "..."
        
        return snippet.strip()
    
    async def search(
        self,
        db: Session,
        query: str,
        topic_id: int,
        limit: int = 10,
        min_score: float = 0.1,
        document_ids: Optional[List[int]] = None
    ) -> List[SearchResult]:
        """
        Perform vector similarity search on document chunks.
        
        Args:
            db: Database session
            query: Search query text
            topic_id: ID of the topic to search within
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold
            document_ids: Optional list of document IDs to restrict search to
            
        Returns:
            List of search results ordered by relevance score
        """
        try:
            # Generate embedding for the query
            logger.info(f"Generating embedding for query: {query[:100]}...")
            query_embeddings = await self.embeddings_client.embed_texts([query])
            
            if not query_embeddings or not query_embeddings[0]:
                logger.warning("Failed to generate query embedding")
                return []
            
            query_embedding = query_embeddings[0]
            
            # Build the base query to get chunks with embeddings
            base_query = db.query(DocumentChunk, Document).join(
                Document, DocumentChunk.document_id == Document.id
            ).filter(
                and_(
                    Document.topic_id == topic_id,
                    DocumentChunk.embedding.isnot(None)
                )
            )
            
            # Filter by specific documents if provided
            if document_ids:
                base_query = base_query.filter(Document.id.in_(document_ids))
            
            # Get all chunks with embeddings
            chunks_with_docs = base_query.all()
            
            if not chunks_with_docs:
                logger.info(f"No chunks with embeddings found for topic {topic_id}")
                return []
            
            # Calculate similarity scores
            results = []
            for chunk, document in chunks_with_docs:
                try:
                    # Parse embedding from JSON
                    chunk_embedding = chunk.embedding
                    if not chunk_embedding:
                        continue
                    
                    # Calculate similarity
                    similarity = self.calculate_cosine_similarity(query_embedding, chunk_embedding)
                    
                    # Filter by minimum score
                    if similarity >= min_score:
                        snippet = self.create_snippet(chunk.text, query)
                        results.append(SearchResult(
                            chunk=chunk,
                            document=document,
                            score=similarity,
                            snippet=snippet
                        ))
                
                except Exception as e:
                    logger.warning(f"Error processing chunk {chunk.id}: {str(e)}")
                    continue
            
            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:limit]
            
            logger.info(f"Found {len(results)} search results for query in topic {topic_id}")
            return results
        
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            raise
    
    async def search_across_topics(
        self,
        db: Session,
        query: str,
        user_id: int,
        limit: int = 10,
        min_score: float = 0.1,
        topic_ids: Optional[List[int]] = None
    ) -> Dict[int, List[SearchResult]]:
        """
        Perform vector search across multiple topics for a user.
        
        Args:
            db: Database session
            query: Search query text
            user_id: ID of the user performing the search
            limit: Maximum number of results per topic
            min_score: Minimum similarity score threshold
            topic_ids: Optional list of topic IDs to restrict search to
            
        Returns:
            Dictionary mapping topic IDs to their search results
        """
        try:
            # Get user's topics
            topics_query = db.query(Topic).filter(Topic.owner_id == user_id)
            
            if topic_ids:
                topics_query = topics_query.filter(Topic.id.in_(topic_ids))
            
            topics = topics_query.all()
            
            if not topics:
                logger.info(f"No topics found for user {user_id}")
                return {}
            
            # Search within each topic
            results_by_topic = {}
            for topic in topics:
                topic_results = await self.search(
                    db=db,
                    query=query,
                    topic_id=topic.id,
                    limit=limit,
                    min_score=min_score
                )
                
                if topic_results:
                    results_by_topic[topic.id] = topic_results
            
            logger.info(f"Search across {len(topics)} topics returned results for {len(results_by_topic)} topics")
            return results_by_topic
        
        except Exception as e:
            logger.error(f"Error performing cross-topic search: {str(e)}")
            raise
    
    async def get_relevant_context(
        self,
        db: Session,
        query: str,
        topic_id: int,
        max_chunks: int = 5,
        max_context_length: int = 2000
    ) -> Tuple[List[SearchResult], str]:
        """
        Get relevant context for a query, optimized for Q&A systems.
        
        Args:
            db: Database session
            query: Query text
            topic_id: Topic ID to search within
            max_chunks: Maximum number of chunks to include
            max_context_length: Maximum total context length
            
        Returns:
            Tuple of (search results, combined context text)
        """
        try:
            # Search for relevant chunks
            search_results = await self.search(
                db=db,
                query=query,
                topic_id=topic_id,
                limit=max_chunks,
                min_score=0.2  # Higher threshold for Q&A context
            )
            
            if not search_results:
                return [], ""
            
            # Combine context from top results
            context_parts = []
            total_length = 0
            
            for result in search_results:
                chunk_text = result.chunk.text
                
                # Check if adding this chunk would exceed the limit
                if total_length + len(chunk_text) > max_context_length:
                    # Try to fit a truncated version
                    remaining_space = max_context_length - total_length
                    if remaining_space > 100:  # Only add if we have reasonable space
                        chunk_text = chunk_text[:remaining_space - 3] + "..."
                        context_parts.append(f"Source: {result.document.filename}\n{chunk_text}")
                    break
                
                context_parts.append(f"Source: {result.document.filename}\n{chunk_text}")
                total_length += len(chunk_text) + len(result.document.filename) + 10  # Account for formatting
            
            combined_context = "\n\n".join(context_parts)
            
            logger.info(f"Generated context with {len(search_results)} chunks, {len(combined_context)} characters")
            return search_results, combined_context
        
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return [], ""