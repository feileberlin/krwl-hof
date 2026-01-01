# Image Analysis Guide

## Overview

The SmartScraper system can extract event information from images (posters, flyers, social media posts) using:
- **EXIF metadata** extraction (GPS, timestamps)
- **OCR** (Optical Character Recognition) 
- **AI-powered** image understanding

## Features

### 1. EXIF Metadata Extraction
- GPS coordinates → event location
- Date/time original → event start time
- Camera info, image dimensions

### 2. OCR Text Recognition
- Extract text from images
- Multiple OCR providers supported
- Multi-language support
- Date/time pattern recognition
- URL extraction

### 3. AI Image Analysis
- Structured event extraction from poster images
- Understanding visual context
- Handling complex layouts

## Configuration

### Basic Setup

```json
{
  "image_analysis": {
    "enabled": true,
    "ocr_enabled": true,
    "ocr_provider": "tesseract",
    "languages": ["eng", "deu"],
    "ai_provider": "duckduckgo"
  }
}
```

### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `enabled` | boolean | Enable image analysis | `false` |
| `ocr_enabled` | boolean | Enable OCR text extraction | `true` |
| `ocr_provider` | string | OCR engine (`tesseract`, `easyocr`, `paddleocr`) | `tesseract` |
| `languages` | array | Language codes for OCR | `["eng"]` |
| `ai_provider` | string | AI provider for image understanding | Default provider |

## Installation

### Tesseract OCR (Recommended)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu
pip install pytesseract Pillow exifread
```

**macOS:**
```bash
brew install tesseract tesseract-lang
pip install pytesseract Pillow exifread
```

**Windows:**
1. Download [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH
3. `pip install pytesseract Pillow exifread`

### Alternative OCR Engines

**EasyOCR** (GPU recommended):
```bash
pip install easyocr
```

**PaddleOCR**:
```bash
pip install paddleocr
```

## Usage

### From Python

```python
from modules.smart_scraper import SmartScraper

config = {...}  # Your configuration
scraper = SmartScraper(config, '/path/to/data')

# Analyze image
event_data = scraper.analyze_image('event_poster.jpg')

if event_data:
    print(f"Title: {event_data.get('title')}")
    print(f"Date: {event_data.get('start_time')}")
    print(f"Location: {event_data.get('location')}")
```

### From CLI

```bash
# Analyze single image
python3 src/main.py analyze-image event_poster.jpg

# Batch analyze directory
python3 src/main.py analyze-images posters/*.jpg
```

## What Gets Extracted

### From EXIF Metadata

```json
{
  "metadata": {
    "gps": {
      "lat": 50.3167,
      "lon": 11.9167
    },
    "datetime": "2024-06-15T14:30:00",
    "width": 1920,
    "height": 1080,
    "format": "JPEG"
  }
}
```

### From OCR

```json
{
  "ocr_text": "Summer Festival\\n15-17 June 2024\\nCentral Park\\nwww.example.com",
  "dates_found": ["15-17 June 2024"],
  "times_found": ["19:00"],
  "urls_found": ["www.example.com"]
}
```

### From AI Analysis

```json
{
  "title": "Summer Festival",
  "description": "Annual music festival with local and international artists",
  "start_time": "2024-06-15T19:00:00",
  "end_time": "2024-06-17T23:00:00",
  "location": {
    "name": "Central Park",
    "lat": 50.3167,
    "lon": 11.9167
  },
  "url": "https://www.example.com"
}
```

## Supported Image Formats

- JPEG/JPG
- PNG
- TIFF
- BMP
- WebP

## Best Practices

### 1. Image Quality

Better quality → better results:
- **Resolution**: 1000x1000px or higher
- **Format**: JPEG or PNG
- **Contrast**: High contrast between text and background
- **Angle**: Straight-on, not skewed

### 2. Preprocessing

For poor quality images, preprocess:
```python
from PIL import Image, ImageEnhance

# Increase contrast
img = Image.open('poster.jpg')
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)
img.save('enhanced.jpg')
```

### 3. Language Configuration

Configure OCR for correct languages:
```json
{
  "languages": ["eng", "deu"]  // English + German
}
```

Available language codes:
- `eng`: English
- `deu`: German
- `fra`: French
- `spa`: Spanish
- `ita`: Italian

### 4. Batch Processing

Process multiple images:
```python
import glob

for image_path in glob.glob('posters/*.jpg'):
    event_data = scraper.analyze_image(image_path)
    if event_data:
        # Add to pending events
        ...
```

### 5. Fallback Strategy

Use multiple extraction methods:
1. Try EXIF metadata (fastest)
2. Try OCR + pattern matching
3. Try AI analysis (most accurate, slowest)

## Troubleshooting

### Tesseract Not Found

```
Error: Tesseract not installed
```

**Solution**: Install Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify installation
tesseract --version
```

### Poor OCR Results

**Symptoms**:
- Gibberish text
- Missing text
- Wrong characters

**Solutions**:
1. Improve image quality
2. Increase image resolution
3. Enhance contrast
4. Try different OCR engine
5. Specify correct language

### AI Not Extracting Data

```
AI image analysis error: ...
```

**Solutions**:
1. Check AI provider configuration
2. Verify API keys (if required)
3. Check image file is readable
4. Try text-only extraction first

### No GPS Data

**Note**: Most downloaded images don't have GPS data

**Solutions**:
- Use AI to extract location from text
- Configure default location per source
- Use geocoding APIs for addresses

## Performance

### Speed Comparison

| Method | Speed | Accuracy |
|--------|-------|----------|
| EXIF only | < 0.1s | High (if present) |
| OCR (Tesseract) | 1-3s | Medium-High |
| OCR (EasyOCR) | 3-10s | High |
| AI Analysis | 5-30s | Very High |

### Optimization Tips

1. **Process images offline** during scraping
2. **Cache OCR results** to avoid reprocessing
3. **Use lightweight OCR** (Tesseract) for speed
4. **Reserve AI analysis** for complex cases
5. **Batch process** images in parallel

## Examples

### Event Poster

**Input**: `summer_fest_2024.jpg`
- Title in large text
- Dates in corner
- Venue address
- Website URL

**Output**:
```json
{
  "title": "Summer Music Festival 2024",
  "description": "3-day outdoor music event",
  "start_time": "2024-07-12T18:00:00",
  "end_time": "2024-07-14T23:00:00",
  "location": {
    "name": "Central Park Amphitheater",
    "address": "123 Park Ave, Hof"
  },
  "url": "https://summerfest2024.com",
  "source": "image_analysis"
}
```

### Social Media Post Screenshot

Can extract events from:
- Facebook event images
- Instagram story screenshots
- Twitter/X event announcements
- WhatsApp group messages

## Integration

### With Social Media Scrapers

Combine social media scraping + image analysis:

```python
# Scrape Facebook page
events = scraper.scrape_source({
    'type': 'facebook',
    'url': '...'
})

# Analyze event images
for event in events:
    if event.get('image_url'):
        # Download image
        image_data = download_image(event['image_url'])
        
        # Analyze
        analysis = scraper.analyze_image(image_data)
        
        # Merge data
        event.update(analysis)
```

## Future Enhancements

- PDF poster extraction
- Video frame analysis
- Multi-image event detection
- QR code scanning
- Barcode reading
- Map screenshot parsing

## Dependencies

```bash
# Required
pip install Pillow>=10.0.0

# Optional - Metadata
pip install exifread>=3.0.0

# Optional - OCR
pip install pytesseract>=0.3.10  # + system Tesseract
pip install easyocr>=1.7.0       # GPU recommended
pip install paddleocr>=2.7.0     # Alternative OCR
```

## Resources

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [ExifRead](https://github.com/ianare/exif-py)
