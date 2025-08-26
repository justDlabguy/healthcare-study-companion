"""
Flashcard Generation Service

This service generates flashcards from document content using LLM APIs.
Supports different flashcard types: basic, cloze, and multiple choice.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import re

from ..services.llm_service import LLMService, LLMRequest
from ..models import Document, DocumentChunk, Flashcard
from ..core.exceptions import LLMError

logger = logging.getLogger(__name__)

class FlashcardType(str, Enum):
    BASIC = "basic"
    CLOZE = "cloze"
    MULTIPLE_CHOICE = "multiple_choice"

class GeneratedFlashcard:
    """Represents a generated flashcard before database storage."""
    
    def __init__(
        self, 
        front: str, 
        back: str, 
        card_type: FlashcardType = FlashcardType.BASIC,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.front = front
        self.back = back
        self.card_type = card_type
        self.metadata = metadata or {}

class FlashcardGeneratorService:
    """Service for generating flashcards from document content using AI."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
    
    async def generate_flashcards_from_content(
        self,
        content: str,
        num_cards: int = 5,
        card_type: FlashcardType = FlashcardType.BASIC,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """
        Generate flashcards from text content.
        
        Args:
            content: The text content to generate flashcards from
            num_cards: Number of flashcards to generate
            card_type: Type of flashcards to generate
            topic_context: Additional context about the topic
            
        Returns:
            List of GeneratedFlashcard objects
        """
        try:
            if card_type == FlashcardType.BASIC:
                return await self._generate_basic_flashcards(content, num_cards, topic_context)
            elif card_type == FlashcardType.CLOZE:
                return await self._generate_cloze_flashcards(content, num_cards, topic_context)
            elif card_type == FlashcardType.MULTIPLE_CHOICE:
                return await self._generate_multiple_choice_flashcards(content, num_cards, topic_context)
            else:
                raise ValueError(f"Unsupported flashcard type: {card_type}")
                
        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise LLMError(f"Failed to generate flashcards: {str(e)}")
    
    async def generate_flashcards_from_documents(
        self,
        documents: List[Document],
        num_cards: int = 5,
        card_type: FlashcardType = FlashcardType.BASIC,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """
        Generate flashcards from multiple documents.
        
        Args:
            documents: List of documents to generate flashcards from
            num_cards: Number of flashcards to generate
            card_type: Type of flashcards to generate
            topic_context: Additional context about the topic
            
        Returns:
            List of GeneratedFlashcard objects
        """
        # Combine text from all processed documents
        combined_text = ""
        for doc in documents:
            if doc.status == "processed" and doc.text:
                combined_text += f"\n\n--- {doc.filename} ---\n{doc.text}"
        
        if not combined_text.strip():
            raise ValueError("No processed document content available for flashcard generation")
        
        # Limit content length to avoid token limits
        max_content_length = 8000  # Adjust based on model limits
        if len(combined_text) > max_content_length:
            combined_text = combined_text[:max_content_length] + "..."
        
        return await self.generate_flashcards_from_content(
            combined_text, num_cards, card_type, topic_context
        )
    
    async def _generate_basic_flashcards(
        self, 
        content: str, 
        num_cards: int,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """Generate basic question-answer flashcards."""
        
        context_prompt = f"Topic context: {topic_context}\n\n" if topic_context else ""
        
        prompt = f"""{context_prompt}Based on the following content, generate {num_cards} high-quality flashcards in JSON format. Each flashcard should have a clear question on the front and a comprehensive answer on the back.

Content:
{content}

Please generate flashcards that:
1. Focus on key concepts, definitions, and important facts
2. Have clear, specific questions
3. Provide comprehensive but concise answers
4. Cover different aspects of the content
5. Are suitable for medical/healthcare study

Return the flashcards as a JSON array with this exact format:
[
  {{
    "front": "Question text here",
    "back": "Answer text here"
  }},
  ...
]

Only return the JSON array, no additional text."""

        request = LLMRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        response = await self.llm_service.generate_text(request)
        return self._parse_flashcard_response(response.text, FlashcardType.BASIC)
    
    async def _generate_cloze_flashcards(
        self, 
        content: str, 
        num_cards: int,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """Generate cloze deletion flashcards."""
        
        context_prompt = f"Topic context: {topic_context}\n\n" if topic_context else ""
        
        prompt = f"""{context_prompt}Based on the following content, generate {num_cards} cloze deletion flashcards in JSON format. Cloze cards have a statement with a key term or phrase replaced by [...], and the answer is the missing term/phrase.

Content:
{content}

Please generate cloze flashcards that:
1. Focus on key terms, definitions, and important concepts
2. Replace the most important word or phrase with [...]
3. Provide the missing term/phrase as the answer
4. Create meaningful learning opportunities
5. Are suitable for medical/healthcare study

Return the flashcards as a JSON array with this exact format:
[
  {{
    "front": "Statement with [...] replacing key term",
    "back": "The missing term or phrase"
  }},
  ...
]

Only return the JSON array, no additional text."""

        request = LLMRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        response = await self.llm_service.generate_text(request)
        return self._parse_flashcard_response(response.text, FlashcardType.CLOZE)
    
    async def _generate_multiple_choice_flashcards(
        self, 
        content: str, 
        num_cards: int,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """Generate multiple choice flashcards."""
        
        context_prompt = f"Topic context: {topic_context}\n\n" if topic_context else ""
        
        prompt = f"""{context_prompt}Based on the following content, generate {num_cards} multiple choice flashcards in JSON format. Each card should have a question and 4 answer choices (A, B, C, D) with one correct answer.

Content:
{content}

Please generate multiple choice flashcards that:
1. Focus on key concepts and important facts
2. Have clear, specific questions
3. Provide 4 plausible answer choices
4. Have one clearly correct answer
5. Are suitable for medical/healthcare study

Return the flashcards as a JSON array with this exact format:
[
  {{
    "front": "Question text\\n\\nA) Option A\\nB) Option B\\nC) Option C\\nD) Option D",
    "back": "Correct answer: X) [Explanation of why this is correct]"
  }},
  ...
]

Only return the JSON array, no additional text."""

        request = LLMRequest(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2500
        )
        
        response = await self.llm_service.generate_text(request)
        return self._parse_flashcard_response(response.text, FlashcardType.MULTIPLE_CHOICE)
    
    def _parse_flashcard_response(self, response_text: str, card_type: FlashcardType) -> List[GeneratedFlashcard]:
        """Parse the LLM response and extract flashcards."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            # Parse JSON
            flashcard_data = json.loads(json_text)
            
            if not isinstance(flashcard_data, list):
                raise ValueError("Response is not a JSON array")
            
            flashcards = []
            for item in flashcard_data:
                if not isinstance(item, dict) or 'front' not in item or 'back' not in item:
                    logger.warning(f"Skipping invalid flashcard item: {item}")
                    continue
                
                flashcard = GeneratedFlashcard(
                    front=item['front'].strip(),
                    back=item['back'].strip(),
                    card_type=card_type,
                    metadata={'generated_by': 'ai', 'card_type': card_type.value}
                )
                flashcards.append(flashcard)
            
            if not flashcards:
                raise ValueError("No valid flashcards found in response")
            
            return flashcards
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise LLMError("Failed to parse flashcard generation response")
        except Exception as e:
            logger.error(f"Error parsing flashcard response: {e}")
            raise LLMError(f"Failed to process flashcard generation: {str(e)}")

# Create a singleton instance
flashcard_generator = FlashcardGeneratorService()