"""Ollama provider (local LLM)."""

from typing import Dict, Any, Optional
import json
import logging
from .base import BaseAIProvider

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Ollama local LLM provider for event categorization."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get('host', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.2')
        self.timeout = config.get('timeout', 30)
        self.available = REQUESTS_AVAILABLE and self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running."""
        if not REQUESTS_AVAILABLE:
            return False
        try:
            import requests
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def is_available(self) -> bool:
        return self.available
    
    def extract_event_info(self, text: str, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract event information from text using Ollama.
        
        Args:
            text: Text to analyze (event title and description)
            prompt: Custom prompt (if None, uses default categorization prompt)
            
        Returns:
            Dictionary with extracted info, or None on failure
        """
        if not self.available:
            return None
        
        self.rate_limiter.wait()
        
        try:
            import requests
            
            # Use default prompt if none provided
            if prompt is None:
                prompt = self._build_categorization_prompt(text)
            else:
                prompt = f"{prompt}\n\nText: {text}"
            
            # Call Ollama API
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Ollama API returned status {response.status_code}")
                return None
            
            # Parse response
            result = response.json()
            response_text = result.get('response', '')
            
            # Parse JSON from response
            try:
                extracted = json.loads(response_text)
                return extracted
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse Ollama JSON response: {response_text[:100]}")
                return None
                
        except Exception as e:
            logger.warning(f"Ollama extraction failed: {e}")
            return None
    
    def _build_categorization_prompt(self, text: str) -> str:
        """Build prompt for event categorization.
        
        Args:
            text: Event text to categorize
            
        Returns:
            Prompt string
        """
        return f"""You are an event categorization assistant. Analyze the following event text and categorize it.

Event text:
{text}

Available categories:
- Performance & Stage: on-stage, music, opera-house, theatre, concert
- Social & Community: pub-games, festivals, community, social, meetup
- Learning & Skills: workshops, school, education, training, seminar
- Shopping & Commerce: shopping, market, bazaar, fair, trade-show
- Sports & Fitness: sports, sports-field, swimming, fitness, athletics
- Arts & Culture: arts, museum, gallery, exhibition, cultural
- Food & Drink: food, restaurant, cafe, dining, culinary
- Religious & Spiritual: church, religious, spiritual, worship, ceremony
- Historical & Monuments: castle, monument, tower, ruins, palace
- Parks & Nature: park, nature, garden, outdoors, recreation
- Government & Civic: parliament, mayors-office, civic, government, public-office
- Education & Research: library, national-archive, research, academic, study
- Technology & Innovation: tech, innovation, startup, hackathon, coding
- Health & Wellness: health, wellness, medical, therapy, healing
- Family & Kids: family, kids, children, youth, playground
- Business & Networking: business, networking, conference, corporate, professional
- Default fallback: default, other, miscellaneous, general

Respond with ONLY a JSON object in this exact format:
{{"category": "selected_category", "confidence": 0.95, "reasoning": "brief explanation"}}

Choose the most appropriate category. Use "default" if uncertain."""
    
    def analyze_image(self, image_data: bytes, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Analyze image to extract event information (requires vision model).
        
        Args:
            image_data: Image binary data
            prompt: Custom prompt
            
        Returns:
            Extracted event data or None
        """
        if not self.available:
            return None
        
        self.rate_limiter.wait()
        
        # Vision models in Ollama require special handling
        # This is a stub - full implementation would need llava or similar
        logger.info("Image analysis not yet implemented for Ollama")
        return None
