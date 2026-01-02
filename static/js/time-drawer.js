/**
 * TimeDrawer - Dynamic time-based marker resizing with interactive timeline
 * 
 * Features:
 * - Interactive timeline slider from "Now" to "Sunrise"
 * - Draggable handle with smooth animations
 * - Dynamic marker scaling based on time proximity
 * - Activation rules: "til sunrise" filter + minimum 5 events
 * - Mobile touch support
 */

class TimeDrawer {
    constructor(map, events, getSunriseCallback, config = {}) {
        this.map = map;
        this.events = events;
        this.getSunriseCallback = getSunriseCallback;
        
        // Configuration with defaults
        this.config = {
            minSize: config.minSize || 0.7,              // 70% minimum scale
            maxSize: config.maxSize || 1.3,              // 130% maximum scale
            baseSize: config.baseSize || 32,             // Base icon size in pixels
            transitionDuration: config.transitionDuration || 300, // Animation duration in ms
            minEventsThreshold: config.minEventsThreshold || 5,   // Minimum events to enable
            updateInterval: config.updateInterval || 60000        // Update interval in ms (1 minute)
        };
        
        this.enabled = false;
        this.drawerElement = null;
        this.handleElement = null;
        this.progressElement = null;
        this.timeDisplayElement = null;
        this.thresholdMessageElement = null;
        
        // Marker registry: { eventId: { marker, event } }
        this.registeredMarkers = new Map();
        
        // Drag state
        this.isDragging = false;
        this.currentPosition = 0; // 0 to 1, where 0 = now, 1 = sunrise
        
        // Update timer
        this.updateTimer = null;
        
        // Bind methods
        this.onMouseDown = this.onMouseDown.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        this.onTouchStart = this.onTouchStart.bind(this);
        this.onTouchMove = this.onTouchMove.bind(this);
        this.onTouchEnd = this.onTouchEnd.bind(this);
        this.onTrackClick = this.onTrackClick.bind(this);
    }
    
    /**
     * Enable the time drawer if conditions are met
     * @param {string} filterType - Current filter type
     * @param {number} eventCount - Number of visible events
     */
    enable(filterType, eventCount) {
        // Check activation conditions
        if (filterType !== 'sunrise') {
            this.disable();
            return;
        }
        
        if (eventCount < this.config.minEventsThreshold) {
            this.disable();
            this.showThresholdMessage(eventCount);
            return;
        }
        
        // Check if sunrise time is available
        const sunriseTime = this.getSunriseCallback();
        if (!sunriseTime) {
            this.disable();
            return;
        }
        
        this.enabled = true;
        this.createDrawerUI();
        this.startUpdateTimer();
        this.updateMarkerSizes();
    }
    
    /**
     * Disable and remove the time drawer
     */
    disable() {
        this.enabled = false;
        this.stopUpdateTimer();
        this.removeDrawerUI();
        this.resetMarkerSizes();
        this.hideThresholdMessage();
    }
    
    /**
     * Create the drawer UI elements
     */
    createDrawerUI() {
        // Remove existing drawer if present
        this.removeDrawerUI();
        
        // Create container
        this.drawerElement = document.createElement('div');
        this.drawerElement.id = 'time-drawer';
        this.drawerElement.className = 'time-drawer';
        
        // Create content structure
        this.drawerElement.innerHTML = `
            <div class="time-drawer-header">
                <span class="time-drawer-label">Time Explorer</span>
                <span class="time-drawer-event-count" id="time-drawer-event-count">0 events</span>
            </div>
            <div class="time-drawer-track" id="time-drawer-track">
                <div class="time-drawer-progress" id="time-drawer-progress"></div>
                <div class="time-drawer-handle" id="time-drawer-handle">
                    <div class="time-drawer-handle-time" id="time-drawer-handle-time">Now</div>
                </div>
            </div>
            <div class="time-drawer-labels">
                <span class="time-drawer-label-start">Now</span>
                <span class="time-drawer-label-end">Sunrise</span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(this.drawerElement);
        
        // Get references
        this.handleElement = document.getElementById('time-drawer-handle');
        this.progressElement = document.getElementById('time-drawer-progress');
        this.timeDisplayElement = document.getElementById('time-drawer-handle-time');
        this.eventCountElement = document.getElementById('time-drawer-event-count');
        
        // Make draggable
        this.makeDrawerDraggable();
        
        // Update display
        this.updateEventCount();
        this.updateDrawerPosition();
        
        // Fade in animation
        requestAnimationFrame(() => {
            this.drawerElement.classList.add('visible');
        });
    }
    
    /**
     * Remove the drawer UI
     */
    removeDrawerUI() {
        if (this.drawerElement) {
            this.drawerElement.classList.remove('visible');
            setTimeout(() => {
                if (this.drawerElement && this.drawerElement.parentElement) {
                    this.drawerElement.remove();
                }
                this.drawerElement = null;
                this.handleElement = null;
                this.progressElement = null;
                this.timeDisplayElement = null;
            }, 300); // Match CSS transition duration
        }
    }
    
    /**
     * Make the drawer draggable
     */
    makeDrawerDraggable() {
        if (!this.handleElement) return;
        
        // Mouse events
        this.handleElement.addEventListener('mousedown', this.onMouseDown);
        
        // Touch events
        this.handleElement.addEventListener('touchstart', this.onTouchStart, { passive: false });
        
        // Track click to jump
        const trackElement = document.getElementById('time-drawer-track');
        if (trackElement) {
            trackElement.addEventListener('click', this.onTrackClick);
        }
    }
    
    onMouseDown(e) {
        e.preventDefault();
        this.isDragging = true;
        this.handleElement.classList.add('dragging');
        document.addEventListener('mousemove', this.onMouseMove);
        document.addEventListener('mouseup', this.onMouseUp);
    }
    
    onMouseMove(e) {
        if (!this.isDragging) return;
        this.updatePositionFromMouseEvent(e);
    }
    
    onMouseUp(e) {
        this.isDragging = false;
        this.handleElement.classList.remove('dragging');
        document.removeEventListener('mousemove', this.onMouseMove);
        document.removeEventListener('mouseup', this.onMouseUp);
    }
    
    onTouchStart(e) {
        e.preventDefault();
        this.isDragging = true;
        this.handleElement.classList.add('dragging');
        document.addEventListener('touchmove', this.onTouchMove, { passive: false });
        document.addEventListener('touchend', this.onTouchEnd);
    }
    
    onTouchMove(e) {
        e.preventDefault();
        if (!this.isDragging) return;
        this.updatePositionFromTouchEvent(e);
    }
    
    onTouchEnd(e) {
        this.isDragging = false;
        this.handleElement.classList.remove('dragging');
        document.removeEventListener('touchmove', this.onTouchMove);
        document.removeEventListener('touchend', this.onTouchEnd);
    }
    
    onTrackClick(e) {
        if (e.target.id !== 'time-drawer-track' && e.target.id !== 'time-drawer-progress') return;
        this.updatePositionFromMouseEvent(e);
    }
    
    /**
     * Update position from mouse event
     */
    updatePositionFromMouseEvent(e) {
        const trackElement = document.getElementById('time-drawer-track');
        if (!trackElement) return;
        
        const rect = trackElement.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const newPosition = Math.max(0, Math.min(1, x / rect.width));
        
        this.currentPosition = newPosition;
        this.updateDrawerPosition();
        this.updateMarkerSizes();
    }
    
    /**
     * Update position from touch event
     */
    updatePositionFromTouchEvent(e) {
        if (e.touches.length === 0) return;
        
        const trackElement = document.getElementById('time-drawer-track');
        if (!trackElement) return;
        
        const rect = trackElement.getBoundingClientRect();
        const x = e.touches[0].clientX - rect.left;
        const newPosition = Math.max(0, Math.min(1, x / rect.width));
        
        this.currentPosition = newPosition;
        this.updateDrawerPosition();
        this.updateMarkerSizes();
    }
    
    /**
     * Update drawer visual position
     */
    updateDrawerPosition() {
        if (!this.handleElement || !this.progressElement) return;
        
        const percentage = this.currentPosition * 100;
        this.handleElement.style.left = `${percentage}%`;
        this.progressElement.style.width = `${percentage}%`;
        
        this.updateHandleTime();
    }
    
    /**
     * Calculate time percentage for a target time
     */
    calculateTimePercentage(targetTime) {
        const now = new Date();
        const sunriseTime = this.getSunriseCallback();
        if (!sunriseTime) return 0;
        
        const totalDuration = sunriseTime.getTime() - now.getTime();
        if (totalDuration <= 0) return 0;
        
        const elapsed = targetTime.getTime() - now.getTime();
        return Math.max(0, Math.min(1, elapsed / totalDuration));
    }
    
    /**
     * Get the current drawer time
     */
    getDrawerTime() {
        const now = new Date();
        const sunriseTime = this.getSunriseCallback();
        if (!sunriseTime) return now;
        
        const totalDuration = sunriseTime.getTime() - now.getTime();
        const drawerTimeMs = now.getTime() + (totalDuration * this.currentPosition);
        
        return new Date(drawerTimeMs);
    }
    
    /**
     * Update the handle time display
     */
    updateHandleTime() {
        if (!this.timeDisplayElement) return;
        
        if (this.currentPosition === 0) {
            this.timeDisplayElement.textContent = 'Now';
            return;
        }
        
        const drawerTime = this.getDrawerTime();
        const sunriseTime = this.getSunriseCallback();
        
        if (this.currentPosition >= 0.99 && sunriseTime) {
            this.timeDisplayElement.textContent = 'Sunrise';
            return;
        }
        
        // Format time
        const hours = drawerTime.getHours();
        const minutes = drawerTime.getMinutes();
        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        
        this.timeDisplayElement.textContent = timeString;
    }
    
    /**
     * Update marker sizes based on current drawer position
     */
    updateMarkerSizes() {
        if (!this.enabled) return;
        
        const drawerTime = this.getDrawerTime();
        
        this.registeredMarkers.forEach((markerData, eventId) => {
            const scale = this.calculateMarkerScale(markerData.event, drawerTime);
            this.applyMarkerScale(markerData.marker, scale);
        });
    }
    
    /**
     * Calculate marker scale for an event
     * @param {Object} event - Event object with start_time
     * @param {Date} drawerTime - Current drawer time
     * @returns {number} Scale factor (0.7 to 1.3)
     */
    calculateMarkerScale(event, drawerTime) {
        const eventTime = new Date(event.start_time);
        const timeDiff = eventTime.getTime() - drawerTime.getTime();
        
        // Past events (before drawer time): 70% size
        if (timeDiff < 0) {
            return this.config.minSize;
        }
        
        // Very soon (within 15 minutes): 130% size (maximum)
        const fifteenMinutes = 15 * 60 * 1000;
        if (timeDiff <= fifteenMinutes) {
            return this.config.maxSize;
        }
        
        // Near (within 1 hour): 100-130% size (smooth gradient)
        const oneHour = 60 * 60 * 1000;
        if (timeDiff <= oneHour) {
            const ratio = 1 - (timeDiff / oneHour);
            return 1.0 + (ratio * (this.config.maxSize - 1.0));
        }
        
        // Future events: 100-70% size (based on distance to sunrise)
        const sunriseTime = this.getSunriseCallback();
        if (!sunriseTime) return 1.0;
        
        const timeToSunrise = sunriseTime.getTime() - drawerTime.getTime();
        if (timeToSunrise <= 0) return this.config.minSize;
        
        const eventTimeToSunrise = sunriseTime.getTime() - eventTime.getTime();
        if (eventTimeToSunrise <= 0) return this.config.minSize;
        
        const ratio = eventTimeToSunrise / timeToSunrise;
        return 1.0 - (ratio * (1.0 - this.config.minSize));
    }
    
    /**
     * Apply scale to a marker
     * @param {L.Marker} marker - Leaflet marker
     * @param {number} scale - Scale factor
     */
    applyMarkerScale(marker, scale) {
        const icon = marker.options.icon;
        if (!icon) return;
        
        const iconElement = marker._icon;
        if (!iconElement) return;
        
        // Apply CSS transform for smooth scaling
        iconElement.style.transition = `transform ${this.config.transitionDuration}ms ease-out`;
        iconElement.style.transform = `scale(${scale})`;
        iconElement.style.transformOrigin = 'bottom center';
        
        // Add highlight effect for largest markers (scale >= 1.2)
        if (scale >= 1.2) {
            iconElement.classList.add('time-drawer-highlight');
        } else {
            iconElement.classList.remove('time-drawer-highlight');
        }
    }
    
    /**
     * Reset all markers to default size
     */
    resetMarkerSizes() {
        this.registeredMarkers.forEach((markerData, eventId) => {
            const iconElement = markerData.marker._icon;
            if (!iconElement) return;
            
            iconElement.style.transform = '';
            iconElement.classList.remove('time-drawer-highlight');
        });
    }
    
    /**
     * Register a marker with the time drawer
     * @param {string} eventId - Event ID
     * @param {L.Marker} marker - Leaflet marker
     * @param {Object} event - Event object
     */
    registerMarker(eventId, marker, event) {
        this.registeredMarkers.set(eventId, { marker, event });
        
        if (this.enabled) {
            const drawerTime = this.getDrawerTime();
            const scale = this.calculateMarkerScale(event, drawerTime);
            this.applyMarkerScale(marker, scale);
        }
    }
    
    /**
     * Unregister a marker
     * @param {string} eventId - Event ID
     */
    unregisterMarker(eventId) {
        this.registeredMarkers.delete(eventId);
    }
    
    /**
     * Clear all registered markers
     */
    clearMarkers() {
        this.registeredMarkers.clear();
    }
    
    /**
     * Show threshold message when not enough events
     * @param {number} eventCount - Current event count
     */
    showThresholdMessage(eventCount) {
        // Remove existing message
        this.hideThresholdMessage();
        
        this.thresholdMessageElement = document.createElement('div');
        this.thresholdMessageElement.className = 'time-drawer-threshold-message';
        this.thresholdMessageElement.innerHTML = `
            <span class="threshold-icon">ℹ️</span>
            <span class="threshold-text">Time Explorer needs at least ${this.config.minEventsThreshold} events (found ${eventCount})</span>
        `;
        
        document.body.appendChild(this.thresholdMessageElement);
        
        // Fade in
        requestAnimationFrame(() => {
            this.thresholdMessageElement.classList.add('visible');
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideThresholdMessage();
        }, 5000);
    }
    
    /**
     * Hide threshold message
     */
    hideThresholdMessage() {
        if (this.thresholdMessageElement) {
            this.thresholdMessageElement.classList.remove('visible');
            setTimeout(() => {
                if (this.thresholdMessageElement && this.thresholdMessageElement.parentElement) {
                    this.thresholdMessageElement.remove();
                }
                this.thresholdMessageElement = null;
            }, 300);
        }
    }
    
    /**
     * Update event count display
     */
    updateEventCount() {
        if (!this.eventCountElement) return;
        
        const count = this.registeredMarkers.size;
        this.eventCountElement.textContent = `${count} event${count !== 1 ? 's' : ''}`;
    }
    
    /**
     * Start update timer (updates every minute)
     */
    startUpdateTimer() {
        this.stopUpdateTimer();
        
        this.updateTimer = setInterval(() => {
            if (this.enabled) {
                this.updateHandleTime();
                this.updateMarkerSizes();
            }
        }, this.config.updateInterval);
    }
    
    /**
     * Stop update timer
     */
    stopUpdateTimer() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }
}
