# 🇹🇭 Thai Algorithm Development

A comprehensive toolkit for Thai language processing, focusing on grapheme classification and reading order algorithms.

## 🚀 Quick Start

### Launch Character Classifier
**Windows Users:**
```bash
# Double-click one of these files:
launcher/open_classifier.bat    # Recommended (starts HTTP server)
launcher/simple_open.bat       # Simple file opening
```

**Python Users:**
```bash
python launcher/open_classifier.py    # With HTTP server
python launcher/simple_open.py       # Direct file opening
```

## 📁 Project Structure

```
Thai Algorithm Development/
├── 🚀 launcher/              # Application launchers
│   ├── open_classifier.bat       # Windows launcher (HTTP server)
│   ├── simple_open.bat          # Windows launcher (direct)
│   ├── open_classifier.py       # Python launcher (HTTP server)
│   └── simple_open.py           # Python launcher (direct)
│
├── 🛠️ tools/                 # Interactive tools
│   └── thai_classifier_improved.html  # Character classification web app
│
├── 📊 script/                # Data processing utilities
│   ├── convertToJson.py         # Convert text mappings to JSON
│   ├── make_foundation_json.py   # Generate foundation character data
│   ├── flatten_sara_combos.py    # Flatten vowel combinations
│   └── unique_start_chars.py     # Extract unique starting characters
│
├── 📂 res/                   # Processed Thai language data
│   ├── foundation/              # Foundation consonant data
│   └── sara/                   # Vowel combination data
│
├── 📓 notebook.ipynb         # Main research notebook
├── 📋 CLAUDE.md             # Detailed technical documentation
└── 📖 README.md             # This file
```

## 🎯 Features

### Thai Grapheme Classification Algorithm
- Classifies Thai characters into 4 main categories:
  - **ฐาน (tan)** - Foundation consonants
  - **สระ (sara)** - Vowel patterns
  - **ยุกต์ (yuk)** - Dependent marks
  - **ข้อยกเว้น (kho yok waen)** - Exception characters (อ, ว)

### Interactive Classification Tool
- 🎨 **Font customization** - Multiple Thai fonts with size/weight controls
- 🖱️ **Drag-and-drop interface** - Easy pattern organization
- 💾 **Save/Load progress** - Browser-based persistence
- 📤 **JSON export** - Export classifications for analysis
- 📊 **Real-time statistics** - Track classification progress

### Data Processing Pipeline
- Convert plain text mappings to structured JSON
- Process vowel combinations and consonant patterns
- Extract unique character sets and starting patterns

## 🔬 Research Focus

The project explores Thai reading order algorithms, particularly handling:
- **Non-linear reading** - Vowels that appear before but read after consonants
- **Consonant clusters** - Multiple foundations acting as units
- **Multi-part vowels** - Complex vowel patterns spanning characters
- **Special cases** - อ and ว dual-role characters

## 📚 Usage Examples

### Simple Classification
```python
result = classifyThaiGraphemes("ยา")
# Returns: [{'grapheme': 'ย', 'class': 'foundation', 'read_order': 0},
#           {'grapheme': 'xา', 'class': 'vowel', 'read_order': 1}]
```

### Complex Patterns
```python
result = classifyThaiGraphemes("เด็ก")
# Handles leading vowel "เ" that reads after foundation "ด"
```

## 🛠️ Technical Details

- **Language**: Python 3.13+ with Jupyter notebooks
- **Web Interface**: HTML/CSS/JavaScript (no external dependencies)
- **Data Format**: UTF-8 encoded JSON files
- **Pattern Matching**: Template-based with x/f placeholders

## 📋 Requirements

- Python 3.13+ (for scripts and launchers)
- Modern web browser (for classification tool)
- UTF-8 support for Thai characters

## 🎓 Academic Context

This research supports understanding of:
- Thai orthographic complexity
- Reading order determination algorithms
- Grapheme-to-phoneme correspondence
- Tone rule applications in Thai

---

For detailed technical documentation, see [CLAUDE.md](CLAUDE.md)