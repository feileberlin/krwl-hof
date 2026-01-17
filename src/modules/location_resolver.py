"""
Location Resolver Module

Resolves generic location names (e.g., "Hof", "Frankenpost") to specific venue names
by scraping event detail pages for actual location information.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configure module logger
logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_ENABLED = True
except ImportError:
    SCRAPING_ENABLED = False
    logger.warning("Scraping libraries not installed. Location resolution will be limited.")


class LocationResolver:
    """
    Resolves generic location names to specific venues by scraping detail pages.
    
    This module handles events that have generic locations like "Hof" or "Frankenpost"
    and attempts to extract the actual venue name and address from event detail pages.
    """
    
    def __init__(self, base_path: Path, config: Dict):
        """
        Initialize location resolver.
        
        Args:
            base_path: Repository root path
            config: Application configuration
        """
        self.base_path = Path(base_path)
        self.config = config
        self.session = None
        
        if SCRAPING_ENABLED:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            self.timeout = 15
    
    def resolve_pending_events(self, dry_run: bool = False) -> Dict:
        """
        Resolve generic locations for all pending events.
        
        Scans pending events for generic location names ("Hof", "Frankenpost")
        and attempts to fetch the actual venue from the event detail page.
        
        Args:
            dry_run: If True, show what would be changed without making changes
            
        Returns:
            Dict with results: total_checked, resolved_count, failed_count, etc.
        """
        if not SCRAPING_ENABLED:
            logger.error("Scraping libraries not installed.")
            logger.error("Install with: pip install requests beautifulsoup4 lxml")
            return {
                'total_checked': 0,
                'resolved_count': 0,
                'failed_count': 0,
                'error': 'Missing dependencies'
            }
        
        # Load pending events
        pending_file = self.base_path / 'assets' / 'json' / 'pending_events.json'
        if not pending_file.exists():
            logger.warning("No pending events file found")
            return {'total_checked': 0, 'resolved_count': 0, 'failed_count': 0}
        
        with open(pending_file, 'r', encoding='utf-8') as f:
            pending_data = json.load(f)
        
        events = pending_data.get('pending_events', [])
        
        # Find events with generic locations
        generic_locations = ['Hof', 'Frankenpost']
        events_to_resolve = [
            event for event in events
            if event.get('location', {}).get('name') in generic_locations
        ]
        
        logger.info(f"Found {len(events_to_resolve)} events with generic locations")
        
        resolved_count = 0
        failed_count = 0
        results = []
        
        for event in events_to_resolve:
            event_id = event.get('id')
            title = event.get('title', 'Unknown')[:50]
            url = event.get('url')
            current_location = event.get('location', {}).get('name')
            
            if not url:
                logger.debug(f"No URL for event: {title}")
                failed_count += 1
                continue
            
            logger.info(f"Resolving location for: {title}...")
            
            try:
                # Fetch and parse detail page
                new_location = self._extract_location_from_url(url)
                
                if new_location and new_location.get('name'):
                    venue_name = new_location['name']
                    
                    # Skip if location is still generic
                    if venue_name in generic_locations:
                        logger.debug(f"  Still generic: {venue_name}")
                        failed_count += 1
                        continue
                    
                    logger.info(f"  ✓ Found venue: {venue_name}")
                    
                    results.append({
                        'event_id': event_id,
                        'title': title,
                        'old_location': current_location,
                        'new_location': venue_name,
                        'url': url
                    })
                    
                    # Update event if not dry run
                    if not dry_run:
                        # Keep coordinates from default location, update name
                        event['location']['name'] = venue_name
                        if new_location.get('address'):
                            event['location']['address'] = new_location['address']
                    
                    resolved_count += 1
                else:
                    logger.debug(f"  ✗ Could not extract location")
                    failed_count += 1
                    
            except Exception as e:
                logger.debug(f"  ✗ Error: {e}")
                failed_count += 1
        
        # Save updated pending events (if not dry run and changes were made)
        if not dry_run and resolved_count > 0:
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(pending_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Updated {resolved_count} events in pending_events.json")
        
        # Print summary
        print(f"\n{'=' * 70}")
        print(f"Location Resolution {'(DRY RUN) ' if dry_run else ''}Summary")
        print(f"{'=' * 70}")
        print(f"Total events checked: {len(events_to_resolve)}")
        print(f"Successfully resolved: {resolved_count}")
        print(f"Failed to resolve: {failed_count}")
        
        if results:
            print(f"\n{'Resolved Locations:' if not dry_run else 'Would Resolve:'}")
            for r in results[:20]:  # Show first 20
                print(f"  • {r['title']}")
                print(f"    {r['old_location']} → {r['new_location']}")
            
            if len(results) > 20:
                print(f"  ... and {len(results) - 20} more")
        
        return {
            'total_checked': len(events_to_resolve),
            'resolved_count': resolved_count,
            'failed_count': failed_count,
            'results': results
        }
    
    def _extract_location_from_url(self, url: str) -> Optional[Dict]:
        """
        Extract location information from an event detail page.
        
        Args:
            url: Event detail page URL
            
        Returns:
            Dict with name, address (if available), or None if extraction failed
        """
        if not self.session:
            return None
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try different extraction strategies
            location = self._extract_location_frankenpost(soup)
            
            return location
            
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return None
    
    def _extract_location_frankenpost(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract location from Frankenpost event detail page.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dict with name and address, or None
        """
        location = {'name': None, 'address': None}
        
        # Strategy 1: Look for explicit location/venue fields
        # Common patterns: "Ort:", "Veranstaltungsort:", "Location:", etc.
        location_patterns = [
            r'(?:Ort|Veranstaltungsort|Location|Venue):\s*(.+)',
            r'Wo:\s*(.+)',
        ]
        
        text = soup.get_text()
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                venue = match.group(1).strip()
                # Clean up common suffixes
                venue = re.sub(r'\s*,.*$', '', venue)  # Remove everything after comma
                venue = re.sub(r'\s*\|.*$', '', venue)  # Remove everything after pipe
                if venue and len(venue) > 2:
                    location['name'] = venue
                    break
        
        # Strategy 2: Look for structured data (schema.org, microdata)
        # Check for itemtype="http://schema.org/Event"
        event_schema = soup.find(attrs={'itemtype': re.compile(r'schema\.org/Event', re.I)})
        if event_schema:
            venue_elem = event_schema.find(attrs={'itemprop': 'location'})
            if venue_elem:
                venue_name = venue_elem.find(attrs={'itemprop': 'name'})
                if venue_name:
                    location['name'] = venue_name.get_text().strip()
                
                venue_address = venue_elem.find(attrs={'itemprop': 'address'})
                if venue_address:
                    location['address'] = venue_address.get_text().strip()
        
        # Strategy 3: Look for common HTML structures
        # div/span with class containing "location", "venue", "ort"
        if not location['name']:
            venue_elems = soup.find_all(
                ['div', 'span', 'p', 'td', 'th'],
                class_=re.compile(r'(location|venue|ort|veranstaltungsort)', re.I)
            )
            for elem in venue_elems:
                text = elem.get_text().strip()
                # Filter out generic values
                if text and len(text) > 2 and text not in ['Hof', 'Frankenpost', 'Bayern']:
                    location['name'] = text
                    break
        
        # Strategy 4: Look for table rows with location labels
        if not location['name']:
            for row in soup.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text().strip().lower()
                    if any(keyword in label for keyword in ['ort', 'location', 'venue', 'wo']):
                        venue = cells[1].get_text().strip()
                        if venue and len(venue) > 2 and venue not in ['Hof', 'Frankenpost']:
                            location['name'] = venue
                            break
        
        # Strategy 5: Look for address information
        if not location['address']:
            # Common address patterns
            address_patterns = [
                r'([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|platz|allee))\s+\d+',
                r'\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+',  # PLZ + Stadt
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text)
                if match:
                    location['address'] = match.group(0)
                    break
        
        return location if location['name'] else None
    
    def resolve_single_event(self, event_id: str, dry_run: bool = False) -> Dict:
        """
        Resolve location for a single event by ID.
        
        Args:
            event_id: Event ID to resolve
            dry_run: If True, show what would be changed without making changes
            
        Returns:
            Dict with result information
        """
        if not SCRAPING_ENABLED:
            return {'error': 'Missing dependencies'}
        
        # Load pending events
        pending_file = self.base_path / 'assets' / 'json' / 'pending_events.json'
        if not pending_file.exists():
            return {'error': 'No pending events file found'}
        
        with open(pending_file, 'r', encoding='utf-8') as f:
            pending_data = json.load(f)
        
        events = pending_data.get('pending_events', [])
        event = next((e for e in events if e.get('id') == event_id), None)
        
        if not event:
            return {'error': f'Event not found: {event_id}'}
        
        url = event.get('url')
        if not url:
            return {'error': 'Event has no URL'}
        
        current_location = event.get('location', {}).get('name')
        
        try:
            new_location = self._extract_location_from_url(url)
            
            if new_location and new_location.get('name'):
                venue_name = new_location['name']
                
                result = {
                    'event_id': event_id,
                    'title': event.get('title'),
                    'old_location': current_location,
                    'new_location': venue_name,
                    'url': url,
                    'success': True
                }
                
                # Update event if not dry run
                if not dry_run:
                    event['location']['name'] = venue_name
                    if new_location.get('address'):
                        event['location']['address'] = new_location['address']
                    
                    with open(pending_file, 'w', encoding='utf-8') as f:
                        json.dump(pending_data, f, indent=2, ensure_ascii=False)
                
                return result
            else:
                return {
                    'event_id': event_id,
                    'error': 'Could not extract location',
                    'success': False
                }
                
        except Exception as e:
            return {
                'event_id': event_id,
                'error': str(e),
                'success': False
            }
