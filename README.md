# Thai Algorithm Development

A research project developing deterministic algorithms for Thai syllable segmentation and vowel detection based on linguistic conjectures. The project aims to create explainable, non-ML approaches to Thai language processing that respect Thai orthographic principles.

## Core Innovation: Conjecture-Based Approach

This project is built on two fundamental linguistic axioms:

### 1. Voraritskul Conjecture for Thai Segmentation
**"Every Thai syllable contains exactly one vowel pattern that serves as an anchor for segmentation."**

- Uses vowels as fixed reference points for syllable boundaries
- Enables deterministic segmentation without exhaustive search
- Provides explainable results based on orthographic rules

### 2. Two-Character Proximity Conjecture
**"For any consonant in Thai text, a vowel component (explicit or hidden) exists within 2 characters distance."**

- Enables systematic detection of hidden vowels (คน → ค[โ-ะ]น)
- Provides search space optimization for pattern matching
- Creates definitive rules for vowel presence

## Current Algorithms

### Conjecture-Based Vowel Detector
**Status: Production Ready**
- **File**: `conjecture_based_vowel_detector.py`
- **Purpose**: Complete vowel detection including hidden vowels
- **Features**:
  - Modular rule engine for extensibility
  - 1-based indexing for linguistic intuition
  - Evidence tracking for explainable results
  - Handles explicit, hidden, and ambiguous vowels

### Thai Reading Order Algorithm v0.2
**Status: Complete Analysis**
- **File**: `thai_reading_order.py`
- **Purpose**: Foundation container model for syllable analysis
- **Coverage**: 100% accuracy on test cases
- **Limitation**: Single syllable only (by design)

## Thai Grapheme Classification System

Characters are classified into four main categories:

1. **ฐาน (tan)** - Foundation consonants (44 total): All Thai consonants that serve as syllable bases
2. **สระ (sara)** - Vowel patterns (72+ patterns): Complete orthographic vowel combinations
3. **ยุกต์ (yuk)** - Dependent marks: Tone marks and diacritics
4. **ข้อยกเว้น (kho yok waen)** - Exceptions: Characters **อ** and **ว** with dual roles

## Pattern Database

### Vowel Patterns with Dual ID System
Each of the 72+ vowel patterns has:
- **Abbreviated ID**: `a_l_o` (a-long-open)
- **Long ID**: `a_long_open`
- **Pattern Template**: `xา` (x=foundation, vowel marks)
- **Linguistic Tags**: Sound, length, openness, glides

**Examples:**
- `xา` → `a_l_o` / `a_long_open` (simple long vowel)
- `เx็f` → `e_s_c` / `e_short_closed` (complex pattern with final)
- `ไxย` → `ai_s_c_jg_3` / `ai_short_closed_jglide_3` (with glide)

## Quick Start

### Basic Vowel Detection
```python
from conjecture_based_vowel_detector import ConjectureBasedVowelDetector

detector = ConjectureBasedVowelDetector("thai_vowels_tagged_9-21-2025-2-31-pm.json")
vowels = detector.find_vowels("ประเทศไทย")

# Access results (1-based indexing)
for i in sorted(vowels.keys()):
    vowel_data = vowels[i]
    print(f"Vowel {i}: {vowel_data.best_candidate.pattern}")
```

### Environment Setup
```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate

# Install dependencies (if needed)
pip install flask
```

### Run Labeling System
```bash
# Windows
launcher/flask_classifier.bat

# Python
python launcher/flask_server.py
```

## Documentation Structure

- **`docs/algorithms/`** - Core algorithm documentation
  - `voraritskul_conjecture_thai_segmentation.md` - Foundational theory
  - `conjecture_based_vowel_detector_documentation.md` - Usage guide
  - `thai_order_algorithm_v_0.2.md` - Algorithm analysis
- **`docs/systems/`** - System documentation
  - `LABELING_SYSTEM_DOCS.md` - Web labeling interface
- **`docs/archive/`** - Historical documents
- **`CLAUDE.md`** - Claude Code integration guidance

## Key Features

### Non-ML Approach
- **Deterministic**: Every decision traceable to linguistic rules
- **Explainable**: Evidence tracking for all detections
- **Extensible**: Modular rule engine for adding domain knowledge
- **Fast**: Linear time complexity with smart indexing

### Hidden Vowel Detection
Systematic detection of implicit vowels:
- **คน** → ค[โ-ะ]น (detect missing short o)
- **สตรี** → ส[ะ]ตรี (detect hidden vowel after ส)
- **กรม** → ก[ะ]รม or กร[โ-ะ]ม (context-dependent)

### Linguistic Fidelity
- Respects Thai orthographic principles
- Handles tone marks, consonant clusters, ambiguous characters
- Maintains Thai phonological structure throughout processing

## Research Applications

1. **Thai NLP**: Syllable segmentation for text-to-speech, spell checkers
2. **Linguistic Analysis**: Corpus analysis, orthographic pattern discovery
3. **Educational Tools**: Thai language learning applications
4. **AI Evaluation**: Novel inference evaluation for Thai language models

## Future Directions

1. **Multi-syllable Segmentation**: Extend vowel anchors to full word segmentation
2. **Tone Analysis**: Integrate tone mark placement rules
3. **Dictionary Validation**: Cross-reference with lexical databases
4. **Performance Optimization**: Advanced indexing and caching

## Contributing

The project uses a conjecture-driven development approach:
1. Formulate linguistic hypotheses as testable conjectures
2. Implement algorithms treating conjectures as axioms
3. Validate against Thai text corpora
4. Refine rules based on edge cases

## License

This research project explores deterministic approaches to Thai language processing. When using or citing this work, please reference the underlying conjectures and methodologies.

---

*Project Focus: Explainable Thai language processing through linguistic conjectures*
*Last Updated: September 26, 2025*