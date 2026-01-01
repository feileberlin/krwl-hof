"""CDN-based static site inliner module

This module generates a single index.html file with all CSS and JavaScript inlined.
It fetches Leaflet from CDN when available, or uses local files as fallback.

Key features:
- Fetches Leaflet CSS and JS from CDN (jsDelivr) or uses local files
- Inlines app CSS and JS from static files
- Creates a single HTML file (1 HTTP request)
- Includes EVENTS placeholder for dynamic event data injection
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime


class CDNInliner:
    """Generator for inline static site from CDN resources"""
    
    # CDN URLs for Leaflet 1.9.4
    LEAFLET_CSS_URL = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
    LEAFLET_JS_URL = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"
    
    def __init__(self, config, base_path):
        self.config = config
        self.base_path = base_path
        self.static_path = base_path / 'static'
    
    def fetch_from_cdn(self, url):
        """Fetch content from CDN URL"""
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e}")
    
    def read_local_file(self, path):
        """Read content from local file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read {path}: {e}")
    
    def get_leaflet_css(self):
        """Get Leaflet CSS from CDN or local fallback"""
        try:
            print("Fetching Leaflet CSS from CDN...")
            return self.fetch_from_cdn(self.LEAFLET_CSS_URL)
        except Exception as e:
            print(f"  ⚠ CDN fetch failed: {e}")
            print("  Using local Leaflet CSS...")
            local_path = self.static_path / 'lib' / 'leaflet' / 'leaflet.css'
            return self.read_local_file(local_path)
    
    def get_leaflet_js(self):
        """Get Leaflet JS from CDN or local fallback"""
        try:
            print("Fetching Leaflet JS from CDN...")
            return self.fetch_from_cdn(self.LEAFLET_JS_URL)
        except Exception as e:
            print(f"  ⚠ CDN fetch failed: {e}")
            print("  Using local Leaflet JS...")
            local_path = self.static_path / 'lib' / 'leaflet' / 'leaflet.js'
            return self.read_local_file(local_path)
    
    def generate_inline_html(self):
        """Generate complete HTML with all resources inlined"""
        leaflet_css = self.get_leaflet_css()
        leaflet_js = self.get_leaflet_js()
        
        print("Reading app CSS...")
        app_css_path = self.static_path / 'css' / 'style.css'
        app_css = self.read_local_file(app_css_path)
        
        print("Reading app JS...")
        app_js_path = self.static_path / 'js' / 'app.js'
        app_js = self.read_local_file(app_js_path)
        
        # Remove auto-generated comments from app files
        app_css = self._remove_autogen_comments(app_css)
        app_js = self._remove_autogen_comments(app_js)
        
        print("Generating inline HTML...")
        
        # Build the complete HTML
        html = self._build_html_template(leaflet_css, leaflet_js, app_css, app_js)
        
        return html
    
    def _remove_autogen_comments(self, content):
        """Remove auto-generated warning comments from content"""
        lines = content.split('\n')
        filtered_lines = []
        skip = False
        
        for line in lines:
            # Skip auto-generated comment blocks
            if 'AUTO-GENERATED' in line or 'DO NOT EDIT' in line:
                skip = True
            elif skip and line.strip() and not line.strip().startswith(('/', '*', '//')):
                skip = False
            
            if not skip:
                filtered_lines.append(line)
        
        # Remove leading empty lines
        while filtered_lines and not filtered_lines[0].strip():
            filtered_lines.pop(0)
        
        return '\n'.join(filtered_lines)
    
    def _build_html_template(self, leaflet_css, leaflet_js, app_css, app_js):
        """Build complete HTML template with inlined resources"""
        
        # Get app configuration for defaults
        app_name = self.config.get('app', {}).get('name', 'KRWL HOF - Community Events')
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    
    <!-- PWA Meta Tags -->
    <meta name="description" content="Discover community events near you with interactive map and filters">
    <meta name="theme-color" content="#FF69B4">
    <link rel="manifest" href="manifest.json">
    
    <!-- Icons -->
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="icon-192.svg">
    
    <!-- Inlined Leaflet CSS from CDN -->
    <style id="leaflet-css">
{leaflet_css}
    </style>
    
    <!-- Inlined App CSS -->
    <style id="app-css">
{app_css}
    </style>
</head>
<body>
    <!-- Main App Container -->
    <div id="app">
        <!-- No-JavaScript Fallback -->
        <noscript>
            <div id="noscript-fallback" style="max-width: 1200px; margin: 0 auto; padding: 2rem; background: #1a1a1a; color: #fff;">
                <header style="text-align: center; margin-bottom: 2rem;">
                    <h1 style="color: #FF69B4; margin-bottom: 0.5rem;">{app_name}</h1>
                    <p style="color: #aaa;">This is a static version. Enable JavaScript for the interactive map and filters.</p>
                </header>
                
                <div style="padding: 1rem; background: rgba(30, 30, 30, 0.95); border: 2px solid #FF69B4; border-radius: 8px; margin-bottom: 2rem; color: #FF69B4; line-height: 1.6;">
                    All upcoming community events in all categories
                </div>
                
                <div id="noscript-events-list">
                    <div style="text-align: center; padding: 3rem; color: #aaa;">
                        <p>No events currently scheduled.</p>
                        <p style="font-size: 0.9rem; margin-top: 1rem;">Events will appear here when they are added by organizers.</p>
                    </div>
                </div>
                
                <footer style="text-align: center; margin-top: 3rem; padding: 2rem; border-top: 1px solid #555;">
                    <p style="color: #aaa; font-size: 0.9rem;">For the best experience with interactive filters and maps, please enable JavaScript.</p>
                </footer>
            </div>
        </noscript>
        
        <!-- Main Content (JavaScript Required) -->
        <div id="main-content" style="display: none;">
            <!-- Environment Watermark -->
            <div id="env-watermark" class="hidden"></div>
            
            <!-- Filter Sentence -->
            <div id="filter-sentence">
                <span id="event-count-text">0 events</span>
                <span id="category-text" class="filter-part">in all categories</span>
                <span id="time-text" class="filter-part">till sunrise</span>
                <span id="distance-text" class="filter-part">within 5 km</span>
                <span id="location-text" class="filter-part">from your location</span>
            </div>
            
            <!-- Location Status -->
            <div id="location-status"></div>
            
            <!-- Map Container -->
            <div id="map"></div>
            
            <!-- Map Overlay for Edge Details -->
            <div id="map-overlay">
                <div id="event-arrows-container"></div>
            </div>
            
            <!-- Event Detail Modal -->
            <div id="event-detail" class="hidden">
                <div class="event-detail-content">
                    <button id="close-detail">&times;</button>
                    <h2 id="detail-title"></h2>
                    <p id="detail-description"></p>
                    <p><strong>Location:</strong> <span id="detail-location"></span></p>
                    <p><strong>Time:</strong> <span id="detail-time"></span></p>
                    <p><strong>Distance:</strong> <span id="detail-distance"></span></p>
                    <a id="detail-link" href="#" target="_blank" rel="noopener noreferrer">View Details</a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Inlined Leaflet JS from CDN -->
    <script id="leaflet-js">
{leaflet_js}
    </script>
    
    <!-- Event Data Placeholder (Updated by Python) -->
    <script id="events-data">
const EVENTS = [];
    </script>
    
    <!-- Inlined App JS -->
    <script id="app-js">
{app_js}
    </script>
    
    <!-- Show main content when JS is enabled -->
    <script>
        document.getElementById('main-content').style.display = 'block';
    </script>
</body>
</html>
'''
        return html
    
    def save_html(self, html_content):
        """Save generated HTML to static/index.html"""
        output_path = self.static_path / 'index.html'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Saved to: {output_path}")
        return output_path
    
    def generate_all(self):
        """Main generation method - replaces generator.py generate_all()"""
        from .utils import archive_old_events
        
        print("\n" + "=" * 60)
        print("CDN Inliner - Generating Single-File HTML")
        print("=" * 60)
        
        # Archive old events first
        print("\nArchiving old events...")
        archived_count = archive_old_events(self.base_path)
        if archived_count > 0:
            print(f"  ✓ Archived {archived_count} past event(s)")
        else:
            print(f"  ✓ No past events to archive")
        
        # Generate inline HTML
        html = self.generate_inline_html()
        
        # Save to static folder
        self.save_html(html)
        
        # Update warning notice
        self._create_warning_notice()
        
        print("\n" + "=" * 60)
        print("✓ Generation complete!")
        print("=" * 60)
        print(f"\nGenerated: {self.static_path / 'index.html'}")
        print(f"Size: ~{len(html) / 1024:.1f} KB")
        print("\nNext steps:")
        print("  1. Test locally: cd static && python3 -m http.server 8000")
        print("  2. Update events: python3 main.py publish <event_id>")
        print("  3. Deploy: git push")
        
        return True
    
    def _create_warning_notice(self):
        """Create a warning notice in static folder about auto-generation"""
        notice_path = self.static_path / 'DO_NOT_EDIT_README.txt'
        notice_content = f'''⚠️  WARNING: AUTO-GENERATED FILE ⚠️
=======================================

The following file in this directory is AUTO-GENERATED by the build system:
  - index.html (generated from CDN resources + app files)

This file is regenerated from:
  - src/modules/cdn_inliner.py (generation logic)
  - static/css/style.css (app styles)
  - static/js/app.js (app logic)
  - CDN: Leaflet CSS and JS

🚫 DO NOT manually edit index.html directly!
   Any manual changes will be OVERWRITTEN during the next build.

✅ To make changes:
   1. Edit app styles in static/css/style.css
   2. Edit app logic in static/js/app.js
   3. Run: python3 src/main.py generate
   4. Commit all changed files

📋 Data files are safe to edit:
   - events.json (published events)
   - pending_events.json (events awaiting review)
   - rejected_events.json (rejected events)
   - config.json (runtime configuration)
   - content.json / content.de.json (translations)

Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

For more information, see the project README.md
'''
        with open(notice_path, 'w') as f:
            f.write(notice_content)
        
        print(f"✓ Updated: {notice_path}")
