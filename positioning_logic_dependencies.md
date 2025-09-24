# Positioning Function Logic Dependencies & Cleanup Reference

## Overview
The `positionDotsForContainer(containerId)` function is ~600 lines handling syllable component positioning using triangular geometry. This document maps all dependencies for cleanup.

## Variable Declaration Order & Dependencies

### 1. DOM Element Lookups (MUST BE FIRST)
**Required Order:** Container → Elements → Null Check
```javascript
// 1. Find container (needed for all subsequent queries)
const container = findReadingOrderContainer(containerId);

// 2. Text elements (dependencies for positioning)
const foundationWrapper = document.getElementById(`foundation-wrapper-${containerId}`);
const finalWrapper = document.getElementById(`final-wrapper-${containerId}`);
const vowelBox = document.getElementById(`vowel-${containerId}`);
const foundationBox = document.getElementById(`foundation-${containerId}`);
const finalBox = document.getElementById(`final-${containerId}`);

// 3. Visualization elements (used in positioning calculations)
const centerDot = document.getElementById(`center-dot-${containerId}`);
const basePoint = document.getElementById(`base-point-${containerId}`);
const pointVowel = document.getElementById(`point-vowel-${containerId}`);
const pointVowelPurple = document.getElementById(`point-vowel-purple-${containerId}`);
const pointVowelPink = document.getElementById(`point-vowel-pink-${containerId}`);
const pointF1 = document.getElementById(`point-f1-${containerId}`);
const pointF2 = document.getElementById(`point-f2-${containerId}`);

// 4. Debug elements (optional, used in final positioning)
const distanceLabel = document.getElementById(`distance-label-${containerId}`);
const greenDistanceLabel = document.getElementById(`green-distance-label-${containerId}`);
// ... other debug elements
```

### 2. Container-Relative Coordinate System
**Dependency:** container → syllableDisplay
```javascript
// Must calculate cyan container center relative to reading-order container
const syllableDisplay = container.parentElement;
const syllableDisplayRect = syllableDisplay.getBoundingClientRect();
const containerRect = container.getBoundingClientRect();

// Core coordinate system (ALL other positioning depends on these)
const cyanCenterX = (syllableDisplayRect.left + syllableDisplayRect.width / 2) - containerRect.left;
const cyanCenterY = (syllableDisplayRect.top + syllableDisplayRect.height / 2) - containerRect.top;
```

### 3. Configuration Values (READ FROM CSS)
**Dependency:** CSS variables must exist
```javascript
// Triangle configuration (affects ALL dot positioning)
const triangle_h = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--triangle-height')) || 70;
const baseCornerAngle = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--base-angle')) || 25;

// Derived values
const angleRadians = baseCornerAngle * (Math.PI / 180);
const triangle_base_pos = cyanCenterY + triangle_h / 2;
const basePointY = triangle_base_pos;
```

### 4. Initial Element Positioning (FOR MEASUREMENT)
**Critical:** Must position elements temporarily to get accurate dimensions
```javascript
// TEMPORARY positioning for measurement (order critical)
foundationWrapper.style.left = '0px';
foundationWrapper.style.top = '0px';
finalWrapper.style.left = '0px';
finalWrapper.style.top = '0px';
vowelBox.style.left = '0px';
vowelBox.style.top = '0px';

// Force layout recalculation (required before measuring)
foundationWrapper.offsetWidth;
finalWrapper.offsetWidth;
vowelBox.offsetWidth;
```

### 5. Element Dimension Measurement
**Dependency:** Elements must be positioned first
```javascript
// Character-only dimensions (used in positioning calculations)
const foundationWidth = foundationBox.offsetWidth;
const foundationHeight = foundationBox.offsetHeight;
const finalWidth = finalBox.offsetWidth;
const finalHeight = finalBox.offsetHeight;
const vowelChar = vowelBox.querySelector('.component-char');
const vowelWidth = vowelChar.offsetWidth;
const vowelHeight = vowelChar.offsetHeight;
```

### 6. Core Dot Position Calculations
**Dependency Chain:**
1. cyanCenterX, triangle_h, basePointY
2. vowelWidth, vowelHeight
3. angleRadians

```javascript
// Constants
const dotmargin = 5; // Spacing between dots and text

// Blue dot (vowel center)
const blueDotX = cyanCenterX;
const blueDotY_actual = basePointY - triangle_h;

// Pink/Purple dots (depend on vowel dimensions)
const pinkDotY_actual = blueDotY_actual - vowelHeight / 2;
const purpleDotY_actual = blueDotY_actual - vowelHeight / 2;
const pinkDotX = blueDotX - vowelWidth / 2 - dotmargin;
const purpleDotX = blueDotX + vowelWidth / 2 + dotmargin;

// Trigonometric offset calculations (depend on angle & vertical distances)
const verticalDistance_to_pink = Math.abs(basePointY - pinkDotY_actual);
const verticalDistance_to_purple = Math.abs(basePointY - purpleDotY_actual);
const horizontalOffset_from_pink = verticalDistance_to_pink / Math.tan(angleRadians);
const horizontalOffset_from_purple = verticalDistance_to_purple / Math.tan(angleRadians);

// Final dot positions (depend on offsets)
const correctedRedDotX = pinkDotX - horizontalOffset_from_pink;
const correctedGreenDotX = purpleDotX + horizontalOffset_from_purple;
```

### 7. Text Element Final Positioning
**Dependency:** correctedRedDotX, correctedGreenDotX, element dimensions
```javascript
// Foundation: left of red dot
foundationWrapper.style.left = (correctedRedDotX - foundationWidth - dotmargin) + 'px';
foundationWrapper.style.top = (basePointY - foundationHeight / 2) + 'px';

// Final: right of green dot
finalWrapper.style.left = (correctedGreenDotX + dotmargin) + 'px';
finalWrapper.style.top = (basePointY - finalHeight / 2) + 'px';

// Vowel: centered on blue dot
vowelBox.style.left = (blueDotX - vowelWidth / 2) + 'px';
vowelBox.style.top = (blueDotY_actual - vowelHeight) + 'px';
```

### 8. Visualization Elements Update
**Dependency:** All calculated positions
```javascript
// Dots positioning (depend on calculated coordinates)
centerDot.style.left = (cyanCenterX - 4) + 'px';
basePoint.style.left = (cyanCenterX - 4) + 'px';
pointVowel.style.left = (cyanCenterX - 4) + 'px';
pointF1.style.left = (correctedRedDotX - 4) + 'px';
pointF2.style.left = (correctedGreenDotX - 4) + 'px';
pointVowelPink.style.left = (pinkDotX - 4) + 'px';
pointVowelPurple.style.left = (purpleDotX - 4) + 'px';

// Lines and arrows (depend on dot positions)
const correctedLineWidth = correctedGreenDotX - correctedRedDotX;
redGreenLine.style.left = correctedRedDotX + 'px';
redGreenLine.style.width = correctedLineWidth + 'px';

// Arrow calculations (depend on start/end coordinates)
const deltaX = pinkDotX - correctedRedDotX;
const deltaY = pinkDotY_actual - basePointY;
const arrowLength = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
// ... arrow positioning and SVG updates
```

### 9. Debug Information Updates
**Dependency:** All calculations complete
```javascript
// Distance labels
const distance = Math.abs(correctedRedDotX - cyanCenterX);
const distance_green = Math.abs(correctedGreenDotX - cyanCenterX);
distanceLabel.textContent = `${Math.round(distance)}px`;
greenDistanceLabel.textContent = `${Math.round(distance_green)}px`;

// Angle calculations (for verification)
// Complex vector math using final dot positions
```

### 10. Layout-Dependent Updates (ASYNC)
**Dependency:** All positioning complete, requires setTimeout
```javascript
setTimeout(() => {
    // Debug borders (depend on final rendered positions)
    const foundationCharRect = foundationBox.getBoundingClientRect();
    foundationBorder.style.left = (foundationCharRect.left - containerRect.left) + 'px';
    // ... border positioning for all elements

    // Label positioning (depend on element final positions)
    const foundationCenterX = correctedRedDotX - foundationWidth - dotmargin + (foundationWidth / 2);
    foundationLabel.style.left = (foundationCenterX - foundationLabelWidth / 2) + 'px';
    // ... other label positioning
}, 10);
```

## Critical Dependencies Summary

### Must Execute In Order:
1. **DOM Queries** → **Null Check** → **Exit if missing**
2. **Container coordinate system** (cyanCenterX/Y)
3. **CSS configuration** (triangle_h, angle)
4. **Temporary element positioning** for measurement
5. **Element dimension measurement**
6. **Core dot calculations** (trigonometry)
7. **Final text positioning**
8. **Visualization updates**
9. **Debug information**
10. **Async layout updates**

### Variable Interdependencies:
- `cyanCenterX/Y` → affects ALL positioning
- `triangle_h` → affects `basePointY` → affects all vertical calculations
- `angleRadians` → affects horizontal offsets → affects red/green dot positions
- `vowelWidth/Height` → affects pink/purple dot positions → affects trigonometric offsets
- `correctedRedDotX/GreenDotX` → affects text positioning → affects final layout

### Conditional Logic:
- Some debug elements are optional (null checks required)
- Final element may not exist (hasNoFinal logic)
- Arrow updates depend on SVG element existence
- Border updates require setTimeout for accurate getBoundingClientRect()

## Cleanup Opportunities
1. **Function decomposition** - separate calculation, positioning, visualization phases
2. **Variable scoping** - eliminate duplicate calculations across scopes
3. **Configuration consolidation** - single CSS variable read section
4. **Error handling** - proper null checks and fallbacks
5. **Debug separation** - move debug logic to separate optional functions
6. **Async handling** - better management of layout-dependent operations