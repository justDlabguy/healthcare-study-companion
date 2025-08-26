"""
Document processing service for text extraction, chunking, and embedding generation.
"""
import asyncio
import logging
import os
import re
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import json

import PyPDF2
import fitz  # pymupdf
from sqlalchemy.orm import Session

from ..models import Document, DocumentChunk, DocumentStatus
from ..database import get_db
from .embeddings import EmbeddingsClient

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing documents: text extraction, chunking, and embedding generation."""
    
    def __init__(self, 
                 embeddings_client: Optional[EmbeddingsClient] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        self.embeddings_client = embeddings_client or EmbeddingsClient()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using async processing.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If text extraction fails
        """
        try:
            # Run PDF processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._extract_pdf_text_sync, file_path)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_pdf_text_sync(self, file_path: str) -> str:
        """
        Synchronous PDF text extraction using both pymupdf (fitz) and PyPDF2 for better coverage.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_content = []
        
        try:
            # First try with pymupdf (fitz) - better for complex layouts
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text and page_text.strip():
                        text_content.append(f"[Page {page_num + 1}]\n{page_text.strip()}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1} with pymupdf: {str(e)}")
                    continue
            
            doc.close()
            
            if text_content:
                return "\n\n".join(text_content)
            
            # Fallback to PyPDF2 if pymupdf fails
            logger.info(f"Falling back to PyPDF2 for {file_path}")
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content.append(f"[Page {page_num}]\n{page_text.strip()}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num} with PyPDF2: {str(e)}")
                        continue
            
            if not text_content:
                raise Exception("No text could be extracted from the PDF")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error in PDF text extraction: {str(e)}")
            raise
    
    async def extract_text_from_file(self, file_path: str, content_type: Optional[str] = None) -> str:
        """
        Extract text from various file formats.
        
        Args:
            file_path: Path to the file
            content_type: MIME type of the file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If text extraction fails or format is unsupported
        """
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf' or (content_type and 'pdf' in content_type):
                return await self.extract_text_from_pdf(file_path)
            
            elif file_ext == '.txt' or (content_type and 'text/plain' in content_type):
                # Handle text files with different encodings
                encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
                
                for encoding in encodings:
                    try:
                        loop = asyncio.get_event_loop()
                        text = await loop.run_in_executor(
                            None, 
                            self._read_text_file, 
                            file_path, 
                            encoding
                        )
                        return text
                    except UnicodeDecodeError:
                        continue
                
                raise Exception("Could not decode text file with any supported encoding")
            
            else:
                raise Exception(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _read_text_file(self, file_path: str, encoding: str) -> str:
        """Read text file with specified encoding."""
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    
    def chunk_text(self, text: str, document_id: int) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap and metadata.
        
        Args:
            text: The text content to chunk
            document_id: ID of the document being chunked
            
        Returns:
            List of chunk dictionaries with text, metadata, and index
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        
        # Split text into sentences for better chunking boundaries
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_chunk_sentences = []
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
                current_chunk_sentences.append(sentence)
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunk_metadata = self._extract_chunk_metadata(current_chunk, chunk_index)
                    chunks.append({
                        'text': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'metadata': chunk_metadata,
                        'document_id': document_id
                    })
                    chunk_index += 1
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences, 
                    self.chunk_overlap
                )
                current_chunk = " ".join(overlap_sentences + [sentence])
                current_chunk_sentences = overlap_sentences + [sentence]
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunk_metadata = self._extract_chunk_metadata(current_chunk, chunk_index)
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_index': chunk_index,
                'metadata': chunk_metadata,
                'document_id': document_id
            })
        
        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex patterns.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Handle page markers and clean up text
        text = re.sub(r'\[Page \d+\]\n', '\n', text)
        
        # Split on sentence boundaries (., !, ?) followed by whitespace and capital letter
        # Also handle common abbreviations
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences and filter out very short ones
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_overlap_sentences(self, sentences: List[str], overlap_chars: int) -> List[str]:
        """
        Get sentences for overlap based on character count.
        
        Args:
            sentences: List of sentences from previous chunk
            overlap_chars: Target number of characters for overlap
            
        Returns:
            List of sentences for overlap
        """
        if not sentences:
            return []
        
        overlap_sentences = []
        char_count = 0
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            if char_count + len(sentence) <= overlap_chars:
                overlap_sentences.insert(0, sentence)
                char_count += len(sentence)
            else:
                break
        
        return overlap_sentences
    
    def _extract_chunk_metadata(self, chunk_text: str, chunk_index: int) -> Dict[str, Any]:
        """
        Extract metadata from chunk text.
        
        Args:
            chunk_text: The chunk text
            chunk_index: Index of the chunk
            
        Returns:
            Dictionary with chunk metadata
        """
        metadata = {
            'chunk_index': chunk_index,
            'char_count': len(chunk_text),
            'word_count': len(chunk_text.split()),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Extract page numbers if present
        page_matches = re.findall(r'\[Page (\d+)\]', chunk_text)
        if page_matches:
            metadata['pages'] = [int(page) for page in page_matches]
            metadata['start_page'] = min(metadata['pages'])
            metadata['end_page'] = max(metadata['pages'])
        
        # Detect if chunk contains headers or special formatting
        lines = chunk_text.split('\n')
        headers = []
        for line in lines:
            line = line.strip()
            # Simple heuristic for headers (short lines, often capitalized)
            if len(line) < 100 and line.isupper() and len(line) > 5:
                headers.append(line)
        
        if headers:
            metadata['headers'] = headers
        
        return metadata
    
    async def create_document_chunks(self, document_id: int, text: str, db: Session) -> List[DocumentChunk]:
        """
        Create and store document chunks in the database.
        
        Args:
            document_id: ID of the document
            text: Text content to chunk
            db: Database session
            
        Returns:
            List of created DocumentChunk objects
        """
        try:
            # Delete existing chunks for this document
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            
            # Create new chunks
            chunk_data = self.chunk_text(text, document_id)
            
            db_chunks = []
            for chunk_info in chunk_data:
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_info['chunk_index'],
                    text=chunk_info['text'],
                    chunk_metadata=chunk_info['metadata']
                )
                db.add(db_chunk)
                db_chunks.append(db_chunk)
            
            db.commit()
            
            # Refresh all chunks to get their IDs
            for chunk in db_chunks:
                db.refresh(chunk)
            
            logger.info(f"Created {len(db_chunks)} chunks for document {document_id}")
            return db_chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks for document {document_id}: {str(e)}")
            db.rollback()
            raise
    
    async def generate_embeddings_for_chunks(self, chunks: List[DocumentChunk], db: Session) -> None:
        """
        Generate embeddings for document chunks and store them.
        
        Args:
            chunks: List of DocumentChunk objects
            db: Database session
        """
        if not chunks:
            return
        
        try:
            # Extract text from chunks for batch processing
            chunk_texts = [chunk.text for chunk in chunks]
            
            logger.info(f"Generating embeddings for {len(chunk_texts)} chunks")
            
            # Generate embeddings in batches to avoid API limits
            batch_size = 10  # Process 10 chunks at a time
            
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_texts = chunk_texts[i:i + batch_size]
                
                # Generate embeddings for this batch
                embeddings = await self.embeddings_client.embed_texts(batch_texts)
                
                # Store embeddings in database
                for chunk, embedding in zip(batch_chunks, embeddings):
                    chunk.embedding = embedding
                
                # Commit this batch
                db.commit()
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
                
                # Small delay to avoid rate limiting
                if i + batch_size < len(chunks):
                    await asyncio.sleep(0.5)
            
            logger.info(f"Successfully generated embeddings for all {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error generating embeddings for chunks: {str(e)}")
            db.rollback()
            raise
    
    async def process_document_with_embeddings(self, document_id: int, db: Session) -> None:
        """
        Complete document processing: extract text, chunk, and generate embeddings.
        
        Args:
            document_id: ID of the document to process
            db: Database session
        """
        try:
            # Get document from database
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return
            
            # Update status to processing
            document.status = DocumentStatus.PROCESSING
            db.commit()
            
            # Construct file path (assuming files are stored in uploads directory)
            file_path = os.path.join("uploads", f"{document_id}{Path(document.filename).suffix}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                # Try alternative path structure
                file_path = os.path.join("uploads", document.filename)
                if not os.path.exists(file_path):
                    raise Exception(f"File not found: {file_path}")
            
            # Extract text
            logger.info(f"Extracting text from document {document_id}")
            text_content = await self.extract_text_from_file(file_path, document.content_type)
            
            if not text_content or not text_content.strip():
                raise Exception("No text content extracted from document")
            
            # Store extracted text in document
            document.text = text_content
            db.commit()
            
            # Create chunks
            logger.info(f"Creating chunks for document {document_id}")
            chunks = await self.create_document_chunks(document_id, text_content, db)
            
            # Generate embeddings for chunks
            logger.info(f"Generating embeddings for document {document_id}")
            await self.generate_embeddings_for_chunks(chunks, db)
            
            # Update document status to processed
            document.status = DocumentStatus.PROCESSED
            document.processed_at = datetime.utcnow()
            document.error_message = None
            
            db.commit()
            logger.info(f"Successfully processed document {document_id} with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            
            # Update document status to error
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = DocumentStatus.ERROR
                    document.error_message = str(e)
                    db.commit()
            except Exception as db_error:
                logger.error(f"Error updating document status: {str(db_error)}")
    
    async def reprocess_document_embeddings(self, document_id: int, db: Session) -> None:
        """
        Regenerate embeddings for an existing processed document.
        
        Args:
            document_id: ID of the document to reprocess
            db: Database session
        """
        try:
            # Get document and its chunks
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise Exception(f"Document {document_id} not found")
            
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).order_by(DocumentChunk.chunk_index).all()
            
            if not chunks:
                raise Exception(f"No chunks found for document {document_id}")
            
            logger.info(f"Regenerating embeddings for {len(chunks)} chunks in document {document_id}")
            
            # Generate new embeddings
            await self.generate_embeddings_for_chunks(chunks, db)
            
            # Update document processed timestamp
            document.processed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Successfully regenerated embeddings for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error reprocessing embeddings for document {document_id}: {str(e)}")
            raise
    
# Create a singleton instance
document_processor = DocumentProcessor()