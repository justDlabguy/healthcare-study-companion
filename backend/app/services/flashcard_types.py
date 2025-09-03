"""
Shared types for flashcard services.

This module contains shared types and classes used by both the flashcard generator
and graceful degradation services to avoid circular imports.
"""

from typing import Dict, Any, Optional
from enum import Enum

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