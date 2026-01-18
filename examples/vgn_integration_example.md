# VGN Integration Example: Discovering Event Sources

This example demonstrates how to use the VGN Transit Integration to discover new event sources in areas reachable by public transport from Hof.

## Scenario

You're managing a community events platform in Hof, Bavaria. You want to:
1. Find which nearby towns are easily reachable by train/bus
2. Discover local event sources (news sites, social media) in those towns
3. Add those sources to your scraping configuration

## Step 1: Analyze Reachability

First, let's see which areas are reachable within 30 minutes:

```bash
python3 src/event_manager.py vgn analyze 30
```

**Output:**
```
🚇 VGN Transit Reachability Analysis
============================================================

📍 Reference Location:
   Hof Hauptbahnhof
   (50.308053, 11.9233)

⏱️  Maximum Travel Time: 30 minutes

────────────────────────────────────────────────────────────

🚉 Reachable Stations:

   • Hof Hauptbahnhof
     Municipality: Hof
     Travel Time: 0 min
     Transfers: 0

   • Hof Neuhof
     Municipality: Hof
     Travel Time: 10 min
     Transfers: 0
     Line: Bus 1

   • Rehau
     Municipality: Rehau
     Travel Time: 25 min
     Transfers: 0
     Line: S4

🏘️  Reachable Municipalities:

   • Hof
     Stations: 2
     Min Travel Time: 0 min

   • Rehau
     Stations: 1
     Min Travel Time: 25 min
```

**Key Findings:**
- Hof and Rehau are reachable within 30 minutes
- Rehau is only 25 minutes away by S4 train
- No transfers needed to reach Rehau

## Step 2: Discover Event Sources

Now let's find event sources in these reachable areas:

```bash
python3 src/event_manager.py vgn suggest-sources 30
```

**Output:**
```
🔍 VGN Event Source Discovery
============================================================

⏱️  Maximum Travel Time: 30 minutes

Analyzing reachable areas for event sources...

✅ Found 5 potential event sources:

────────────────────────────────────────────────────────────

📍 Hof (0 min travel time):

   • Hof Tourist Info
     Type: html
     Category: community
     URL: https://www.hof.de/hof/hof_deu/leben/veranstaltungen.html
     Description: Official city events calendar

   • Frankenpost Hof
     Type: html
     Category: news
     URL: https://event.frankenpost.de/index.php?kat=&community=95028+Hof&range=50
     Description: Regional newspaper events section

📍 Rehau (25 min travel time):

   • Stadt Rehau
     Type: html
     Category: community
     URL: https://rehau.bayern/de/kultur/veranstaltungen
     Description: City of Rehau official events

   • Rehau Facebook
     Type: facebook
     Category: social
     URL: https://www.facebook.com/StadtRehau
     Description: City of Rehau social media
```

**Insights:**
- Hof sources are already in our config (marked as `existing: true`)
- Rehau has 2 potential sources we're not scraping yet
- Rehau's Facebook page could have local events
- Rehau's official website has an events calendar

## Step 3: Add New Sources to Config

Let's add Rehau's sources to our scraping configuration:

Edit `config.json`:

```json
{
  "scraping": {
    "sources": [
      // ... existing sources ...
      
      {
        "name": "Stadt Rehau",
        "url": "https://rehau.bayern/de/kultur/veranstaltungen",
        "type": "html",
        "enabled": true,
        "notes": "City of Rehau events - 25 min by S4",
        "options": {
          "filter_ads": true,
          "max_days_ahead": 90,
          "category": "community",
          "default_location": {
            "name": "Rehau",
            "lat": 50.2489,
            "lon": 12.0364
          }
        }
      },
      {
        "name": "Rehau Facebook",
        "url": "https://www.facebook.com/StadtRehau",
        "type": "facebook",
        "enabled": true,
        "notes": "City social media - 25 min by S4",
        "options": {
          "filter_ads": true,
          "scan_posts": true,
          "ocr_enabled": true,
          "max_days_ahead": 90,
          "category": "community",
          "default_location": {
            "name": "Rehau",
            "lat": 50.2489,
            "lon": 12.0364
          }
        }
      }
    ]
  }
}
```

## Step 4: Test Scraping

Now test scraping from the new sources:

```bash
python3 src/event_manager.py scrape
```

**Expected Output:**
```
Scraping events from configured sources...
✓ Scraped 2 new events from Stadt Rehau
✓ Scraped 1 new event from Rehau Facebook
✓ Scraped 15 new events total
```

## Step 5: Export Analysis Report

Generate a comprehensive report for documentation:

```bash
python3 src/event_manager.py vgn export-report 30 assets/json/vgn_analysis.json
```

**Output:**
```
📄 Exporting VGN Analysis Report
============================================================

⏱️  Maximum Travel Time: 30 minutes
📁 Output: assets/json/vgn_analysis.json

Generating report...

✅ Report generated successfully!

📊 Summary:
   • Stations: 3
   • Municipalities: 2
   • Suggested Sources: 5

📁 Full report saved to: assets/json/vgn_analysis.json
```

The report contains:
- Full list of reachable stations with coordinates
- Municipality breakdown
- All suggested sources with metadata
- Transit times and distances
- Timestamp for tracking changes

## Step 6: Expand Radius

Want to reach more areas? Try a longer travel time:

```bash
python3 src/event_manager.py vgn analyze 45
```

**Output:**
```
🚉 Reachable Stations:

   • Hof Hauptbahnhof (0 min)
   • Hof Neuhof (10 min, Bus 1)
   • Rehau (25 min, S4)
   • Selb (35 min, S4, 1 transfer)  ← NEW!

🏘️  Reachable Municipalities:

   • Hof (0 min)
   • Rehau (25 min)
   • Selb (35 min)  ← NEW!
```

Now Selb is reachable! Check for sources:

```bash
python3 src/event_manager.py vgn suggest-sources 45
```

**Output:**
```
📍 Selb (35 min travel time):

   • Stadt Selb
     Type: html
     URL: https://www.selb.de/freizeit-tourismus/veranstaltungen
     Description: City of Selb events calendar

   • Porzellanikon Selb
     Type: html
     URL: https://www.porzellanikon.org/veranstaltungen
     Description: Porcelain museum events
```

## Benefits of This Workflow

1. **Data-Driven Decisions**: Know exactly how far events are
2. **Transit Context**: "This event is 25 min away by S4 train"
3. **Coverage Analysis**: Identify gaps in event source coverage
4. **Scalability**: Easily expand to new regions as transit improves
5. **User Value**: Users can filter events by transit accessibility

## Python API Example

You can also use the VGN module programmatically:

```python
from pathlib import Path
from modules.vgn_transit import VGNTransit
from modules.utils import load_config

# Initialize
base_path = Path(".")
config = load_config(base_path)
vgn = VGNTransit(config, base_path)

# Get reachable areas
stations = vgn.get_reachable_stations(max_travel_time_minutes=30)
municipalities = vgn.get_reachable_municipalities(30)
sources = vgn.suggest_event_sources(30)

# Analyze coverage
current_sources = set(s['name'] for s in config['scraping']['sources'])
suggested_sources = set(s.name for s in sources)
missing_sources = suggested_sources - current_sources

print(f"Coverage: {len(current_sources)} / {len(suggested_sources)} sources")
print(f"Missing: {', '.join(missing_sources)}")
```

## Next Steps

1. **Add Transit Info to Events**: Show "How to get there" on event cards
2. **Filter by Reachability**: Let users filter events by transit time
3. **Automated Discovery**: Run VGN analysis weekly to find new sources
4. **Accessibility Analysis**: Identify wheelchair-accessible stations
5. **Multi-Modal Routes**: Include walking/cycling options

## Troubleshooting

**VGN Library Not Installed:**
```bash
pip install vgn
```

**No Sources Found:**
- Check `assets/json/regional_sources.json` has entries for reachable municipalities
- Add new municipalities to the database
- Increase travel time: `vgn analyze 60`

**API Errors:**
- VGN API may have rate limits
- Analysis results are cached for 24 hours
- Use mock data for testing (works without API)

## Additional Resources

- Full Documentation: `docs/VGN_TRANSIT_INTEGRATION.md`
- VGN Open Data: https://www.vgn.de/web-entwickler/open-data/
- Python Library: https://github.com/becheran/vgn
- Tests: `tests/test_vgn_transit.py`
