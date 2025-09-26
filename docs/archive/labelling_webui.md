# Thai Syllable Labeling Web UI

## Current Status: In Development (Not Finished)

This document tracks the development progress of the Thai syllable labeling web interface.

## Recent Changes

### Triangle-Based Positioning System

**Implementation Date**: Current session

**Overview**: Replaced the previous text positioning system with a geometric triangle-based layout for syllable components.

#### Key Features:

1. **Triangle Geometry**:
   - 120° angle at top (vowel position)
   - 30° angles at each base corner
   - Configurable triangle height: 90 pixels
   - Dynamic horizontal offset calculation using trigonometry

2. **Positioning System**:
   - **Gold dot**: Absolute center reference (cyan container center)
   - **Black dot**: Base point (50px below gold dot)
   - **Blue dot**: Vowel position (90px above base point)
   - **Red dot**: Foundation position (left triangle corner)
   - **Green dot**: Final position (right triangle corner)

3. **Text Positioning**:
   - Foundation text positioned at red dot
   - Vowel text positioned at blue dot
   - Final text positioned at green dot
   - Per-interpretation positioning (each syllable card independent)

4. **Debug Visualization**:
   - Colored dots show triangle reference points
   - Debug borders outline text at new positions
   - Dimension labels show text box sizes
   - Debug mode toggle for showing/hiding visualization

#### Technical Implementation:

1. **Font Support**:
   - Microsoft Sans Serif font required for vowel patterns with tone marks
   - Dynamic font size and family changes trigger repositioning
   - Text measurement and triangle recalculation on font changes

2. **Coordinate System**:
   - All positioning relative to cyan syllable container
   - Uses getBoundingClientRect() for precise positioning
   - Container-relative coordinates for consistent layout

3. **Dynamic Recalculation**:
   - Font changes trigger automatic repositioning
   - Works on page load, server restart, and word analysis
   - Per-interpretation recalculation system

#### Fixes Applied:

1. **Hardcoded Position Override**: Removed inline `top: 110px` styles that prevented dynamic positioning
2. **Per-Interpretation Logic**: Moved positioning from global to per-interpretation scope
3. **Debug Border Sync**: Updated debug borders to follow text positions with setTimeout delay
4. **Coordinate System Consistency**: Ensured dots and text use identical positioning logic

## Known Issues

- This is a work in progress - positioning system needs refinement
- Debug visualization may need performance optimization
- Font loading timing could affect initial positioning

## Next Steps

- Further refinement of triangle positioning
- Integration with existing labeling workflow
- Performance optimization for large interpretation sets
- User interface improvements

## Files Modified

- `thai_syllable_labeler.html` - Main interface file with triangle positioning system
- Font handling and dynamic recalculation systems
- Debug visualization and border positioning

---

**Note**: This system is experimental and under active development. The triangle-based positioning represents a foundational step toward a more sophisticated syllable layout system.