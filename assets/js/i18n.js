/**
 * Internationalization (i18n) Module
 * 
 * Handles loading and switching between different language translations.
 * Supports language detection via:
 * 1. URL path (e.g., /en/ → English, / → German)
 * 2. Config file setting (if URL doesn't specify)
 * 3. Browser language preference
 * 4. Default fallback to German (de)
 * 
 * URL Routing:
 * - krwl.in/ → German (default)
 * - krwl.in/en/ → English
 */

class I18n {
    constructor() {
        this.currentLocale = 'de'; // Default to German
        this.content = null;
        this.fallbackContent = null;
    }
    
    /**
     * Detect language from URL path
     * 
     * @returns {string|null} Two-letter language code or null if not in URL
     */
    detectLanguageFromURL() {
        const pathname = window.location.pathname;
        
        // Check for /en/ or /en (at start of path)
        if (pathname.startsWith('/en/') || pathname === '/en') {
            return 'en';
        }
        
        // Check for /de/ or /de (at start of path)
        if (pathname.startsWith('/de/') || pathname === '/de') {
            return 'de';
        }
        
        // Root path (/) defaults to German
        if (pathname === '/' || pathname === '') {
            return 'de';
        }
        
        // No language in URL, will use other detection methods
        return null;
    }
    
    /**
     * Detect language from browser settings
     * 
     * @returns {string} Two-letter language code
     */
    detectBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        return browserLang.split('-')[0].toLowerCase();
    }
    
    /**
     * Initialize i18n system
     * Priority: URL path > Config > Browser > Default (de)
     * 
     * @param {Object} config - Application config
     * @returns {Promise<void>}
     */
    async init(config) {
        // Priority 1: Check URL path first
        const urlLang = this.detectLanguageFromURL();
        
        if (urlLang) {
            this.currentLocale = urlLang;
            console.log(`[i18n] Using language from URL: ${urlLang}`);
        } else {
            // Priority 2: Check config
            const configLang = config?.app?.language || 'auto';
            const browserLang = this.detectBrowserLanguage();
            
            if (configLang && configLang !== 'auto') {
                this.currentLocale = configLang;
                console.log(`[i18n] Using language from config: ${configLang}`);
            } else {
                // Priority 3: Auto-detect from browser
                const supportedLangs = ['en', 'de'];
                if (supportedLangs.includes(browserLang)) {
                    this.currentLocale = browserLang;
                    console.log(`[i18n] Using browser language: ${browserLang}`);
                } else {
                    // Priority 4: Default to German
                    this.currentLocale = 'de';
                    console.log(`[i18n] Using default language: de (German)`);
                }
            }
        }
        
        // Load content files
        await this.loadContent();
    }
    
    /**
     * Get base path for content files based on current directory
     * Handles both root (/) and language subdirectories (/en/)
     * 
     * @returns {string} Base path for content files
     */
    getContentBasePath() {
        const pathname = window.location.pathname;
        
        // If we're in /en/ subdirectory, go up one level
        if (pathname.startsWith('/en/') || pathname === '/en') {
            return '../';
        }
        
        // If we're at root or in another path, content is in same directory
        return '';
    }
    
    /**
     * Load content file for current locale
     * Always loads English as fallback
     * 
     * @returns {Promise<void>}
     */
    async loadContent() {
        try {
            const basePath = this.getContentBasePath();
            
            // Always load English as fallback
            const fallbackResponse = await fetch(`${basePath}content.json`);
            this.fallbackContent = await fallbackResponse.json();
            
            // If not English, load the requested language
            if (this.currentLocale !== 'en') {
                const contentFile = `${basePath}content.${this.currentLocale}.json`;
                try {
                    const response = await fetch(contentFile);
                    if (response.ok) {
                        this.content = await response.json();
                        console.log(`[i18n] Loaded ${contentFile}`);
                    } else {
                        console.warn(`[i18n] Content file ${contentFile} not found, using English fallback`);
                        this.content = this.fallbackContent;
                    }
                } catch (error) {
                    console.warn(`[i18n] Error loading ${contentFile}:`, error);
                    this.content = this.fallbackContent;
                }
            } else {
                this.content = this.fallbackContent;
            }
            
        } catch (error) {
            console.error('[i18n] Error loading content files:', error);
            // Create minimal fallback
            this.content = {
                locale: 'de',
                app: { title: 'KRWL HOF Community Events' }
            };
            this.fallbackContent = this.content;
        }
    }
    
    /**
     * Get translated string by key path
     * Supports nested keys like "filters.event_count.singular"
     * Falls back to English if translation missing
     * 
     * @param {string} keyPath - Dot-separated path to translation key
     * @param {Object} replacements - Object with placeholder replacements
     * @returns {string} Translated string
     */
    t(keyPath, replacements = {}) {
        const keys = keyPath.split('.');
        let value = this.content;
        let fallbackValue = this.fallbackContent;
        
        // Navigate through nested object
        for (const key of keys) {
            value = value?.[key];
            fallbackValue = fallbackValue?.[key];
        }
        
        // Use fallback if translation not found
        if (value === undefined || value === null) {
            value = fallbackValue;
            if (value === undefined || value === null) {
                console.warn(`[i18n] Translation key not found: ${keyPath}`);
                return keyPath; // Return key as fallback
            }
        }
        
        // Handle non-string values
        if (typeof value !== 'string') {
            return value;
        }
        
        // Replace placeholders {variable}
        let result = value;
        for (const [key, val] of Object.entries(replacements)) {
            result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), val);
        }
        
        return result;
    }
    
    /**
     * Get current locale code
     * 
     * @returns {string} Current locale (e.g., 'en', 'de')
     */
    getLocale() {
        return this.currentLocale;
    }
    
    /**
     * Switch to a different language
     * 
     * @param {string} locale - Language code to switch to
     * @returns {Promise<void>}
     */
    async switchLanguage(locale) {
        this.currentLocale = locale;
        await this.loadContent();
        
        // Dispatch event so app can re-render with new language
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { locale }
        }));
    }
    
    /**
     * Get all available languages
     * 
     * @returns {Array<Object>} Array of {code, name} objects
     */
    getAvailableLanguages() {
        return [
            { code: 'en', name: 'English', nativeName: 'English' },
            { code: 'de', name: 'German', nativeName: 'Deutsch' }
        ];
    }
    
    /**
     * Format number based on current locale
     * 
     * @param {number} number - Number to format
     * @param {Object} options - Intl.NumberFormat options
     * @returns {string} Formatted number
     */
    formatNumber(number, options = {}) {
        const locale = this.currentLocale === 'en' ? 'en-US' : `${this.currentLocale}-${this.currentLocale.toUpperCase()}`;
        return new Intl.NumberFormat(locale, options).format(number);
    }
    
    /**
     * Format date based on current locale
     * 
     * @param {Date|string} date - Date to format
     * @param {Object} options - Intl.DateTimeFormat options
     * @returns {string} Formatted date
     */
    formatDate(date, options = {}) {
        const dateObj = date instanceof Date ? date : new Date(date);
        const locale = this.currentLocale === 'en' ? 'en-US' : `${this.currentLocale}-${this.currentLocale.toUpperCase()}`;
        return new Intl.DateTimeFormat(locale, options).format(dateObj);
    }
    
    /**
     * Get pluralized translation
     * 
     * @param {string} keyBase - Base key path (e.g., "filters.event_count")
     * @param {number} count - Count to determine plural form
     * @param {Object} replacements - Additional replacements
     * @returns {string} Pluralized and translated string
     */
    plural(keyBase, count, replacements = {}) {
        let key;
        if (count === 0) {
            key = `${keyBase}.none`;
        } else if (count === 1) {
            key = `${keyBase}.singular`;
        } else {
            key = `${keyBase}.plural`;
        }
        
        return this.t(key, { count, ...replacements });
    }
}

// Create global instance
window.i18n = new I18n();
