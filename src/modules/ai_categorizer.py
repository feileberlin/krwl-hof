"""
AI-Powered Event Categorization Module

Uses local LLM (Ollama) to intelligently categorize scraped events into
schema-defined categories. Falls back to keyword-based categorization
if AI is unavailable.

This module provides a KISS approach to AI-powered event categorization:
- Single responsibility: categorize events
- Graceful fallback to keyword matching
- Optional feature (can be disabled)
- No external API dependencies (runs locally)

Usage:
    from ai_categorizer import AICategorizer
    
    categorizer = AICategorizer(config, base_path)
    category = categorizer.categorize_event(title, description)
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Keyword to category mapping for fallback categorization
# Ordered by priority - more specific categories first
KEYWORD_CATEGORY_MAP = {
    'tech': ['tech', 'technology', 'digital', 'software', 'coding', 'hackathon', 'developer', 'developers'],
    'workshops': ['workshop', 'class', 'training', 'learn', 'course', 'seminar', 'tutorial'],
    'music': ['music', 'concert', 'band', 'orchestra', 'song', 'singer', 'rock', 'jazz'],
    'theatre': ['theatre', 'theater', 'play', 'drama', 'performance', 'stage show'],
    'sports': ['sport', 'game', 'match', 'tournament', 'competition', 'team', 'football', 'soccer'],
    'arts': ['art', 'exhibition', 'gallery', 'paint', 'draw', 'sculpture', 'contemporary'],
    'shopping': ['market', 'shopping', 'bazaar', 'sale', 'shop', 'store', 'vendor', 'christmas market'],
    'food': ['restaurant', 'dining', 'culinary', 'chef', 'meal', 'cuisine'],
    'festivals': ['festival', 'celebration', 'carnival', 'fest'],
    'museum': ['museum', 'history', 'heritage', 'artifact'],
    'church': ['church', 'religious', 'worship', 'prayer', 'spiritual'],
    'park': ['park', 'nature', 'garden', 'outdoor', 'recreation'],
    'library': ['library', 'book', 'reading', 'literature'],
    'health': ['health', 'wellness', 'medical', 'fitness', 'gym'],
    'family': ['family', 'kids', 'children', 'youth', 'child'],
    'business': ['business', 'networking', 'conference', 'professional', 'corporate'],
    'community': ['community', 'meetup', 'gathering', 'social event'],  # Generic terms last
}


class AICategorizer:
    """
    AI-powered event categorizer using local LLM.
    
    Categorizes events into schema-defined categories using Ollama (local LLM).
    Falls back to keyword-based categorization if AI is unavailable.
    """
    
    def __init__(self, config: Dict[str, Any], base_path: Path):
        """Initialize AI categorizer.
        
        Args:
            config: Full configuration dictionary
            base_path: Base path for data files
        """
        self.config = config
        self.base_path = base_path
        self.enabled = config.get('ai', {}).get('categorization', {}).get('enabled', False)
        self.ai_provider = None
        self.keyword_fallback_enabled = True
        
        # Initialize AI provider if enabled
        if self.enabled:
            self._init_ai_provider()
    
    def _init_ai_provider(self):
        """Initialize Ollama AI provider."""
        try:
            from .smart_scraper.ai_providers.ollama import OllamaProvider
            
            # Get Ollama config from ai.ollama section
            ollama_config = self.config.get('ai', {}).get('ollama', {})
            if not ollama_config:
                # Use defaults
                ollama_config = {
                    'host': 'http://localhost:11434',
                    'model': 'llama3.2',
                    'timeout': 30,
                    'rate_limit': {
                        'min_delay': 0.5,
                        'max_delay': 2.0,
                        'max_requests_per_session': 50
                    }
                }
            
            # Initialize provider
            provider = OllamaProvider(ollama_config)
            
            if provider.is_available():
                self.ai_provider = provider
                logger.info("✓ AI categorization enabled (Ollama)")
            else:
                logger.warning("Ollama not available - falling back to keyword categorization")
                self.ai_provider = None
                
        except ImportError as e:
            logger.warning(f"AI categorization libraries not available: {e}")
            self.ai_provider = None
        except Exception as e:
            logger.error(f"Failed to initialize AI provider: {e}")
            self.ai_provider = None
    
    def categorize_event(self, title: str, description: str = "") -> Tuple[str, float, str]:
        """
        Categorize an event using AI or keyword fallback.
        
        Args:
            title: Event title
            description: Event description (optional)
            
        Returns:
            Tuple of (category, confidence, method)
            - category: Selected category string
            - confidence: Confidence score (0.0 to 1.0)
            - method: Categorization method used ('ai', 'keyword', or 'default')
        """
        # Try AI categorization first if available
        if self.enabled and self.ai_provider:
            result = self._categorize_with_ai(title, description)
            if result:
                return result
        
        # Fall back to keyword categorization
        if self.keyword_fallback_enabled:
            return self._categorize_with_keywords(title, description)
        
        # Ultimate fallback
        return 'default', 0.5, 'default'
    
    def _categorize_with_ai(self, title: str, description: str) -> Optional[Tuple[str, float, str]]:
        """Categorize using AI (Ollama).
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            Tuple of (category, confidence, 'ai') or None on failure
        """
        try:
            # Combine title and description
            text = f"Title: {title}\nDescription: {description}".strip()
            
            # Call AI provider
            result = self.ai_provider.extract_event_info(text)
            
            if result and 'category' in result:
                category = result.get('category', 'default')
                confidence = result.get('confidence', 0.8)
                
                # Validate category is in our schema
                from .event_schema import EVENT_CATEGORIES
                if category not in EVENT_CATEGORIES:
                    logger.warning(f"AI returned invalid category '{category}', using default")
                    return 'default', 0.5, 'ai'
                
                logger.debug(f"AI categorized as '{category}' (confidence: {confidence:.2f})")
                return category, confidence, 'ai'
            
            return None
            
        except Exception as e:
            logger.warning(f"AI categorization failed: {e}")
            return None
    
    def _categorize_with_keywords(self, title: str, description: str) -> Tuple[str, float, str]:
        """Categorize using keyword matching (fallback method).
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            Tuple of (category, confidence, 'keyword')
        """
        text = f"{title} {description}".lower()
        
        # Score each category by keyword matches
        matches = self._score_categories(text)
        
        # Return best match or default
        if matches:
            best_category, best_score = matches[0]
            confidence = min(0.9, 0.6 + best_score * 0.3)
            logger.debug(f"Keyword categorized as '{best_category}' (score: {best_score:.2f})")
            return best_category, confidence, 'keyword'
        
        logger.debug("No keyword match, using default category")
        return 'default', 0.5, 'keyword'
    
    def _score_categories(self, text: str) -> List[Tuple[str, float]]:
        """Score categories based on keyword matches.
        
        Args:
            text: Lowercased event text
            
        Returns:
            List of (category, score) tuples sorted by score descending
        """
        scores = []
        for category, keywords in KEYWORD_CATEGORY_MAP.items():
            match_count = sum(1 for keyword in keywords if keyword in text)
            if match_count > 0:
                score = match_count / len(keywords)
                scores.append((category, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def is_available(self) -> bool:
        """Check if AI categorization is available.
        
        Returns:
            True if AI provider is initialized and available
        """
        return self.enabled and self.ai_provider is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get categorizer status information.
        
        Returns:
            Dictionary with status info
        """
        return {
            'enabled': self.enabled,
            'ai_available': self.ai_provider is not None if self.enabled else False,
            'provider': 'ollama' if self.ai_provider else None,
            'fallback_enabled': self.keyword_fallback_enabled,
        }


def create_categorizer(config: Dict[str, Any], base_path: Path) -> AICategorizer:
    """Factory function to create AICategorizer instance.
    
    Args:
        config: Configuration dictionary
        base_path: Base path for data files
        
    Returns:
        AICategorizer instance
    """
    return AICategorizer(config, base_path)
