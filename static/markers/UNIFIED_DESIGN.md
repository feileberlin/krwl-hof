# Unified Gyro Marker Design System

## Core Principle

**ALL markers use the same teardrop/location pin (gyro) shape.**
**Only the icon inside varies.**

## Standard Template

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 48" width="32" height="48">
  <!-- Drop shadow -->
  <ellipse cx="16" cy="46" rx="6" ry="2" fill="#000" opacity="0.5"/>
  
  <!-- STANDARD GYRO SHAPE (same for all) -->
  <path d="M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z" 
        fill="none" stroke="#00ff00" stroke-width="2"/>
  
  <!-- ICON GOES HERE (8x8 to 12x12 area, centered at cx=16, cy=15) -->
  <!-- Example: Simple circle -->
  <circle cx="16" cy="15" r="5" fill="none" stroke="#00ff00" stroke-width="1.5"/>
  
</svg>
```

## Design Rules

### 1. Gyro Shape (Never Changes)
- **Path**: `M16 2 C9 2 3 8 3 15 C3 24 16 46 16 46 C16 46 29 24 29 15 C29 8 23 2 16 2 Z`
- **Stroke**: `#00ff00`
- **Width**: `2px`
- **Fill**: `none`

### 2. Icon Area
- **Center point**: `cx="16" cy="15"`
- **Size**: 8x8 to 14x14 pixels max
- **Bounds**: Roughly x: 9-23, y: 8-22
- **Style**: Outline only, no fills

### 3. Icon Stroke Weights
- **Main icon**: 1.5px (clearly visible)
- **Details**: 1px
- **Fine details**: 0.5px (sparingly)

### 4. What Makes Markers Different

**ONLY the icon inside the gyro:**
- Geolocation: Person silhouette
- Church: Cross
- Hospital: Medical cross
- Library: Book
- etc.

**The gyro shape stays identical for all.**

## Color Variations (Optional)

For **active/hover states only**, can vary:
- Glow effect (outer path with opacity)
- Thicker stroke
- But keep same gyro shape

## Examples

### Simple Icons (Preferred)
```svg
<!-- Church - just a cross -->
<line x1="16" y1="11" x2="16" y2="19" stroke="#00ff00" stroke-width="1.5"/>
<line x1="12" y1="15" x2="20" y2="15" stroke="#00ff00" stroke-width="1.5"/>
```

### Compound Icons (When needed)
```svg
<!-- Hospital - medical cross in shield -->
<circle cx="16" cy="15" r="6" fill="none" stroke="#00ff00" stroke-width="1.5"/>
<line x1="16" y1="11" x2="16" y2="19" stroke="#00ff00" stroke-width="1.5"/>
<line x1="12" y1="15" x2="20" y2="15" stroke="#00ff00" stroke-width="1.5"/>
```

## Benefits of Unified Shape

1. ✓ **Consistent visual language**
2. ✓ **Easy to recognize as markers**
3. ✓ **Icons are the differentiator**
4. ✓ **Simpler to create new markers**
5. ✓ **Professional, cohesive appearance**
6. ✓ **Scales well at all sizes**

## Quick Reference

```
Same for ALL markers:
- Gyro outline shape
- Color: #00ff00
- Stroke width: 2px
- Drop shadow
- ViewBox: 0 0 32 48

Different per marker:
- Icon inside (centered at 16, 15)
- Icon should be immediately recognizable
- Keep icons simple and clean
```
