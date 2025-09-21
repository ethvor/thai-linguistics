# Thai Algorithm Development

Development towards making an inference evaluation algorithm that respects Thai's nonlinear reading order and the properties of the Thai abugida. Future goals are to generalize to all abugidas. This is just one part of a larger project.

## Quick Start

Launch the interactive character classifier:

**Windows:**
```bash
launcher/open_classifier.bat     # Recommended (Flask server)
launcher/simple_open.bat        # Direct file opening
```

**Python:**
```bash
python launcher/open_classifier.py    # Flask server
python launcher/simple_open.py       # Direct file
```

## Project Structure

```
Thai Algorithm Development/
├── launcher/              # Application launchers
├── tools/                # Interactive classification web app
├── script/               # Data processing utilities
├── res/                  # Thai language data (JSON)
├── notebook.ipynb        # Main research notebook
└── CLAUDE.md            # Technical documentation
```

## Features

### Thai Grapheme Classification
Classifies Thai characters into four main categories:
- **ฐาน (tan)** - Foundation consonants that serve as bases
- **สระ (sara)** - Vowel patterns that attach to foundations
- **ยุกต์ (yuk)** - Dependent marks (tone marks, diacritics)
- **ข้อยกเว้น (exceptions)** - Special case characters like อ

### Interactive Web Tool
- Drag-and-drop pattern organization with grid-based positioning
- Font customization for Thai text display
- Pattern creation with validation and dual save modes
- Session persistence through server restarts
- JSON export for further analysis

### Data Processing Pipeline
- Convert plain text vowel mappings to structured JSON
- Process foundation consonants and vowel combinations
- Extract unique character patterns and starting sequences

## Research Focus

The project explores algorithms for handling Thai's complex orthography:
- **Nonlinear reading order** - vowels that appear before but read after consonants
- **Consonant clusters** - multiple foundations acting as single units
- **Multi-part vowels** - complex patterns spanning multiple character positions
- **Special cases** - dual-role characters and exceptions

## Technical Details

- **Language**: Python 3.13+ with Jupyter for research
- **Web Interface**: HTML/CSS/JavaScript with Flask backend
- **Data Format**: UTF-8 encoded JSON with template patterns
- **Pattern Matching**: Template-based using x/f placeholders for consonants

## Requirements

- Python 3.13+ (for scripts and server)
- Modern web browser with JavaScript enabled
- UTF-8 support for Thai character display

For detailed technical documentation, see [CLAUDE.md](CLAUDE.md)