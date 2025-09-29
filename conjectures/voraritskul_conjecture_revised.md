# The Voraritskul Conjecture (Revised)
**Based on Absolute Vowel Position (AVP)**

**Date Created:** September 28, 2025
**Status:** Active Development
**Version:** 2.0 (Revised)

---

## Core Definition

**Absolute Vowel Position (AVP)**: The location in spoken Thai of the first vowel phoneme. For any vowel pattern, the AVP is exactly one position - the position directly after the initial foundation where the vowel is phonetically realized.

## The Conjecture Statement

> **For any Thai syllable, there is exactly one Absolute Vowel Position (AVP).**

## Key Principles

### 1. Uniqueness
Each syllable has precisely one AVP, never zero, never multiple.

### 2. Invariance
Regardless of how the vowel pattern is written orthographically (before, after, above, below the consonant), the AVP is always the same phonetic position.

### 3. Segmentation Anchor
The AVP serves as the definitive anchor point for syllable identification.

## Theoretical Implications

1. **Syllable Boundaries**: Can be determined by locating AVPs and working bidirectionally
2. **Deterministic Segmentation**: No ambiguity in syllable core identification
3. **Orthographic Independence**: Written form variations don't affect the fundamental AVP location
4. **Computational Efficiency**: Single anchor point per syllable reduces search space

## Implementation Strategy

### Phase 1: AVP Detection
- Locate all vowel patterns in text
- Map each pattern to its corresponding AVP
- Validate one-to-one syllable-to-AVP correspondence

### Phase 2: Boundary Determination
- Use AVPs as fixed anchor points
- Apply bidirectional boundary rules
- Validate against phonotactic constraints

### Phase 3: Segmentation Algorithm
- Complete syllable extraction based on AVP anchors
- Handle edge cases and ambiguous characters
- Optimize for performance

## Status

**Current State**: Conceptual framework established
**Next Steps**: Define precise AVP mapping rules for all Thai vowel patterns
**Implementation**: Pending AVP detection algorithm development

---

*Revision of the original Voraritskul Conjecture with simplified, phonetically-grounded foundation.*