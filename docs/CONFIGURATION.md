# Configuration Guide

## Overview

The KRWL HOF app uses JSON configuration files to control behavior, data sources, and feature flags. Different configurations are used for different environments.

## Configuration Files

### Source Configuration Files (Repository Root)

- **config.prod.json** - Production configuration
  - Environment: `production`
  - Data source: Real events only
  - Watermark: Disabled by default
  - Performance: Optimized (caching enabled)
  - Used by: `main` branch deployment

- **config.preview.json** - Preview configuration
  - Environment: `preview`
  - Data source: Real events only
  - Watermark: Enabled with "PREVIEW" text (yellow)
  - Performance: Debug mode enabled
  - Used by: `preview` branch deployment

- **config.dev.json** - Development/Testing configuration
  - Environment: `testing`
  - Data source: Both real and demo events
  - Watermark: Enabled with "TESTING" text (blue)
  - Performance: Debug mode enabled
  - Used by: Local development

### Runtime Configuration (static/config.json)

The `static/config.json` file is the configuration loaded by the frontend application at runtime.

**For local development:**
- This file is tracked in git and contains the development configuration
- Copy from `config.dev.json` when updating: `cp config.dev.json static/config.json`

**During deployment:**
- Production: Replaced by `config.prod.json`
- Preview: Replaced by `config.preview.json`
- Deployment workflows inject additional `build_info` metadata

## Configuration Structure

### App Section

```json
{
  "app": {
    "name": "KRWL HOF Community Events",
    "description": "Community events scraper and viewer",
    "environment": "production|preview|testing"
  }
}
```

### Watermark Section (New)

```json
{
  "watermark": {
    "enabled": true,
    "text": "PREVIEW"
  }
}
```

Controls the environment watermark display:
- `enabled`: Whether to show the watermark
- `text`: Text to display (can include environment name)

The watermark automatically includes:
- Environment name
- Commit SHA (short form)
- PR number (if available from build_info)

Example display: `PREVIEW • abc1234 • PR#42`

### Build Info Section (Injected During Deployment)

```json
{
  "build_info": {
    "commit_short": "abc1234",
    "commit_sha": "abc1234567890abcdef1234567890abcdef1234",
    "pr_number": "42",
    "ref": "refs/heads/preview",
    "deployed_by": "github-actions",
    "deployed_at": "2025-12-29T16:30:00Z"
  }
}
```

This section is automatically added during deployment by the GitHub Actions workflows. It should NOT be manually edited in the source config files.

## Data Sources

### Production (`config.prod.json`)

```json
{
  "data": {
    "source": "real"
  }
}
```

Loads only real scraped events from `events.json`.

### Preview (`config.preview.json`)

```json
{
  "data": {
    "source": "real"
  }
}
```

Loads only real scraped events - same as production but with debugging enabled.

### Testing/Development (`config.dev.json`)

```json
{
  "data": {
    "source": "both",
    "sources": {
      "real": {
        "url": "events.json",
        "description": "Real scraped events data"
      },
      "demo": {
        "url": "events.demo.json",
        "description": "Demo events with current timestamps"
      },
      "both": {
        "urls": ["events.json", "events.demo.json"],
        "description": "Combine real and demo events"
      }
    }
  }
}
```

Loads both real and demo events for testing. Demo events are generated with current timestamps using `generate_demo_events.py`.

## Modifying Configuration

### For Production Changes

1. Edit `config.prod.json`
2. Commit and push to a feature branch
3. Create PR to `preview` branch for testing
4. After preview testing, promote to `main`

### For Preview Changes

1. Edit `config.preview.json`
2. Commit and push to `preview` branch
3. Deployment will use the updated config

### For Local Development

1. Edit `config.dev.json`
2. Copy to static: `cp config.dev.json static/config.json`
3. Restart local server if running

## Environment Watermark Colors

Each environment has a distinct border color:

- **Production**: Green (`#4CAF50`) - Watermark usually disabled
- **Preview**: Yellow/Amber (`#FFC107`) - For pre-production testing
- **Testing**: Blue (`#2196F3`) - For local development with demo data
- **Development**: Purple (`#9C27B0`) - Reserved for future use

## Deployment Workflows

### Production Deployment (main branch)

File: `.github/workflows/deploy-pages.yml`

```yaml
# Use production config
cp config.prod.json publish/config.json

# Inject build metadata
jq --argjson build_info "$BUILD_INFO" '. + {build_info: $build_info}' \
  publish/config.json > publish/config.json.tmp
```

### Preview Deployment (preview branch)

File: `.github/workflows/deploy-preview.yml`

```yaml
# Use preview config
cp config.preview.json publish/preview/config.json

# Inject build metadata (includes PR number)
jq --argjson build_info "$BUILD_INFO" '. + {build_info: $build_info}' \
  publish/preview/config.json > publish/preview/config.json.tmp
```

## See Also

- [Deployment Guide](../.github/DEPLOYMENT.md)
- [Feature Registry](../features.json)
- [Event Scraping Guide](SCRAPING.md)
