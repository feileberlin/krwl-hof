# Interactive Batch Selection Guide

This guide demonstrates the new interactive batch selection feature for editorial workflows.

## Overview

The batch selection mode provides a checkbox-based interface for selecting and processing multiple events at once, making editorial review more efficient.

## Accessing Batch Selection Mode

### From TUI Review
1. Launch interactive review: `python3 src/event_manager.py review`
2. Press `(b)` during any event review to enter batch mode

### Visual Interface

```
================================================================================
📦 BATCH SELECTION MODE
================================================================================
Select events for batch operations using checkboxes
────────────────────────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────────────────────────
📋 All Pending Events:
────────────────────────────────────────────────────────────────────────────────
  1. ☐ Summer Music Festival - City Park
      ID: pending_official_001 | Source: Official Events
  2. ☐ Art Exhibition Opening Night
      ID: pending_gallery_002 | Source: Local Gallery
  3. ☑ Weekly Farmers Market
      ID: pending_market_003 | Source: Market Board
  4. ☐ Jazz Concert at Riverside
      ID: pending_music_004 | Source: Concert Hall
  5. ☑ Tech Meetup - AI & ML Discussion
      ID: pending_tech_005 | Source: Meetup.com
  6. ☐ Community Cleanup Day
      ID: pending_community_006 | Source: City Council
  7. ☑ Photography Workshop for Beginners
      ID: pending_workshop_007 | Source: Art School
  8. ☐ Street Food Festival Downtown
      ID: pending_food_008 | Source: Tourism Board

────────────────────────────────────────────────────────────────────────────────
Selected: 3 event(s)
────────────────────────────────────────────────────────────────────────────────
Commands:
  [number]      Toggle selection (e.g., '1' or '1,3,5')
  all           Select all events
  none          Clear selection
  range N-M     Select range (e.g., 'range 1-5')
  pattern WORD  Select by title pattern (e.g., 'pattern concert')
  approve       Batch approve selected events
  reject        Batch reject selected events
  show          Show details of selected events
  back          Exit batch mode
────────────────────────────────────────────────────────────────────────────────

Command: _
```

## Selection Methods

### 1. Toggle Individual Events

**Select single event:**
```
Command: 1
☑ Selected event 1
```

**Select multiple events at once:**
```
Command: 1,4,7
☑ Selected event 1
☑ Selected event 4
☑ Selected event 7
```

**Deselect (toggle off):**
```
Command: 1
☐ Deselected event 1
```

### 2. Select All

```
Command: all
✓ Selected all 8 events
```

**Visual Result:**
```
  1. ☑ Summer Music Festival - City Park
  2. ☑ Art Exhibition Opening Night
  3. ☑ Weekly Farmers Market
  4. ☑ Jazz Concert at Riverside
  5. ☑ Tech Meetup - AI & ML Discussion
  6. ☑ Community Cleanup Day
  7. ☑ Photography Workshop for Beginners
  8. ☑ Street Food Festival Downtown

Selected: 8 event(s)
```

### 3. Clear Selection

```
Command: none
✓ Cleared selection
```

**Visual Result:**
```
  1. ☐ Summer Music Festival - City Park
  2. ☐ Art Exhibition Opening Night
  ...

Selected: 0 event(s)
```

### 4. Select Range

**Select events 1 through 5:**
```
Command: range 1-5
✓ Selected events 1 to 5
```

**Visual Result:**
```
  1. ☑ Summer Music Festival - City Park
  2. ☑ Art Exhibition Opening Night
  3. ☑ Weekly Farmers Market
  4. ☑ Jazz Concert at Riverside
  5. ☑ Tech Meetup - AI & ML Discussion
  6. ☐ Community Cleanup Day
  7. ☐ Photography Workshop for Beginners
  8. ☐ Street Food Festival Downtown

Selected: 5 event(s)
```

### 5. Pattern Matching

**Select all events with "music" or "concert" in title:**
```
Command: pattern music
✓ Selected 2 events matching 'music'

Command: pattern concert
✓ Selected 3 events matching 'concert'
```

**Visual Result:**
```
  1. ☑ Summer Music Festival - City Park       ← matched "music"
  2. ☐ Art Exhibition Opening Night
  3. ☐ Weekly Farmers Market
  4. ☑ Jazz Concert at Riverside               ← matched "concert"
  5. ☐ Tech Meetup - AI & ML Discussion
  6. ☐ Community Cleanup Day
  7. ☐ Photography Workshop for Beginners
  8. ☐ Street Food Festival Downtown

Selected: 2 event(s)
```

**Case insensitive matching:**
- `pattern MUSIC` = `pattern music` = `pattern MuSiC`

## Batch Operations

### 1. View Selected Events

```
Command: show

================================================================================
📋 Selected Events Details:
================================================================================

1. Summer Music Festival - City Park
   ID: pending_official_001
   Source: Official Events
   Time: 2024-06-15T18:00:00

4. Jazz Concert at Riverside
   ID: pending_music_004
   Source: Concert Hall
   Time: 2024-06-20T19:30:00

7. Photography Workshop for Beginners
   ID: pending_workshop_007
   Source: Art School
   Time: 2024-06-25T10:00:00

Press Enter to continue...
```

### 2. Batch Approve

```
Command: approve

⚠️  Approve 3 event(s)? (yes/no): yes

✅ Approved 3 event(s)
```

**What happens:**
1. Selected events published to `events.json`
2. Removed from `pending_events.json`
3. HTML automatically updated
4. Changes saved to repository
5. Exit batch mode and return to main review

### 3. Batch Reject

```
Command: reject

⚠️  Reject 3 event(s)? (yes/no): yes

✅ Rejected 3 event(s)
```

**What happens:**
1. Selected events added to `rejected_events.json`
2. Removed from `pending_events.json`
3. Changes saved to repository
4. Exit batch mode and return to main review

## Workflow Examples

### Example 1: Quick Approve Trusted Sources

**Scenario**: You want to approve all events from "Official Events" source.

**Steps:**
1. Enter batch mode: `(b)`
2. Pattern match: `pattern official`
3. Review selection: `show`
4. Approve: `approve` → `yes`

**Result**: All official events published in one operation.

---

### Example 2: Reject Low-Quality Events

**Scenario**: Events 5, 6, 7 look suspicious, need to reject them.

**Steps:**
1. Enter batch mode: `(b)`
2. Select range: `range 5-7`
3. Verify selection: `show`
4. Reject: `reject` → `yes`

**Result**: Events removed and logged to rejected list.

---

### Example 3: Mixed Operations

**Scenario**: You reviewed 10 events. Want to approve #1,2,3, reject #8,9,10, skip rest.

**Steps (Approve):**
1. Enter batch mode: `(b)`
2. Select: `1,2,3`
3. Approve: `approve` → `yes`

**Steps (Reject):**
1. Re-enter batch mode: `(b)` (from new event #1, which was #4)
2. Select: `5,6,7` (these are now the last 3)
3. Reject: `reject` → `yes`

**Result**: 3 approved, 3 rejected, 4 still pending.

---

### Example 4: Selective Pattern Matching

**Scenario**: Approve all "concert" events except one.

**Steps:**
1. Enter batch mode: `(b)`
2. Select pattern: `pattern concert`
3. Review: `show`
4. Toggle off unwanted: `4` (if event 4 shouldn't be approved)
5. Approve: `approve` → `yes`

**Result**: All concert events approved except the one toggled off.

---

## Combining Selection Methods

You can combine multiple selection methods in one session:

```
Command: pattern music
✓ Selected 2 events matching 'music'

Command: 5,6
☑ Selected event 5
☑ Selected event 6

Command: range 1-3
✓ Selected events 1 to 3

Selected: 7 event(s)
```

**Result**: Events matching "music" + events 5,6 + events 1-3 (union of all selections)

---

## Safety Features

### 1. Confirmation Prompts
All batch operations require explicit confirmation:
- `approve` → Must type `yes` to confirm
- `reject` → Must type `yes` to confirm

### 2. Visual Feedback
- ☑ = Selected (will be processed)
- ☐ = Not selected (will be skipped)
- Selection counter shows total selected

### 3. Review Before Action
Use `show` command to view full details of selected events before approving/rejecting.

### 4. Non-Destructive Commands
- `all`, `none`, `range`, `pattern`, `[numbers]` - Just select/deselect
- `show` - Read-only view
- Only `approve` and `reject` modify data

---

## Performance Considerations

### Batch Size
Batch operations process 10 events at a time internally for efficiency:

```bash
📦 Processing 50 events in 5 batch(es) of 10
🔄 Batch 1/5 (10 events)...
   ✓ Batch 1: 10 published, 0 failed
🔄 Batch 2/5 (10 events)...
   ✓ Batch 2: 10 published, 0 failed
...
```

### Large Datasets
For 100+ pending events:
- Use pattern matching to narrow down
- Use range selection for consecutive events
- Batch mode handles large selections efficiently

---

## Keyboard Shortcuts Summary

| Key/Command | Action |
|-------------|--------|
| `[number]` | Toggle single event (e.g., `5`) |
| `[n,n,n]` | Toggle multiple events (e.g., `1,3,5`) |
| `all` | Select all events |
| `none` | Clear selection |
| `range N-M` | Select range of events |
| `pattern WORD` | Select by title pattern |
| `approve` | Batch approve selected |
| `reject` | Batch reject selected |
| `show` | View selected event details |
| `back` | Exit batch mode |

---

## Error Handling

### Invalid Number
```
Command: 99
❌ Invalid event number: 99
```

### Invalid Range
```
Command: range abc
❌ Invalid range format: invalid literal for int() with base 10: 'abc'
```

### No Selection
```
Command: approve
❌ No events selected
```

### Invalid Command
```
Command: xyz
❌ Invalid command. Type 'back' to exit batch mode.
```

---

## Integration with Workflow

The batch selection mode integrates seamlessly:

1. **Local TUI**: Interactive selection with visual feedback
2. **CLI Batching**: Automated processing via `bulk-publish`/`bulk-reject`
3. **GitHub Actions**: Workflow-based batch operations

**Best for Local TUI:**
- Initial review and selection
- Complex selection criteria
- Visual verification

**Best for CLI:**
- Automated workflows
- Scripted operations
- CI/CD integration

**Best for GitHub Actions:**
- Remote publishing
- Scheduled batch operations
- Team collaboration

---

## Tips & Best Practices

1. **Start with Patterns**: Use pattern matching to quickly select event categories
2. **Use Show Liberally**: Always verify selection with `show` before bulk operations
3. **Work in Batches**: For large datasets, process in smaller groups (e.g., 10-20 at a time)
4. **Combine Methods**: Pattern match + manual toggle = precise selection
5. **Save Frequently**: Batch mode auto-saves after approve/reject
6. **Exit Safely**: Use `back` command to exit without changes

---

## Future Enhancements

Potential additions:

1. **Filter by Source**: `source official` to select all from specific source
2. **Filter by Date**: `date 2024-06` to select events in June
3. **Undo Last Action**: Reverse last batch operation
4. **Save Selection**: Save selection for later use
5. **Export Selection**: Export selected event IDs to file
6. **Multi-Criteria**: Combine filters (e.g., `pattern music AND source official`)

---

## Support

For issues or questions:
1. Check this guide for command syntax
2. Use `show` to verify selection before operations
3. Review GitHub repository issues
4. Contact maintainers via GitHub

---

**Remember**: Batch selection mode is designed to make editorial review faster and more efficient while maintaining safety through confirmations and visual feedback. Use it to streamline your workflow!
