# CSS Modules

> Modular CSS architecture for maintainability and reusability

## 🎯 Overview

The CSS is split into 10 focused modules following ITCSS (Inverted Triangle CSS) methodology. Each module handles a specific aspect of the UI, making it easier to maintain, update, and understand.

## 📦 Modules (ITCSS Order)

### Layer 1: Foundation
**foundation.css** (39 lines)
- Global base styles and typography
- CSS custom properties (--app-width, --app-height)
- Body and HTML styles
- Heading styles
- Universal reset for non-Leaflet elements

### Layer 2: Layout
**layout.css** (20 lines)
- Grid and flexbox layouts
- Scrollbar customization
- Positioning utilities

### Layer 3: Components
**components.css** (283 lines)
- Reusable UI elements
- Speech bubbles
- Buttons
- Modals
- Notifications
- Logo and branding

**forms.css** (216 lines)
- Form input styling
- Custom location coordinates
- Input fields and controls

### Layer 4: Features
**map.css** (104 lines)
- Map container and positioning
- Leaflet integration styles
- Custom marker styles
- Map overlays

**filters.css** (236 lines)
- Interactive filter bar
- Filter controls and dropdowns
- Distance slider
- Time range selector

**dashboard.css** (401 lines)
- Dashboard modal and overlay
- Content sections
- Open/close animations
- Environment indicators (DEV/PRODUCTION)

### Layer 5: Interactions
**interactions.css** (167 lines)
- Hover effects
- Focus states
- Active states
- Touch interactions

### Layer 6: Utilities
**utilities.css** (33 lines)
- Helper classes
- Visibility utilities
- Text alignment
- Spacing helpers

### Layer 7: Debug
**debug.css** (180 lines)
- Development tools
- Debug groups and sections
- Performance indicators
- Development-only utilities

## 🚀 Usage

Modules are automatically loaded by the site generator (`src/modules/site_generator.py`) in ITCSS order:

```python
css_modules = [
    # Layer 1: Foundation
    'foundation.css',
    # Layer 2: Layout
    'layout.css',
    # Layer 3: Components
    'components.css',
    'forms.css',
    # Layer 4: Features
    'map.css',
    'filters.css',
    'dashboard.css',
    # Layer 5: Interactions
    'interactions.css',
    # Layer 6: Utilities
    'utilities.css',
    # Layer 7: Debug
    'debug.css'
]
```

During build:
1. Each module is loaded from `assets/css/`
2. Modules are concatenated in ITCSS order
3. Combined CSS is inlined into `public/index.html`

## 🔧 Editing

To modify styles:

1. Edit the specific module file in `assets/css/`
2. Regenerate the site: `python3 src/event_manager.py generate`
3. The modules are combined and inlined during generation

**Important:** Never edit `public/index.html` directly - it's auto-generated!

## 💡 Design Tokens

All modules use CSS custom properties from `design-tokens.css`:
- `var(--color-primary)` - Barbie Pink
- `var(--color-bg-primary)` - Dark background
- `var(--color-text-primary)` - Light text
- And more...

See `assets/html/variables-reference.md` for complete token reference.

## 📝 Adding New Modules

1. Create new `.css` file in `assets/css/`
2. Add module header comment: `/* Module Name */`
3. Write focused, scoped styles (keep under 500 lines for KISS compliance)
4. Update `src/modules/site_generator.py` to include new module in `css_modules` list
5. Test with `python3 src/event_manager.py generate`

## ✅ Benefits

- **Maintainability**: Easy to find and update specific styles
- **Modularity**: Independent modules, minimal coupling
- **Readability**: Small, focused files (largest is 401 lines)
- **Reusability**: Modules can be included/excluded as needed
- **KISS Principle**: Simple, flat structure
- **ITCSS Organization**: Ordered by specificity (Foundation → Utilities)
- **Performance**: 80/100 score (VERY GOOD rating)
- **Git-Friendly**: Changes are isolated to relevant modules

## 📊 Statistics

- **Total**: 10 CSS modules
- **Lines**: ~1,679 lines
- **Largest**: dashboard.css (401 lines)
- **Smallest**: layout.css (20 lines)
- **Performance**: 80/100 (VERY GOOD)
- **Organization**: ITCSS methodology

---

See `CSS_OPTIMIZATION_SUMMARY.md` for detailed performance metrics and optimization guidelines.
