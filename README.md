# Thai Algorithm Development

Currently, this project is an attempt to formally label every grapheme in thai with properties like 'long vowel' and 'closed ending' for vowels or 'high class' for consonants. These tags will be used to
read thai characters in the correct order, which will aid in evaluating AI inference in the thai language. This logic can be used both in determining the tone of an arbitrary (though orthographically correct) set of thai characters, and 
also in the novel inference evaluation algorithm I intend to create.


## Thai Grapheme Classification

Classifies Thai characters into four main categories:
- **ฐาน (tan)** - Foundation consonants that serve as bases
- **สระ (sara)** - Vowel patterns that attach to foundations
- **ยุกต์ (yuk)** - Dependent marks (tone marks, diacritics)
- **ข้อยกเว้น (exceptions)** - Special case characters. Currently, อ and ว.

### Pattern Examples

**Simple vowel patterns:**
- `xา` - long a vowel (e.g., ยา)
- `เxอ` - e vowel with foundation in middle (e.g., เยอ)
- `โxะ` - o vowel (e.g., โยะ)

**Complex multi-part vowels:**
- `เxียะ` - short open diphthong ia (e.g., เปียะ)
- `เxือะ` - short open diphthong uea (e.g., เนือะ)

**Foundation consonants:**
- All 44 Thai consonants including อ and ว (now properly handled)

**Dependent marks (yuk):**
- Tone marks: ◌่ ◌้ ◌๊ ◌๋
- Diacritics: ◌็ ◌์ ◌ํ ◌๎

**Exceptions**
- ว and อ, because they appear both as a foundation (ฐาน / tan) and a vowel (สระ / sara)

## Thai Reading Order Algorithm

The `findThaiGraphemeOrderDomain` algorithm determines all possible canonical reading orders for Thai text by treating consonants as **foundation containers** that can hold:
- One or more consonants (clusters like กร, คล)
- Tone marks (่ ้ ๊ ๋) attached to specific consonants
- Position information for accurate text reconstruction

### How It Works

1. **Pattern Matching**: Uses 72+ vowel patterns (e.g., `xา`, `เxียf`) where:
   - `x` = foundation container (initial consonant(s) + optional tone)
   - `f` = final consonant (optional)
   - Other characters = exact vowel marks

2. **Foundation Containers**: When matching `x`, the algorithm builds a complete foundation object including all consonants and any attached tone marks. For example, "อย่า" matches as:
   - Foundation: {consonants: ['อ','ย'], tone: '่', tone_owner: 1}
   - Pattern: `xา`
   - Reading order: อย่ า

3. **Ambiguity Detection**: Generates multiple interpretations when characters like ว could be:
   - Part of a consonant cluster (ลว)
   - A final consonant (pattern `เxf`)
   - Part of a vowel pattern (pattern `เxว`)

4. **Output Domain**: Returns all possible readings as a structured domain that can be reduced later with linguistic rules (e.g., valid cluster rules, tone constraints).

### Usage

```python
from thai_reading_order import ThaiReadingOrderAnalyzer

analyzer = ThaiReadingOrderAnalyzer(foundation_file, patterns_file)
result = analyzer.findThaiGraphemeOrderDomain("เลว")

# Returns all possible interpretations:
# 1. ลว + เx (cluster interpretation)
# 2. ล + เxf (ว as final consonant)
# 3. ล + เxว (ว as part of vowel)
```

## Features

### Interactive Web Tool
- Drag-and-drop pattern organization with customizable grid layout
- Advanced tag filtering with logical operators (NOT, AND, OR)
- Pattern deletion with automatic backup creation
- Font customization for optimal Thai text display
- Session persistence and automatic restoration through server restarts
- 24-hour time file naming for chronological organization
- JSON export and source file updating capabilities

### Data Processing Pipeline
- Convert plain text vowel mappings to structured JSON
- Process foundation consonants and vowel combinations
- Extract unique character patterns and starting sequences
- Analyze and remove duplicate patterns

## Research Focus

The project explores creating algorithms and labelling data needed for handling Thai's complex orthography:
- **Nonlinear reading order** - vowels that appear before but read after consonants
- **Consonant clusters** - multiple foundations acting as single units
- **Multi-part vowels** - complex patterns spanning multiple character positions
- **Special cases** - dual-role characters and exceptions

## Technical Details

- **Language**: Python 3.13+
- **Web Interface**: HTML/CSS/JavaScript with Flask backend
- **Data Format**: UTF-8 encoded JSON with template patterns
- **Pattern Matching**: Template-based using x/f placeholders for consonants

## Requirements

- Python 3.13+ (for scripts and server)
- Modern web browser with JavaScript enabled
- UTF-8 support for Thai character display

## How to Use

Launch the interactive pattern classifier:

```
launcher/flask_classifier.bat
```

This will start a Flask server and open the classification tool in your browser. The tool allows you to drag and drop Thai patterns into different categories and save your classifications.
