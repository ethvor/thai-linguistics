# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Thai language processing project focused on developing algorithms for classifying Thai graphemes. The main research is conducted in `notebook.ipynb`, which explores a Thai grapheme classification system that categorizes characters into four main classes:

1. **ฐาน (tan)** - Foundation class: Consonant letters that serve as the base for dependent marks
2. **สระ (sara)** - Vowel class: Vowel graphemes (both independent and dependent) that attach to foundation consonants
3. **ยุกต์ (yuk)** - Dependent class: Tone marks and diacritics that cannot exist without a foundation consonant
4. **ข้อยกเว้น (kho yok waen)** - Exception class: The consonant **อ** which functions both as foundation and as part of vowel symbols

## Environment Setup

The project uses Python 3.13 with a virtual environment:

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Unix/Mac)
source .venv/bin/activate
```

## Data Processing Scripts

The `script/` directory contains utilities for processing Thai language data:

- **`convertToJson.py`** - Transforms plain-text Thai vowel mappings into structured JSON format
  - Usage: `python script/convertToJson.py INPUT.txt OUTPUT.json --dotted strip`
  - Handles dotted circle (◌) characters with options: keep, strip, or replace

- **`make_foundation_json.py`** - Generates JSON file with Thai foundation consonants
  - Usage: `python script/make_foundation_json.py INPUT.txt OUTPUT.json`
  - Contains hardcoded list of 43 Thai consonants

- **`flatten_sara_combos.py`** - Flattens vowel template dictionaries into single lists
  - Usage: `python script/flatten_sara_combos.py INPUT.json OUTPUT.json`

- **`unique_start_chars.py`** - Extracts unique starting characters from vowel templates
  - Usage: `python script/unique_start_chars.py INPUT.json OUTPUT.json`

## Data Structure

The `res/` directory contains processed Thai language data:

- `res/foundation/` - Foundation consonant data (plaintext and JSON)
- `res/sara/` - Vowel combination data including:
  - `sara_combos.json` - Main vowel template mappings
  - `classified_sara_combos.json` - Classified vowel data
  - `sara_start_chars.json` - Unique starting characters

## Development Workflow

1. **Research and algorithm development** happens in `notebook.ipynb`
2. **Data processing** uses the scripts in `script/` directory to transform raw Thai language data
3. **Processed data** is stored in JSON format in the `res/` directory
4. **Testing** is done interactively in the Jupyter notebook with various Thai text examples
5. **Character classification** can be done using the web app in `tools/` directory

## Project Structure

```
├── launcher/              # Application launchers
│   ├── flask_classifier.bat      # Windows launcher (Flask server)
│   └── flask_server.py          # Python Flask server
├── tools/                # Interactive tools
│   └── thai_classifier_improved.html  # Character classification web app
├── script/               # Data processing utilities
├── res/                  # Processed Thai language data
├── progress/             # Saved classification progress (auto-created)
├── notebook.ipynb        # Main research notebook
└── CLAUDE.md            # This file
```

## Quick Start

To launch the character classifier:
- **Windows**: Double-click `launcher/flask_classifier.bat`
- **Python**: Run `python launcher/flask_server.py`

The server will show you a link to open in your browser (no auto-opening).

## Character Classification Tool

The `tools/thai_classifier_improved.html` provides an interactive interface for:
- **Tag-based classification**: Patterns can have multiple tags simultaneously
- **Drag-and-drop tagging**: Drag patterns to tag containers
- **Selection-based tagging**: Select multiple patterns and assign tags
- **Search functionality**: Find patterns containing specific characters
- **Bulk operations**: Move/copy patterns between tags
- **Font customization**: Better Thai text readability
- **File-based progress**: Save/load progress as JSON files
- **Export functionality**: Export classifications as JSON for analysis

### Save/Load Workflow
- **Save Progress**: Automatically saves to `progress/` directory (with graceful fallback to Downloads)
- **Load Progress**: Click Load Progress → select file from `progress/` directory
- **Progress files**: Named `thai_classifier_progress_[timestamp].json`
- **Server Features**: Flask server handles direct file saving, auto-creates directories

## Key Files

- `notebook.ipynb` - Main research notebook with algorithm development and testing
- `script/convertToJson.py` - Primary data processing utility for Thai text parsing
- `res/foundation/foundation.json` - Contains the 43 Thai foundation consonants
- `res/sara/sara_combos.json` - Contains 79 vowel combinations for classification

## Thai Text Processing Notes

The algorithm handles complex Thai text patterns including:
- Simple cases: foundation + atomic vowel (e.g., "ยา")
- Complex cases: multi-part vowels that appear before their foundation consonant (e.g., "เด็ก")
- Cluster cases: multiple consonants with shared vowels (e.g., "ไกล")
- Special อ cases: where อ acts as silent foundation or vowel component (e.g., "เอือม")