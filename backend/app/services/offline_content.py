"""
Offline Content Service

This service provides content that can be used when the system is completely offline.
It includes pre-generated templates and fallback content for various scenarios.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OfflineContentService:
    """Service providing offline content and templates."""
    
    def __init__(self):
        self.offline_templates = self._load_offline_templates()
        self.usage_stats = {
            "template_requests": 0,
            "offline_sessions": 0,
            "last_offline_access": None
        }
    
    def _load_offline_templates(self) -> Dict[str, Any]:
        """Load pre-defined offline templates and content."""
        return {
            "study_tips": [
                "Review flashcards regularly using spaced repetition",
                "Focus on understanding concepts rather than memorization",
                "Create connections between different topics",
                "Use active recall techniques when studying",
                "Take breaks to improve retention and focus"
            ],
            "generic_flashcards": {
                "basic": [
                    {
                        "front": "What is active recall?",
                        "back": "Active recall is a learning technique where you actively try to remember information without looking at the source material."
                    },
                    {
                        "front": "What is spaced repetition?",
                        "back": "Spaced repetition is a learning technique that involves reviewing information at increasing intervals to improve long-term retention."
                    },
                    {
                        "front": "How can you improve your study efficiency?",
                        "back": "Improve study efficiency by using active learning techniques, taking regular breaks, and focusing on understanding rather than memorization."
                    }
                ],
                "study_methods": [
                    {
                        "front": "What is the Feynman Technique?",
                        "back": "The Feynman Technique involves explaining a concept in simple terms as if teaching it to someone else, helping identify gaps in understanding."
                    },
                    {
                        "front": "What is the Pomodoro Technique?",
                        "back": "The Pomodoro Technique is a time management method using 25-minute focused work sessions followed by short breaks."
                    }
                ]
            },
            "motivational_content": [
                "Every expert was once a beginner. Keep practicing!",
                "Learning is a journey, not a destination.",
                "Consistency beats perfection in learning.",
                "Your brain grows stronger with every challenge.",
                "Progress, not perfection, is the goal."
            ],
            "offline_study_guide": {
                "title": "Offline Study Guide",
                "sections": [
                    {
                        "title": "Review Previously Generated Content",
                        "content": "Use your cached flashcards and study materials to continue learning even when offline."
                    },
                    {
                        "title": "Practice Active Recall",
                        "content": "Test yourself on the material without looking at the answers first."
                    },
                    {
                        "title": "Organize Your Notes",
                        "content": "Use this time to organize and review your existing study materials."
                    },
                    {
                        "title": "Plan Your Next Study Session",
                        "content": "Think about what topics you want to focus on when you're back online."
                    }
                ]
            }
        }
    
    def get_offline_study_tips(self, count: int = 5) -> List[str]:
        """Get offline study tips."""
        self.usage_stats["template_requests"] += 1
        tips = self.offline_templates["study_tips"]
        return tips[:count] if count <= len(tips) else tips
    
    def get_generic_flashcards(self, category: str = "basic", count: int = 3) -> List[Dict[str, str]]:
        """Get generic flashcards for offline study."""
        self.usage_stats["template_requests"] += 1
        
        if category not in self.offline_templates["generic_flashcards"]:
            category = "basic"
        
        cards = self.offline_templates["generic_flashcards"][category]
        return cards[:count] if count <= len(cards) else cards
    
    def get_motivational_content(self, count: int = 1) -> List[str]:
        """Get motivational content for offline users."""
        self.usage_stats["template_requests"] += 1
        content = self.offline_templates["motivational_content"]
        return content[:count] if count <= len(content) else content
    
    def get_offline_study_guide(self) -> Dict[str, Any]:
        """Get the complete offline study guide."""
        self.usage_stats["template_requests"] += 1
        return self.offline_templates["offline_study_guide"]
    
    def create_offline_session_content(
        self,
        user_context: Optional[str] = None,
        topic_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create comprehensive offline session content."""
        self.usage_stats["offline_sessions"] += 1
        self.usage_stats["last_offline_access"] = datetime.utcnow().isoformat()
        
        return {
            "session_id": f"offline_{int(datetime.utcnow().timestamp())}",
            "created_at": datetime.utcnow().isoformat(),
            "user_context": user_context,
            "topic_context": topic_context,
            "content": {
                "study_tips": self.get_offline_study_tips(),
                "flashcards": self.get_generic_flashcards(),
                "motivation": self.get_motivational_content(),
                "study_guide": self.get_offline_study_guide(),
                "offline_message": self._create_offline_message(topic_context)
            },
            "instructions": [
                "Review your cached flashcards and materials",
                "Practice active recall with existing content",
                "Use this time to organize your study notes",
                "Plan your next online study session"
            ]
        }
    
    def _create_offline_message(self, topic_context: Optional[str] = None) -> str:
        """Create a personalized offline message."""
        base_message = "You're currently offline, but learning never stops! "
        
        if topic_context:
            return f"{base_message}Continue studying {topic_context} with your cached materials and the offline resources provided."
        else:
            return f"{base_message}Use your cached study materials and the offline resources to keep learning."
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get offline content usage statistics."""
        return {
            **self.usage_stats,
            "available_templates": len(self.offline_templates),
            "template_categories": list(self.offline_templates.keys())
        }
    
    def add_custom_offline_content(
        self,
        category: str,
        content: Any,
        replace: bool = False
    ) -> bool:
        """Add custom offline content (for future extensibility)."""
        try:
            if category not in self.offline_templates or replace:
                self.offline_templates[category] = content
            else:
                # Merge with existing content if it's a list or dict
                if isinstance(self.offline_templates[category], list) and isinstance(content, list):
                    self.offline_templates[category].extend(content)
                elif isinstance(self.offline_templates[category], dict) and isinstance(content, dict):
                    self.offline_templates[category].update(content)
                else:
                    self.offline_templates[category] = content
            
            logger.info(f"Added custom offline content for category: {category}")
            return True
        except Exception as e:
            logger.error(f"Error adding custom offline content: {str(e)}")
            return False

# Create singleton instance
offline_content = OfflineContentService()