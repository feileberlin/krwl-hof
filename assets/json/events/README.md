# Event Data Organization

This directory contains organized event data files following a structured approach.

## Directory Structure

```
assets/json/events/
├── published/          # Future: Published events (events.json will move here)
├── pending/            # Future: Pending events awaiting approval
├── rejected/           # Future: Rejected events log
├── demo/               # Future: Demo events for testing
└── archived/           # Archived past events organized by month
    ├── 202601.json     # Events from January 2026
    ├── 202602.json     # Events from February 2026
    └── ...
```

## Current Implementation (Backward Compatible)

Currently, event files remain in `assets/json/` for backward compatibility:
- `events.json` - Published events
- `pending_events.json` - Pending events
- `rejected_events.json` - Rejected events
- `events.demo.json` - Demo events
- `archived_events.json` - Legacy archived events

## Archiving System

The archiving system automatically moves old events based on configuration in `config.json`:
- **Enabled**: `config.json → archiving.enabled`
- **Schedule**: First day of month at 2:00 AM UTC (configurable)
- **Retention**: 60 days active window (configurable)
- **Organization**: Monthly archives in `archived/` directory

## CLI Commands

```bash
# Run archiving manually
python3 src/event_manager.py archive-monthly

# View archiving configuration
python3 src/event_manager.py archive-info
```

## Future Migration

The new directory structure is prepared for future migration. When ready:
1. Update path constants in `src/modules/utils.py`
2. Update all references in scraper, editor, and site generator
3. Migrate existing files to new locations
4. Update documentation
