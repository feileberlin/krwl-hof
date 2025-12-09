# SVG Marker Design System

## Design Principles

All 68 markers follow a consistent terminal/hacker aesthetic with these unified design rules:

### 1. Color System
- **Single color**: `#00ff00` (bright terminal green)
- **No fills**: All shapes use `stroke` only, never `fill` (except small accent dots)
- **Shadow**: Black ellipse with 50% opacity at base
- **Transparency**: Backgrounds are transparent

### 2. Geometric Structure

#### Pin Base (All Markers)
Every marker uses the same pin stem connecting to the map point:
```svg
<!-- Standard pin stem -->
<path d="M14 20 L16 46 L18 20" stroke="#00ff00" stroke-width="2"/>
<!-- OR for wider base -->
<path d="M12 20 L16 46 L20 20" stroke="#00ff00" stroke-width="2"/>
```

#### Icon Head (20x20px area)
- **Position**: Top 20px of the 32x48 canvas
- **Bounds**: x: 6-26, y: 2-22
- **Stem connection**: y=20 (where icon meets pin)

### 3. Visual Hierarchy

#### Primary Shapes (Stroke Width: 2px)
- Main building outlines
- Pin stems
- Primary structural elements

#### Secondary Details (Stroke Width: 1.5px)
- Windows, doors
- Interior walls
- Secondary structural elements

#### Tertiary Details (Stroke Width: 1px)
- Decorative patterns
- Fine details
- Texture indicators

#### Micro Details (Stroke Width: 0.5px)
- Very fine patterns
- Text representations
- Subtle textures

### 4. Shape Language

Each marker category uses distinct geometric shapes:

| Category | Primary Shape | Visual Identity |
|----------|---------------|-----------------|
| **Locations** | Geometric polygons | Angular, structural |
| **Religious** | Organic curves + symmetry | Spiritual, balanced |
| **Historic** | Irregular, aged forms | Weathered, ancient |
| **Commercial** | Letter-based shapes | Branded, recognizable |
| **Cultural** | Unique cultural patterns | Authentic, diverse |
| **Nature/Parks** | Organic curves | Natural, flowing |

### 5. Drop Shadow Standard

Every marker has the same shadow:
```svg
<ellipse cx="16" cy="46" rx="6" ry="2" fill="#000" opacity="0.5"/>
```

### 6. Icon Categories & Design Rules

#### A. Location Markers (Navigation)
- **Geolocation**: Square (90° angles)
- **Main Station**: Rectangle + X
- **City Center**: Octagon (8 sides)
- **Mayor's Office**: Classical pillars
- **Design**: Clean, geometric, easy to recognize quickly

#### B. Religious Buildings
- **Church**: Cross shape
- **Mosque**: Dome + minarets
- **Synagogue**: Star of David
- **Temple**: Cultural architecture
- **Design**: Culturally authentic, respectful, symmetrical

#### C. Historic Landmarks
- **Castle**: Battlements, towers
- **Ruins**: Broken, irregular
- **Monument**: Tall, vertical
- **Palace**: Ornate, regal
- **Design**: Period-appropriate details, weathered feel

#### D. Commercial (Brands)
- **Supermarkets**: Letter shapes (A, L, E, etc.)
- **Post Offices**: Mail symbols
- **Design**: Brand-recognizable but minimal

#### E. Community Places
- **Library**: Books/pages
- **Hospital**: Medical cross
- **School**: Graduation cap
- **Park**: Trees/nature
- **Design**: Universal symbols, immediately clear

#### F. Cultural/Indigenous
- **Aboriginal**: Dot painting patterns
- **Pueblo**: Multi-level adobe
- **Yurt**: Circular dome
- **Marae**: Platform + posts
- **Design**: Authentic cultural elements, respectful representation

### 7. Text in Markers

When brand names are needed:
```svg
<text x="16" y="17" 
      font-family="monospace" 
      font-size="3-5" 
      fill="#00ff00" 
      text-anchor="middle">BRAND</text>
```

- **Font**: Monospace (terminal style)
- **Size**: 3-5px depending on length
- **Color**: #00ff00
- **Alignment**: Center
- **Usage**: Only for commercial brands where recognition is critical

### 8. Stroke Standards

```svg
<!-- Main structure -->
stroke="#00ff00" stroke-width="2"

<!-- Secondary details -->
stroke="#00ff00" stroke-width="1.5"

<!-- Fine details -->
stroke="#00ff00" stroke-width="1"

<!-- Micro patterns -->
stroke="#00ff00" stroke-width="0.5"
```

### 9. Fill Usage (Minimal)

**ONLY use `fill` for:**
- Small accent dots (< 1px radius circles)
- Shadow ellipse
- Critical small details that would be invisible as outlines

**Examples:**
```svg
<!-- Allowed: Small dot -->
<circle cx="16" cy="10" r="0.5" fill="#00ff00"/>

<!-- Allowed: Shadow -->
<ellipse cx="16" cy="46" rx="6" ry="2" fill="#000" opacity="0.5"/>

<!-- NOT allowed: Large filled shape -->
<rect x="10" y="10" width="12" height="8" fill="#00ff00"/>  <!-- ✗ WRONG -->
```

### 10. Consistency Checklist

Every marker must have:
- [ ] Drop shadow at base (y=46)
- [ ] Pin stem connecting icon to point
- [ ] Only #00ff00 color
- [ ] Transparent background
- [ ] No large filled shapes
- [ ] Stroke widths: 2, 1.5, 1, or 0.5 only
- [ ] ViewBox="0 0 32 48"
- [ ] Icon anchor point: [16, 48]
- [ ] Recognizable at 32x48px size

### 11. Common Mistakes to Avoid

❌ **Don't:**
- Use colors other than #00ff00
- Fill large areas
- Make strokes thinner than 0.5px
- Create details smaller than 1px
- Vary shadow or pin stem
- Use gradients
- Add opacity to strokes (only shadow has opacity)
- Create text larger than 5px

✅ **Do:**
- Keep outlines clean and sharp
- Use appropriate stroke weights
- Test visibility at actual size
- Maintain cultural authenticity
- Follow geometric hierarchy
- Use consistent spacing

### 12. Marker Naming Convention

```
marker-[category]-[specific-name].svg
marker-[specific-location-name].svg
marker-[brand-name].svg
```

Examples:
- `marker-default.svg` (base)
- `marker-active.svg` (state)
- `marker-geolocation.svg` (location)
- `marker-city-center.svg` (location)
- `marker-church.svg` (religious)
- `marker-mosque.svg` (religious)
- `marker-aldi.svg` (commercial)
- `marker-aboriginal-site.svg` (cultural)

### 13. Size Standards

```
Canvas: 32 x 48 pixels
Icon head: ~20px tall (top portion)
Pin stem: ~26px tall (bottom portion)
Overlap: 2px at junction (y=20)
```

### 14. Testing Requirements

Before finalizing any marker:
1. ✓ View at actual size (32x48px)
2. ✓ Test on dark background (#000 or #1a1a1a)
3. ✓ Verify stroke visibility (minimum 0.5px)
4. ✓ Check cultural accuracy (if applicable)
5. ✓ Ensure uniqueness (distinguishable from others)
6. ✓ Validate SVG syntax
7. ✓ Confirm anchor point works with Leaflet

### 15. Future Additions

When creating new markers:
1. Review existing 68 markers for similar types
2. Follow this design system strictly
3. Choose appropriate category shape language
4. Test alongside existing markers for distinction
5. Update README.md with new marker documentation

## Implementation Notes

### Leaflet Integration
```javascript
const icon = L.icon({
    iconUrl: 'markers/marker-[name].svg',
    iconSize: [32, 48],
    iconAnchor: [16, 48],  // Bottom center of pin
    popupAnchor: [0, -48]  // Above marker
});
```

### CSS Enhancements (Optional)
```css
.leaflet-marker-icon {
    /* CRT glow effect */
    filter: drop-shadow(0 0 2px #00ff00);
}

.leaflet-marker-icon:hover {
    /* Enhanced glow on hover */
    filter: drop-shadow(0 0 4px #00ff00) 
            drop-shadow(0 0 8px #00ff00);
}
```

## Design Philosophy

This marker system embodies:
- **Terminal aesthetics** - Green on black, monochrome, glowing
- **Cultural respect** - Authentic representation of global heritage
- **Practical clarity** - Immediately recognizable at small sizes
- **Consistent experience** - All markers feel like part of one system
- **Accessibility** - High contrast, distinct shapes, not relying on color alone

## Current Marker Inventory

Total: **68 markers**

Categories:
- Navigation/Locations: 4
- Religious buildings: 8
- Historic landmarks: 10
- Commercial brands: 11
- Community places: 10
- Cultural/Indigenous: 8
- Event types: 5
- Capital city landmarks: 10
- Postal services: 4

All follow this unified design system.
