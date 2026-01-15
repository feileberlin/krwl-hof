"""
Weather Scraper Module - KISS Implementation

Simple weather dresscode scraper for MSN Weather.
Extracts dresscode, validates against whitelist, caches for 1 hour.
"""

import os
import json
import requests
from urllib.parse import quote
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WeatherScraper:
    """Simple weather dresscode scraper with hourly caching."""
    
    def __init__(self, base_path=None, config=None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config = config or {}
        
        # Paths
        json_dir = os.path.join(self.base_path, 'assets', 'json')
        self.cache_file = os.path.join(json_dir, 'weather_cache.json')
        self.dresscodes_file = os.path.join(json_dir, 'weather_dresscodes.json')
        
        # Load accepted dresscodes
        self.accepted_dresscodes = self._load_accepted_dresscodes()
        
        # Config
        weather_config = self.config.get('weather', {})
        self.cache_hours = weather_config.get('cache_hours', 1)
        self.timeout = weather_config.get('timeout', 10)
        self.user_agent = weather_config.get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    def get_weather(self, location_name=None, lat=None, lon=None, force_refresh=False):
        """Get weather for location, using cache if available."""
        # Check cache
        if not force_refresh:
            cached = self._get_from_cache(location_name, lat, lon)
            if cached:
                return cached
        
        # Scrape fresh data using coordinates if provided
        weather_data = self._scrape_weather(location_name, lat, lon)
        
        # Save to cache
        if weather_data:
            self._save_to_cache(location_name, lat, lon, weather_data)
        
        return weather_data
    
    def _scrape_weather(self, location_name, lat=None, lon=None):
        """Scrape weather from MSN Weather using coordinates."""
        try:
            # Build URL using coordinates if provided, otherwise use location name
            if lat is not None and lon is not None:
                # Round coordinates to 4 decimal places for URL compatibility and caching consistency
                lat_rounded = round(float(lat), 4)
                lon_rounded = round(float(lon), 4)
                # MSN Weather accepts "lat,lon" format in the location URL
                url = f"https://www.msn.com/en-us/weather/forecast/in-{lat_rounded},{lon_rounded}"
            elif location_name:
                # Fallback to location name (URL-encoded)
                encoded_location = quote(location_name)
                url = f"https://www.msn.com/en-us/weather/forecast/in-{encoded_location}"
            else:
                # Default fallback
                url = "https://www.msn.com/en-us/weather/forecast/in-Hof,Bavaria,Germany"
            
            logger.debug(f"Fetching weather from: {url}")
            
            # Fetch page
            response = requests.get(url, headers={'User-Agent': self.user_agent}, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract dresscode
            dresscode = self._extract_dresscode(soup)
            if not dresscode or not self._is_valid_dresscode(dresscode):
                return None
            
            # Extract temperature (optional)
            temperature = self._extract_temperature(soup)
            
            return {
                'dresscode': dresscode,
                'temperature': temperature,
                'location': location_name,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Weather scraping failed: {e}")
            return None
    
    def _extract_dresscode(self, soup):
        """Extract dresscode from page."""
        # Try aria-label on dressingIndex elements
        for selector in ['[data-id="dressingIndex"]', '[aria-label*="dress"]']:
            elements = soup.select(selector)
            for element in elements:
                aria_label = element.get('aria-label', '')
                if 'dress' in aria_label.lower():
                    return self._clean_dresscode(aria_label)
        return None
    
    def _clean_dresscode(self, text):
        """Clean and simplify dresscode text."""
        text = text.strip()
        # Remove "recommended" suffix
        if 'recommended' in text.lower():
            text = text.lower().split('recommended')[0].strip().title()
        return text[:100]  # Limit length
    
    def _extract_temperature(self, soup):
        """Extract temperature from page."""
        for selector in ['.temperature', '[data-id="temperature"]']:
            elements = soup.select(selector)
            for element in elements:
                temp = element.get_text().strip()
                if '°' in temp or any(c.isdigit() for c in temp):
                    return temp
        return None
    
    def _load_accepted_dresscodes(self):
        """Load accepted dresscodes list."""
        try:
            with open(self.dresscodes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [dc.lower() for dc in data.get('accepted_dresscodes', [])]
        except:
            return []
    
    def _is_valid_dresscode(self, dresscode):
        """Check if dresscode is in accepted list."""
        if not dresscode or not self.accepted_dresscodes:
            return False
        dresscode_lower = dresscode.lower().strip()
        # Exact or partial match
        return any(acc in dresscode_lower or dresscode_lower in acc 
                   for acc in self.accepted_dresscodes)
    
    def _get_from_cache(self, location_name, lat, lon):
        """Get weather from cache if valid."""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # Find matching entry
            key = self._cache_key(location_name, lat, lon)
            entry = cache.get(key)
            
            if not entry:
                return None
            
            # Check if expired
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time >= timedelta(hours=self.cache_hours):
                return None
            
            return entry['data']
        except:
            return None
    
    def _save_to_cache(self, location_name, lat, lon, weather_data):
        """Save weather to cache."""
        try:
            # Load existing cache
            cache = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            # Add/update entry
            key = self._cache_key(location_name, lat, lon)
            cache[key] = {
                'timestamp': datetime.now().isoformat(),
                'data': weather_data
            }
            
            # Save
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Cache save failed: {e}")
    
    def _cache_key(self, location_name, lat, lon):
        """Generate cache key."""
        if location_name:
            return f"location_{location_name}"
        elif lat and lon:
            # Round coordinates to 4 decimal places for consistency with URL generation
            lat_rounded = round(float(lat), 4)
            lon_rounded = round(float(lon), 4)
            return f"coords_{lat_rounded}_{lon_rounded}"
        return "default"
