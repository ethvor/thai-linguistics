# Thai Language Conjectures Summary

**Date Created:** September 28, 2025
**Total Conjectures:** 3

---

## 1. The Absolute Vowel Position Conjecture

**File**: [absolute_vowel_position_conjecture.md](./absolute_vowel_position_conjecture.md)

**Core Statement**: For any Thai syllable, there is exactly one Absolute Vowel Position (AVP).

**Key Concept**: Absolute Vowel Position (AVP) - The location in spoken Thai of the first vowel phoneme, positioned directly after the initial foundation where the vowel is phonetically realized.

**Purpose**: Provides deterministic anchor points for Thai syllable segmentation.

---

## 2. The Two-Character Proximity Conjecture

**File**: [proximity_conjecture.md](./proximity_conjecture.md)

**Core Statement**: For any consonant c, there exists some absolute vowel position v within at most 2 characters, noninclusive.

**Purpose**: Final-pass rule for identifying hidden vowel positions after explicit vowel detection.

**Scope**: Completion and validation rule, not primary detection method.

---

## 3. The Initial Foundation Terminal Conjecture (IFTC)

**File**: [initial_foundation_terminal_conjecture.md](./initial_foundation_terminal_conjecture.md)

**Core Statement**: If any consonant c has any tone mark, then c is the last character in an initial foundation for that syllable.

**Key Concept**: Tone marks on consonants signal the boundary/terminus of initial consonant clusters.

**Purpose**: Enables syllable boundary detection and foundation container identification.

---

## Relationship Between Conjectures

1. **Absolute Vowel Position Conjecture** establishes the concept of Absolute Vowel Positions
2. **Proximity Conjecture** uses AVPs to ensure complete consonant-vowel coverage
3. **Initial Foundation Terminal Conjecture** provides syllable boundary detection through tone mark positioning
4. Together they provide a framework for comprehensive Thai text analysis

## Implementation Status

- **Absolute Vowel Position Conjecture**: Conceptual framework established, implementation pending
- **Proximity Conjecture**: Ready for implementation as final-pass algorithm
- **Initial Foundation Terminal Conjecture**: Documented, needs empirical validation across Thai corpus

---

*A foundation for deterministic, rule-based Thai language processing.*