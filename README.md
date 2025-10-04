# Thai Algorithm Development

A research project developing deterministic algorithms for Thai syllable segmentation and vowel detection based on linguistic conjectures. The project aims to create explainable, non-ML approaches to Thai language processing that respect Thai orthographic principles.

## Conjecture-Based Approach

This project is built on several fundamental linguistic conjectures

### 1. Absolute Vowel Position (AVP) Conjecture
**"For any Thai syllable, there is exactly one Absolute Vowel Position (AVP)."**

- **AVP Definition**: The phonetic location where the first vowel is realized in spoken Thai, positioned directly after the initial foundation consonant
- Uses AVPs as fixed anchor points for syllable boundaries
- Enables deterministic segmentation without exhaustive search
- Provides explainable results based on orthographic rules
- Invariant to written form (vowels may appear before, after, above, or below consonants)

### 2. Two-Character Proximity Conjecture
**"For any consonant in Thai text, a vowel component (explicit or hidden) exists within 2 characters distance."**

- Enables systematic detection of hidden vowels (คน → ค[โ-ะ]น)
- Provides search space optimization for pattern matching
- Final-pass validation rule for complete vowel coverage
- Reference: Uses AVPs defined in the Absolute Vowel Position Conjecture

### 3. Extended Initial Foundation Terminal Conjecture (Extended IFTC)
**"If any consonant c has a vowel part OR tone mark (yuk), then c is a terminal initial-foundation consonant."**

- **Confirmed**: 2025-10-03 - Extended version empirically validated as primary formulation
- Both vowel parts and tone marks signal syllable boundaries
- Enables comprehensive syllable boundary detection
- Helps identify foundation container boundaries
- Example: `ปร้าว` → `ร` has tone mark `้` → `ร` is terminal in initial foundation `ปร`
- Example: `เมือง` → `ม` has vowel part `เ` → `ม` is terminal
- Implemented in `projects/highlight_algorithm/src/renderer.py`
- See: [`conjectures/initial_foundation_terminal_conjecture.md`](conjectures/initial_foundation_terminal_conjecture.md)

### 4. AVP Terminal Position Conjecture
**"Absolute Vowel Positions (AVPs) are ALWAYS directly after terminal initial-foundation consonants."**

- **Discovered**: 2025-10-04 - New conjecture requiring empirical validation
- Provides deterministic AVP localization after terminal consonants
- AVP follows the last consonant of initial foundation (single or clustered)
- Enables precise vowel pattern boundary detection
- Links foundation structure to vowel realization in Thai phonetics
- Example: `มา` → Terminal `ม` → AVP directly after `ม`
- Example: `ครู` → Terminal `ร` (in cluster `คร`) → AVP directly after `ร`
- See: [`conjectures/avp_terminal_position_conjecture.md`](conjectures/avp_terminal_position_conjecture.md)

## Web Applications

### 1. Thai Pattern Classifier
**Launch**: `launcher/flask_classifier.bat` (Windows) or `python launcher/flask_classifier.py`

Interactive web tool for classifying and organizing Thai vowel patterns:
- Tag-based classification (multiple tags per pattern)
- Drag-and-drop interface with auto-scroll
- Advanced search with logical operators (NOT, AND, OR)
- Pattern deletion with automatic backups
- Bulk operations (move/copy between tags)
- Font customization for Thai text
- Progress persistence with 24-hour time naming
- Session auto-restore through server restarts
- Export to JSON

### 2. Thai Grapheme Highlighter
**Launch**: `launcher/flask_highlighter.bat` (Windows) or `python launcher/flask_highlighter.py`

Real-time visual classification of Thai characters:
- Color-coded grapheme highlighting:
  - **ฐาน (tan)** - Foundation consonants
  - **สระ (sara)** - Vowel patterns
  - **ยุกต์ (yuk)** - Dependent marks (tone marks, diacritics)
  - **ข้อยกเว้น (kho yok waen)** - Exception characters (อ, ว, ย)
- AVP (Absolute Vowel Position) markers
- Toggle visibility per class
- Real-time text input processing
- Multiple Thai fonts with customization

### 3. Thai Syllable Labeler
**Launch**: `launcher/syllable_label_server.bat` (Windows)

Database-backed labeling system for validating syllable interpretations:
- Interactive labeling interface
- Validity tracking (valid, invalid, synonymous, unlabeled)
- Custom interpretation support
- Session management
- Algorithm feedback collection

## Thai Grapheme Classification System

Characters are classified into four main categories:

1. **ฐาน (tan)** - Foundation consonants (44 total): All Thai consonants that serve as syllable bases
2. **สระ (sara)** - Vowel patterns (72+ patterns): Complete orthographic vowel combinations
3. **ยุกต์ (yuk)** - Dependent marks: Tone marks and diacritics that cannot exist without a foundation
4. **ข้อยกเว้น (kho yok waen)** - Exceptions: Characters **อ**, **ว**, and **ย** which function both as foundation consonants and as parts of vowel patterns

## Pattern Database

### Vowel Patterns with Dual ID System
Each of the 72+ vowel patterns has:
- **Abbreviated ID**: `a_l_o` (a-long-open)
- **Long ID**: `a_long_open`
- **Pattern Template**: `xา` (x=foundation, vowel marks, f=final)
- **Linguistic Tags**: Sound, length, openness, glides
- **Metadata**: Timestamp, source, classification status

**File**: `data/thai_vowels_tagged_9-21-2025-2-31-pm.json` (923 lines, 72+ patterns)

**Examples:**
- `xา` → `a_l_o` / `a_long_open` (simple long vowel)
- `xวf` → `ua_l_c_wg` / `ua_long_closed_wglide` (diphthong with final)
- `เx็f` → `e_s_c` / `e_short_closed` (complex pattern with final)
- `ไxย` → `ai_s_c_jg_3` / `ai_short_closed_jglide_3` (with glide)

### Foundation Consonants
**File**: `res/foundation/foundation.json` (44 consonants)
- All Thai consonants including exceptions (อ, ว, ย)
- Simple JSON array format

## Quick Start

### Launch Web Applications
```bash
# Pattern Classifier (Windows)
launcher\flask_classifier.bat

# Grapheme Highlighter (Windows)
launcher\flask_highlighter.bat

# Syllable Labeler (Windows)
launcher\syllable_label_server.bat

# Cross-platform alternative
python launcher/flask_classifier.py
python launcher/flask_highlighter.py
```

### Basic Vowel Detection
```python
from src.get_vowels_multi import get_vowels_multi

text = "ประเทศไทย"
vowels = get_vowels_multi(text, "data/thai_vowels_tagged_9-21-2025-2-31-pm.json")

# Access results (1-based indexing)
for vowel_num in sorted(vowels.keys()):
    interpretations = vowels[vowel_num]
    print(f"Vowel {vowel_num}:")
    for interp in interpretations:
        print(f"  Pattern: {interp['pattern']}")
        print(f"  ID: {interp['abbrev_id']}")
```

### Reading Order Analysis
```python
from src.thai_reading_order import ThaiReadingOrderAnalyzer

analyzer = ThaiReadingOrderAnalyzer("data/thai_vowels_tagged_9-21-2025-2-31-pm.json")
results = analyzer.findThaiGraphemeOrderDomain("ประ")

for result in results:
    print(f"Reading order: {result}")
```

## Database Systems

### Thai AVP Graphemes Database
**File**: `database/thai_avp_graphemes.db`
- **Categories**: foundation, vowel_pattern, dependent
- **Characters**: Individual graphemes with metadata
- **Tags**: Classification tags for organization
- **Clusters**: Valid consonant cluster storage

### Thai Syllable Labels Database
**File**: `database/thai_syllable_labels.db`
- **Sessions**: Labeling session tracking
- **Words**: Thai words with interpretations
- **Interpretations**: Syllable breakdowns
- **Validity**: Status tracking (valid, invalid, synonymous, unlabeled)
- **Invalid Components**: Detailed error tracking
- **Feedback**: Algorithm performance data

## Documentation Structure

- **`conjectures/`** - Research conjectures
  - `absolute_vowel_position_conjecture.md` - Core AVP theory
  - `proximity_conjecture.md` - Two-character proximity rule
  - `summary.md` - Conjecture relationships
- **`docs/algorithms/`** - Core algorithm documentation
  - `absolute_vowel_position_conjecture_thai_segmentation.md` - Foundational theory
  - `conjecture_based_vowel_detector_documentation.md` - Usage guide
- **`docs/systems/`** - System documentation
  - `LABELING_SYSTEM_DOCS.md` - Web labeling interface
- **`CLAUDE.md`** - Claude Code integration guidance

## Key Features

### Non-ML Approach
- **Deterministic**: Every decision traceable to linguistic rules
- **Explainable**: Evidence tracking for all detections
- **Extensible**: Modular rule engine for adding domain knowledge
- **Fast**: Linear time complexity with smart indexing
- **No Training**: Pure rule-based, no corpus required
