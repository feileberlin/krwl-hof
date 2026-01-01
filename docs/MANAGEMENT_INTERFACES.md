# Management Interfaces Guide

## Overview

KRWL HOF provides **three complementary interfaces** for managing community events, following KISS (Keep It Simple, Stupid) principles. All interfaces provide the same core functionality with different user experiences.

## Interface Comparison

| Feature | GitHub UI | CLI | TUI |
|---------|-----------|-----|-----|
| **Scrape Events** | ✅ Manual trigger | ✅ `scrape` | ✅ Menu option 1 |
| **Review Events** | ✅ Approve/Reject | ✅ `publish/reject` | ✅ Menu option 2 |
| **Bulk Operations** | ✅ With wildcards | ✅ With wildcards | ❌ Not needed |
| **Generate Site** | ❌ Not exposed | ✅ `generate` | ✅ Menu option 4 |
| **View Events** | ❌ Via static site | ✅ `list/list-pending` | ✅ Menu option 3 |
| **Automation** | ✅ Best (workflows) | ✅ Good (scripts) | ❌ Interactive only |
| **Learning Curve** | Low (point-click) | Medium (commands) | Low (guided) |
| **Remote Access** | ✅ Yes (web) | ❌ SSH required | ❌ SSH required |

## 1. GitHub UI Management

### Purpose
- **Best for**: Non-technical users, remote management, scheduled automation
- **Access**: Via GitHub.com web interface
- **Authentication**: GitHub account

### Available Workflows

#### A. Review Events (Manual)
**File**: `.github/workflows/review-events.yml`

**Trigger**: Actions → Review Events → Run workflow

**Inputs**:
```yaml
action:
  - list           # Show all pending events
  - approve        # Approve single event
  - reject         # Reject single event
  - bulk-approve   # Approve multiple events
  - bulk-reject    # Reject multiple events

event_id: "pending_1"           # For single operations
event_ids: "pending_1,pending_2" # For bulk operations
```

**Examples**:
1. **List pending events**:
   - Action: `list`
   - Event ID: (leave empty)
   - Event IDs: (leave empty)

2. **Approve single event**:
   - Action: `approve`
   - Event ID: `test_event_001`
   - Event IDs: (leave empty)

3. **Bulk reject with wildcards**:
   - Action: `bulk-reject`
   - Event ID: (leave empty)
   - Event IDs: `html_frankenpost_*,pending_5`

#### B. Scrape Events (Automated)
**File**: `.github/workflows/scrape-events.yml`

**Trigger**:
- **Automatic**: Twice daily (4 AM, 4 PM CET)
- **Manual**: Actions → Scrape Events → Run workflow

**No inputs required** - uses `config.json` settings

#### C. Promote Preview to Production
**File**: `.github/workflows/promote-preview.yml`

**Trigger**: Actions → Promote Preview → Run workflow

**Creates PR**: preview → main (requires manual merge)

#### D. Commit and Push Everything
**File**: `.github/workflows/commit-and-push.yml`

**Trigger**: Actions → Commit and Push Everything → Run workflow

**Inputs**:
```yaml
commit_message: "Required commit message"
path_filter: "." # Optional: e.g., "static/", "*.json", or leave as "." for all
```

**Purpose**: Manual utility to commit and push all pending changes (or filtered paths) with a custom commit message. Useful for maintenance tasks, bulk updates, or repository cleanup.

**Examples**:
1. **Commit all changes**:
   - Commit message: `chore: update configuration files`
   - Path filter: `.` (or leave as default)

2. **Commit specific directory**:
   - Commit message: `fix: update static assets`
   - Path filter: `static/`

3. **Commit specific file types**:
   - Commit message: `docs: update markdown files`
   - Path filter: `*.md`

⚠️ **Warning**: Use with caution on protected branches. Always verify changes before running.

### Advantages
✅ No local setup required  
✅ Works from any device with browser  
✅ Built-in logging and history  
✅ Schedule automation  
✅ Team collaboration friendly  

### Limitations
❌ No site generation (use CLI/TUI)  
❌ Requires GitHub Actions minutes  
❌ Internet connection required  

## 2. CLI Management

### Purpose
- **Best for**: Automation, scripting, CI/CD, power users
- **Access**: Terminal/command line
- **Authentication**: Local filesystem

### Core Commands

#### Event Management
```bash
# List events
python3 src/main.py list              # Published events
python3 src/main.py list-pending      # Pending events

# Scrape new events
python3 src/main.py scrape

# Approve/reject single event
python3 src/main.py publish test_event_001
python3 src/main.py reject test_event_002

# Bulk operations with wildcards
python3 src/main.py bulk-publish "pending_*"
python3 src/main.py bulk-reject "html_frankenpost_*"

# Archive old events
python3 src/main.py archive
```

#### Site Generation
```bash
# Generate static site (with CDN fallback)
python3 src/main.py generate

# Steps performed:
# 1. Archive past events
# 2. Fetch Leaflet from CDN (or use local)
# 3. Inline all CSS/JS
# 4. Generate single index.html
# 5. Update events data
```

#### Workflow Management
```bash
# List workflows
python3 src/main.py workflow list

# Trigger workflow
python3 src/main.py workflow run scrape-events --branch preview

# Check workflow status
python3 src/main.py workflow status scrape-events --limit 5
```

#### Development
```bash
# Load example data
python3 src/main.py load-examples

# Clear all data
python3 src/main.py clear-data

# Interactive review
python3 src/main.py review
```

### Wildcard Patterns

Support Unix-style globbing:
```bash
*               # Match any characters
?               # Match one character
[seq]           # Match any char in seq
[!seq]          # Match any char not in seq

# Examples:
pending_*                    # All pending IDs
html_frankenpost_*          # All Frankenpost events
*AUCHEVENT*                 # Any event with AUCHEVENT in ID
pending_[1-3]               # pending_1, pending_2, pending_3
```

### Advantages
✅ Fast and efficient  
✅ Scriptable and automatable  
✅ Works offline (with local fallback)  
✅ Full feature access  
✅ Ideal for CI/CD pipelines  

### Limitations
❌ Requires Python setup  
❌ Learning curve for commands  
❌ No visual feedback  

## 3. TUI Management

### Purpose
- **Best for**: Interactive use, learning the system, visual feedback
- **Access**: Terminal/command line (interactive)
- **Authentication**: Local filesystem

### Launch TUI
```bash
python3 src/main.py
# or just:
python3 src/main.py
```

### Main Menu
```
1. Scrape New Events        → Fetch from configured sources
2. Review Pending Events    → Interactive approve/reject/edit
3. View Published Events    → Browse published events
4. Generate Static Site     → Create/update index.html
5. Launch GitHub Workflows  → Trigger workflows via gh CLI
6. Settings                 → Load examples, clear data, view config
7. View Documentation       → Built-in docs viewer
8. Exit                     → Close TUI
```

### Review Flow (Option 2)

**Interactive review** with keyboard shortcuts:
```
Event: Test Community Gathering
Title: Test Community Gathering
Location: Test Venue Berlin (52.52, 13.405)
Time: 2026-01-15T19:00:00
URL: https://example.com/test-event

Actions:
  (a) Approve and publish
  (e) Edit event details
  (r) Reject event
  (s) Skip to next
  (q) Quit review

Choice: _
```

**What happens**:
- **(a) Approve**: Moves to `events.json`, updates HTML, creates backup
- **(e) Edit**: Modify fields before approving
- **(r) Reject**: Moves to `rejected_events.json`
- **(s) Skip**: Continue to next pending event
- **(q) Quit**: Exit review mode

### Settings Menu (Option 6)
```
1. View Configuration       → Show config.json
2. Load Example Data        → Load sample events for testing
3. Clear All Data          → Delete all events (with backup)
4. Back to Main Menu
```

### Advantages
✅ User-friendly guided interface  
✅ Visual feedback and tooltips  
✅ Edit before approval  
✅ Built-in documentation viewer  
✅ Great for learning  

### Limitations
❌ Not scriptable  
❌ Single-threaded (one event at a time)  
❌ No bulk operations  

## KISS Principles Applied

### 1. Modularity
Each interface is **self-contained**:
- **GitHub UI**: Workflow YAML files
- **CLI**: Command functions in `main.py`
- **TUI**: EventManagerTUI class in `main.py`

### 2. Simplicity
**One source of truth** for core logic:
```python
src/modules/
  ├── scraper.py     → Event scraping logic (all interfaces use)
  ├── editor.py      → Event editing logic (TUI uses)
  ├── cdn_inliner.py → Site generation (CLI/TUI use)
  └── utils.py       → Shared functions (all use)
```

### 3. No Duplication
**Shared functions** prevent code duplication:
```python
# All interfaces use the same functions:
- load_events()
- save_events()
- load_pending_events()
- save_pending_events()
- add_rejected_event()
- update_events_in_html()
```

### 4. Clear Separation
**Interface layer vs. business logic**:
```
Interface Layer (UI):           Business Logic:
├─ GitHub workflows            ├─ scraper.py
├─ CLI commands                ├─ editor.py
└─ TUI menus                   └─ utils.py
```

## Decision Matrix

### When to Use Each Interface

| Scenario | Recommended Interface | Why |
|----------|----------------------|-----|
| **First-time user** | TUI | Guided, visual, forgiving |
| **Daily editorial review** | TUI or GitHub UI | Interactive, easy |
| **Bulk operations** | CLI or GitHub UI | Wildcards, efficient |
| **Automation** | GitHub UI | Scheduled, logged |
| **Development** | CLI | Fast, offline |
| **Remote management** | GitHub UI | Web-based |
| **CI/CD pipelines** | CLI | Scriptable |
| **Site generation** | CLI or TUI | Not in workflows |

## Examples by Task

### Task: Review and Approve 5 New Events

**GitHub UI**:
1. Go to Actions → Review Events
2. Run workflow with action: `list`
3. Check output for event IDs
4. Run workflow with action: `bulk-approve`
5. Input: `pending_1,pending_2,pending_3,pending_4,pending_5`

**CLI**:
```bash
python3 src/main.py list-pending
python3 src/main.py bulk-publish "pending_*"
```

**TUI**:
```bash
python3 src/main.py
# Select: 2. Review Pending Events
# Press 'a' for each event (5 times)
```

### Task: Reject All Events from Specific Source

**GitHub UI**:
1. Actions → Review Events
2. Action: `bulk-reject`
3. Event IDs: `html_frankenpost_*`

**CLI**:
```bash
python3 src/main.py bulk-reject "html_frankenpost_*"
```

**TUI**:
```bash
# Not efficient for bulk - use CLI or GitHub UI
```

### Task: Generate Site After Approving Events

**GitHub UI**:
```
Not available - use CLI or TUI
```

**CLI**:
```bash
python3 src/main.py publish test_event_001
python3 src/main.py generate
```

**TUI**:
```bash
python3 src/main.py
# 2. Review Pending Events → Approve events
# 4. Generate Static Site
```

## Configuration

All interfaces share the same configuration:

**File**: `config.json` (or `config.dev.json`, `config.prod.json`)

**Key sections**:
```json
{
  "scraping": {
    "sources": [...]        // Used by: scrape command (all interfaces)
  },
  "editor": {
    "require_approval": true  // Used by: review flow (all interfaces)
  },
  "filtering": {
    "max_distance_km": 5.0    // Used by: site generation
  }
}
```

## Testing

Each interface can be tested independently:

```bash
# Test CLI
python3 src/main.py list
python3 src/main.py list-pending

# Test TUI (non-interactive)
echo "8" | python3 src/main.py

# Test GitHub workflows (requires gh CLI)
python3 src/main.py workflow list
```

## Troubleshooting

### GitHub UI: Workflow Failed
**Check**: Actions → workflow run → logs  
**Common issues**: Missing permissions, invalid event IDs

### CLI: Command Not Found
**Check**: Are you in the right directory?  
**Solution**: `cd /path/to/krwl-hof`

### TUI: Menu Not Showing
**Check**: Is Python 3.x installed?  
**Solution**: `python3 --version`

## Best Practices

1. **Use GitHub UI for**: Remote management, scheduling, team collaboration
2. **Use CLI for**: Automation, scripting, bulk operations, development
3. **Use TUI for**: Learning, interactive review, visual feedback
4. **Keep it simple**: Don't over-engineer - use the right tool for the job
5. **Test locally first**: Use CLI/TUI before triggering GitHub workflows

## Related Documentation

- **CLI Reference**: Run `python3 src/main.py --help`
- **Workflow Guide**: See `.github/workflows/README.md`
- **KISS Principles**: See `check_kiss.py` and project guidelines
- **Feature Registry**: See `features.json` for all features
