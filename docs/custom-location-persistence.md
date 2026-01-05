# Custom Location Persistence Feature

## Overview

The KRWL HOF Community Events app now saves custom location settings to browser localStorage, allowing users to:
- Set a custom location once and have it persist across sessions
- Switch between location types without losing their custom coordinates
- Return to their saved custom location at any time

## How It Works

### 1. Setting a Custom Location

1. Click on the location filter in the top bar (e.g., "from here")
2. Select "Custom location" radio button
3. Enter latitude and longitude coordinates
4. Click "Apply"

**Result**: Your coordinates are saved to localStorage under the key `krwl_filters`

### 2. Switching Between Location Types

You can freely switch between:
- **Geolocation** ("from here") - Uses your current GPS location
- **Predefined Locations** - Uses configured locations from config.json
- **Custom Location** - Uses your saved coordinates

**Important**: When you switch away from custom location, your custom coordinates remain saved in localStorage. When you switch back, they automatically reappear in the input fields!

### 3. Persistence Across Sessions

Your custom location persists:
- ✅ Across page reloads
- ✅ Across browser sessions (as long as localStorage isn't cleared)
- ✅ When switching between location types
- ✅ When other filters change (distance, time, category)

### 4. How to Clear Custom Location

To remove your saved custom location:
1. Open browser developer tools (F12)
2. Go to Application > Local Storage > `krwl_filters`
3. Delete the entry, or
4. Run: `localStorage.removeItem('krwl_filters')`

## Technical Details

### localStorage Structure

All filter settings are stored in a single localStorage item:

```json
{
  "maxDistance": 2,
  "timeFilter": "sunrise",
  "category": "all",
  "locationType": "custom",
  "selectedPredefinedLocation": null,
  "customLat": 50.3167,
  "customLon": 11.9167
}
```

### Key Functions

**Save to localStorage:**
```javascript
saveFiltersToCookie() {
    const filterData = JSON.stringify(this.filters);
    localStorage.setItem('krwl_filters', filterData);
}
```

**Load from localStorage:**
```javascript
loadFiltersFromCookie() {
    const filterData = localStorage.getItem('krwl_filters');
    return filterData ? JSON.parse(filterData) : null;
}
```

### Browser Compatibility

This feature uses the [Web Storage API (localStorage)](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage), which is supported by:
- ✅ Chrome/Edge 4+
- ✅ Firefox 3.5+
- ✅ Safari 4+
- ✅ Opera 10.50+
- ✅ iOS Safari 3.2+
- ✅ Android Browser 2.1+

**Fallback**: If localStorage is not available, the app will still work but custom locations won't persist across page reloads.

## Testing

A test page is available at `tests/test_custom_location_localstorage.html` which allows you to:

1. **Test 1**: Save custom location to localStorage
2. **Test 2**: Load custom location from localStorage
3. **Test 3**: Verify persistence across page reloads
4. **Test 4**: Verify preservation when switching location types
5. View real-time localStorage state

### Running the Tests

1. Open `tests/test_custom_location_localstorage.html` in a web browser
2. Run each test in sequence
3. For Test 3, reload the page after saving to verify persistence
4. Check that no errors appear in the browser console

## User Benefits

✨ **Convenience**: Set your custom location once, use it forever
🔄 **Flexibility**: Switch between location types without losing settings  
💾 **Persistence**: Settings survive page reloads and browser restarts
🎯 **Accuracy**: Use precise coordinates for locations not in predefined list

## Developer Notes

### Bug Fix (2025-01-04)

**Issue**: Custom location coordinates were being cleared when switching to other location types.

**Solution**: Removed code that was setting `customLat` and `customLon` to `null` when switching location types. Now coordinates persist in the filter object even when not actively used.

**Files Changed**:
- `assets/js/app.js` (lines 2631-2677)
- `public/index.html` (auto-generated)

**Affected Functions**:
- Location type switch handler (geolocation case)
- Location type switch handler (predefined case)
- Custom location input pre-fill logic

### Future Enhancements

Possible improvements:
- [ ] Add "Clear custom location" button in UI
- [ ] Show indicator when custom location is saved
- [ ] Allow saving multiple custom locations with names
- [ ] Export/import saved locations
- [ ] Add coordinate validation with helpful error messages

## Examples

### Example 1: Setting Hof Hauptbahnhof

```
Latitude: 50.3125
Longitude: 11.9189
```

### Example 2: Setting Berlin

```
Latitude: 52.5200
Longitude: 13.4050
```

### Example 3: Checking Saved Data

Open browser console and run:
```javascript
JSON.parse(localStorage.getItem('krwl_filters'))
```

Output:
```json
{
  "maxDistance": 2,
  "timeFilter": "sunrise", 
  "category": "all",
  "locationType": "custom",
  "selectedPredefinedLocation": null,
  "customLat": 50.3125,
  "customLon": 11.9189
}
```

## Support

For issues or questions about this feature:
1. Check browser console for errors
2. Verify localStorage is enabled in browser settings
3. Try clearing localStorage and setting custom location again
4. Report bugs via GitHub Issues

---

**Last Updated**: 2025-01-04  
**Feature Version**: 1.0  
**Status**: ✅ Implemented and Working
