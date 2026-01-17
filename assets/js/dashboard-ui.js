/**
 * DashboardUI Module - Reorganized Debug Cockpit
 * 
 * Handles dashboard debug information display with improved structure:
 * - Deployment info (git commit, environment, deployment time)
 * - Data & Performance (events, caching, file size, DOM cache)
 * - Warnings (duplicates, unpublished events)
 * 
 * KISS: Single responsibility - dashboard UI updates with clean structure
 */

class DashboardUI {
    constructor(config, utils) {
        this.config = config;
        this.utils = utils;
    }
    
    /**
     * Update all dashboard debug information
     * @param {Object} duplicateStats - Statistics about duplicate events
     */
    update(duplicateStats = null) {
        const debugInfo = window.DEBUG_INFO || {};
        
        // Deployment section
        this.updateGitInfo(debugInfo);
        this.updateDeploymentTime(debugInfo);
        this.updateEnvironmentInfo(debugInfo);
        
        // Data & Performance section
        this.updateEventCounts(debugInfo);
        this.updateFileSizeInfo(debugInfo);
        this.updateCachingInfo(debugInfo);
        this.updateDOMCacheInfo();
        this.updateSizeBreakdown(debugInfo);
        
        // Warnings section
        this.updateWarnings(duplicateStats);
        
        // Show the debug section
        this.showDebugSection();
    }
    
    updateGitInfo(debugInfo) {
        if (!debugInfo.git_commit) return;
        
        const git = debugInfo.git_commit;
        this.setElementText('debug-commit-hash', git.hash || 'unknown');
        this.setElementText('debug-commit-author', git.author || 'unknown');
        this.setElementText('debug-commit-date', git.date || 'unknown');
        
        const commitMessage = document.getElementById('debug-commit-message');
        if (commitMessage) {
            commitMessage.textContent = git.message || 'No commit message';
            commitMessage.title = git.message || 'No commit message';
        }
    }
    
    updateDeploymentTime(debugInfo) {
        const deploymentTime = document.getElementById('debug-deployment-time');
        if (!deploymentTime || !debugInfo.deployment_time) return;
        
        try {
            const date = new Date(debugInfo.deployment_time);
            deploymentTime.textContent = date.toLocaleString();
            deploymentTime.title = `Deployment timestamp: ${debugInfo.deployment_time}`;
        } catch (e) {
            deploymentTime.textContent = debugInfo.deployment_time;
        }
    }
    
    updateEnvironmentInfo(debugInfo) {
        const debugEnvironment = document.getElementById('debug-environment');
        if (!debugEnvironment) return;
        
        const environment = debugInfo.environment || 
                          this.config?.watermark?.text || 
                          this.config?.app?.environment || 
                          'UNKNOWN';
        
        debugEnvironment.textContent = environment.toUpperCase();
        debugEnvironment.className = 'debug-value debug-env-badge';
        
        const envLower = environment.toLowerCase();
        if (envLower.includes('dev')) {
            debugEnvironment.classList.add('env-dev');
        } else if (envLower.includes('production')) {
            debugEnvironment.classList.add('env-production');
        } else if (envLower.includes('ci')) {
            debugEnvironment.classList.add('env-ci');
        }
    }
    
    updateEventCounts(debugInfo) {
        if (!debugInfo.event_counts) return;
        
        const counts = debugInfo.event_counts;
        this.setElementText('debug-event-counts-published', counts.published || 0);
        this.setElementText('debug-event-counts-pending', counts.pending || 0);
        this.setElementText('debug-event-counts-archived', counts.archived || 0);
    }
    
    updateFileSizeInfo(debugInfo) {
        const debugFileSize = document.getElementById('debug-file-size');
        if (!debugFileSize || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const totalKB = (sizes.total / 1024).toFixed(1);
        debugFileSize.textContent = `${totalKB} KB`;
        
        if (debugInfo.cache_enabled && debugInfo.cache_file_size) {
            const cacheKB = (debugInfo.cache_file_size / 1024).toFixed(1);
            debugFileSize.title = `HTML: ${totalKB} KB, Cache: ${cacheKB} KB`;
        }
    }
    
    updateCachingInfo(debugInfo) {
        const debugCaching = document.getElementById('debug-caching');
        if (!debugCaching) return;
        
        const cacheEnabled = debugInfo.cache_enabled;
        if (cacheEnabled !== undefined) {
            debugCaching.textContent = cacheEnabled ? 'Enabled' : 'Disabled';
            debugCaching.className = cacheEnabled ? 'debug-value cache-enabled' : 'debug-value cache-disabled';
        } else {
            debugCaching.textContent = 'Unknown';
            debugCaching.className = 'debug-value';
        }
    }
    
    updateDOMCacheInfo() {
        const debugDOMCache = document.getElementById('debug-dom-cache');
        if (debugDOMCache && this.utils) {
            const cacheSize = Object.keys(this.utils.domCache || {}).length;
            debugDOMCache.textContent = `${cacheSize} elements`;
            debugDOMCache.title = `DOM elements cached: ${Object.keys(this.utils.domCache || {}).join(', ') || 'none'}`;
        }
    }
    
    updateSizeBreakdown(debugInfo) {
        const debugSizeBreakdown = document.getElementById('debug-size-breakdown');
        if (!debugSizeBreakdown || !debugInfo.html_sizes) return;
        
        const sizes = debugInfo.html_sizes;
        const components = [
            { name: 'Events Data', size: sizes.events_data },
            { name: 'Scripts', size: sizes.scripts },
            { name: 'Styles', size: sizes.stylesheets },
            { name: 'Translations', size: sizes.translations },
            { name: 'Markers', size: sizes.marker_icons },
            { name: 'Other', size: sizes.other }
        ];
        
        components.sort((a, b) => b.size - a.size);
        
        let breakdownHTML = '<ul class="debug-size-list">';
        components.forEach(comp => {
            const kb = (comp.size / 1024).toFixed(1);
            const percent = ((comp.size / sizes.total) * 100).toFixed(1);
            breakdownHTML += `<li>${comp.name}: ${kb} KB (${percent}%)</li>`;
        });
        breakdownHTML += '</ul>';
        
        debugSizeBreakdown.innerHTML = breakdownHTML;
    }
    
    updateWarnings(duplicateStats) {
        const warningsContainer = document.getElementById('debug-warnings-container');
        const duplicateWarnings = document.getElementById('debug-duplicate-warnings');
        const unpublishedWarnings = document.getElementById('debug-unpublished-warnings');
        
        let hasWarnings = false;
        
        // Update duplicate warnings
        if (duplicateStats && duplicateStats.total > 0) {
            hasWarnings = true;
            this.updateDuplicateWarnings(duplicateStats, duplicateWarnings);
        } else if (duplicateWarnings) {
            duplicateWarnings.style.display = 'none';
        }
        
        // Check if unpublished warnings exist (populated by app.js)
        if (unpublishedWarnings && unpublishedWarnings.style.display !== 'none') {
            hasWarnings = true;
        }
        
        // Show/hide warnings container
        if (warningsContainer) {
            warningsContainer.style.display = hasWarnings ? 'block' : 'none';
        }
    }
    
    updateDuplicateWarnings(duplicateStats, warningElement) {
        if (!warningElement) return;
        
        warningElement.style.display = 'block';
        
        const stats = duplicateStats;
        const warningMessage = `⚠️ ${stats.total} duplicate event${stats.total > 1 ? 's' : ''} found across ${stats.events} event${stats.events > 1 ? 's' : ''}`;
        
        let detailsHTML = '';
        const displayLimit = 5;
        stats.details.slice(0, displayLimit).forEach(d => {
            const shortTitle = d.title.length > 40 ? d.title.substring(0, 40) + '...' : d.title;
            detailsHTML += `<li><strong>${shortTitle}</strong>: ${d.count} duplicates</li>`;
        });
        
        const moreText = stats.details.length > displayLimit ? `<li>...and ${stats.details.length - displayLimit} more</li>` : '';
        
        warningElement.innerHTML = `
            <div class="debug-duplicate-warning-header">${warningMessage}</div>
            <ul class="debug-duplicate-list">
                ${detailsHTML}
                ${moreText}
            </ul>
        `;
    }
    
    showDebugSection() {
        const debugSection = document.getElementById('dashboard-debug-section');
        if (debugSection && debugSection.style.display === 'none') {
            debugSection.style.display = 'block';
        }
    }
    
    /**
     * Helper to set element text content safely
     * @param {string} id - Element ID
     * @param {string|number} text - Text content to set
     */
    setElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardUI;
}
