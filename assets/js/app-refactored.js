// KRWL HOF Community Events App - Refactored for KISS Compliance
// 
// This file is organized into logical modules, each < 500 lines:
// 1. EventStorage - Data persistence (bookmarks, filters)
// 2. EventFilter - Filtering logic (time, distance, category)
// 3. MapManager - Leaflet map management
// 4. SpeechBubbles - UI bubble components
// 5. EventUtils - Utility functions
// 6. EventsApp - Main application coordinator
//
// Original: 3344 lines (6.7x over KISS limit)
// Refactored: ~1500 lines organized into clear sections
//

// ============================================================================
// MODULE 1: EventStorage - Data Persistence
// ============================================================================
/**
 * EventStorage Module
 * 
 * Handles all localStorage/cookie operations for:
 * - Filter settings persistence
 * - Bookmark management
 * - Browser feature detection
 * 
 * KISS: Single responsibility - data persistence only
 */

class EventStorage {
    constructor(config) {
        this.config = config;
        this.MAX_BOOKMARKS = 15;
        this.bookmarks = this.loadBookmarks();
        this.browserFeatures = this.detectBrowserFeatures();
    }
    
    /**
     * Feature detection for browser capabilities
     * @returns {Object} Object with feature availability flags
     */
    detectBrowserFeatures() {
        const features = {
            localStorage: false,
            backdropFilter: false
        };
        
        // Test localStorage
        try {
            const testKey = '__krwl_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            features.localStorage = true;
        } catch (e) {
            features.localStorage = false;
        }
        
        // Test backdrop-filter support
        const testElement = document.createElement('div');
        const backdropFilterSupport = 
            testElement.style.backdropFilter !== undefined ||
            testElement.style.webkitBackdropFilter !== undefined;
        features.backdropFilter = backdropFilterSupport;
        
        return features;
    }
    
    /**
     * Check if bookmarking features should be enabled
     * Requires localStorage and backdrop-filter support
     * @returns {boolean} True if bookmarking is supported
     */
    isBookmarkingSupported() {
        return this.browserFeatures.localStorage && this.browserFeatures.backdropFilter;
    }
    
    /**
     * Save current filter settings to localStorage
     * @param {Object} filters - Filter settings object
     */
    saveFiltersToCookie(filters) {
        try {
            const filterData = JSON.stringify(filters);
            localStorage.setItem('krwl_filters', filterData);
            this.log('Filters saved to localStorage');
        } catch (error) {
            console.warn('Failed to save filters:', error);
        }
    }
    
    /**
     * Load filter settings from localStorage
     * @returns {Object|null} Saved filter settings or null
     */
    loadFiltersFromCookie() {
        try {
            const filterData = localStorage.getItem('krwl_filters');
            if (filterData) {
                const filters = JSON.parse(filterData);
                this.log('Filters loaded from localStorage', filters);
                return filters;
            }
        } catch (error) {
            console.warn('Failed to load filters:', error);
        }
        return null;
    }
    
    /**
     * Load bookmarks from localStorage
     * @returns {Array} Array of bookmarked event IDs
     */
    loadBookmarks() {
        try {
            const bookmarksData = localStorage.getItem('krwl_bookmarks');
            if (bookmarksData) {
                const bookmarks = JSON.parse(bookmarksData);
                this.log('Bookmarks loaded from localStorage', bookmarks);
                return Array.isArray(bookmarks) ? bookmarks : [];
            }
        } catch (error) {
            console.warn('Failed to load bookmarks:', error);
        }
        return [];
    }
    
    /**
     * Save bookmarks to localStorage
     */
    saveBookmarks() {
        try {
            const bookmarksData = JSON.stringify(this.bookmarks);
            localStorage.setItem('krwl_bookmarks', bookmarksData);
            this.log('Bookmarks saved to localStorage', this.bookmarks);
        } catch (error) {
            console.warn('Failed to save bookmarks:', error);
        }
    }
    
    /**
     * Toggle bookmark for an event
     * @param {string} eventId - Event ID to bookmark/unbookmark
     * @returns {boolean} True if bookmarked, false if unbookmarked
     */
    toggleBookmark(eventId) {
        const index = this.bookmarks.indexOf(eventId);
        
        if (index !== -1) {
            // Remove bookmark
            this.bookmarks.splice(index, 1);
            this.saveBookmarks();
            this.log('Bookmark removed:', eventId);
            return false;
        } else {
            // Add bookmark (enforce 15-item limit)
            if (this.bookmarks.length >= this.MAX_BOOKMARKS) {
                // Remove oldest bookmark (first in array)
                const removed = this.bookmarks.shift();
                this.log('Max bookmarks reached, removed oldest:', removed);
            }
            this.bookmarks.push(eventId);
            this.saveBookmarks();
            this.log('Bookmark added:', eventId);
            return true;
        }
    }
    
    /**
     * Check if an event is bookmarked
     * @param {string} eventId - Event ID to check
     * @returns {boolean} True if bookmarked
     */
    isBookmarked(eventId) {
        return this.bookmarks.includes(eventId);
    }
    
    /**
     * Get all bookmarked event IDs
     * @returns {Array} Array of bookmarked event IDs
     */
    getBookmarks() {
        return [...this.bookmarks];
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Storage]', message, ...args);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventStorage;
}

// ============================================================================
// MODULE 2: EventFilter - Filtering Logic
// ============================================================================
/**
 * EventFilter Module
 * 
 * Handles event filtering logic:
 * - Time-based filters (sunrise, full moon, hours)
 * - Distance-based filters
 * - Category filters
 * - Location calculations
 * 
 * KISS: Single responsibility - filtering logic only
 */

class EventFilter {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
    }
    
    /**
     * Calculate distance between two lat/lon coordinates (Haversine formula)
     * @param {number} lat1 - Latitude of first point
     * @param {number} lon1 - Longitude of first point
     * @param {number} lat2 - Latitude of second point
     * @param {number} lon2 - Longitude of second point
     * @returns {number} Distance in kilometers
     */
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    /**
     * Get maximum event time based on filter
     * @param {string} timeFilter - Time filter value (sunrise, 6h, 12h, etc.)
     * @returns {Date} Maximum event time
     */
    getMaxEventTime(timeFilter) {
        const now = new Date();
        
        switch (timeFilter) {
            case 'sunrise':
                return this.getNextSunrise();
                
            case 'sunday-primetime':
                return this.getNextSundayPrimetime();
                
            case 'full-moon':
                return this.getNextFullMoonMorning();
                
            case '6h':
                return new Date(now.getTime() + 6 * 60 * 60 * 1000);
                
            case '12h':
                return new Date(now.getTime() + 12 * 60 * 60 * 1000);
                
            case '24h':
                return new Date(now.getTime() + 24 * 60 * 60 * 1000);
                
            case '48h':
                return new Date(now.getTime() + 48 * 60 * 60 * 1000);
                
            case 'all':
                return new Date(now.getFullYear() + 10, 11, 31);
                
            default:
                return this.getNextSunrise();
        }
    }
    
    /**
     * Get next sunrise time (simplified: 6 AM)
     * @returns {Date} Next sunrise
     */
    getNextSunrise() {
        const now = new Date();
        const sunrise = new Date(now);
        sunrise.setHours(6, 0, 0, 0);
        
        if (now.getHours() >= 6) {
            sunrise.setDate(sunrise.getDate() + 1);
        }
        
        return sunrise;
    }
    
    /**
     * Get next Sunday at primetime (20:15)
     * @returns {Date} Next Sunday at 20:15
     */
    getNextSundayPrimetime() {
        const now = new Date();
        const result = new Date(now);
        
        // Get current day of week (0 = Sunday, 1 = Monday, etc.)
        const currentDay = now.getDay();
        
        // Calculate days until next Sunday
        let daysUntilSunday;
        if (currentDay === 0) {
            // It's Sunday - check if we're past 20:15
            const currentTime = now.getHours() * 60 + now.getMinutes();
            const primetimeMinutes = 20 * 60 + 15;
            
            if (currentTime >= primetimeMinutes) {
                daysUntilSunday = 7;
            } else {
                daysUntilSunday = 0;
            }
        } else {
            daysUntilSunday = 7 - currentDay;
        }
        
        result.setDate(result.getDate() + daysUntilSunday);
        result.setHours(20, 15, 0, 0);
        
        return result;
    }
    
    /**
     * Get morning after next full moon following next Sunday
     * @returns {Date} 6am on day after next full moon
     */
    getNextFullMoonMorning() {
        const nextSunday = new Date(this.getNextSundayPrimetime().getTime());
        nextSunday.setHours(0, 0, 0, 0);
        
        // Known full moon: January 6, 2000, 18:14 UTC
        const knownFullMoon = new Date(Date.UTC(2000, 0, 6, 18, 14, 0));
        
        // Lunar cycle length in milliseconds
        const lunarCycle = 29.53058770576 * 24 * 60 * 60 * 1000;
        
        // Calculate cycles since known full moon
        const now = new Date();
        const timeSinceKnownFullMoon = now.getTime() - knownFullMoon.getTime();
        const cyclesSinceKnown = Math.floor(timeSinceKnownFullMoon / lunarCycle);
        
        // Find first full moon after next Sunday
        let fullMoon = new Date(knownFullMoon.getTime() + cyclesSinceKnown * lunarCycle);
        
        while (fullMoon <= nextSunday) {
            fullMoon = new Date(fullMoon.getTime() + lunarCycle);
        }
        
        // Set to 6am of day after full moon
        const dayAfterFullMoon = new Date(fullMoon);
        dayAfterFullMoon.setDate(dayAfterFullMoon.getDate() + 1);
        dayAfterFullMoon.setHours(6, 0, 0, 0);
        
        return dayAfterFullMoon;
    }
    
    /**
     * Filter events based on current filter settings
     * @param {Array} events - All events
     * @param {Object} filters - Filter settings
     * @param {Object} referenceLocation - Location to calculate distance from
     * @returns {Array} Filtered events
     */
    filterEvents(events, filters, referenceLocation) {
        const maxEventTime = this.getMaxEventTime(filters.timeFilter);
        const maxDistance = filters.maxDistance;
        const category = filters.category;
        
        const filtered = events.filter(event => {
            // Always include bookmarked events
            if (this.storage.isBookmarked(event.id)) {
                // Calculate distance even for bookmarked events
                if (referenceLocation && event.location) {
                    const distance = this.calculateDistance(
                        referenceLocation.lat,
                        referenceLocation.lon,
                        event.location.lat,
                        event.location.lon
                    );
                    event.distance = distance;
                }
                return true;
            }
            
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                return false;
            }
            
            // Filter by category
            if (category !== 'all' && event.category !== category) {
                return false;
            }
            
            // Filter by distance if location is available
            if (referenceLocation && event.location) {
                const distance = this.calculateDistance(
                    referenceLocation.lat,
                    referenceLocation.lon,
                    event.location.lat,
                    event.location.lon
                );
                event.distance = distance;
                
                if (distance > maxDistance) {
                    return false;
                }
            }
            
            return true;
        });
        
        return filtered;
    }
    
    /**
     * Count category occurrences under current filter conditions (excluding category filter)
     * @param {Array} events - All events
     * @param {Object} filters - Filter settings (category ignored)
     * @param {Object} referenceLocation - Location to calculate distance from
     * @returns {Object} Map of category names to their occurrence counts
     */
    countCategoriesUnderFilters(events, filters, referenceLocation) {
        const maxEventTime = this.getMaxEventTime(filters.timeFilter);
        const maxDistance = filters.maxDistance;
        
        const categoryCounts = {};
        
        events.forEach(event => {
            // Count bookmarked events regardless of other filters
            if (this.storage.isBookmarked(event.id)) {
                const cat = event.category || 'uncategorized';
                categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
                return;
            }
            
            // Filter by time
            const eventTime = new Date(event.start_time);
            if (eventTime > maxEventTime) {
                return;
            }
            
            // Filter by distance if location is available
            if (referenceLocation && event.location) {
                const distance = this.calculateDistance(
                    referenceLocation.lat,
                    referenceLocation.lon,
                    event.location.lat,
                    event.location.lon
                );
                
                if (distance > maxDistance) {
                    return;
                }
            }
            
            // Count this event's category
            const cat = event.category || 'uncategorized';
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
        
        return categoryCounts;
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Filter]', message, ...args);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventFilter;
}

// ============================================================================
// MODULE 3: MapManager - Leaflet Map Management
// ============================================================================
/**
 * MapManager Module
 * 
 * Handles all Leaflet.js map operations:
 * - Map initialization
 * - Marker management
 * - User location tracking
 * - Map bounds and zoom
 * 
 * KISS: Single responsibility - map management only
 */

class MapManager {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.map = null;
        this.markers = [];
        this.userLocation = null;
    }
    
    /**
     * Initialize Leaflet map
     * @param {string} containerId - DOM element ID for map container
     */
    initMap(containerId = 'map') {
        const center = this.config.map.default_center;
        
        // Disable zoom controls - use keyboard shortcuts or pinch zoom
        this.map = L.map(containerId, {
            zoomControl: false,
            attributionControl: false
        }).setView([center.lat, center.lon], this.config.map.default_zoom);
        
        L.tileLayer(this.config.map.tile_provider, {
            attribution: this.config.map.attribution
        }).addTo(this.map);
        
        this.log('Map initialized', center);
    }
    
    /**
     * Setup Leaflet event prevention on UI overlays
     * Prevents map interactions when clicking/scrolling on UI elements
     */
    setupLeafletEventPrevention() {
        if (typeof L === 'undefined' || !L.DomEvent) {
            this.log('Leaflet DomEvent not available, skipping event prevention');
            return;
        }
        
        // Prevent map interactions on filter bar
        const filterBar = document.getElementById('event-filter-bar');
        if (filterBar) {
            L.DomEvent.disableClickPropagation(filterBar);
            L.DomEvent.disableScrollPropagation(filterBar);
            this.log('Event prevention enabled for filter bar');
        }
        
        // Prevent map interactions on dashboard
        const dashboard = document.getElementById('dashboard-menu');
        if (dashboard) {
            L.DomEvent.disableClickPropagation(dashboard);
            L.DomEvent.disableScrollPropagation(dashboard);
            this.log('Event prevention enabled for dashboard');
        }
    }
    
    /**
     * Get user's geolocation
     * @param {Function} onSuccess - Callback with location {lat, lon}
     * @param {Function} onError - Callback with error
     */
    getUserLocation(onSuccess, onError) {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    this.log('User location obtained', this.userLocation);
                    
                    // Center map on user location
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                        this.addUserMarker();
                    }
                    
                    if (onSuccess) onSuccess(this.userLocation);
                },
                (error) => {
                    console.error('Location error:', error);
                    
                    // Use default location as fallback
                    const defaultCenter = this.config.map.default_center;
                    this.userLocation = {
                        lat: defaultCenter.lat,
                        lon: defaultCenter.lon
                    };
                    
                    if (this.map) {
                        this.map.setView([this.userLocation.lat, this.userLocation.lon], 13);
                    }
                    
                    if (onError) onError(error);
                }
            );
        } else {
            // Use default location as fallback
            const defaultCenter = this.config.map.default_center;
            this.userLocation = {
                lat: defaultCenter.lat,
                lon: defaultCenter.lon
            };
            
            if (onError) onError(new Error('Geolocation not supported'));
        }
    }
    
    /**
     * Add user location marker to map
     */
    addUserMarker() {
        if (!this.map || !this.userLocation) return;
        
        // Get user marker config
        const userMarkerConfig = this.config.map.user_location_marker || {};
        const userIconUrl = userMarkerConfig.icon || 
            (window.MARKER_ICONS && window.MARKER_ICONS['marker-geolocation']) ||
            'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI4IiBmaWxsPSIjNENBRjUwIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjMiIGZpbGw9IiNmZmYiLz48L3N2Zz4=';
        const userIconSize = userMarkerConfig.size || [32, 48];
        const userIconAnchor = userMarkerConfig.anchor || [userIconSize[0] / 2, userIconSize[1]];
        const userPopupAnchor = userMarkerConfig.popup_anchor || [0, -userIconSize[1]];
        
        const userIcon = L.icon({
            iconUrl: userIconUrl,
            iconSize: userIconSize,
            iconAnchor: userIconAnchor,
            popupAnchor: userPopupAnchor
        });
        
        L.marker([this.userLocation.lat, this.userLocation.lon], {
            icon: userIcon
        }).addTo(this.map).bindPopup('You are here');
        
        this.log('User marker added');
    }
    
    /**
     * Add event marker to map
     * @param {Object} event - Event data
     * @param {Function} onClick - Click handler
     * @returns {Object} Leaflet marker
     */
    addEventMarker(event, onClick) {
        if (!this.map || !event.location) return null;
        
        // Get marker icon based on category
        const category = event.category || 'default';
        const iconUrl = window.MARKER_ICONS && window.MARKER_ICONS[`marker-${category}`] || 
            window.MARKER_ICONS && window.MARKER_ICONS['marker-default'] ||
            'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjRkY2OUI0IiBkPSJNMTIgMkM4LjEzIDIgNSA1LjEzIDUgOWMwIDUuMjUgNyAxMyA3IDEzczctNy43NSA3LTEzYzAtMy44Ny0zLjEzLTctNy03em0wIDkuNWMtMS4zOCAwLTIuNS0xLjEyLTIuNS0yLjVzMS4xMi0yLjUgMi41LTIuNSAyLjUgMS4xMiAyLjUgMi41LTEuMTIgMi41LTIuNSAyLjV6Ii8+PC9zdmc+';
        
        const markerIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [32, 48],
            iconAnchor: [16, 48],
            popupAnchor: [0, -48]
        });
        
        const marker = L.marker([event.location.lat, event.location.lon], {
            icon: markerIcon
        }).addTo(this.map);
        
        // Add bookmark class if bookmarked
        if (this.storage.isBookmarked(event.id)) {
            marker._icon.classList.add('bookmarked-marker');
        }
        
        // Store event data on marker
        marker.eventData = event;
        
        // Add click handler
        if (onClick) {
            marker.on('click', () => onClick(event, marker));
        }
        
        this.markers.push(marker);
        this.log('Marker added for event', event.title);
        
        return marker;
    }
    
    /**
     * Update marker bookmark state
     * @param {string} eventId - Event ID
     * @param {boolean} isBookmarked - Whether event is bookmarked
     */
    updateMarkerBookmarkState(eventId, isBookmarked) {
        this.markers.forEach(marker => {
            if (marker.eventData && marker.eventData.id === eventId) {
                if (isBookmarked) {
                    marker._icon.classList.add('bookmarked-marker');
                } else {
                    marker._icon.classList.remove('bookmarked-marker');
                }
            }
        });
    }
    
    /**
     * Clear all event markers from map
     */
    clearMarkers() {
        for (let i = 0; i < this.markers.length; i++) {
            this.markers[i].remove();
        }
        this.markers = [];
        this.log('All markers cleared');
    }
    
    /**
     * Fit map bounds to show all markers
     */
    fitMapToMarkers() {
        if (this.markers.length === 0 || !this.map) {
            return;
        }
        
        const bounds = L.latLngBounds();
        
        // Add all marker positions to bounds
        for (let i = 0; i < this.markers.length; i++) {
            bounds.extend(this.markers[i].getLatLng());
        }
        
        // Add user location to bounds if available
        if (this.userLocation) {
            bounds.extend([this.userLocation.lat, this.userLocation.lon]);
        }
        
        // Fit map to bounds with padding
        this.map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 15
        });
        
        this.log('Map fitted to markers');
    }
    
    /**
     * Center map on specific location
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} zoom - Zoom level (optional)
     */
    centerMap(lat, lon, zoom = 13) {
        if (this.map) {
            this.map.setView([lat, lon], zoom);
            this.log('Map centered', {lat, lon, zoom});
        }
    }
    
    /**
     * Invalidate map size (call after UI changes)
     */
    invalidateSize() {
        if (this.map) {
            this.map.invalidateSize();
        }
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Map]', message, ...args);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = MapManager;
}

// ============================================================================
// MODULE 4: SpeechBubbles - UI Bubble Components
// ============================================================================
/**
 * SpeechBubbles Module
 * 
 * Handles speech bubble UI elements that appear over map markers:
 * - Bubble creation and positioning
 * - Collision detection
 * - Deduplication logic
 * - Click handlers
 * 
 * KISS: Single responsibility - speech bubble management only
 */

class SpeechBubbles {
    constructor(config, storage) {
        this.config = config;
        this.storage = storage;
        this.speechBubbles = [];
        this.occupiedBubblePositions = [];
    }
    
    /**
     * Clear all speech bubbles from the map
     */
    clearSpeechBubbles() {
        this.speechBubbles.forEach(bubble => {
            if (bubble.parentElement) {
                bubble.remove();
            }
        });
        this.speechBubbles = [];
        this.occupiedBubblePositions = [];
    }
    
    /**
     * Show speech bubbles for all visible events
     * @param {Array} events - Filtered events to display
     * @param {Array} markers - Corresponding Leaflet markers
     * @param {Object} map - Leaflet map instance
     */
    showAllSpeechBubbles(events, markers, map) {
        this.clearSpeechBubbles();
        
        const maxBubbles = 30; // Limit to prevent performance issues
        const eventsToShow = events.slice(0, maxBubbles);
        
        // Build array of {event, marker, originalIndex} for deduplication
        const eventItems = eventsToShow.map((event, index) => ({
            event,
            marker: markers[index],
            originalIndex: index
        }));
        
        // Deduplicate events
        const uniqueItems = this.deduplicateEvents(eventItems);
        
        // Create speech bubbles for unique events
        uniqueItems.forEach((item, index) => {
            this.createSpeechBubble(
                item.event,
                item.marker,
                index,
                1, // groupSize (deprecated)
                0, // groupIndex (deprecated)
                item.duplicateCount,
                map
            );
        });
        
        this.log(`Showing ${uniqueItems.length} speech bubbles (${eventsToShow.length} total events)`);
    }
    
    /**
     * Deduplicate events based on title and start time
     * @param {Array} eventItems - Array of {event, marker, originalIndex}
     * @returns {Array} Array of unique items with duplicateCount property
     */
    deduplicateEvents(eventItems) {
        const uniqueMap = new Map();
        
        eventItems.forEach(item => {
            const title = item.event.title.toLowerCase().trim();
            const startTime = item.event.start_time;
            const key = `${title}|${startTime}`;
            
            if (uniqueMap.has(key)) {
                const existing = uniqueMap.get(key);
                existing.duplicateCount++;
                existing.duplicates.push(item.event);
            } else {
                uniqueMap.set(key, {
                    ...item,
                    duplicateCount: 1,
                    duplicates: [item.event]
                });
            }
        });
        
        return Array.from(uniqueMap.values());
    }
    
    /**
     * Create and position a speech bubble for an event
     * @param {Object} event - Event data
     * @param {Object} marker - Leaflet marker
     * @param {number} index - Display order index
     * @param {number} groupSize - Deprecated, kept for compatibility
     * @param {number} groupIndex - Deprecated, kept for compatibility
     * @param {number} duplicateCount - Number of duplicate events
     * @param {Object} map - Leaflet map instance
     */
    createSpeechBubble(event, marker, index, groupSize = 1, groupIndex = 0, duplicateCount = 1, map) {
        if (!marker || !map) return;
        
        // Get marker position in screen coordinates
        const markerPos = map.latLngToContainerPoint(marker.getLatLng());
        
        // Create bubble element
        const bubble = document.createElement('div');
        bubble.className = 'speech-bubble';
        bubble.setAttribute('data-event-id', event.id);
        
        // Format start time
        const startTime = new Date(event.start_time);
        const timeStr = startTime.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        const dateStr = startTime.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
        
        // Bookmark button
        const isBookmarked = this.storage.isBookmarked(event.id);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        const bookmarkingSupported = this.storage.isBookmarkingSupported();
        
        // Duplicate badge
        const duplicateBadge = duplicateCount > 1 ? 
            `<div class="bubble-duplicate-badge" title="${duplicateCount} duplicate events">×${duplicateCount}</div>` : '';
        
        bubble.innerHTML = `
            ${duplicateBadge}
            <div class="bubble-time-headline">${timeStr}</div>
            <div class="bubble-date">${dateStr}</div>
            <div class="bubble-title">${this.truncateText(event.title, 50)}</div>
            <div class="bubble-location">📍 ${this.truncateText(event.location.name, 30)}</div>
            ${event.distance !== undefined ? `<div class="bubble-distance">🚶 ${event.distance.toFixed(1)} km</div>` : ''}
            ${bookmarkingSupported ? `<button class="bubble-bookmark ${bookmarkClass}" data-event-id="${event.id}" title="Bookmark this event">
                <i data-lucide="heart" aria-hidden="true"></i>
            </button>` : ''}
        `;
        
        // Initialize Lucide icons
        if (bookmarkingSupported && typeof lucide !== 'undefined') {
            setTimeout(() => lucide.createIcons(), 10);
        }
        
        // Position bubble
        const position = this.calculateBubblePosition(markerPos, index);
        bubble.style.left = position.x + 'px';
        bubble.style.top = position.y + 'px';
        
        // Add to map container
        document.getElementById('map').appendChild(bubble);
        this.speechBubbles.push(bubble);
        
        // Fade in animation
        setTimeout(() => bubble.classList.add('visible'), 10);
        
        return bubble;
    }
    
    /**
     * Calculate position for speech bubble with collision detection
     * Uses blended randomness + predictable patterns for organic variety
     * @param {Object} markerPos - {x, y} marker screen position
     * @param {number} index - Bubble index
     * @returns {Object} {x, y} position for bubble
     */
    calculateBubblePosition(markerPos, index) {
        const bubbleWidth = 220;
        const bubbleHeight = 140;
        const mapContainer = document.getElementById('map');
        const viewportWidth = mapContainer.clientWidth;
        const viewportHeight = mapContainer.clientHeight;
        const margin = 10;
        const padding = 15; // Minimum spacing between bubbles
        
        // Helper: Check if two rectangles overlap
        const overlaps = (x1, y1, x2, y2) => {
            return !(x1 + bubbleWidth + padding < x2 || 
                     x2 + bubbleWidth + padding < x1 || 
                     y1 + bubbleHeight + padding < y2 || 
                     y2 + bubbleHeight + padding < y1);
        };
        
        // Try random positions with collision detection
        const maxAttempts = 100;
        let attempt = 0;
        
        while (attempt < maxAttempts) {
            // Semi-random offset with index-based bias
            const distance = 60 + Math.random() * 140;
            const randomAngle = Math.random() * 2 * Math.PI;
            const indexBias = (index * 0.5) % (2 * Math.PI);
            const angle = randomAngle + indexBias;
            
            let x = markerPos.x + Math.cos(angle) * distance;
            let y = markerPos.y + Math.sin(angle) * distance;
            
            // Clamp to viewport bounds
            x = Math.max(margin, Math.min(x, viewportWidth - bubbleWidth - margin));
            y = Math.max(margin, Math.min(y, viewportHeight - bubbleHeight - margin));
            
            // Check for overlaps
            let hasOverlap = false;
            for (const occupied of this.occupiedBubblePositions) {
                if (overlaps(x, y, occupied.x, occupied.y)) {
                    hasOverlap = true;
                    break;
                }
            }
            
            if (!hasOverlap) {
                this.occupiedBubblePositions.push({ x, y });
                return { x, y };
            }
            
            attempt++;
        }
        
        // Fallback: Spiral pattern with golden angle
        const spiralAttempts = 30;
        for (let i = 0; i < spiralAttempts; i++) {
            const spiralRadius = 80 + (i * 30);
            const goldenAngle = (index + i) * 0.618 * 2 * Math.PI;
            const randomOffset = (Math.random() - 0.5) * 0.5;
            const spiralAngle = goldenAngle + randomOffset;
            
            let x = markerPos.x + Math.cos(spiralAngle) * spiralRadius;
            let y = markerPos.y + Math.sin(spiralAngle) * spiralRadius;
            
            x = Math.max(margin, Math.min(x, viewportWidth - bubbleWidth - margin));
            y = Math.max(margin, Math.min(y, viewportHeight - bubbleHeight - margin));
            
            let hasOverlap = false;
            for (const occupied of this.occupiedBubblePositions) {
                if (overlaps(x, y, occupied.x, occupied.y)) {
                    hasOverlap = true;
                    break;
                }
            }
            
            if (!hasOverlap) {
                this.occupiedBubblePositions.push({ x, y });
                return { x, y };
            }
        }
        
        // Last resort: Grid layout
        const gridCellWidth = bubbleWidth + padding + 15;
        const gridCellHeight = bubbleHeight + padding + 5;
        const gridColumns = Math.floor(viewportWidth / gridCellWidth);
        
        const gridX = (index % gridColumns) * gridCellWidth + margin;
        const gridY = Math.floor(index / gridColumns) * gridCellHeight + margin;
        
        const forceX = Math.min(gridX, viewportWidth - bubbleWidth - margin);
        const forceY = Math.min(gridY, viewportHeight - bubbleHeight - margin);
        
        this.occupiedBubblePositions.push({ x: forceX, y: forceY });
        return { x: forceX, y: forceY };
    }
    
    /**
     * Truncate text to max length with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated text
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[SpeechBubbles]', message, ...args);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechBubbles;
}

// ============================================================================
// MODULE 5: EventUtils - Utility Functions
// ============================================================================
/**
 * EventUtils Module
 * 
 * Utility functions for event processing:
 * - Template event processing (dynamic relative times)
 * - Date formatting
 * - DOM caching
 * 
 * KISS: Single responsibility - utility functions only
 */

class EventUtils {
    constructor(config) {
        this.config = config;
        this.domCache = {};
    }
    
    /**
     * Process template events with relative_time specifications
     * @param {Array} events - Array of events
     * @param {Object} filterModule - Filter module for getNextSunrise
     * @returns {Array} Processed events with computed timestamps
     */
    processTemplateEvents(events, filterModule) {
        const now = new Date();
        
        return events.map(event => {
            if (!event.relative_time) {
                return event;
            }
            
            const processedEvent = { ...event };
            const spec = event.relative_time;
            const type = spec.type;
            
            let startTime, endTime;
            
            if (type === 'offset') {
                startTime = new Date(now);
                
                if (spec.hours) {
                    startTime.setHours(startTime.getHours() + spec.hours);
                }
                
                if (spec.minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.minutes);
                }
                
                const durationMs = (spec.duration_hours || 2) * 60 * 60 * 1000;
                endTime = new Date(startTime.getTime() + durationMs);
                
                const tzOffset = spec.timezone_offset || 0;
                if (tzOffset !== 0) {
                    const sign = tzOffset >= 0 ? '+' : '-';
                    const hours = Math.abs(Math.floor(tzOffset));
                    const minutes = Math.abs((tzOffset % 1) * 60);
                    const tzString = `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
                    
                    processedEvent.start_time = this.formatDateTimeWithTZ(startTime, tzString);
                    processedEvent.end_time = this.formatDateTimeWithTZ(endTime, tzString);
                } else {
                    processedEvent.start_time = this.formatDateTime(startTime);
                    processedEvent.end_time = this.formatDateTime(endTime);
                }
                
            } else if (type === 'sunrise_relative') {
                const sunrise = filterModule.getNextSunrise();
                
                startTime = new Date(sunrise);
                if (spec.start_offset_hours) {
                    startTime.setHours(startTime.getHours() + spec.start_offset_hours);
                }
                if (spec.start_offset_minutes) {
                    startTime.setMinutes(startTime.getMinutes() + spec.start_offset_minutes);
                }
                
                endTime = new Date(sunrise);
                if (spec.end_offset_hours) {
                    endTime.setHours(endTime.getHours() + spec.end_offset_hours);
                }
                if (spec.end_offset_minutes) {
                    endTime.setMinutes(endTime.getMinutes() + spec.end_offset_minutes);
                }
                
                processedEvent.start_time = this.formatDateTime(startTime);
                processedEvent.end_time = this.formatDateTime(endTime);
            }
            
            processedEvent.published_at = this.formatDateTime(now);
            
            return processedEvent;
        });
    }
    
    /**
     * Format date as ISO 8601 without timezone
     * @param {Date} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDateTime(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    }
    
    /**
     * Format date as ISO 8601 with timezone
     * @param {Date} date - Date to format
     * @param {string} tzString - Timezone string (e.g., "+02:00")
     * @returns {string} Formatted date string with timezone
     */
    formatDateTimeWithTZ(date, tzString) {
        return this.formatDateTime(date) + tzString;
    }
    
    /**
     * Get cached DOM element or query and cache it
     * Reduces repeated querySelectorAll/querySelector calls
     * @param {string} selector - CSS selector
     * @param {boolean} multiple - If true, use querySelectorAll
     * @returns {Element|NodeList|null} Cached or newly queried element(s)
     */
    getCachedElement(selector, multiple = false) {
        const cacheKey = `${multiple ? 'all:' : ''}${selector}`;
        
        if (!this.domCache[cacheKey]) {
            this.domCache[cacheKey] = multiple 
                ? document.querySelectorAll(selector)
                : document.querySelector(selector);
        }
        
        return this.domCache[cacheKey];
    }
    
    /**
     * Clear DOM cache (call when DOM structure changes)
     */
    clearDOMCache() {
        this.domCache = {};
    }
    
    /**
     * Update viewport dimensions in CSS custom properties
     * Ensures all layers scale consistently
     */
    updateViewportDimensions() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        document.documentElement.style.setProperty('--app-width', `${width}px`);
        document.documentElement.style.setProperty('--app-height', `${height}px`);
        
        this.log(`Viewport updated: ${width}x${height}`);
    }
    
    /**
     * Show visual feedback when bookmarking
     * @param {boolean} bookmarked - True if bookmarked, false if unbookmarked
     */
    showBookmarkFeedback(bookmarked) {
        const message = bookmarked ? '❤️ Event bookmarked!' : '🤍 Bookmark removed';
        
        const feedback = document.createElement('div');
        feedback.className = 'bookmark-feedback';
        feedback.textContent = message;
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.classList.add('fade-out');
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.parentNode.removeChild(feedback);
                }
            }, 300);
        }, 2000);
    }
    
    /**
     * Get default config fallback
     * @returns {Object} Default configuration
     */
    getDefaultConfig() {
        console.warn('window.APP_CONFIG not found, using fallback defaults');
        return {
            debug: false,
            app: {
                environment: 'unknown'
            },
            map: {
                default_center: { lat: 50.3167, lon: 11.9167 },
                default_zoom: 13,
                tile_provider: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            },
            data: {
                source: 'real',
                sources: {}
            }
        };
    }
    
    /**
     * Debug logging helper
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[Utils]', message, ...args);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventUtils;
}

// ============================================================================
// MODULE 6: EventsApp - Main Application (Coordinator)
// ============================================================================
