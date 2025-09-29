# Thai Language Conjectures Summary

**Date Created:** September 28, 2025
**Total Conjectures:** 2

---

## 1. The Voraritskul Conjecture (Revised)

**File**: [voraritskul_conjecture_revised.md](./voraritskul_conjecture_revised.md)

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

## Relationship Between Conjectures

1. **Voraritskul Conjecture** establishes the concept of Absolute Vowel Positions
2. **Proximity Conjecture** uses AVPs to ensure complete consonant-vowel coverage
3. Together they provide a framework for comprehensive Thai text analysis

## Implementation Status

- **Voraritskul Conjecture**: Conceptual framework established, implementation pending
- **Proximity Conjecture**: Ready for implementation as final-pass algorithm

---

*A foundation for deterministic, rule-based Thai language processing.*