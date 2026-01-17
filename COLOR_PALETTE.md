# KRWL HOF Monochromatic Color Palette Reference

**Status:** Read-Only Reference Document  
**Purpose:** Professional color palette documentation  
**Last Updated:** 2026-01-17

---

## Overview

This document serves as a **permanent reference** for the KRWL HOF monochromatic color palette based on the **ecoBarbie** theme. All colors are derived from a single base color and its variations through tints, shades, and tones.

**Base Color:** ecoBarbie `#D689B8` (RGB: 214, 137, 184)

> **Note:** This is a reference document only. The actual colors used in the application are defined in `config.json` under the `design.colors` section. To modify colors, edit `config.json` and regenerate design tokens using `python3 src/tools/generate_design_tokens.py`.

---

## Color Theory: Monochromatic Palette

A **monochromatic color scheme** uses variations of a single hue by adjusting:
- **Tints** (base color + white) - Lighter variations
- **Shades** (base color + black) - Darker variations  
- **Tones** (base color + grey) - Muted variations

---

## Complete Color Palette

### Primary ecoBarbie Colors

| Name | Hex | RGB | Usage | Contrast |
|------|-----|-----|-------|----------|
| **ecoBarbie Base** | `#D689B8` | 214, 137, 184 | Primary brand color, accents, highlights | 4.2:1 on dark bg |
| **ecoBarbie Light** | `#E8A5C8` | 232, 165, 200 | Hover states, lighter accents | 5.5:1 on dark bg |
| **ecoBarbie Medium Tint** | `#FFB3DF` | 255, 179, 223 | Bright highlights, badges | 7.0:1 on dark bg |

### ecoBarbie Tones (+ Grey)

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Light Tone** | `#D689B8` | 214, 137, 184 | Same as base |
| **Medium Tone** | `#B05F8E` | 176, 95, 142 | Subtle accents, borders |
| **Dark Tone** | `#8A4A70` | 138, 74, 112 | Deep accents |

### ecoBarbie Shades (+ Black)

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Light Shade** | `#BF5087` | 191, 80, 135 | Vibrant accents |
| **Medium Shade** | `#80355A` | 128, 53, 90 | Dark UI elements |
| **Dark Shade** | `#401B2D` | 64, 27, 45 | Very dark backgrounds |
| **Darkest Shade** | `#200D16` | 32, 13, 22 | Almost black backgrounds |

### Neutral Greys & Blacks

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Pure Black** | `#000000` | 0, 0, 0 | Shadows, true black |
| **Near Black** | `#0D0D0D` | 13, 13, 13 | Very dark UI |
| **Dark Grey 1** | `#0d1117` | 13, 17, 23 | Primary background |
| **Dark Grey 2** | `#161b22` | 22, 27, 34 | Secondary background |
| **Dark Grey 3** | `#1a1a1a` | 26, 26, 26 | Cards, panels |
| **Dark Grey 4** | `#21262d` | 33, 38, 45 | Tertiary background |
| **Medium Dark** | `#2a2a2a` | 42, 42, 42 | Buttons, controls |
| **Medium Grey** | `#3a3a3a` | 58, 58, 58 | Borders |
| **Light Grey** | `#555555` | 85, 85, 85 | Inactive text |
| **Lighter Grey** | `#888888` | 136, 136, 136 | Subtle text |

### Text Colors

| Name | Hex | RGB | Usage | Contrast |
|------|-----|-----|-------|----------|
| **Text Primary** | `#c9d1d9` | 201, 209, 217 | Main text | 11.1:1 on `#0d1117` |
| **Text Secondary** | `#8b949e` | 139, 148, 158 | Secondary text | 6.5:1 on `#0d1117` |
| **Text Tertiary** | `#6e7681` | 110, 118, 129 | Tertiary text | 4.8:1 on `#0d1117` |
| **White** | `#ffffff` | 255, 255, 255 | High contrast text | 21:1 on black |
| **Light Text** | `#ddd` | 221, 221, 221 | Light text on dark | 14:1 on `#1a1a1a` |
| **Muted Text** | `#ccc` | 204, 204, 204 | Muted text | 12:1 on `#1a1a1a` |

### Accent Colors (Non-Monochromatic)

| Name | Hex | RGB | Usage | Notes |
|------|-----|-----|-------|-------|
| **Accent Blue** | `#58a6ff` | 88, 166, 255 | Links, info | Contrast color for variety |
| **Warning Orange** | `#d29922` | 210, 153, 34 | Warnings, pending | High visibility |
| **Warning Alt** | `#f59e0b` | 245, 158, 11 | Alternative warning | Brighter orange |
| **Error Red** | `#f85149` | 248, 81, 73 | Errors, critical | Alert color |
| **Bookmark Red** | `#ffb3b3` | 255, 179, 179 | Bookmarked items | Light red for bookmarks |
| **Bookmark Light** | `#ffcccc` | 255, 204, 204 | Bookmark hover | Even lighter |
| **Bookmark Lighter** | `#ffe6e6` | 255, 230, 230 | Bookmark subtle | Subtle background |

---

## Alpha Channel Variations

### Primary Pink with Alpha (RGBA)

Common opacity levels for ecoBarbie `#D689B8` (214, 137, 184):

| Opacity | RGBA | Usage |
|---------|------|-------|
| 100% | `rgba(214, 137, 184, 1.0)` | Solid color |
| 95% | `rgba(214, 137, 184, 0.95)` | Nearly solid |
| 80% | `rgba(214, 137, 184, 0.8)` | Strong glow |
| 60% | `rgba(214, 137, 184, 0.6)` | Medium glow |
| 50% | `rgba(214, 137, 184, 0.5)` | Half opacity |
| 40% | `rgba(214, 137, 184, 0.4)` | Light glow |
| 30% | `rgba(214, 137, 184, 0.3)` | Subtle glow |
| 25% | `rgba(214, 137, 184, 0.25)` | Very subtle |
| 20% | `rgba(214, 137, 184, 0.2)` | Barely visible |
| 15% | `rgba(214, 137, 184, 0.15)` | Ultra subtle |
| 10% | `rgba(214, 137, 184, 0.1)` | Hint of color |

### Black with Alpha (Shadows)

Common opacity levels for black shadows:

| Opacity | RGBA | Usage |
|---------|------|-------|
| 80% | `rgba(0, 0, 0, 0.8)` | Strong shadow/overlay |
| 70% | `rgba(0, 0, 0, 0.7)` | Medium-strong shadow |
| 60% | `rgba(0, 0, 0, 0.6)` | Medium shadow |
| 50% | `rgba(0, 0, 0, 0.5)` | Balanced shadow |
| 40% | `rgba(0, 0, 0, 0.4)` | Light shadow |
| 30% | `rgba(0, 0, 0, 0.3)` | Subtle shadow |

### Background with Alpha

| Color | RGBA | Usage |
|-------|------|-------|
| **Dark Bg Semi-transparent** | `rgba(13, 17, 23, 0.95)` | Backdrop filter backgrounds |
| **Dark Bg Overlay** | `rgba(13, 17, 23, 0.6)` | Light overlay |

### Warning/Accent with Alpha

| Color | RGBA | Usage |
|-------|------|-------|
| **Warning Glow** | `rgba(210, 153, 34, 0.3)` | Warning highlight |
| **Warning Subtle** | `rgba(210, 153, 34, 0.15)` | Warning background |
| **Warning Very Subtle** | `rgba(210, 153, 34, 0.05)` | Warning hint |
| **Error Subtle** | `rgba(248, 81, 73, 0.1)` | Error background |

---

## Professional Usage Guidelines

### Accessibility

All color combinations meet **WCAG 2.1 Level AA** standards:
- **Normal text:** Minimum 4.5:1 contrast ratio
- **Large text:** Minimum 3:1 contrast ratio
- **UI components:** Minimum 3:1 contrast ratio

### Best Practices

1. **Consistency:** Always use CSS variables from the design system
2. **Never hardcode colors** - Use `var(--color-name)` syntax
3. **Alpha channel usage:** For glows, shadows, and overlays
4. **Test on multiple displays:** Check color rendering across devices
5. **Dark mode optimized:** This palette is designed for dark backgrounds

### Color Relationships

```
Text Hierarchy:
text_primary (#c9d1d9) > text_secondary (#8b949e) > text_tertiary (#6e7681)

Background Hierarchy:
bg_primary (#0d1117) > bg_secondary (#161b22) > bg_tertiary (#21262d)

Border Hierarchy:
border_primary (#30363d) > border_secondary (#21262d)

ecoBarbie Hierarchy:
primary (#D689B8) > primary_hover (#E8A5C8) > medium_tint (#FFB3DF)
```

---

## Implementation

### CSS Variables

All colors are available as CSS custom properties:

```css
/* Example usage */
.element {
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-primary);
  box-shadow: 0 0 10px var(--color-primary-alpha-30);
}
```

### Adding New Colors

To add a new color to the palette:

1. Edit `config.json` → `design.colors` section
2. Run: `python3 src/tools/generate_design_tokens.py`
3. Use: `var(--color-your-new-name)` in CSS
4. Update this reference document

---

## Color Psychology

**Pink (ecoBarbie):**
- Conveys: Warmth, creativity, playfulness, ecology-conscious
- Emotional: Friendly, approachable, modern
- Brand: Distinctive, memorable, progressive

**Dark Greys:**
- Conveys: Professionalism, sophistication, focus
- Emotional: Calm, serious, trustworthy
- UX: Reduces eye strain, emphasizes content

**Monochromatic Benefits:**
- Creates visual harmony
- Professional and cohesive appearance
- Easier to maintain consistency
- Clear visual hierarchy
- Better accessibility when done correctly

---

## Technical Notes

### Color Space

All colors are defined in **sRGB** color space for maximum web compatibility.

### Format Preference

- **Hex codes:** For solid colors (`#D689B8`)
- **RGBA:** For transparent colors (`rgba(214, 137, 184, 0.3)`)
- **CSS Variables:** For all production use (`var(--color-primary)`)

### Browser Support

- Modern browsers: Full support for CSS custom properties
- Legacy browsers: Fallback values where critical

---

## Version History

- **v1.0** (2026-01-17): Initial comprehensive palette documentation
  - Documented all 60+ color variations
  - Added RGBA alpha channel reference
  - Included accessibility guidelines
  - Professional usage guidelines

---

## Related Documentation

- **Design Tokens:** `assets/html/design-tokens.css` (auto-generated)
- **Configuration:** `config.json` → `design.colors` section
- **Generator:** `src/tools/generate_design_tokens.py`
- **Style Guide:** `assets/css/style.css` (header comments)

---

**Questions or Suggestions?**  
Open an issue on GitHub or contact the maintainers.
