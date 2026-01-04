# Utils.py Refactoring Plan

## Current State
- `utils.py`: 721 lines, 21 functions
- Mixed responsibilities (config, I/O, events, geo)
- Violates single responsibility principle

## Proposed Split (Flat Structure)

### 1. **config_utils.py** (Environment & Configuration)
**Size**: ~150 lines  
**Functions**:
- `is_ci()` - Detect CI environment
- `is_production()` - Detect production environment  
- `is_development()` - Detect development environment
- `validate_config()` - Validate config structure
- `load_config()` - Load config with environment overrides

**Purpose**: All environment detection and configuration loading

---

### 2. **data_io.py** (File I/O Operations)
**Size**: ~180 lines  
**Functions**:
- `load_events()` - Load published events
- `save_events()` - Save published events
- `load_pending_events()` - Load pending events
- `save_pending_events()` - Save pending events
- `load_rejected_events()` - Load rejected events
- `save_rejected_events()` - Save rejected events
- `load_historical_events()` - Load archived events

**Purpose**: All JSON file read/write operations

---

### 3. **event_utils.py** (Event Operations)
**Size**: ~200 lines  
**Functions**:
- `update_pending_count_in_events()` - Update pending count
- `is_event_rejected()` - Check if event is rejected
- `add_rejected_event()` - Add event to rejected list
- `backup_published_event()` - Backup event to history
- `update_events_in_html()` - Update HTML with new events
- `archive_old_events()` - Archive past events
- `filter_events_by_time()` - Filter events by time rules

**Purpose**: Event manipulation and lifecycle operations

---

### 4. **geo_utils.py** (Geography & Time)
**Size**: ~80 lines  
**Functions**:
- `calculate_distance()` - Haversine distance calculation
- `get_next_sunrise()` - Calculate next sunrise time

**Purpose**: Geographic and astronomical calculations

---

### 5. **utils.py** (Backward Compatibility)
**Size**: ~50 lines  
**Content**: Re-exports all functions from split modules

```python
"""Utility functions - Re-exports for backward compatibility"""

# Re-export all split modules
from .config_utils import *
from .data_io import *
from .event_utils import *
from .geo_utils import *

__all__ = [
    # Config
    'is_ci', 'is_production', 'is_development',
    'validate_config', 'load_config',
    # Data I/O
    'load_events', 'save_events',
    'load_pending_events', 'save_pending_events',
    'load_rejected_events', 'save_rejected_events',
    'load_historical_events',
    # Event operations
    'update_pending_count_in_events',
    'is_event_rejected', 'add_rejected_event',
    'backup_published_event', 'update_events_in_html',
    'archive_old_events', 'filter_events_by_time',
    # Geo
    'calculate_distance', 'get_next_sunrise',
]
```

**Purpose**: Maintain backward compatibility with existing imports

---

## Benefits

### 1. **Single Responsibility**
- Each module has one clear purpose
- Easier to understand what each module does
- Changes isolated to relevant module

### 2. **Maintainability**
- Smaller files (~80-200 lines each)
- Easy to navigate and modify
- Clear separation of concerns

### 3. **Testability**
- Test each module in isolation
- Mock dependencies easily
- Focused unit tests

### 4. **Backward Compatibility**
- Old imports still work: `from modules.utils import load_config`
- No breaking changes for existing code
- Gradual migration possible

### 5. **Discoverability**
- Clear naming: `config_utils`, `data_io`, `event_utils`, `geo_utils`
- Self-documenting structure
- Easy to find specific functions

---

## Migration Strategy

### Phase 1: Create New Modules (Non-Breaking)
1. Create `config_utils.py` with config functions
2. Create `data_io.py` with I/O functions
3. Create `event_utils.py` with event operations
4. Create `geo_utils.py` with geographic functions
5. Keep original `utils.py` unchanged

### Phase 2: Update utils.py to Re-Export (Still Non-Breaking)
1. Modify `utils.py` to import from new modules
2. Re-export all functions
3. All existing code continues to work

### Phase 3: Update Imports Gradually (Optional)
1. Update new code to use specific modules:
   - `from modules.config_utils import load_config`
   - `from modules.data_io import load_events`
2. Leave existing imports unchanged
3. Complete migration over time

---

## Import Examples

### Old Style (Still Works)
```python
from modules.utils import load_config, load_events, calculate_distance
```

### New Style (Recommended)
```python
# Config operations
from modules.config_utils import load_config, is_production

# File I/O
from modules.data_io import load_events, save_events

# Event operations
from modules.event_utils import archive_old_events

# Geography
from modules.geo_utils import calculate_distance
```

### Mixed (Transition Period)
```python
# Old imports continue to work
from modules.utils import load_config

# New imports for clarity
from modules.event_utils import archive_old_events
```

---

## File Size Comparison

| File | Before | After |
|------|--------|-------|
| utils.py | 721 lines | 50 lines (re-exports) |
| config_utils.py | - | 150 lines |
| data_io.py | - | 180 lines |
| event_utils.py | - | 200 lines |
| geo_utils.py | - | 80 lines |
| **Total** | **721 lines** | **660 lines** (better organized) |

---

## KISS Compliance

**Before**:
- ❌ Single 721-line file
- ❌ Mixed responsibilities
- ❌ Hard to navigate

**After**:
- ✅ Five focused modules (50-200 lines each)
- ✅ Single responsibility per module
- ✅ Easy to find and modify code
- ✅ Clear module naming
- ✅ Backward compatible

---

## Implementation Steps

1. **Create config_utils.py** (✅ Done)
   - Move environment detection functions
   - Move config loading and validation

2. **Create data_io.py** (✅ Done)
   - Move all load/save functions
   - Ensure consistent error handling

3. **Create event_utils.py** (Next)
   - Move event manipulation functions
   - Keep HTML update logic here

4. **Create geo_utils.py** (Next)
   - Move geographic calculations
   - Move sunrise calculations

5. **Update utils.py** (Final)
   - Import all from new modules
   - Re-export for compatibility
   - Add deprecation notice (optional)

---

## Testing

After split, verify:
```bash
# Test backward compatibility
python3 -c "from modules.utils import load_config; print('✓ Old imports work')"

# Test new imports
python3 -c "from modules.config_utils import load_config; print('✓ New imports work')"

# Test all modules import
python3 -c "import modules.config_utils, modules.data_io; print('✓ All modules load')"

# Run existing tests
python3 src/event_manager.py test
```

---

## Recommendation

**Implement this split** because:
1. ✅ Follows Python best practices (flat structure + focused modules)
2. ✅ Non-breaking (backward compatible)
3. ✅ KISS compliant (small, focused files)
4. ✅ Better organization without subdirectories
5. ✅ Easy to test and maintain

**Don't** use nested directories (`utils/` subfolder) because:
1. ❌ Causes import conflicts with `utils.py`
2. ❌ Not standard Python practice
3. ❌ Breaks existing imports
4. ❌ More complex than needed

---

## Next Steps

1. Review this plan
2. Complete creating remaining modules:
   - `event_utils.py`
   - `geo_utils.py`
3. Update `utils.py` to re-export
4. Test backward compatibility
5. Document in module README
6. (Optional) Gradually update imports in new code
