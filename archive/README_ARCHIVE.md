# Archive Directory

This directory contains historical code and documentation that has been superseded by newer implementations but is preserved for reference.

## Code Archive Structure

### `prototype_algorithms/`
Early versions of vowel detection algorithms that led to the final conjecture-based approach:

- **`vowel_anchor_detection_algorithm.py`** - First vowel anchor implementation
- **`vowel_anchor_detection_v2.py`** - Enhanced with dual ID system
- **`vowel_anchor_detection_v3.py`** - Database integration version
- **`vowel_finder_simple.py`** - Simple brute-force approach

**Superseded by**: `conjecture_based_vowel_detector.py` (production version)

### `debug_scripts/`
Development debugging tools:

- **`check_patterns.py`** - Pattern existence checker
- **`debug_elw.py`** - Debug script for เลว interpretation issues
- **`debug_tone_marks.py`** - Tone mark placement debugging

**Status**: No longer needed with current algorithm's evidence tracking

### `development_tools/`
Utility scripts used during development:

- **`analyze_pattern_uniqueness.py`** - Pattern ID collision analysis
- **`add_ids_to_database.py`** - Script that added IDs to pattern database
- **`test_vowel_distance_conjecture.py`** - Validation of proximity conjecture

**Status**: Development completed, database updated

## Documentation Archive

### `docs/archive/`

- **`enhanced_id_system_design.md`** - Design document for dual ID system (implemented)
- **`positioning_logic_dependencies.md`** - Old positioning approach (superseded by conjectures)
- **`labelling_webui.md`** - Redundant UI documentation (consolidated into LABELING_SYSTEM_DOCS.md)

## Active vs Archived Code

### Active (Production) Files:
- `conjecture_based_vowel_detector.py` - Main vowel detection algorithm
- `thai_reading_order.py` - Single-syllable analysis (complete)
- `thai_labeling_app.py` - Web labeling system
- `run.py` - Test runner for reading order algorithm

### Active (Database/System) Files:
- `database/` - Database management and labeling system
- `launcher/` - Application launchers
- `script/` - Data processing utilities

### Archived Files:
All files in `archive/` subdirectories represent completed development phases or superseded approaches.

---

*Files archived: September 26, 2025*
*Reason: Project maturation to conjecture-based approach*