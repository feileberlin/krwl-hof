# Docstring Guide - Single Source of Truth Documentation

## 📖 Philosophy

**This project uses Python docstrings as the primary documentation method.**

Instead of maintaining separate documentation files, README sections, help text, and inline comments that inevitably drift out of sync, we follow a **single source of truth** approach:

1. Write comprehensive docstrings in the code
2. Extract them programmatically for CLI help, README generation, and API docs
3. Avoid duplicating information across multiple files

## 🎯 Benefits

| Approach | Issues |
|----------|--------|
| ❌ **Separate docs** | Drift out of sync, duplication, maintenance burden |
| ✅ **Docstrings** | Always accurate, no duplication, IDE integration works |

**Key advantages:**
- 📝 **Write once, use everywhere** - No duplication
- 🔄 **Always up-to-date** - Documentation lives with code
- 🤖 **Programmatic access** - Extract for CLI, web docs, README
- 💡 **IDE support** - Hover hints and autocomplete work automatically
- 🐍 **Standard Python** - No custom doc system needed

## 📚 Docstring Levels

### 1. Module-Level Docstrings (Required)

**Every Python module must start with a module docstring.**

```python
#!/usr/bin/env python3
"""
Event Archiving Module - KISS Implementation

Simple monthly event archiving based on config.json settings.
Archives old events to keep active list manageable.

Key Features:
- Configurable retention window (default: 60 days)
- Monthly organization (YYYYMM.json format)
- Dry-run support for safe testing
- Backward compatible with legacy paths

Usage:
    from modules.archive_events import EventArchiver
    archiver = EventArchiver(config, base_path)
    results = archiver.archive_events(dry_run=True)
"""
```

### 2. Class Docstrings (Required)

**Every class needs a docstring explaining its purpose.**

```python
class EventArchiver:
    """
    Simple event archiver based on config.json settings.
    
    Moves events older than retention window to monthly archive files.
    Archives are organized by month (e.g., 202601.json) in the
    configured archive directory.
    
    Example:
        config = load_config(base_path)
        archiver = EventArchiver(config, base_path)
        results = archiver.archive_events(dry_run=False)
    """
```

### 3. Function/Method Docstrings

#### Public Functions (Detailed Required)

**Public functions and CLI commands need comprehensive docstrings.**

These are extracted for:
- CLI `--help` output
- README documentation
- API documentation
- IDE tooltips

```python
def cli_archive_monthly(base_path, config, dry_run=False):
    """
    Archive old events based on configurable retention window.
    
    This command moves events older than the configured retention window
    (default: 60 days) to monthly archive files. This keeps the active
    events list manageable and improves site performance.
    
    Configuration: config.json → archiving section
    - retention.active_window_days: How many days to keep active
    - organization.path: Where to save archives
    - organization.format: Archive filename format (YYYYMM or YYYY-MM)
    
    Usage:
        python3 src/event_manager.py archive-monthly           # Run archiving
        python3 src/event_manager.py archive-monthly --dry-run # Preview changes
    
    Archives are organized by month (e.g., 202601.json for January 2026)
    and stored in assets/json/events/archived/
    
    Args:
        base_path: Repository root path
        config: Loaded configuration dictionary
        dry_run: If True, show what would be archived without making changes
        
    Returns:
        Exit code (0 for success, 1 for error)
        
    Examples:
        >>> cli_archive_monthly(Path('.'), config, dry_run=True)
        0
    """
```

#### Internal Functions (Brief OK)

**Internal/private functions can have shorter docstrings.**

```python
def _parse_event_date(self, start_str):
    """Parse event start date string to datetime, return None if invalid."""
    if not start_str:
        return None
    try:
        if 'T' in start_str:
            return datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        return datetime.strptime(start_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None
```

### 4. Simple Getters/Setters (Optional)

Very simple functions can skip docstrings if the name is self-explanatory:

```python
# ✅ OK - Name is clear
def get_config_info(self):
    """Get archiving configuration as dict."""  # Brief is fine
    return {...}

# ✅ Also OK - Super obvious
def is_enabled(self):
    return self.enabled
```

## 🎨 Docstring Style Guide

### Format: Google Style

We use **Google Style** docstrings (readable, concise):

```python
def function(arg1, arg2, optional=None):
    """
    Short one-line summary (required).
    
    Longer explanation if needed (optional). Can span multiple paragraphs.
    Explain what the function does, why it exists, and how to use it.
    Include configuration, limitations, side effects.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        optional: Description of optional argument (default: None)
        
    Returns:
        Description of return value and its structure.
        For complex returns, show the dict/object structure:
        {
            'total': int,
            'archived': int,
            'active': int
        }
        
    Raises:
        ValueError: When arg1 is invalid
        FileNotFoundError: When config file doesn't exist
        
    Examples:
        >>> function("hello", "world")
        {'status': 'ok'}
        
    Note:
        Any important notes, warnings, or caveats
    """
```

### Section Order

1. **Summary** - One-line description (always first)
2. **Description** - Longer explanation (if needed)
3. **Args** - Function parameters
4. **Returns** - What it returns
5. **Raises** - Exceptions it may raise
6. **Examples** - Usage examples
7. **Note/Warning** - Important information

## 🔧 Extracting Docstrings

### CLI Help Text

Extract docstrings for command help:

```python
def print_help():
    """Print CLI help."""
    # Extract from function docstrings
    print(cli_archive_monthly.__doc__)
```

### Interactive Help

```bash
# Get help on any function
python3 -c "from src.modules.archive_events import EventArchiver; help(EventArchiver)"

# Get help on specific method
python3 -c "from src.modules.archive_events import EventArchiver; help(EventArchiver.archive_events)"
```

### Documentation Generation

```bash
# Auto-generate README from docstrings
python3 scripts/generate_readme.py

# Extract API documentation
pydoc src.modules.archive_events
```

## ✍️ When to Write Docstrings

| Code Element | Docstring Required? | Detail Level |
|--------------|-------------------|--------------|
| Module (file top) | ✅ **Always** | Comprehensive |
| Public class | ✅ **Always** | Detailed with examples |
| CLI command | ✅ **Always** | Very detailed with usage |
| Public function/method | ✅ **Always** | Detailed with args/returns |
| Complex internal function | ⚠️ **Recommended** | Brief but clear |
| Simple internal function | ✅ **Brief OK** | One-line is fine |
| Obvious getter/setter | ⭕ **Optional** | Can skip if name is clear |

## 📝 Comments vs Docstrings

**Know the difference:**

- **Docstrings** → WHAT and HOW (external interface)
- **Comments** → WHY and IMPLEMENTATION (internal reasoning)

```python
def archive_events(self, dry_run=False):
    """
    Archive old events based on retention window.
    
    This docstring explains WHAT the function does and HOW to use it.
    It's the external documentation users/maintainers read.
    """
    
    # This comment explains WHY we chose this approach
    # KISS principle: Simple month-based grouping instead of complex date math
    # Avoids timezone issues and keeps code maintainable
    filename = f"{event_date.strftime('%Y%m')}.json"
    
    # This comment explains implementation detail
    # Load existing archive first to avoid overwriting events from same month
    archive_data = self._load_archive_file(filename)
```

## 🚫 Anti-Patterns to Avoid

### ❌ Don't Duplicate Information

```python
# ❌ BAD: Same text in multiple places
ARCHIVE_HELP = "Archive old events based on retention window..."

def cli_archive():
    """Archive old events based on retention window..."""  # Duplicate!
    pass

# In README.md:
## Archiving
Archive old events based on retention window...  # Duplicate again!
```

```python
# ✅ GOOD: Single source of truth
def cli_archive():
    """
    Archive old events based on retention window.
    
    Full detailed description here...
    """
    pass

# Extract for README:
# This gets auto-generated from the docstring above
```

### ❌ Don't Write Obvious Docstrings

```python
# ❌ BAD: Docstring adds no value
def get_name(self):
    """Get the name."""  # Duh, the function name already says this
    return self.name

# ✅ GOOD: Skip or add value
def get_name(self):
    """Get event name for display (sanitized, max 100 chars)."""
    return self.name[:100]
```

### ❌ Don't Let Docstrings Get Stale

```python
# ❌ BAD: Code changed but docstring didn't
def archive_events(self, retention_days=60):  # Parameter changed!
    """
    Archive old events.
    
    Args:
        cutoff_date: Date to archive before  # Old parameter!
    """
```

## 🎓 Examples from This Project

### Example 1: Module-Level (archive_events.py)

```python
"""
Event Archiving Module - KISS Implementation

Simple monthly event archiving based on config.json settings.
Archives old events to keep active list manageable.
"""
```

### Example 2: CLI Command (event_manager.py)

```python
def cli_archive_monthly(base_path, config, dry_run=False):
    """
    Archive old events based on configurable retention window.
    
    This command moves events older than the configured retention window
    (default: 60 days) to monthly archive files. This keeps the active
    events list manageable and improves site performance.
    
    Configuration: config.json → archiving section
    - retention.active_window_days: How many days to keep active
    - organization.path: Where to save archives
    
    Usage:
        python3 src/event_manager.py archive-monthly           # Run archiving
        python3 src/event_manager.py archive-monthly --dry-run # Preview
    
    Args:
        base_path: Repository root path
        config: Loaded configuration
        dry_run: If True, show what would be archived without changes
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
```

### Example 3: Simple Helper Function

```python
def _get_archive_filename(self, event_date):
    """Get archive filename for an event date (e.g., 202601.json)."""
    return f"{event_date.strftime('%Y%m')}.json"
```

## 🔍 Tools and Validation

### Check Docstring Coverage

```bash
# Install docstring coverage tool
pip install interrogate

# Check docstring coverage
interrogate src/modules/

# Generate badge
interrogate --generate-badge docs/
```

### Lint Docstrings

```bash
# Install pydocstyle
pip install pydocstyle

# Check docstring style
pydocstyle src/modules/archive_events.py
```

## 📋 Checklist for New Functions

Before committing new code, verify:

- [ ] Module has top-level docstring
- [ ] Class has docstring with usage example
- [ ] Public functions have detailed docstrings
- [ ] Docstrings include Args, Returns, Examples
- [ ] No duplicate text in comments/README/help
- [ ] Docstring is up-to-date with current code
- [ ] Used Google Style format consistently

## 🔗 Resources

- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Sphinx Documentation Generator](https://www.sphinx-doc.org/)
- [pydoc - Documentation Generator](https://docs.python.org/3/library/pydoc.html)

## 💡 Remember

> "Code is read much more often than it is written." - Guido van Rossum

Good docstrings are an investment in your future self and your collaborators. Write them well, and they'll serve the project for years to come.
