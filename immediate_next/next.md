# Immediate Next Steps: Grapheme Classification Algorithm

**Date Created:** September 29, 2025
**Status:** Planning Phase

---

## Objective

Develop a novel algorithm that identifies Thai grapheme classes through visual highlighting in a web UI.

## Implementation Strategy

### Phase 1: Foundation Consonant Identification
- **Target**: Characters we know are consonants (ฐาน/tan)
- **Method**: Highlight confirmed consonants
- **Color**: [TBD - assign color]

### Phase 2: Vowel-Only Character Identification
- **Target**: Pure vowel characters (สระ/sara)
- **Method**: Highlight confirmed vowels
- **Color**: [TBD - assign color]

### Phase 3: Dependent Diacritics
- **Target**: Tone marks and other dependent characters (ยุกต์/yuk)
- **Method**: Highlight confirmed dependents
- **Color**: [TBD - assign color]

### Phase 4: Exception Characters
- **Target**: อ and ว when functioning as vowel components (ข้อยกเว้น/kho yok waen)
- **Method**: Highlight exception usage
- **Color**: [TBD - assign color]

### Phase 5: Unsure/Ambiguous
- **Initial Behavior**: No highlighting for uncertain classifications
- **Later**: Add disambiguation logic

### Phase 6: AVP Markers
- **Target**: Absolute Vowel Positions (from Absolute Vowel Position Conjecture)
- **Method**: Mark AVPs with character/pointer overlay
- **Marker**: [TBD - choose symbol/indicator]

---

## Color Scheme (To Be Determined)

| Class | Thai Name | English | Color | Purpose |
|-------|-----------|---------|-------|---------|
| ฐาน | tan | Foundation | ? | Consonant bases |
| สระ | sara | Vowel | ? | Vowel patterns |
| ยุกต์ | yuk | Dependent | ? | Tone marks, diacritics |
| ข้อยกเว้น | kho yok waen | Exception | ? | อ/ว as vowel components |
| AVP | - | Vowel Position | ? | Phonetic vowel location |

---

## Technical Requirements

### Web UI Features
- Real-time text input
- Character-level highlighting
- Color-coded classification
- AVP position markers
- Toggle visibility for each class

### Algorithm Requirements
- Deterministic classification rules
- Handle ambiguous cases gracefully
- Support incremental certainty (start with known cases)
- Extensible for future refinements

---

## Development Approach

1. **Start Conservative**: Only highlight what we're absolutely certain about
2. **Iterative Refinement**: Add classification rules progressively
3. **Visual Feedback**: Use UI to validate algorithm accuracy
4. **Phonetic Grounding**: Base on Absolute Vowel Position Conjecture principles

---

*Next: Define color scheme and begin Phase 1 implementation*