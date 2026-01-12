# app.js Refactoring Plan - KISS Compliance

## Current State
- **app.js**: 3344 lines (6.7x over 500-line KISS limit)
- **Problem**: Monolithic class, hard to maintain, violates KISS principles

## Solution: Module Extraction

### Completed Modules (All < 500 lines ✅)

1. **storage.js** (180 lines) - Data persistence
   - localStorage/cookie operations
   - Bookmark management (15-item limit)
   - Browser feature detection
   - Methods: loadBookmarks, saveBookmarks, toggleBookmark, isBookmarked, saveFiltersToCookie, loadFiltersFromCookie

2. **filters.js** (281 lines) - Event filtering logic
   - Distance calculations (Haversine formula)
   - Time-based filters (sunrise, full moon, hours)
   - Category counting
   - Methods: filterEvents, getMaxEventTime, getNextSunrise, getNextSundayPrimetime, getNextFullMoonMorning, calculateDistance, countCategoriesUnderFilters

3. **map.js** (288 lines) - Leaflet map management
   - Map initialization
   - Marker management
   - User location tracking
   - Bounds fitting
   - Methods: initMap, getUserLocation, addEventMarker, clearMarkers, fitMapToMarkers, centerMap, updateMarkerBookmarkState

4. **speech-bubbles.js** (302 lines) - UI bubble components
   - Bubble creation and positioning
   - Collision detection (prevents overlaps)
   - Deduplication logic
   - Methods: showAllSpeechBubbles, createSpeechBubble, calculateBubblePosition, clearSpeechBubbles, deduplicateEvents

5. **utils.js** (219 lines) - Utility functions
   - Template event processing (dynamic relative times)
   - Date formatting
   - DOM caching
   - Viewport management
   - Methods: processTemplateEvents, formatDateTime, getCachedElement, updateViewportDimensions, showBookmarkFeedback

### Remaining in app.js (~500-800 lines target)

**Core Responsibilities:**
- App initialization and coordination
- Event loading and processing
- Dashboard updates (debug info, duplicate warnings, pending events)
- Filter bar UI updates
- Event listeners setup (dashboard, filters, keyboard shortcuts)
- Event detail popups
- Weather display

**Key Methods to Keep:**
- init() - Initialize app and modules
- loadEvents() - Fetch and process events
- displayEvents() - Coordinate filtering, markers, bubbles
- updateDashboard() - Update debug dashboard
- updateFilterDescription() - Update filter sentence UI
- setupEventListeners() - Setup all UI interactions
- showEventDetail() - Show event detail popup
- loadWeather() / displayWeatherDresscode() - Weather integration
- checkPendingEvents() / startPendingEventsPolling() - Pending event notifications

### Integration Pattern

```javascript
class EventsApp {
    constructor() {
        // Initialize modules
        this.config = window.APP_CONFIG || EventUtils.getDefaultConfig();
        this.storage = new EventStorage(this.config);
        this.filters = new EventFilter(this.config, this.storage);
        this.mapManager = new MapManager(this.config, this.storage);
        this.speechBubbles = new SpeechBubbles(this.config, this.storage);
        this.utils = new EventUtils(this.config);
        
        // App state
        this.events = [];
        this.currentEventIndex = null;
        this.duplicateStats = null;
        
        // Filter settings
        this.filterSettings = this.storage.loadFiltersFromCookie() || {/* defaults */};
        
        this.init();
    }
    
    // Delegate to modules
    displayEvents() {
        // Use filters.filterEvents()
        // Use mapManager.clearMarkers() and addEventMarker()
        // Use speechBubbles.showAllSpeechBubbles()
    }
}
```

## Benefits

✅ **KISS Compliant**: Each file < 500 lines
✅ **Single Responsibility**: Each module has one clear purpose
✅ **Testable**: Modules can be tested independently
✅ **Maintainable**: Easier to understand and modify
✅ **Reusable**: Modules can be used in other contexts
✅ **Backwards Compatible**: Same API, just refactored internally

## Implementation Status

- [x] Phase 1: Create storage.js
- [x] Phase 2: Create filters.js
- [x] Phase 3: Create map.js
- [x] Phase 4: Create speech-bubbles.js
- [x] Phase 5: Create utils.js
- [ ] Phase 6: Refactor app.js to use modules
- [ ] Phase 7: Update HTML to include all JS files
- [ ] Phase 8: Test and verify functionality
- [ ] Phase 9: Run KISS checker for compliance

## Testing Strategy

1. **Unit Tests** (if test infrastructure exists):
   - Test each module independently
   - Verify methods return expected values

2. **Integration Tests**:
   - Use existing HTML test files
   - Verify map loads correctly
   - Verify filters work
   - Verify bookmarks persist
   - Verify speech bubbles display

3. **Manual Testing**:
   - Load app in browser
   - Check console for errors
   - Test all filters
   - Test bookmarking
   - Test dashboard
   - Test keyboard shortcuts

4. **KISS Compliance**:
   - Run: `python3 src/modules/kiss_checker.py --repo-root . --verbose`
   - Verify all files < 500 lines
   - Verify no violations

## File Size Targets

| File | Current | Target | Status |
|------|---------|--------|--------|
| app.js | 3344 | <500 | 🚧 In Progress |
| storage.js | 180 | <500 | ✅ Done |
| filters.js | 281 | <500 | ✅ Done |
| map.js | 288 | <500 | ✅ Done |
| speech-bubbles.js | 302 | <500 | ✅ Done |
| utils.js | 219 | <500 | ✅ Done |

## Next Actions

1. Create minimal refactored app.js (delegate to modules)
2. Update component HTML templates to include new JS files
3. Test functionality
4. Update features.json if needed
5. Run KISS checker
6. Submit PR

