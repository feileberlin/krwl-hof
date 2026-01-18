# INITIATE.md - Bootstrap Guide for KRWL HOF-Style Projects

> **Quick Start Guide**: How to implement a project like KRWL HOF from scratch without common pitfalls, orphan files, or wrong paths. Get up and running "quite fast and quite fat" (rapid setup with comprehensive foundation).

## 🎯 What You're Building

A **mobile-first Progressive Web App (PWA)** for discovering local events with:
- Interactive Leaflet.js map with event markers
- Geolocation-based filtering (show events within X km)
- Time-based filtering (e.g., "until sunrise")
- Python backend for event scraping and management
- Static site generation (single HTML file with everything inlined)
- Automatic environment detection (dev/production)
- Editorial workflow (scrape → review → publish)

**Live Example**: [krwl.in](https://krwl.in)

---

## 📋 Prerequisites

Before you start, ensure you have:

### Required
- **Python 3.x** (3.10 or higher recommended)
- **Git** for version control
- **Modern web browser** (Chrome, Firefox, Safari)
- **Text editor/IDE** (VS Code recommended)

### Optional (for enhanced features)
- **Tesseract OCR** (for Facebook flyer image scraping)
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng`
  - macOS: `brew install tesseract tesseract-lang`
- **Ollama** (for AI-powered event categorization)
  - Install from [ollama.ai](https://ollama.ai/)
  - Pull model: `ollama pull llama3.2`

---

## ⚡ Quick Bootstrap (5 Minutes)

```bash
# 1. Create new repository on GitHub
# Name: your-project-name

# 2. Clone and setup
git clone https://github.com/YOUR_USERNAME/your-project-name.git
cd your-project-name

# 3. Initialize Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Create requirements.txt
cat > requirements.txt << 'EOF'
# Core dependencies
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
feedparser>=6.0.10
pydantic>=2.0.0
tenacity>=8.2.0

# Optional: Image OCR (for Facebook flyers)
Pillow>=10.0.0
pytesseract>=0.3.10
exifread>=3.0.0

# Optional: Documentation
markdown>=3.5.0
Pygments>=2.17.0
EOF

# 5. Install dependencies
pip install -r requirements.txt

# 6. You're ready! Continue with "Essential Project Structure" below
```

---

## 📁 Essential Project Structure

**CRITICAL**: Create this exact structure to avoid orphan files and path confusion.

```
your-project/
├── config.json              # ⭐ SINGLE unified config (auto-detects environment)
├── features.json            # Feature registry (document ALL features here)
├── requirements.txt         # Python dependencies
├── .gitignore              # Exclude build artifacts, caches, dependencies
│
├── src/                    # Python backend
│   ├── event_manager.py    # ⭐ SINGLE entry point (CLI + TUI)
│   └── modules/            # Modular components
│       ├── scraper.py      # Event scraping logic
│       ├── editor.py       # Editorial workflow
│       ├── site_generator.py  # HTML generation
│       └── utils.py        # Common utilities
│
├── assets/                 # Frontend resources
│   ├── css/                # Source stylesheets
│   │   └── style.css       # ✅ EDIT THIS (source)
│   ├── js/                 # Source JavaScript
│   │   └── app.js          # ✅ EDIT THIS (source)
│   ├── html/               # HTML components/templates
│   ├── svg/                # Icons and graphics
│   └── json/               # Data files
│       ├── events.json     # Published events
│       ├── pending_events.json  # Awaiting review
│       └── events.demo.json    # Demo data for testing
│
├── public/                 # Build output (gitignored)
│   └── index.html          # 🚫 AUTO-GENERATED (do not edit)
│
├── lib/                    # Third-party libraries (gitignored)
│   └── leaflet/            # Leaflet.js (downloaded at build)
│
├── tests/                  # Test suite
│   ├── test_scraper.py
│   ├── test_event_schema.py
│   └── ...
│
└── scripts/                # Utility scripts
    └── generate_readme.py
```

### Key Rules

1. **Single Entry Point**: ONLY `src/event_manager.py` (NEVER create `src/main.py`)
2. **Edit Source Files**: Edit `assets/css/*.css` and `assets/js/*.js`, NOT `public/index.html`
3. **Auto-Generated Files**: `public/index.html` is regenerated from templates
4. **Single Config**: One `config.json` that auto-adapts to environment
5. **Feature Registry**: Update `features.json` whenever you add features

---

## 🔧 Core Configuration Setup

### 1. Create `config.json`

**This is your single source of truth for all configuration.**

```json
{
  "_comment": "Automatic Environment Detection - NO manual switching needed!",
  "environment": "auto",
  
  "app": {
    "name": "Your Project Name",
    "description": "Brief description of your event discovery app"
  },
  
  "map": {
    "default_center": {
      "lat": 50.3167,
      "lon": 11.9167
    },
    "default_zoom": 13,
    "tile_provider": "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
  },
  
  "filtering": {
    "max_distance_km": 5.0,
    "show_until": "next_sunrise"
  },
  
  "scraping": {
    "schedule": {
      "timezone": "Europe/Berlin",
      "times": ["04:00", "16:00"]
    },
    "sources": [
      {
        "name": "Example RSS Feed",
        "url": "https://example.com/events.rss",
        "type": "rss",
        "enabled": true,
        "options": {
          "category": "community",
          "default_location": {
            "name": "Example Venue",
            "lat": 50.3167,
            "lon": 11.9167
          }
        }
      }
    ]
  },
  
  "editor": {
    "require_approval": true,
    "auto_publish": false
  },
  
  "data": {
    "sources": {
      "real": {
        "url": "events.json"
      },
      "demo": {
        "url": "events.demo.json"
      },
      "both": {
        "urls": ["events.json", "events.demo.json"]
      }
    }
  }
}
```

**Environment Auto-Detection**:
- Local dev: `debug=true`, loads both real + demo events
- CI/Production: `debug=false`, loads only real events
- Works with: GitHub Pages, Vercel, Netlify, Heroku, Railway, Render, etc.

### 2. Create `features.json`

**Document ALL features here** (required for validation).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "Your Project Feature Registry",
  "version": "1.0.0",
  "features": [
    {
      "id": "event-scraping",
      "name": "Event Scraping",
      "description": "Scrape events from RSS feeds and HTML pages",
      "category": "backend",
      "implemented": true,
      "files": ["src/modules/scraper.py"],
      "config_keys": ["scraping.sources"],
      "test_method": "check_files_exist"
    },
    {
      "id": "interactive-map",
      "name": "Interactive Map",
      "description": "Leaflet.js map with event markers",
      "category": "frontend",
      "implemented": true,
      "files": ["assets/js/app.js", "assets/html/map-main.html"],
      "test_method": "check_code_patterns"
    }
  ]
}
```

### 3. Create `.gitignore`

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/

# Build outputs (auto-generated)
public/
lib/

# Local development
.env
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
*.tmp

# Cache
.cache/
```

---

## 🏗️ Step-by-Step Implementation Roadmap

Follow these steps in order to build your project **without going wrong paths**.

### Phase 1: Foundation (Day 1)

**Goal**: Get basic structure running locally.

#### 1.1 Create Entry Point

Create `src/event_manager.py`:

```python
#!/usr/bin/env python3
"""
Event Manager - Single Entry Point for CLI and TUI

This is the ONLY entry point. Never create src/main.py!
"""

import sys
import json
from pathlib import Path


def main():
    """Main CLI entry point"""
    print("🚀 Event Manager")
    
    if len(sys.argv) == 1:
        # Launch TUI
        print("Launch TUI here (coming soon)")
    else:
        # Handle CLI commands
        command = sys.argv[1]
        
        if command == "--help":
            print_help()
        elif command == "generate":
            print("Generate static site (coming soon)")
        else:
            print(f"Unknown command: {command}")
            print_help()


def print_help():
    """Print CLI help"""
    print("""
Usage: python3 src/event_manager.py [COMMAND]

Commands:
    (no command)    Launch interactive TUI
    generate        Generate static site
    --help          Show this help
    """)


if __name__ == "__main__":
    main()
```

#### 1.2 Test It

```bash
python3 src/event_manager.py --help
# Should print help text
```

#### 1.3 Create Utils Module

Create `src/modules/utils.py`:

```python
"""
Utility functions - Configuration loading, distance calculation, etc.
"""

import json
import os
from pathlib import Path


def load_config(base_path):
    """
    Load unified config.json with automatic environment detection.
    
    Environment detection (auto):
    - Development: NOT in CI and NOT in production
    - CI: GitHub Actions, GitLab CI, etc.
    - Production: Vercel, Netlify, Heroku, etc.
    """
    config_path = base_path / "config.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Auto-detect environment
    env_mode = config.get('environment', 'auto')
    
    if env_mode == 'auto':
        if is_ci():
            config['debug'] = False
            config['data']['source'] = 'real'
            print("🚀 Running in CI mode")
        elif is_production():
            config['debug'] = False
            config['data']['source'] = 'real'
            print("🚀 Running in production mode")
        else:
            config['debug'] = True
            config['data']['source'] = 'both'
            print("🚀 Running in development mode")
    
    return config


def is_ci():
    """Detect if running in CI environment"""
    ci_indicators = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'TRAVIS', 
                     'CIRCLECI', 'JENKINS_HOME']
    return any(os.environ.get(var) for var in ci_indicators)


def is_production():
    """Detect if running in production"""
    prod_indicators = [
        ('ENVIRONMENT', 'production'),
        ('NODE_ENV', 'production'),
        ('VERCEL_ENV', 'production'),
        ('NETLIFY', 'true'),
        ('DYNO', None),  # Heroku
    ]
    
    for var, value in prod_indicators:
        env_val = os.environ.get(var)
        if env_val:
            if value is None or env_val == value:
                return True
    
    return False
```

### Phase 2: Basic Frontend (Day 1-2)

**Goal**: Display a map with mock events.

#### 2.1 Create HTML Template

Create `assets/html/html-head.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{app.name}}</title>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
```

Create `assets/html/map-main.html`:

```html
<div id="map"></div>
```

#### 2.2 Create JavaScript

Create `assets/js/app.js`:

```javascript
/**
 * Event Discovery App
 * Mobile-first PWA with Leaflet.js map
 */

class EventsApp {
    constructor(config) {
        this.config = config;
        this.map = null;
        this.markers = [];
    }
    
    async init() {
        console.log('🚀 Initializing app...');
        
        // Initialize map
        this.initMap();
        
        // Load events
        await this.loadEvents();
        
        console.log('✅ App ready!');
    }
    
    initMap() {
        const center = this.config.map.default_center;
        const zoom = this.config.map.default_zoom;
        
        this.map = L.map('map').setView([center.lat, center.lon], zoom);
        
        // Add tile layer
        L.tileLayer(this.config.map.tile_provider, {
            attribution: this.config.map.attribution || ''
        }).addTo(this.map);
    }
    
    async loadEvents() {
        // Mock events for now
        const mockEvents = [
            {
                id: 'demo_1',
                title: 'Demo Event',
                location: { lat: 50.3167, lon: 11.9167, name: 'Demo Venue' },
                start: new Date().toISOString()
            }
        ];
        
        this.displayEvents(mockEvents);
    }
    
    displayEvents(events) {
        events.forEach(event => {
            const marker = L.marker([event.location.lat, event.location.lon])
                .addTo(this.map)
                .bindPopup(`<b>${event.title}</b><br>${event.location.name}`);
            
            this.markers.push(marker);
        });
    }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    // Mock config for now
    const mockConfig = {
        map: {
            default_center: { lat: 50.3167, lon: 11.9167 },
            default_zoom: 13,
            tile_provider: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        }
    };
    
    const app = new EventsApp(mockConfig);
    app.init();
});
```

#### 2.3 Create CSS

Create `assets/css/style.css`:

```css
/* Mobile-first styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
    width: 100%;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

#map {
    height: 100%;
    width: 100%;
}

/* Leaflet popup customization */
.leaflet-popup-content-wrapper {
    border-radius: 8px;
}
```

#### 2.4 Create Site Generator

Create `src/modules/site_generator.py`:

```python
"""
Static Site Generator
Assembles HTML from components and inlines all assets
"""

from pathlib import Path


def generate_site(base_path, config):
    """Generate static HTML site"""
    print("🏗️  Generating static site...")
    
    # Load components
    html_head = load_component(base_path, 'html-head.html')
    map_main = load_component(base_path, 'map-main.html')
    
    # Load assets
    css = load_file(base_path / 'assets/css/style.css')
    js = load_file(base_path / 'assets/js/app.js')
    
    # Build complete HTML
    html = f"""
{html_head}
<body>
{map_main}

<style>
{css}
</style>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
// Inline config
window.APP_CONFIG = {json.dumps(config)};
</script>

<script>
{js}
</script>

</body>
</html>
"""
    
    # Write output
    output_path = base_path / 'public/index.html'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated: {output_path}")
    return output_path


def load_component(base_path, filename):
    """Load HTML component"""
    path = base_path / 'assets/html' / filename
    return load_file(path)


def load_file(path):
    """Load text file"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

Update `src/event_manager.py` to call generator:

```python
# Add to imports
from pathlib import Path
from modules import site_generator, utils

# Update main() function
def main():
    base_path = Path(__file__).parent.parent
    
    if len(sys.argv) == 1:
        print("Launch TUI here (coming soon)")
    else:
        command = sys.argv[1]
        
        if command == "generate":
            config = utils.load_config(base_path)
            site_generator.generate_site(base_path, config)
        elif command == "--help":
            print_help()
        else:
            print(f"Unknown command: {command}")
```

#### 2.5 Test It

```bash
# Generate site
python3 src/event_manager.py generate

# Serve locally
cd public
python3 -m http.server 8000

# Open http://localhost:8000 in browser
# You should see a map with one marker!
```

### Phase 3: Event Scraping (Day 2-3)

**Goal**: Scrape real events from sources.

#### 3.1 Create Scraper Module

Create `src/modules/scraper.py`:

```python
"""
Event Scraper
Fetch events from RSS feeds, HTML pages, and APIs
"""

import requests
import feedparser
from bs4 import BeautifulSoup


class EventScraper:
    def __init__(self, config):
        self.config = config
        self.scraped_events = []
    
    def scrape_all_sources(self):
        """Scrape events from all enabled sources"""
        sources = self.config['scraping']['sources']
        
        for source in sources:
            if not source.get('enabled', True):
                continue
            
            print(f"📡 Scraping: {source['name']}")
            
            if source['type'] == 'rss':
                self.scrape_rss(source)
            elif source['type'] == 'html':
                self.scrape_html(source)
            else:
                print(f"⚠️  Unknown source type: {source['type']}")
        
        return self.scraped_events
    
    def scrape_rss(self, source):
        """Scrape events from RSS feed"""
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries:
                event = {
                    'id': f"rss_{source['name']}_{entry.id}",
                    'title': entry.title,
                    'description': entry.get('summary', ''),
                    'url': entry.link,
                    'start': entry.get('published', ''),
                    'location': source['options'].get('default_location', {}),
                    'category': source['options'].get('category', 'community')
                }
                
                self.scraped_events.append(event)
            
            print(f"  ✅ Found {len(feed.entries)} events")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def scrape_html(self, source):
        """Scrape events from HTML page"""
        print(f"  ⚠️  HTML scraping not implemented yet")
```

#### 3.2 Test Scraping

```bash
# Add scrape command to event_manager.py
python3 src/event_manager.py scrape
```

### Phase 4: Testing & Validation (Day 3-4)

**Goal**: Ensure everything works correctly.

#### 4.1 Create Test Suite

Create `tests/test_scraper.py`:

```python
"""
Test Event Scraper
"""

import unittest
from pathlib import Path
from src.modules import scraper, utils


class TestScraper(unittest.TestCase):
    def setUp(self):
        base_path = Path(__file__).parent.parent
        self.config = utils.load_config(base_path)
    
    def test_scraper_initialization(self):
        """Test scraper can be initialized"""
        s = scraper.EventScraper(self.config)
        self.assertIsNotNone(s)
    
    def test_scrape_sources(self):
        """Test scraping from configured sources"""
        s = scraper.EventScraper(self.config)
        events = s.scrape_all_sources()
        
        # Should find at least some events
        self.assertIsInstance(events, list)


if __name__ == '__main__':
    unittest.main()
```

#### 4.2 Run Tests

```bash
python3 tests/test_scraper.py --verbose
```

### Phase 5: Deployment (Day 4-5)

**Goal**: Deploy to GitHub Pages.

#### 5.1 Create GitHub Actions Workflow

Create `.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate site
        run: python3 src/event_manager.py generate
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: ./public
      
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v2
```

#### 5.2 Enable GitHub Pages

1. Go to repository Settings → Pages
2. Source: "GitHub Actions"
3. Save

#### 5.3 Push and Deploy

```bash
git add .
git commit -m "Initial deployment"
git push origin main

# Check Actions tab for deployment status
```

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Create duplicate entry points

```bash
# WRONG - Do NOT create these:
src/main.py        # Use src/event_manager.py only!
src/cli.py
src/run.py
```

### ❌ DON'T: Edit auto-generated files

```bash
# WRONG - Do NOT edit:
public/index.html  # This is auto-generated!

# CORRECT - Edit source files:
assets/css/style.css
assets/js/app.js
```

### ❌ DON'T: Hardcode environment values

```json
// WRONG - Do NOT do this:
{
  "debug": true,
  "data": { "source": "both" }
}

// CORRECT - Use auto-detection:
{
  "environment": "auto"
}
```

### ❌ DON'T: Skip feature registry

```bash
# WRONG - Adding features without updating registry
# This will cause validation tests to fail!

# CORRECT - Always update features.json when adding features
```

### ❌ DON'T: Put sensitive data in config

```json
// WRONG:
{
  "api_key": "secret123",
  "password": "mypass"
}

// CORRECT: Use environment variables
import os
api_key = os.environ.get('API_KEY')
```

---

## ✅ Validation Checklist

Before considering your implementation complete, verify:

- [ ] Project structure matches recommended layout
- [ ] Single entry point at `src/event_manager.py`
- [ ] Config auto-detection works (test in dev/prod)
- [ ] Source files editable (not editing `public/index.html`)
- [ ] All features documented in `features.json`
- [ ] Tests pass: `python3 tests/test_*.py`
- [ ] Site generates: `python3 src/event_manager.py generate`
- [ ] Local preview works: `cd public && python3 -m http.server`
- [ ] Map displays with markers
- [ ] `.gitignore` excludes build artifacts
- [ ] GitHub Actions workflow deploys successfully

---

## 📚 Next Steps & Advanced Features

Once your foundation is solid, consider adding:

### Backend Enhancements
- **Editorial Workflow**: Review/approve events before publishing
- **Multiple Scrapers**: HTML parsing, API integration
- **OCR for Flyers**: Extract events from images (Tesseract)
- **AI Categorization**: Use Ollama for smart categorization
- **Location Resolution**: Resolve venue names to coordinates
- **Event Archiving**: Archive old events automatically

### Frontend Enhancements
- **Filters**: Category, time range, distance filters
- **Geolocation**: User's current location
- **Speech Bubbles**: Event info cards on map
- **Time Drawer**: Timeline-based event visualization
- **Keyboard Navigation**: Arrow keys, ESC, zoom controls
- **Responsive Design**: Mobile-first with touch gestures
- **PWA Features**: Installability, offline mode, manifest

### Infrastructure
- **CI/CD**: Automated testing, deployment
- **Documentation**: Auto-generate README from docstrings
- **WCAG Compliance**: Accessibility linting
- **Performance**: Asset optimization, caching
- **Monitoring**: Error tracking, analytics

---

## 📖 Reference Documentation

For detailed information, see:

- **README.md** - Comprehensive project documentation
- **.github/copilot-instructions.md** - Detailed coding guidelines
- **features.json** - Complete feature registry
- **config.json** - Configuration reference (inline comments)

---

## 💡 Philosophy: KISS Principles

This project follows **Keep It Simple, Stupid** (KISS):

1. **No Frameworks** - Vanilla JavaScript (just Leaflet.js)
2. **Single Entry Point** - One `event_manager.py` (not multiple)
3. **Single Config** - One `config.json` with auto-detection
4. **Single HTML** - All assets inlined in one file
5. **Minimal Complexity** - Avoid over-engineering
6. **Progressive Enhancement** - Start simple, add features gradually

**Remember**: It's easier to add complexity later than to simplify complex code.

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
# Ensure you're in project root and venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "Map not loading"
```bash
# Check browser console for errors
# Verify Leaflet CDN is accessible
# Ensure config.json has valid map center coordinates
```

### "Events not appearing"
```bash
# Verify events.json exists and has valid data
# Check config.json -> data.source setting
# Look for JavaScript errors in browser console
```

### "Site generator fails"
```bash
# Verify all HTML components exist in assets/html/
# Check file paths are correct
# Ensure output directory (public/) is writable
```

---

## 🎉 Success Indicators

You'll know your implementation is successful when:

1. ✅ Map loads with your event markers
2. ✅ Events are clickable and show details
3. ✅ Filters work (distance, time, category)
4. ✅ Works on mobile devices
5. ✅ Deploys automatically via GitHub Actions
6. ✅ Tests pass without errors
7. ✅ Environment auto-detection works
8. ✅ No orphan files or duplicate code

---

**Built with 💖 following KISS principles**

*Last updated: 2026-01-18*
