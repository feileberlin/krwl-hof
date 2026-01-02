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
from pathlib import Path
from typing import Dict, List, Tuple


# Library definitions for download
LIBRARIES = {
    "leaflet": {
        "version": "1.9.4",
        "base_url": "https://unpkg.com/leaflet@{version}/dist",
        "files": [
            {"src": "leaflet.css", "dest": "leaflet/leaflet.css"},
            {"src": "leaflet.js", "dest": "leaflet/leaflet.js"},
            {"src": "images/marker-icon.png", "dest": "leaflet/images/marker-icon.png"},
            {"src": "images/marker-icon-2x.png", "dest": "leaflet/images/marker-icon-2x.png"},
            {"src": "images/marker-shadow.png", "dest": "leaflet/images/marker-shadow.png"}
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
    
    def download_file(self, url: str, dest: Path) -> bool:
        """Download a single file from URL"""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"  Downloading {dest.name}...", end=" ", flush=True)
            
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            
            with open(dest, 'wb') as f:
                f.write(content)
            
            print(f"✓ ({len(content) / 1024:.1f} KB)")
            return True
        except Exception as e:
            print(f"✗ {e}")
            return False
    
    def download_library(self, lib_name: str, lib_config: Dict) -> bool:
        """Download all files for one library"""
        print(f"\n📦 {lib_name} v{lib_config['version']}")
        base_url = lib_config['base_url'].format(version=lib_config['version'])
        
        success = True
        for file_info in lib_config['files']:
            url = f"{base_url}/{file_info['src']}"
            dest = self.lib_dir / file_info['dest']
            if not self.download_file(url, dest):
                success = False
        
        status = "✅" if success else "⚠️ "
        print(f"{status} {lib_name} download {'complete' if success else 'incomplete'}")
        return success
    
    def download_libs(self) -> bool:
        """Download all CDN libraries"""
        print("=" * 60)
        print("📦 Downloading CDN Libraries")
        print("=" * 60)
        
        results = [self.download_library(name, cfg) for name, cfg in LIBRARIES.items()]
        
        print("\n" + "=" * 60)
        status = "✅ All libraries downloaded" if all(results) else "⚠️  Some libraries failed"
        print(status)
        print("=" * 60)
        return all(results)
    
    def verify_library(self, lib_name: str, lib_config: Dict) -> Tuple[bool, List[str]]:
        """Verify one library's files exist"""
        missing = []
        for file_info in lib_config['files']:
            dest = self.lib_dir / file_info['dest']
            if not dest.exists():
                missing.append(file_info['dest'])
        return len(missing) == 0, missing
    
    def verify_libs(self, quiet=False) -> bool:
        """Verify all libraries are installed"""
        if not quiet:
            print("=" * 60)
            print("📋 Verifying Libraries")
            print("=" * 60)
        
        all_ok = True
        for lib_name, lib_config in LIBRARIES.items():
            verified, missing = self.verify_library(lib_name, lib_config)
            
            if not quiet:
                version = lib_config['version']
                if verified:
                    print(f"\n📋 {lib_name} v{version}")
                    print(f"  ✓ All files present")
                else:
                    print(f"\n📋 {lib_name} v{version}")
                    print(f"  ✗ Missing {len(missing)} files:")
                    for m in missing:
                        print(f"    - {m}")
            
            if not verified:
                all_ok = False
        
        if not quiet:
            print("\n" + "=" * 60)
            if all_ok:
                print("✅ All libraries verified")
            else:
                print("❌ Missing libraries")
                print("   Run: python3 src/main.py libs")
            print("=" * 60)
        
        return all_ok
    
    # ==================== HTML Generation ====================
    
    def load_config(self, mode: str) -> Dict:
        """Load config for specified mode"""
        config_file = 'config.prod.json' if mode == 'production' else 'config.dev.json'
        with open(self.base_path / config_file, 'r') as f:
            return json.load(f)
    
    def load_events(self, mode: str) -> List[Dict]:
        """Load events based on mode"""
        events = []
        
        # Real events
        events_file = self.static_path / 'events.json'
        if events_file.exists():
            with open(events_file, 'r') as f:
                events.extend(json.load(f).get('events', []))
        
        # Demo events in development
        if mode == 'development':
            demo_file = self.static_path / 'events.demo.json'
            if demo_file.exists():
                with open(demo_file, 'r') as f:
                    events.extend(json.load(f).get('events', []))
        
        return events
    
    def load_resources(self) -> Dict[str, str]:
        """Load all CSS/JS resources"""
        return {
            'leaflet_css': self._read_file(self.lib_dir / 'leaflet' / 'leaflet.css'),
            'leaflet_js': self._read_file(self.lib_dir / 'leaflet' / 'leaflet.js'),
            'app_css': self._read_file(self.static_path / 'css' / 'style.css'),
            'i18n_js': self._read_file(self.static_path / 'js' / 'i18n.js'),
            'app_js': self._read_file(self.static_path / 'js' / 'app.js')
        }
    
    def load_i18n(self) -> Tuple[Dict, Dict]:
        """Load translation files"""
        with open(self.static_path / 'content.json', 'r') as f:
            content_en = json.load(f)
        with open(self.static_path / 'content.de.json', 'r') as f:
            content_de = json.load(f)
        return content_en, content_de
    
    def _read_file(self, path: Path) -> str:
        """Read text file"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _ensure_libs(self) -> bool:
        """Ensure libraries are downloaded"""
        if not self.verify_libs(quiet=True):
            print("\n⚠️  Libraries missing - downloading now...")
            if not self.download_libs():
                print("❌ Failed to download libraries")
                return False
            print()
        return True
    
    def _generate_watermark(self, mode: str) -> str:
        """Generate watermark CSS for development mode"""
        if mode != 'development':
            return ''
        
        return '''<style>
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
    
    def _generate_favicon(self) -> str:
        """Generate base64 favicon data URL"""
        favicon_svg = self.static_path / 'favicon.svg'
        if not favicon_svg.exists():
            return "favicon.svg"
        
        import base64
        svg_content = self._read_file(favicon_svg)
        b64_data = base64.b64encode(svg_content.encode()).decode()
        return f"data:image/svg+xml;base64,{b64_data}"
    
    def _build_html(self, config: Dict, events: List[Dict], content_en: Dict, 
                    content_de: Dict, resources: Dict, mode: str) -> str:
        """Build complete HTML from components"""
        app_name = config.get('app', {}).get('name', 'KRWL HOF Community Events')
        watermark = self._generate_watermark(mode)
        favicon = self._generate_favicon()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{app_name}</title>
<link rel="icon" href="{favicon}">
<style>{resources['leaflet_css']}</style>
<style>{resources['app_css']}</style>{watermark}
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

(function() {{
    const f = window.fetch;
    window.fetch = function(url, opts) {{
        if (url.includes('config.json')) return Promise.resolve({{ok: 1, json: () => Promise.resolve(window.EMBEDDED_CONFIG)}});
        if (url.includes('events.json')) return Promise.resolve({{ok: 1, json: () => Promise.resolve({{events: window.EMBEDDED_EVENTS}})}});
        if (url.includes('content.json')) {{
            const c = url.includes('.de.') ? window.EMBEDDED_CONTENT_DE : window.EMBEDDED_CONTENT_EN;
            return Promise.resolve({{ok: 1, json: () => Promise.resolve(c)}});
        }}
        return f.apply(this, arguments);
    }};
}})();

{resources['leaflet_js']}
{resources['i18n_js']}
{resources['app_js']}

document.getElementById('main-content').style.display = 'block';
</script>
</body>
</html>'''
        return html
    
    def build_html(self, mode='production') -> bool:
        """Generate single-file HTML - main build method"""
        print("=" * 60)
        print(f"🔨 Building HTML ({mode} mode)")
        print("=" * 60)
        
        if not self._ensure_libs():
            return False
        
        print(f"\nLoading configuration ({mode})...")
        config = self.load_config(mode)
        
        print("Loading resources...")
        resources = self.load_resources()
        
        print("Loading events data...")
        events = self.load_events(mode)
        
        print("Loading i18n content...")
        content_en, content_de = self.load_i18n()
        
        print(f"Generating HTML ({len(events)} events)...")
        html = self._build_html(config, events, content_en, content_de, resources, mode)
        
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
    
    # ==================== Event Updates ====================
    
    def _detect_mode(self, html: str) -> str:
        """Detect mode from HTML content"""
        return 'development' if 'DEV' in html and 'body::before' in html else 'production'
    
    def _find_events_marker(self, html: str) -> Tuple[int, int]:
        """Find EMBEDDED_EVENTS positions in HTML"""
        marker = 'window.EMBEDDED_EVENTS = '
        start = html.find(marker)
        if start == -1:
            return -1, -1
        
        start += len(marker)
        end = html.find('];', start)
        return start, end
    
    def update_events(self) -> bool:
        """Fast event update - only replaces events data"""
        print("=" * 60)
        print("⚡ Fast Event Update")
        print("=" * 60)
        
        html_file = self.static_path / 'index.html'
        if not html_file.exists():
            print("\n❌ Error: index.html not found")
            print("   Run: python3 src/main.py build production")
            return False
        
        print("\nReading existing HTML...")
        html = self._read_file(html_file)
        
        mode = self._detect_mode(html)
        print(f"Loading events ({mode} mode)...")
        events = self.load_events(mode)
        
        print("Updating events data...")
        start, end = self._find_events_marker(html)
        if start == -1 or end == -1:
            print("\n⚠️  Warning: EMBEDDED_EVENTS marker not found")
            return False
        
        new_html = html[:start] + json.dumps(events) + html[end:]
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"\n✅ Events updated successfully!")
        print(f"   Output: {html_file}")
        print(f"   Events: {len(events)}")
        print(f"   Mode: {mode}")
        print("\n" + "=" * 60)
        return True
