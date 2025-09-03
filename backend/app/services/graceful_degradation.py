"""
Graceful Degradation Service

This service provides fallback functionality when all LLM providers fail.
It includes mock flashcard generation, cached responses, and user-friendly error handling.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json
import hashlib
import time
from datetime import datetime, timedelta
import random
import re

from ..models import Document
from ..services.flashcard_types import GeneratedFlashcard, FlashcardType
from ..core.exceptions import LLMError

logger = logging.getLogger(__name__)

class DegradationMode(str, Enum):
    MOCK_GENERATION = "mock_generation"
    CACHED_RESPONSES = "cached_responses"
    TEMPLATE_BASED = "template_based"
    OFFLINE_MODE = "offline_mode"

class RecoveryAction(str, Enum):
    RETRY_LATER = "retry_later"
    USE_DIFFERENT_CONTENT = "use_different_content"
    CONTACT_SUPPORT = "contact_support"
    CHECK_NETWORK = "check_network"
    REDUCE_CONTENT_SIZE = "reduce_content_size"

class GracefulError:
    """Enhanced error with recovery suggestions and user-friendly messages."""
    
    def __init__(
        self,
        error_id: str,
        user_message: str,
        technical_message: str,
        recovery_actions: List[RecoveryAction],
        retry_after: Optional[int] = None,
        fallback_available: bool = True
    ):
        self.error_id = error_id
        self.user_message = user_message
        self.technical_message = technical_message
        self.recovery_actions = recovery_actions
        self.retry_after = retry_after
        self.fallback_available = fallback_available
        self.timestamp = datetime.utcnow()

class ResponseCache:
    """Simple in-memory cache for LLM responses."""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, content: str, num_cards: int, card_type: str) -> str:
        """Generate cache key from request parameters."""
        key_data = f"{content[:500]}-{num_cards}-{card_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, content: str, num_cards: int, card_type: str) -> Optional[List[GeneratedFlashcard]]:
        """Get cached response if available and not expired."""
        key = self._generate_key(content, num_cards, card_type)
        
        if key in self.cache:
            response, timestamp = self.cache[key]
            if datetime.utcnow() - timestamp < self.ttl:
                logger.info(f"Cache hit for key: {key[:8]}...")
                return response
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache entry expired for key: {key[:8]}...")
        
        return None
    
    def set(self, content: str, num_cards: int, card_type: str, response: List[GeneratedFlashcard]):
        """Cache a response."""
        key = self._generate_key(content, num_cards, card_type)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (response, datetime.utcnow())
        logger.debug(f"Cached response for key: {key[:8]}...")

class FlashcardTemplates:
    """Templates for generating fallback flashcards."""
    
    # Basic question-answer templates
    BASIC_TEMPLATES = [
        ("What is {concept}?", "Definition and explanation of {concept}"),
        ("Define {term}", "A {term} is..."),
        ("Explain {topic}", "Detailed explanation of {topic}"),
        ("What are the key features of {subject}?", "Key features include..."),
        ("How does {process} work?", "The process involves..."),
        ("What is the purpose of {item}?", "The purpose is to..."),
        ("List the components of {system}", "Components include..."),
        ("What are the benefits of {approach}?", "Benefits include..."),
    ]
    
    # Cloze deletion templates
    CLOZE_TEMPLATES = [
        ("{concept} is defined as [...]", "the definition"),
        ("The main function of {item} is [...]", "its primary purpose"),
        ("The process of {action} involves [...]", "the key steps"),
        ("{system} consists of [...] components", "the number/types"),
        ("The benefit of {approach} is [...]", "the main advantage"),
        ("In {context}, [...] is most important", "the key factor"),
    ]
    
    # Multiple choice templates
    MC_TEMPLATES = [
        ("What is the primary function of {concept}?", ["Correct answer", "Distractor 1", "Distractor 2", "Distractor 3"]),
        ("Which of the following best describes {term}?", ["Correct definition", "Incorrect option 1", "Incorrect option 2", "Incorrect option 3"]),
        ("What are the main components of {system}?", ["Correct components", "Partial list", "Incorrect components", "Unrelated items"]),
    ]

class GracefulDegradationService:
    """Service providing graceful degradation when LLM services fail."""
    
    def __init__(self):
        self.cache = ResponseCache()
        self.templates = FlashcardTemplates()
        self.degradation_stats = {
            "mock_generations": 0,
            "cache_hits": 0,
            "template_generations": 0,
            "total_fallbacks": 0
        }
    
    def create_graceful_error(
        self,
        original_error: Exception,
        context: str = "flashcard_generation"
    ) -> GracefulError:
        """Create a user-friendly error with recovery suggestions."""
        error_id = f"ERR_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Determine error type and create appropriate response
        if "authentication" in str(original_error).lower() or "api key" in str(original_error).lower():
            return GracefulError(
                error_id=error_id,
                user_message="We're having trouble connecting to our AI service. Don't worry - we can still help you create flashcards using our backup system!",
                technical_message=f"API authentication failed: {str(original_error)}",
                recovery_actions=[RecoveryAction.RETRY_LATER, RecoveryAction.CONTACT_SUPPORT],
                retry_after=300,  # 5 minutes
                fallback_available=True
            )
        elif "rate limit" in str(original_error).lower():
            return GracefulError(
                error_id=error_id,
                user_message="Our AI service is currently busy. We'll use our backup system to create your flashcards right away!",
                technical_message=f"Rate limit exceeded: {str(original_error)}",
                recovery_actions=[RecoveryAction.RETRY_LATER],
                retry_after=60,  # 1 minute
                fallback_available=True
            )
        elif "network" in str(original_error).lower() or "connection" in str(original_error).lower():
            return GracefulError(
                error_id=error_id,
                user_message="We're having network connectivity issues. Let's create your flashcards using our offline system!",
                technical_message=f"Network error: {str(original_error)}",
                recovery_actions=[RecoveryAction.CHECK_NETWORK, RecoveryAction.RETRY_LATER],
                retry_after=120,  # 2 minutes
                fallback_available=True
            )
        elif "token" in str(original_error).lower() or "length" in str(original_error).lower():
            return GracefulError(
                error_id=error_id,
                user_message="Your content is quite extensive! Try breaking it into smaller sections, or let us create flashcards using our template system.",
                technical_message=f"Content too long: {str(original_error)}",
                recovery_actions=[RecoveryAction.REDUCE_CONTENT_SIZE, RecoveryAction.USE_DIFFERENT_CONTENT],
                fallback_available=True
            )
        else:
            return GracefulError(
                error_id=error_id,
                user_message="We encountered an unexpected issue with our AI service. No problem - we'll create your flashcards using our reliable backup system!",
                technical_message=f"Unknown error: {str(original_error)}",
                recovery_actions=[RecoveryAction.RETRY_LATER, RecoveryAction.CONTACT_SUPPORT],
                retry_after=180,  # 3 minutes
                fallback_available=True
            )
    
    async def get_cached_response(
        self,
        content: str,
        num_cards: int,
        card_type: FlashcardType
    ) -> Optional[List[GeneratedFlashcard]]:
        """Try to get a cached response for similar content."""
        cached = self.cache.get(content, num_cards, card_type.value)
        if cached:
            self.degradation_stats["cache_hits"] += 1
            logger.info(f"Using cached response for {card_type.value} flashcards")
        return cached
    
    def cache_response(
        self,
        content: str,
        num_cards: int,
        card_type: FlashcardType,
        response: List[GeneratedFlashcard]
    ):
        """Cache a successful response for future use."""
        self.cache.set(content, num_cards, card_type.value, response)
    
    def extract_key_concepts(self, content: str, max_concepts: int = 20) -> List[str]:
        """Extract key concepts from content for template-based generation."""
        # Simple keyword extraction - in production, this could be more sophisticated
        content = content.lower()
        
        # Remove common words and extract potential concepts
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Extract words that might be concepts (2+ characters, not common words)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', content)
        concepts = []
        
        for word in words:
            if word.lower() not in common_words and len(word) > 2:
                if word not in concepts:  # Avoid duplicates
                    concepts.append(word)
                if len(concepts) >= max_concepts:
                    break
        
        # If we don't have enough concepts, add some generic ones
        if len(concepts) < 3:
            concepts.extend(['concept', 'process', 'system', 'method', 'approach'])
        
        return concepts[:max_concepts]
    
    async def generate_mock_flashcards(
        self,
        content: str,
        num_cards: int,
        card_type: FlashcardType,
        topic_context: Optional[str] = None
    ) -> List[GeneratedFlashcard]:
        """Generate mock flashcards using templates and content analysis."""
        self.degradation_stats["mock_generations"] += 1
        self.degradation_stats["total_fallbacks"] += 1
        
        logger.info(f"Generating {num_cards} mock {card_type.value} flashcards")
        
        # Extract key concepts from content
        concepts = self.extract_key_concepts(content, max_concepts=num_cards * 2)
        
        flashcards = []
        
        if card_type == FlashcardType.BASIC:
            flashcards = self._generate_mock_basic_cards(concepts, content, num_cards, topic_context)
        elif card_type == FlashcardType.CLOZE:
            flashcards = self._generate_mock_cloze_cards(concepts, content, num_cards, topic_context)
        elif card_type == FlashcardType.MULTIPLE_CHOICE:
            flashcards = self._generate_mock_mc_cards(concepts, content, num_cards, topic_context)
        
        # Add metadata indicating this is a mock generation
        for card in flashcards:
            card.metadata.update({
                'generated_by': 'mock_system',
                'degradation_mode': DegradationMode.MOCK_GENERATION.value,
                'generated_at': datetime.utcnow().isoformat(),
                'content_length': len(content),
                'concepts_used': len(concepts)
            })
        
        return flashcards
    
    def _generate_mock_basic_cards(
        self,
        concepts: List[str],
        content: str,
        num_cards: int,
        topic_context: Optional[str]
    ) -> List[GeneratedFlashcard]:
        """Generate mock basic flashcards."""
        flashcards = []
        templates = self.templates.BASIC_TEMPLATES
        
        for i in range(min(num_cards, len(concepts))):
            concept = concepts[i]
            template = templates[i % len(templates)]
            
            # Create question and answer from template
            front = template[0].format(
                concept=concept.title(),
                term=concept.title(),
                topic=concept.title(),
                subject=concept.title(),
                process=concept.title(),
                item=concept.title(),
                system=concept.title(),
                approach=concept.title()
            )
            
            back = template[1].format(
                concept=concept.title(),
                term=concept.title(),
                topic=concept.title(),
                subject=concept.title(),
                process=concept.title(),
                item=concept.title(),
                system=concept.title(),
                approach=concept.title()
            )
            
            # Try to extract relevant context from content
            context_snippet = self._extract_context_for_concept(content, concept)
            if context_snippet:
                back = f"{back}\n\nContext: {context_snippet}"
            
            flashcard = GeneratedFlashcard(
                front=front,
                back=back,
                card_type=FlashcardType.BASIC,
                metadata={'template_used': i % len(templates), 'concept': concept}
            )
            flashcards.append(flashcard)
        
        # If we need more cards than concepts, create generic ones
        while len(flashcards) < num_cards:
            generic_templates = [
                ("What is the main topic of this content?", f"The content discusses {topic_context or 'various concepts'}."),
                ("What are the key points covered?", "The key points include the main concepts and their relationships."),
                ("How can this information be applied?", "This information can be used for study and understanding of the subject matter."),
            ]
            
            template = generic_templates[len(flashcards) % len(generic_templates)]
            flashcard = GeneratedFlashcard(
                front=template[0],
                back=template[1],
                card_type=FlashcardType.BASIC,
                metadata={'template_used': 'generic', 'concept': 'general'}
            )
            flashcards.append(flashcard)
        
        return flashcards
    
    def _generate_mock_cloze_cards(
        self,
        concepts: List[str],
        content: str,
        num_cards: int,
        topic_context: Optional[str]
    ) -> List[GeneratedFlashcard]:
        """Generate mock cloze deletion flashcards."""
        flashcards = []
        templates = self.templates.CLOZE_TEMPLATES
        
        for i in range(min(num_cards, len(concepts))):
            concept = concepts[i]
            template = templates[i % len(templates)]
            
            front = template[0].format(
                concept=concept.title(),
                item=concept.title(),
                action=concept.title(),
                system=concept.title(),
                approach=concept.title(),
                context=topic_context or "the subject"
            )
            
            back = template[1].format(
                concept=concept.title(),
                item=concept.title(),
                action=concept.title(),
                system=concept.title(),
                approach=concept.title(),
                context=topic_context or "the subject"
            )
            
            flashcard = GeneratedFlashcard(
                front=front,
                back=back,
                card_type=FlashcardType.CLOZE,
                metadata={'template_used': i % len(templates), 'concept': concept}
            )
            flashcards.append(flashcard)
        
        return flashcards[:num_cards]
    
    def _generate_mock_mc_cards(
        self,
        concepts: List[str],
        content: str,
        num_cards: int,
        topic_context: Optional[str]
    ) -> List[GeneratedFlashcard]:
        """Generate mock multiple choice flashcards."""
        flashcards = []
        templates = self.templates.MC_TEMPLATES
        
        for i in range(min(num_cards, len(concepts))):
            concept = concepts[i]
            template = templates[i % len(templates)]
            
            question = template[0].format(
                concept=concept.title(),
                term=concept.title(),
                system=concept.title()
            )
            
            # Create multiple choice options
            options = template[1].copy()
            options[0] = options[0].replace("Correct", concept.title())
            
            front = f"{question}\n\nA) {options[0]}\nB) {options[1]}\nC) {options[2]}\nD) {options[3]}"
            back = f"Correct answer: A) {options[0]}\n\nThis is the correct answer based on the content provided."
            
            flashcard = GeneratedFlashcard(
                front=front,
                back=back,
                card_type=FlashcardType.MULTIPLE_CHOICE,
                metadata={'template_used': i % len(templates), 'concept': concept}
            )
            flashcards.append(flashcard)
        
        return flashcards[:num_cards]
    
    def _extract_context_for_concept(self, content: str, concept: str, max_length: int = 200) -> str:
        """Extract relevant context for a concept from the content."""
        # Find sentences containing the concept
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if concept.lower() in sentence.lower():
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            context = '. '.join(relevant_sentences[:2])  # Take first 2 relevant sentences
            if len(context) > max_length:
                context = context[:max_length] + "..."
            return context
        
        return ""
    
    def get_degradation_stats(self) -> Dict[str, Any]:
        """Get statistics about degradation usage."""
        return {
            **self.degradation_stats,
            "cache_size": len(self.cache.cache),
            "cache_hit_rate": (
                self.degradation_stats["cache_hits"] / max(self.degradation_stats["total_fallbacks"], 1)
            ) * 100
        }
    
    def create_offline_response(self, error: GracefulError) -> Dict[str, Any]:
        """Create a structured offline response for the frontend."""
        return {
            "error_id": error.error_id,
            "message": error.user_message,
            "fallback_available": error.fallback_available,
            "recovery_actions": [action.value for action in error.recovery_actions],
            "retry_after": error.retry_after,
            "timestamp": error.timestamp.isoformat(),
            "degradation_mode": DegradationMode.OFFLINE_MODE.value,
            "suggestions": self._get_recovery_suggestions(error.recovery_actions)
        }
    
    def _get_recovery_suggestions(self, actions: List[RecoveryAction]) -> List[str]:
        """Get user-friendly recovery suggestions."""
        suggestions = {
            RecoveryAction.RETRY_LATER: "Try again in a few minutes when our AI service is back online.",
            RecoveryAction.USE_DIFFERENT_CONTENT: "Try using shorter content or breaking it into smaller sections.",
            RecoveryAction.CONTACT_SUPPORT: "Contact our support team if this issue persists.",
            RecoveryAction.CHECK_NETWORK: "Check your internet connection and try again.",
            RecoveryAction.REDUCE_CONTENT_SIZE: "Reduce the amount of content or split it into smaller parts."
        }
        
        return [suggestions.get(action, "Try again later.") for action in actions]

# Create singleton instance
graceful_degradation = GracefulDegradationService()