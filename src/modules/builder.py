"""
Unified Build Module - KISS Compliant

This module consolidates all build-related functionality:
- Library management (download, verify CDN libraries)
- HTML generation (single-file builds with everything inlined)
- Event updates (fast updates without full regeneration)

Replaces:
- scripts/manage_libs.py
- scripts/generate_html.py
- scripts/download-libs.sh
- src/modules/cdn_inliner.py
"""

import json
import urllib.request
import urllib.error
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


# Library definitions for download
LIBRARIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {
                "src": "leaflet.css",
                "dest": "leaflet/leaflet.css",
                "type": "css"
            },
            {
                "src": "leaflet.js",
                "dest": "leaflet/leaflet.js",
                "type": "js"
            },
            {
                "src": "images/marker-icon.png",
                "dest": "leaflet/images/marker-icon.png",
                "type": "image"
            },
            {
                "src": "images/marker-icon-2x.png",
                "dest": "leaflet/images/marker-icon-2x.png",
                "type": "image"
            },
            {
                "src": "images/marker-shadow.png",
                "dest": "leaflet/images/marker-shadow.png",
                "type": "image"
            }
        ]
    }
}


class Builder:
    """Unified builder for KRWL HOF - handles libraries, HTML generation, and event updates"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.static_path = self.base_path / 'static'
        self.lib_dir = self.static_path / 'lib'
        self.lib_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== Library Management ====================
    
    def download_file(self, url: str, dest: Path, timeout: int = 30) -> bool:
        """Download a file from URL to destination"""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"  Downloading {dest.name}...", end=" ", flush=True)
            
            with urllib.request.urlopen(url, timeout=timeout) as response:
                content = response.read()
            
            with open(dest, 'wb') as f:
                f.write(content)
            
            size_kb = len(content) / 1024
            print(f"✓ ({size_kb:.1f} KB)")
            return True
            
        except urllib.error.URLError as e:
            print(f"✗ Error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def download_libs(self) -> bool:
        """Download all CDN libraries to static/lib/"""
        print("=" * 60)
        print("📦 Downloading CDN Libraries")
        print("=" * 60)
        
        all_success = True
        
        for lib_name, lib_config in LIBRARIES.items():
            print(f"\n📦 Downloading {lib_name} v{lib_config['version']}...")
            base_url = lib_config['base_url'].format(version=lib_config['version'])
            
            lib_success = True
            for file_info in lib_config['files']:
                src = file_info['src']
                dest = self.lib_dir / file_info['dest']
                url = f"{base_url}/{src}"
                
                if not self.download_file(url, dest):
                    lib_success = False
                    all_success = False
            
            if lib_success:
                print(f"✅ {lib_name}: All files downloaded")
            else:
                print(f"⚠️  {lib_name}: Some files failed")
        
        print("\n" + "=" * 60)
        if all_success:
            print("✅ All libraries downloaded successfully")
        else:
            print("⚠️  Some libraries had errors")
        print("=" * 60)
        
        return all_success
    
    def verify_libs(self, quiet=False) -> bool:
        """Verify all library files exist"""
        if not quiet:
            print("=" * 60)
            print("📋 Verifying Libraries")
            print("=" * 60)
        
        all_verified = True
        
        for lib_name, lib_config in LIBRARIES.items():
            if not quiet:
                print(f"\n📋 Verifying {lib_name} v{lib_config['version']}...")
            
            missing = []
            for file_info in lib_config['files']:
                dest = self.lib_dir / file_info['dest']
                if not dest.exists():
                    missing.append(file_info['dest'])
            
            if missing:
                all_verified = False
                if not quiet:
                    print(f"  ✗ Missing {len(missing)} files:")
                    for m in missing:
                        print(f"    - {m}")
            else:
                if not quiet:
                    print(f"  ✓ All files present")
        
        if not quiet:
            print("\n" + "=" * 60)
            if all_verified:
                print("✅ All libraries verified")
            else:
                print("❌ Some libraries have missing files")
                print("   Run: python3 src/main.py libs")
            print("=" * 60)
        
        return all_verified
    
    # ==================== HTML Generation ====================
    
    def load_config(self, mode='production') -> Dict:
        """Load configuration based on mode"""
        if mode == 'production':
            config_file = self.base_path / 'config.prod.json'
        else:  # development
            config_file = self.base_path / 'config.dev.json'
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def load_events(self, mode='production') -> List[Dict]:
        """Load events based on mode"""
        events = []
        
        # Load real events
        events_file = self.static_path / 'events.json'
        if events_file.exists():
            with open(events_file, 'r') as f:
                data = json.load(f)
                events.extend(data.get('events', []))
        
        # In development mode, also load demo events
        if mode == 'development':
            demo_file = self.static_path / 'events.demo.json'
            if demo_file.exists():
                with open(demo_file, 'r') as f:
                    data = json.load(f)
                    events.extend(data.get('events', []))
        
        return events
    
    def load_i18n(self) -> Tuple[Dict, Dict]:
        """Load i18n content files"""
        en_file = self.static_path / 'content.json'
        de_file = self.static_path / 'content.de.json'
        
        with open(en_file, 'r') as f:
            content_en = json.load(f)
        
        with open(de_file, 'r') as f:
            content_de = json.load(f)
        
        return content_en, content_de
    
    def read_file(self, path: Path) -> str:
        """Read text file content"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def build_html(self, mode='production') -> bool:
        """Generate single-file HTML with everything inlined"""
        print("=" * 60)
        print(f"🔨 Building HTML ({mode} mode)")
        print("=" * 60)
        
        # Auto-download libs if missing
        if not self.verify_libs(quiet=True):
            print("\n⚠️  Libraries missing - downloading now...")
            if not self.download_libs():
                print("❌ Failed to download libraries")
                return False
            print()
        
        # Load configuration
        print(f"\nLoading configuration ({mode})...")
        config = self.load_config(mode)
        
        # Load resources
        print("Loading Leaflet CSS...")
        leaflet_css = self.read_file(self.lib_dir / 'leaflet' / 'leaflet.css')
        
        print("Loading Leaflet JS...")
        leaflet_js = self.read_file(self.lib_dir / 'leaflet' / 'leaflet.js')
        
        print("Loading app CSS...")
        app_css = self.read_file(self.static_path / 'css' / 'style.css')
        
        print("Loading app JS...")
        i18n_js = self.read_file(self.static_path / 'js' / 'i18n.js')
        app_js = self.read_file(self.static_path / 'js' / 'app.js')
        
        print("Loading events data...")
        events = self.load_events(mode)
        
        print("Loading i18n content...")
        content_en, content_de = self.load_i18n()
        
        # Build HTML
        print(f"Generating HTML ({len(events)} events)...")
        html = self._build_html_template(
            config, events, content_en, content_de,
            leaflet_css, leaflet_js, app_css, i18n_js, app_js, mode
        )
        
        # Save HTML
        output_file = self.static_path / 'index.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ HTML generated successfully!")
        print(f"   Output: {output_file}")
        print(f"   Size: {len(html) / 1024:.1f} KB")
        print(f"   Events: {len(events)}")
        print(f"   Mode: {mode}")
        
        print("\n" + "=" * 60)
        return True
    
    def _build_html_template(self, config, events, content_en, content_de,
                            leaflet_css, leaflet_js, app_css, i18n_js, app_js, mode):
        """Build complete HTML template with inlined resources"""
        app_name = config.get('app', {}).get('name', 'KRWL HOF Community Events')
        
        # Build watermark CSS for development mode
        watermark = ''
        if mode == 'development':
            watermark = '''<style>
body::before {
    content: "DEV";
    position: fixed;
    top: 10px;
    right: 10px;
    background: rgba(255, 105, 180, 0.8);
    color: #000;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 12px;
    z-index: 10000;
}
</style>'''
        
        # Generate base64 favicon
        favicon_svg = self.static_path / 'favicon.svg'
        if favicon_svg.exists():
            import base64
            favicon_content = self.read_file(favicon_svg)
            favicon_data = base64.b64encode(favicon_content.encode()).decode()
            favicon_url = f"data:image/svg+xml;base64,{favicon_data}"
        else:
            favicon_url = "favicon.svg"
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{app_name}</title>
<link rel="icon" href="{favicon_url}">
<style>{leaflet_css}</style>
<style>{app_css}</style>{watermark}
</head>
<body>
<div id="app">
<noscript>
<div style="max-width:1200px;margin:0 auto;padding:2rem;background:#1a1a1a;color:#fff">
<h1 style="color:#FF69B4">{app_name}</h1>
<p>Enable JavaScript to view {len(events)} events</p>
</div>
</noscript>
<div id="main-content" style="display:none">
<div id="filter-sentence">
<span id="event-count-text">0 events</span>
<span id="category-text" class="filter-part">in all categories</span>
<span id="time-text" class="filter-part">till sunrise</span>
<span id="distance-text" class="filter-part">within 5 km</span>
<span id="location-text" class="filter-part">from your location</span>
</div>
<div id="location-status"></div>
<div id="map"></div>
<div id="event-detail" class="hidden">
<div class="event-detail-content">
<button id="close-detail">&times;</button>
<h2 id="detail-title"></h2>
<p id="detail-description"></p>
<p><strong>Location:</strong> <span id="detail-location"></span></p>
<p><strong>Time:</strong> <span id="detail-time"></span></p>
<p><strong>Distance:</strong> <span id="detail-distance"></span></p>
<a id="detail-link" href="#" target="_blank">View Details</a>
</div>
</div>
</div>
</div>
<script>
window.EMBEDDED_CONFIG = {json.dumps(config)};
window.EMBEDDED_EVENTS = {json.dumps(events)};
window.EMBEDDED_CONTENT_EN = {json.dumps(content_en)};
window.EMBEDDED_CONTENT_DE = {json.dumps(content_de)};

// Intercept fetch calls to return embedded data
(function() {{
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
        if (url.includes('config.json')) {{
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve(window.EMBEDDED_CONFIG)
            }});
        }}
        if (url.includes('events.json')) {{
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve({{events: window.EMBEDDED_EVENTS}})
            }});
        }}
        if (url.includes('content.json')) {{
            const content = url.includes('.de.') ? window.EMBEDDED_CONTENT_DE : window.EMBEDDED_CONTENT_EN;
            return Promise.resolve({{
                ok: true,
                json: () => Promise.resolve(content)
            }});
        }}
        return originalFetch.apply(this, arguments);
    }};
}})();

{leaflet_js}
{i18n_js}
{app_js}

document.getElementById('main-content').style.display = 'block';
</script>
</body>
</html>'''
        
        return html
    
    # ==================== Event Updates ====================
    
    def update_events(self) -> bool:
        """Update only events in existing HTML (fast, no regeneration)"""
        print("=" * 60)
        print("⚡ Fast Event Update")
        print("=" * 60)
        
        html_file = self.static_path / 'index.html'
        
        if not html_file.exists():
            print("\n❌ Error: index.html not found")
            print("   Run: python3 src/main.py build production")
            return False
        
        # Read existing HTML
        print("\nReading existing HTML...")
        html = self.read_file(html_file)
        
        # Determine mode from HTML content
        if 'DEV' in html and 'body::before' in html:
            mode = 'development'
        else:
            mode = 'production'
        
        # Load events
        print(f"Loading events ({mode} mode)...")
        events = self.load_events(mode)
        
        # Replace EMBEDDED_EVENTS in HTML
        print("Updating events data...")
        events_json = json.dumps(events)
        
        # Find and replace the EMBEDDED_EVENTS line
        # Use a simple string replacement approach to avoid regex escape issues
        pattern = 'window.EMBEDDED_EVENTS = '
        start_idx = html.find(pattern)
        
        if start_idx == -1:
            print("\n⚠️  Warning: EMBEDDED_EVENTS pattern not found")
            return False
        
        # Find the end of the JSON array (looking for "];")
        start_idx += len(pattern)
        end_idx = html.find('];', start_idx)
        
        if end_idx == -1:
            print("\n⚠️  Warning: End of EMBEDDED_EVENTS not found")
            return False
        
        # Build new HTML with updated events
        new_html = html[:start_idx] + events_json + html[end_idx:]
        
        if new_html == html:
            print("\n⚠️  Warning: No changes made")
            return False
        
        # Save updated HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"\n✅ Events updated successfully!")
        print(f"   Output: {html_file}")
        print(f"   Events: {len(events)}")
        print(f"   Mode: {mode}")
        
        print("\n" + "=" * 60)
        return True
