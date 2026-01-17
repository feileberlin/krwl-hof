# Debugging Facebook Scraping - Troubleshooting Guide

## Common Issue: Getting No Events/Data

When Facebook scraping returns 0 events, follow this systematic debugging approach:

---

## 🔍 Quick Diagnostics

### 1. Check Basic Connectivity
```bash
# Test if you can reach Facebook
curl -I https://m.facebook.com

# Expected: HTTP 200 or 301/302 redirect
# If fails: Network issue (firewall, VPN, blocked)
```

### 2. Check Scraper Configuration
```bash
# View your Facebook sources
python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
    fb_sources = [s for s in config['scraping']['sources'] if s['type'] == 'facebook']
    for src in fb_sources:
        print(f\"✓ {src['name']}: {src['url']}\")
        print(f\"  Enabled: {src.get('enabled', False)}\")
        print(f\"  scan_posts: {src.get('options', {}).get('scan_posts', False)}\")
        print(f\"  ocr_enabled: {src.get('options', {}).get('ocr_enabled', False)}\")
"
```

### 3. Run With Verbose Logging
```bash
# Enable Python logging to see detailed output
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)

import sys
sys.path.insert(0, 'src')
from modules.utils import load_config
from modules.smart_scraper.core import SmartScraper
from pathlib import Path

config = load_config(Path('.'))
scraper = SmartScraper(config, '.')

# Test single Facebook source
fb_source = [s for s in config['scraping']['sources'] 
             if s['name'] == 'Galeriehaus'][0]  # Change name as needed
events = scraper.scrape_source(fb_source)
print(f'\nResult: {len(events)} events found')
for e in events:
    print(f\"  - {e.get('title', 'No title')}\")
"
```

---

## 🐛 Step-by-Step Debugging

### Step 1: Test Network Access
```bash
# Can you reach the specific Facebook page?
curl -L "https://www.facebook.com/GaleriehausHof/events" | head -100

# Check response:
# - If empty or "Page not found": URL is wrong
# - If shows HTML: Network works, check HTML structure
# - If shows "rate limit" or "security check": Facebook blocking you
```

### Step 2: Test URL Format
Facebook URLs must be public pages. Test different formats:
```python
# Good URLs:
✅ https://www.facebook.com/GaleriehausHof/events
✅ https://www.facebook.com/GaleriehausHof
✅ https://m.facebook.com/GaleriehausHof

# Bad URLs:
❌ https://facebook.com/profile.php?id=123 (private profile)
❌ https://facebook.com/groups/123 (requires login)
❌ https://facebook.com/events/123 (single event, not page)
```

### Step 3: Check Page Accessibility
```bash
# Download page HTML for inspection
curl -L -A "Mozilla/5.0" "https://m.facebook.com/GaleriehausHof" > /tmp/fb_page.html

# Check file size
ls -lh /tmp/fb_page.html

# If < 10KB: Likely blocked or login required
# If > 100KB: Page loaded, inspect content
```

### Step 4: Inspect HTML Structure
```bash
# Look for event indicators in the HTML
grep -i "event\|veranstaltung\|konzert" /tmp/fb_page.html | head -10

# Look for post containers
grep -i "story\|post\|article" /tmp/fb_page.html | head -10

# If nothing found: Page structure changed or no posts
```

### Step 5: Test Post Extraction
```python
# Test if scraper can find posts
python3 -c "
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, 'src')

with open('/tmp/fb_page.html') as f:
    soup = BeautifulSoup(f.read(), 'lxml')

# Try different selectors
selectors = [
    'article',
    '[data-ft]',
    '.story_body_container',
    '[role=\"article\"]',
    'div[id^=\"u_\"]'
]

for selector in selectors:
    posts = soup.select(selector)
    print(f'{selector}: {len(posts)} elements found')
"
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "0 events scraped" (scan_posts = false)
**Cause**: Not looking at regular posts, only /events page

**Solution**: Enable post scanning
```json
{
  "name": "Galeriehaus",
  "url": "https://www.facebook.com/GaleriehausHof/events",
  "type": "facebook",
  "enabled": true,
  "options": {
    "scan_posts": true,  // ← ADD THIS
    "ocr_enabled": true
  }
}
```

### Issue 2: "Request error: Failed to resolve"
**Cause**: Network blocked (firewall, VPN, Copilot Workspace)

**Solution**: 
- **Local testing**: Disable VPN, check firewall
- **Production**: Works automatically in GitHub Actions
- **Copilot Workspace**: Expected (no fix needed)

### Issue 3: "OCR enabled: False"
**Cause**: Tesseract not installed

**Solution**:
```bash
# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng

# macOS:
brew install tesseract tesseract-lang

# Verify:
tesseract --version
```

### Issue 4: Facebook rate limiting
**Cause**: Too many requests, detected as bot

**Solution**:
```json
{
  "options": {
    "rate_limit_delay": 5.0,  // Increase delay between requests
    "max_retries": 2           // Reduce retries
  }
}
```

### Issue 5: Posts found but no events extracted
**Cause**: Posts don't contain event indicators

**Solution**: Lower confidence threshold or check keywords
```json
{
  "options": {
    "min_ocr_confidence": 0.2,  // Lower from 0.3 (more lenient)
    "include_keywords": ["konzert", "live", "event", "veranstaltung"]
  }
}
```

---

## 📊 Debug Output Interpretation

### Good Output (Working):
```
INFO: Scraping from: Galeriehaus
    📸 OCR enabled: True
      Analyzing image: https://scontent.xx.fbcdn.net/...
      ✓ OCR confidence: 0.85
      ✓ Found date: 2026-02-15
      ✓ Found title: Simone White Live
    📊 Found 3 potential events
INFO: Found 3 events from Galeriehaus
```

### Bad Output (Network Issue):
```
INFO: Scraping from: Galeriehaus
      Request error: HTTPSConnectionPool(host='m.m.facebook.com'...)
    🔍 Trying web search fallback...
    📸 OCR enabled: True
    📊 Found 0 potential events
INFO: Found 0 events from Galeriehaus
```

### Bad Output (No Posts Found):
```
INFO: Scraping from: Galeriehaus
    📸 OCR enabled: True
    📊 Found 0 potential events  ← No posts extracted!
INFO: Found 0 events from Galeriehaus
```

---

## 🧪 Advanced Debugging

### Test 1: Manual HTML Parsing
```python
import sys
sys.path.insert(0, 'src')
from modules.smart_scraper.sources.social.facebook import FacebookSource
from modules.smart_scraper.base import SourceOptions
from pathlib import Path

# Configure source
source_config = {
    'name': 'Test',
    'url': 'https://www.facebook.com/GaleriehausHof',
    'type': 'facebook',
    'options': {'scan_posts': True, 'ocr_enabled': True}
}
options = SourceOptions.from_dict(source_config.get('options', {}))

# Create scraper
scraper = FacebookSource(source_config, options, base_path=Path('.'))

# Test scraping
events = scraper.scrape()
print(f"Events found: {len(events)}")
for event in events:
    print(f"  - {event.get('title')}")
    print(f"    Date: {event.get('start_time')}")
    print(f"    Source: {event.get('source')}")
```

### Test 2: Check Post Cache
```bash
# See if posts are being cached (and skipped)
cat data/scraper_cache/facebook_posts_galeriehaus.json | python3 -m json.tool | head -30

# If cache exists and you want fresh scrape:
rm data/scraper_cache/facebook_posts_*.json

# Or use force_scan option:
# "force_scan": true
```

### Test 3: Test OCR Directly
```python
from src.modules.smart_scraper.image_analyzer import ImageAnalyzer

# Download a test flyer
import requests
response = requests.get('https://scontent.xx.fbcdn.net/...jpg')  # Real URL
with open('/tmp/test_flyer.jpg', 'wb') as f:
    f.write(response.content)

# Test OCR
analyzer = ImageAnalyzer({'ocr_enabled': True, 'languages': ['deu', 'eng']})
result = analyzer.analyze('/tmp/test_flyer.jpg')

print(f"OCR confidence: {result.get('ocr_confidence')}")
print(f"Text extracted: {result.get('text')[:200]}")
print(f"Event data: {result}")
```

---

## 📋 Debugging Checklist

When debugging Facebook scraping, go through this checklist:

- [ ] **Network**: Can reach facebook.com? (`curl -I https://m.facebook.com`)
- [ ] **URL**: Is URL correct and public? (not private profile/group)
- [ ] **Config**: Is source enabled in config.json?
- [ ] **scan_posts**: Is scan_posts=true for post scraping?
- [ ] **OCR**: Is Tesseract installed? (`tesseract --version`)
- [ ] **HTML**: Can download page HTML? (`curl` test)
- [ ] **Posts**: Does HTML contain posts? (`grep` test)
- [ ] **Rate Limit**: Being blocked by Facebook? (check HTML for "security check")
- [ ] **Cache**: Clear cache if posts were previously processed
- [ ] **Threshold**: Try lower min_ocr_confidence (0.2 instead of 0.3)

---

## 🆘 Still Not Working?

### Last Resort Debugging
```bash
# 1. Run with maximum verbosity
PYTHONPATH=src python3 -u src/event_manager.py scrape 2>&1 | tee debug.log

# 2. Check the log for specific errors
grep -i "error\|fail\|exception" debug.log

# 3. Test with known working page
# Try a page that definitely has events
# Example: facebook.com/events/local (if in your area)

# 4. Compare HTML structure
# Download HTML from both working and non-working pages
# Compare structure to see what's different
```

### Get Help
1. **Check logs**: Review full scraping logs for error messages
2. **Share debug output**: Post the output from verbose logging
3. **Check page HTML**: Download and inspect the actual HTML
4. **Try different page**: Test with another Facebook page to isolate issue

---

## 💡 Quick Fixes Summary

| Symptom | Quick Fix |
|---------|-----------|
| "0 events scraped" | Enable `scan_posts: true` |
| "Request error" | Check network/firewall |
| "OCR enabled: False" | Install Tesseract (`apt-get install tesseract-ocr`) |
| "0 potential events" found | Lower `min_ocr_confidence` to 0.2 |
| Works locally, not in CI | Expected - CI has network restrictions |
| Was working, now broken | Clear cache: `rm data/scraper_cache/facebook_posts_*.json` |

---

## 🎯 Expected Behavior

**Working Facebook scraper should show:**
```
INFO: Scraping from: Galeriehaus
    📸 OCR enabled: True
    📊 Found 5 potential events
INFO: Found 5 events from Galeriehaus
```

**Each event should have:**
- Title (from post text or OCR)
- Date (extracted from text/image)
- Location (from config default_location)
- Source (page name)
- URL (link to Facebook post/event)
