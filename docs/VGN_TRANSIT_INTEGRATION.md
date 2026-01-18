# VGN Public Transport Integration

## Overview

The VGN (Verkehrsverbund Großraum Nürnberg) Transit Integration module provides public transport reachability analysis for the KRWL HOF Community Events platform. It helps answer key questions:

1. **Which stations/municipalities can we reach from Hof** within a specified time?
2. **What social media and news sources** do people in those areas use to promote events?
3. **How can we scrape those sources** for local event data analysis?

## Features

### ✅ Station Reachability Analysis
- Calculate which VGN stations are reachable within X minutes
- Show travel times, transfer counts, and line information
- Group stations by municipality/region

### ✅ Regional Source Discovery
- Suggest event sources (social media, news, cultural venues) in reachable areas
- Map municipalities to known event publishers
- Identify gaps in current scraping coverage

### ✅ Transit Time Information
- Calculate transit time to event locations
- Provide "How to get there" information
- Support accessibility analysis

### ✅ Analysis Reports
- Export comprehensive JSON reports
- Cache results to avoid excessive API calls
- Integration with existing event workflow

## Installation

### Prerequisites

```bash
# Install VGN Python library
pip install vgn

# Or add to requirements.txt
echo "vgn>=0.1.0" >> requirements.txt
pip install -r requirements.txt
```

### Configuration

Enable VGN integration in `config.json`:

```json
{
  "vgn": {
    "enabled": true,
    "reference_location": {
      "name": "Hof Hauptbahnhof",
      "lat": 50.308053,
      "lon": 11.9233
    },
    "reachability": {
      "max_travel_time_minutes": 30,
      "max_transfers": 2,
      "include_walking": true
    },
    "analysis": {
      "cache_hours": 24,
      "output_path": "assets/json/vgn_analysis.json"
    },
    "source_discovery": {
      "enabled": true,
      "min_population": 5000,
      "categories": ["community", "culture", "news", "social"]
    }
  }
}
```

## CLI Usage

### Analyze Reachability

Show stations and municipalities reachable within specified time:

```bash
# Default: 30 minutes
python3 src/event_manager.py vgn analyze

# Custom time: 45 minutes
python3 src/event_manager.py vgn analyze 45
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

### Suggest Event Sources

Identify potential event sources in reachable areas:

```bash
# Default: 30 minutes
python3 src/event_manager.py vgn suggest-sources

# Custom time: 45 minutes
python3 src/event_manager.py vgn suggest-sources 45
```

**Output:**
```
🔍 VGN Event Source Discovery
============================================================

⏱️  Maximum Travel Time: 30 minutes

Analyzing reachable areas for event sources...

✅ Found 8 potential event sources:

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
     URL: https://event.frankenpost.de/...
     Description: Regional newspaper events section

📍 Rehau (25 min travel time):

   • Stadt Rehau
     Type: html
     Category: community
     URL: https://rehau.bayern/de/kultur/veranstaltungen
     Description: City of Rehau official events
```

### Export Analysis Report

Generate comprehensive JSON report:

```bash
# Default output: assets/json/vgn_analysis.json
python3 src/event_manager.py vgn export-report

# Custom time and output
python3 src/event_manager.py vgn export-report 45 /path/to/report.json
```

**Report Structure:**
```json
{
  "generated_at": "2026-01-18T10:00:00",
  "reference_location": {
    "latitude": 50.308053,
    "longitude": 11.9233,
    "name": "Hof Hauptbahnhof"
  },
  "max_travel_time_minutes": 30,
  "reachable_stations": [
    {
      "name": "Hof Hauptbahnhof",
      "id": "vgn_hof_hbf",
      "municipality": "Hof",
      "coordinates": {"lat": 50.308053, "lon": 11.9233},
      "travel_time_minutes": 0,
      "transfers": 0,
      "line": null
    }
  ],
  "reachable_municipalities": [
    {
      "name": "Hof",
      "stations": [...],
      "min_travel_time": 0,
      "station_count": 2
    }
  ],
  "suggested_sources": [
    {
      "name": "Hof Tourist Info",
      "type": "html",
      "url": "https://...",
      "municipality": "Hof",
      "category": "community",
      "description": "...",
      "distance_km": 0.0,
      "travel_time_minutes": 0
    }
  ]
}
```

## Python API

### Basic Usage

```python
from pathlib import Path
from modules.vgn_transit import VGNTransit
from modules.utils import load_config

# Initialize
base_path = Path(".")
config = load_config(base_path)
vgn = VGNTransit(config, base_path)

# Check availability
if vgn.is_available():
    # Get reachable stations
    stations = vgn.get_reachable_stations(max_travel_time_minutes=30)
    
    for station in stations:
        print(f"{station.name}: {station.travel_time_minutes} min")
    
    # Get municipalities
    municipalities = vgn.get_reachable_municipalities(30)
    
    # Suggest sources
    sources = vgn.suggest_event_sources(30)
    
    # Export report
    report = vgn.export_analysis_report(30, Path("report.json"))
```

### Calculate Transit Time

```python
# Get transit time to specific location
transit_info = vgn.calculate_transit_time(
    destination_lat=50.2489,
    destination_lon=12.0364
)

if transit_info:
    print(f"Duration: {transit_info['duration_minutes']} minutes")
    print(f"Transfers: {transit_info['transfers']}")
    print(f"Lines: {', '.join(transit_info['lines'])}")
```

## Regional Sources Database

Event sources are organized in `assets/json/regional_sources.json`:

```json
{
  "Municipality Name": [
    {
      "name": "Source Name",
      "type": "html|facebook|rss|instagram",
      "url": "https://...",
      "category": "community|culture|news|social",
      "description": "Brief description",
      "distance_km": 0.0,
      "existing": true|false
    }
  ]
}
```

**Adding New Sources:**

1. Identify municipality name (must match VGN station data)
2. Add source object to municipality array
3. Set `existing: false` for new suggestions
4. Run analysis to see suggested sources

## Use Cases

### 1. Discovering New Event Sources

**Problem:** We want to find more event sources in areas people can easily reach by public transport.

**Solution:**
```bash
# Find reachable areas
python3 src/event_manager.py vgn analyze 45

# Get source suggestions
python3 src/event_manager.py vgn suggest-sources 45

# Review suggestions and add to config.json
```

### 2. Transit-Based Event Filtering

**Problem:** Users want to see only events they can reach by public transport.

**Solution:**
```python
# For each event
transit_time = vgn.calculate_transit_time(
    event['location']['lat'],
    event['location']['lon']
)

# Filter events
if transit_time and transit_time['duration_minutes'] <= 30:
    # Show event with transit info
    event['transit'] = transit_time
```

### 3. Regional Coverage Analysis

**Problem:** Are we missing events from certain reachable areas?

**Solution:**
```bash
# Export analysis report
python3 src/event_manager.py vgn export-report 60

# Review suggested_sources in report
# Compare with current config.json sources
# Add missing sources to config
```

### 4. Social Media Discovery

**Problem:** What social media pages do people in reachable areas use?

**Solution:**
1. Run `vgn suggest-sources` to get Facebook/Instagram suggestions
2. Review suggested sources by municipality
3. Check if those sources are already in `config.json`
4. Add new sources to scraping configuration

## Integration with Event Workflow

### Current Workflow
```
Scrape Events → Pending Queue → Editorial Review → Published
```

### Enhanced Workflow with VGN
```
Scrape Events (from VGN-discovered sources)
    ↓
Add Transit Info (travel time, lines)
    ↓
Pending Queue
    ↓
Editorial Review
    ↓
Published (with "How to get there" info)
```

## Testing

### Run Tests

```bash
# All VGN tests
python3 tests/test_vgn_transit.py --verbose

# Specific test
python3 tests/test_vgn_transit.py TestVGNTransit.test_get_reachable_stations_mock
```

### Mock Data

When VGN library is not installed, the module uses mock data:
- Hof Hauptbahnhof (0 min)
- Hof Neuhof (10 min)
- Rehau (25 min)
- Selb (35 min, filtered if max_time < 35)

This allows development and testing without VGN API access.

## Limitations

### Current Limitations
1. **VGN library required** - Full functionality needs `pip install vgn`
2. **Regional scope** - Only covers VGN network (Nürnberg metropolitan area)
3. **Mock data** - Without VGN library, uses static mock stations
4. **API rate limits** - VGN API may have usage limits (cached to minimize)

### Future Enhancements
1. **Real-time data** - Integrate live departure information
2. **Route planning** - Show exact routes and connections
3. **Accessibility info** - Indicate wheelchair-accessible stations
4. **Multi-modal** - Include walking, cycling distances
5. **Isochrone maps** - Visual reachability zones on map
6. **Auto-discovery** - Automatically scrape suggested sources

## Troubleshooting

### VGN Library Not Available

**Problem:**
```
❌ VGN integration not available
To enable VGN integration:
1. Install VGN library: pip install vgn
```

**Solution:**
```bash
pip install vgn
```

### No Stations Found

**Problem:**
```
No stations found within travel time
```

**Solutions:**
- Increase max travel time: `vgn analyze 60`
- Check reference location in config.json
- Verify VGN API is accessible

### Empty Source Suggestions

**Problem:**
```
⚠️  No additional sources found
Currently configured sources already cover reachable areas.
```

**Solutions:**
- This is normal if all reachable areas are already covered
- Increase travel time to reach more areas
- Add more municipalities to `regional_sources.json`

## API Documentation

### VGNTransit Class

**Methods:**

- `__init__(config, base_path)` - Initialize VGN integration
- `is_available()` - Check if VGN is enabled and library installed
- `get_reachable_stations(max_travel_time_minutes, max_transfers, departure_time)` - Get reachable stations
- `get_reachable_municipalities(max_travel_time_minutes)` - Get reachable municipalities
- `suggest_event_sources(max_travel_time_minutes)` - Suggest event sources
- `calculate_transit_time(destination_lat, destination_lon, departure_time)` - Calculate transit time
- `export_analysis_report(max_travel_time_minutes, output_path)` - Export report

### Data Classes

**ReachableStation:**
- `name: str` - Station name
- `id: str` - Station ID
- `municipality: str` - Municipality name
- `latitude: float` - Latitude
- `longitude: float` - Longitude
- `travel_time_minutes: int` - Travel time from reference
- `transfers: int` - Number of transfers
- `line: Optional[str]` - Line name

**RegionalSource:**
- `name: str` - Source name
- `type: str` - Source type (html, facebook, rss)
- `url: str` - Source URL
- `municipality: str` - Municipality
- `category: str` - Category
- `description: str` - Description
- `distance_km: float` - Distance from reference
- `travel_time_minutes: int` - Transit time

## Contributing

### Adding Regional Sources

To add sources for a new municipality:

1. Edit `assets/json/regional_sources.json`
2. Add municipality key (must match VGN station data)
3. Add array of source objects
4. Set `existing: false` for suggestions
5. Test: `python3 src/event_manager.py vgn suggest-sources`

### Improving Mock Data

To improve mock station data:

1. Edit `vgn_transit.py` → `_get_mock_reachable_stations()`
2. Add more realistic stations with accurate coordinates
3. Include realistic travel times and lines
4. Test: `python3 tests/test_vgn_transit.py`

## References

- **VGN Open Data**: https://www.vgn.de/web-entwickler/open-data/
- **VGN Python Library**: https://github.com/becheran/vgn
- **GTFS Format**: https://developers.google.com/transit/gtfs/
- **VGN Tools Collection**: https://github.com/justusjonas74/vgn

## Support

For issues or questions:
1. Check this documentation
2. Review `tests/test_vgn_transit.py` for examples
3. Open GitHub issue: https://github.com/feileberlin/krwl-hof/issues
4. Include VGN library version: `pip show vgn`
