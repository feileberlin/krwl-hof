"""
Weather Scraper Module - MSN Weather Integration

Scrapes current weather conditions and dressing recommendations from MSN Weather.
Extracts dresscode information from dressingIndex aria-label attribute.
Implements hourly caching to minimize API/scraping load.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WeatherScraper:
    """
    Scrapes and caches weather dresscode information from MSN Weather.
    
    Hourly caching prevents excessive requests and improves performance.
    Dresscode is extracted from the dressingIndex element's aria-label attribute.
    """
    
    def __init__(self, base_path=None, config=None):
        """
        Initialize weather scraper with configuration.
        
        Args:
            base_path: Base path for data files
            config: Configuration dict with weather settings
        """
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config = config or {}
        
        # Cache file location
        self.cache_dir = os.path.join(self.base_path, 'assets', 'json')
        self.cache_file = os.path.join(self.cache_dir, 'weather_cache.json')
        
        # Accepted dresscodes file
        self.dresscodes_file = os.path.join(self.base_path, 'assets', 'json', 'weather_dresscodes.json')
        self.accepted_dresscodes = self._load_accepted_dresscodes()
        
        # Weather configuration
        weather_config = self.config.get('weather', {})
        self.locations = weather_config.get('locations', [])
        self.cache_hours = weather_config.get('cache_hours', 1)
        self.timeout = weather_config.get('timeout', 10)
        
        # MSN Weather URL template
        self.msn_weather_url = "https://www.msn.com/en-us/weather/forecast/in-{city},{region},{country}"
        
    def get_weather(self, location_name=None, lat=None, lon=None, force_refresh=False):
        """
        Get weather dresscode for a location.
        
        Args:
            location_name: Location name (e.g., "Hof")
            lat: Latitude (optional, for geo-based lookup)
            lon: Longitude (optional, for geo-based lookup)
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dict with weather data including dresscode, temperature, conditions
        """
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self._load_cache()
            if cached_data:
                cache_key = self._get_cache_key(location_name, lat, lon)
                if cache_key in cached_data:
                    entry = cached_data[cache_key]
                    # Check if cache is still valid (within cache_hours)
                    cache_time = datetime.fromisoformat(entry['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=self.cache_hours):
                        logger.info(f"Using cached weather for {cache_key}")
                        return entry['data']
        
        # Fetch fresh weather data
        weather_data = self._scrape_weather(location_name, lat, lon)
        
        # Save to cache
        if weather_data:
            self._save_cache(location_name, lat, lon, weather_data)
        
        return weather_data
    
    def _scrape_weather(self, location_name, lat, lon):
        """
        Scrape weather data from MSN Weather.
        
        Args:
            location_name: Location name
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict with dresscode and weather info, or None if scraping fails
        """
        try:
            # Build URL for location
            if location_name:
                # Use location name (e.g., "Hof, Bavaria, Germany")
                url = self._build_msn_url(location_name)
            elif lat and lon:
                # Use coordinates (convert to location name via reverse geocoding or default)
                location_name = "Hof"  # Default for this project
                url = self._build_msn_url(location_name)
            else:
                logger.error("No location specified for weather scraping")
                return None
            
            logger.info(f"Fetching weather from: {url}")
            
            # Fetch page with headers to avoid bot detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract dresscode from dressingIndex aria-label
            dresscode = self._extract_dresscode(soup)
            
            # Extract additional weather info
            temperature = self._extract_temperature(soup)
            conditions = self._extract_conditions(soup)
            
            weather_data = {
                'dresscode': dresscode,
                'temperature': temperature,
                'conditions': conditions,
                'location': location_name,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Weather scraped successfully: {dresscode}")
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping weather: {e}")
            return None
    
    def _extract_dresscode(self, soup):
        """
        Extract dresscode from dressingIndex element's aria-label.
        Validates against accepted dresscodes list.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dresscode string if valid, or None if not found or not accepted
        """
        try:
            # Look for dressingIndex element with aria-label
            # Try multiple possible selectors
            selectors = [
                '[data-id="dressingIndex"]',
                '.dressingIndex',
                '#dressingIndex',
                '[aria-label*="dressing"]',
                '[aria-label*="dress"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    aria_label = element.get('aria-label', '')
                    if aria_label and ('dress' in aria_label.lower() or 'clothing' in aria_label.lower()):
                        logger.info(f"Found dresscode in aria-label: {aria_label}")
                        parsed_dresscode = self._parse_dresscode(aria_label)
                        # Validate against accepted list
                        if parsed_dresscode and self._validate_dresscode(parsed_dresscode):
                            return parsed_dresscode
                        else:
                            logger.warning(f"Dresscode '{parsed_dresscode}' not in accepted list, skipping")
            
            # Fallback: Look for any text content about dressing
            text_elements = soup.find_all(text=lambda t: t and ('dress' in t.lower() or 'wear' in t.lower()))
            if text_elements:
                for text in text_elements:
                    text_str = str(text).strip()
                    if len(text_str) > 10 and len(text_str) < 200:  # Reasonable length
                        logger.info(f"Found dresscode in text: {text_str}")
                        parsed_dresscode = self._parse_dresscode(text_str)
                        # Validate against accepted list
                        if parsed_dresscode and self._validate_dresscode(parsed_dresscode):
                            return parsed_dresscode
                        else:
                            logger.warning(f"Dresscode '{parsed_dresscode}' not in accepted list, skipping")
            
            logger.warning("No valid dresscode found in page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting dresscode: {e}")
            return None
    
    def _parse_dresscode(self, text):
        """
        Parse and simplify dresscode text.
        
        Args:
            text: Raw dresscode text
            
        Returns:
            Simplified dresscode string
        """
        # Clean up the text
        text = text.strip()
        
        # Extract key recommendation (e.g., "Light jacket recommended" -> "Light jacket")
        # Common patterns: "X recommended", "Wear X", "Dress for X"
        if 'recommended' in text.lower():
            parts = text.lower().split('recommended')
            if parts[0]:
                return parts[0].strip().title()
        
        if 'wear' in text.lower():
            parts = text.lower().split('wear')
            if len(parts) > 1:
                return parts[1].strip()[:50].title()
        
        # If no pattern matched, return first reasonable chunk
        if len(text) > 100:
            return text[:100] + "..."
        
        return text
    
    def _extract_temperature(self, soup):
        """
        Extract current temperature from page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Temperature string (e.g., "15°C"), or None
        """
        try:
            # Common temperature selectors on MSN Weather
            selectors = [
                '.temperature',
                '[data-id="temperature"]',
                '.current-temp',
                'span[class*="temp"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    temp_text = element.get_text().strip()
                    if temp_text and ('°' in temp_text or temp_text.replace('-', '').isdigit()):
                        return temp_text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting temperature: {e}")
            return None
    
    def _extract_conditions(self, soup):
        """
        Extract weather conditions (e.g., "Partly cloudy").
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Conditions string, or None
        """
        try:
            # Common condition selectors
            selectors = [
                '.weather-condition',
                '[data-id="condition"]',
                '.current-condition',
                'span[class*="condition"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    condition_text = element.get_text().strip()
                    if condition_text and len(condition_text) > 3 and len(condition_text) < 50:
                        return condition_text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting conditions: {e}")
            return None
    
    def _load_accepted_dresscodes(self):
        """
        Load list of accepted dresscodes from JSON file.
        
        Returns:
            List of accepted dresscode strings (lowercase for matching)
        """
        try:
            if os.path.exists(self.dresscodes_file):
                with open(self.dresscodes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    dresscodes = data.get('accepted_dresscodes', [])
                    # Convert to lowercase for case-insensitive matching
                    return [dc.lower() for dc in dresscodes]
            else:
                logger.warning(f"Dresscodes file not found: {self.dresscodes_file}")
                return []
        except Exception as e:
            logger.error(f"Error loading accepted dresscodes: {e}")
            return []
    
    def _validate_dresscode(self, dresscode):
        """
        Validate dresscode against accepted list.
        Uses case-insensitive partial matching.
        
        Args:
            dresscode: Dresscode string to validate
            
        Returns:
            True if dresscode is accepted, False otherwise
        """
        if not dresscode or not self.accepted_dresscodes:
            return False
        
        dresscode_lower = dresscode.lower().strip()
        
        # Exact match (case-insensitive)
        if dresscode_lower in self.accepted_dresscodes:
            return True
        
        # Partial match - check if any accepted dresscode is contained in the scraped value
        # or if the scraped value is contained in any accepted dresscode
        for accepted in self.accepted_dresscodes:
            if accepted in dresscode_lower or dresscode_lower in accepted:
                return True
        
        return False
    
    def _build_msn_url(self, location_name):
        """
        Build MSN Weather URL for location.
        
        Args:
            location_name: Location name (e.g., "Hof")
            
        Returns:
            MSN Weather URL string
        """
        # For this project, default to Hof, Bavaria, Germany
        # In the future, this could be more dynamic
        city = "Hof"
        region = "Bavaria"
        country = "Germany"
        
        # URL encode spaces and special characters
        city_encoded = city.replace(" ", "%20")
        region_encoded = region.replace(" ", "%20")
        country_encoded = country.replace(" ", "%20")
        
        return f"https://www.msn.com/en-us/weather/forecast/in-{city_encoded},{region_encoded},{country_encoded},{country_encoded}"
    
    def _get_cache_key(self, location_name, lat, lon):
        """
        Generate cache key for location.
        
        Args:
            location_name: Location name
            lat: Latitude
            lon: Longitude
            
        Returns:
            Cache key string
        """
        if location_name:
            return f"location_{location_name}"
        elif lat and lon:
            return f"coords_{lat}_{lon}"
        else:
            return "default"
    
    def _load_cache(self):
        """
        Load weather cache from file.
        
        Returns:
            Dict with cached weather data, or None
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading weather cache: {e}")
        
        return None
    
    def _save_cache(self, location_name, lat, lon, weather_data):
        """
        Save weather data to cache.
        
        Args:
            location_name: Location name
            lat: Latitude
            lon: Longitude
            weather_data: Weather data dict
        """
        try:
            # Load existing cache
            cached_data = self._load_cache() or {}
            
            # Add new entry
            cache_key = self._get_cache_key(location_name, lat, lon)
            cached_data[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'data': weather_data
            }
            
            # Save to file
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Weather cache saved for {cache_key}")
            
        except Exception as e:
            logger.error(f"Error saving weather cache: {e}")
    
    def scrape_all_locations(self):
        """
        Scrape weather for all configured locations.
        
        Returns:
            Dict mapping location names to weather data
        """
        results = {}
        
        for location in self.locations:
            location_name = location.get('name')
            lat = location.get('lat')
            lon = location.get('lon')
            
            weather_data = self.get_weather(location_name, lat, lon)
            if weather_data:
                results[location_name] = weather_data
        
        return results
