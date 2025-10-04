# Thai Language Conjectures Summary

**Date Created:** September 28, 2025
**Last Updated:** October 4, 2025
**Total Conjectures:** 4

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

## 3. The Initial Foundation Terminal Conjecture (IFTC) - ✅ Extended & Confirmed

**File**: [initial_foundation_terminal_conjecture.md](./initial_foundation_terminal_conjecture.md)

**Extended Statement (✅ Confirmed 2025-10-03)**: If any consonant c has a vowel part OR tone mark (yuk), then c is a terminal initial-foundation consonant.

**Original Statement**: If any consonant c has any tone mark, then c is the last character in an initial foundation for that syllable.

**Key Concept**: Vowel parts and tone marks on consonants signal the boundary/terminus of initial consonant clusters.

**Purpose**: Enables syllable boundary detection and foundation container identification.

**Status**: Extended IFTC empirically validated and confirmed as primary formulation.

---

## 4. The AVP Terminal Position Conjecture - Discovered

**File**: [avp_terminal_position_conjecture.md](./avp_terminal_position_conjecture.md)

**Core Statement**: Absolute Vowel Positions (AVPs) are ALWAYS directly after terminal initial-foundation consonants.

**Key Insight**: The AVP location is deterministic - it always follows the last consonant of the initial foundation, whether single or clustered.

**Purpose**: Provides precise AVP localization for vowel pattern detection and syllable segmentation.

**Status**: New conjecture discovered 2025-10-04, requires empirical validation.

---

## Relationship Between Conjectures

1. **Absolute Vowel Position Conjecture** establishes the concept of Absolute Vowel Positions
2. **Proximity Conjecture** uses AVPs to ensure complete consonant-vowel coverage
3. **Initial Foundation Terminal Conjecture (Extended)** provides syllable boundary detection through vowel part and tone mark positioning
4. **AVP Terminal Position Conjecture** specifies exactly WHERE the AVP is located (directly after terminal)
5. Together they provide a complete framework for deterministic Thai text analysis

## Implementation Status

- **Absolute Vowel Position Conjecture**: Conceptual framework established, implementation pending
- **Proximity Conjecture**: Ready for implementation as final-pass algorithm
- **Initial Foundation Terminal Conjecture**: ✅ Extended version confirmed and implemented in `projects/highlight_algorithm/src/renderer.py`

---

*A foundation for deterministic, rule-based Thai language processing.*