# The Two-Character Proximity Conjecture
*For Hidden Vowel Detection in Thai Text*

**Date Created:** September 26, 2025
**Status:** Active - Refined
**Last Updated:** September 28, 2025

---

## Verbatim Statement

> **"For any consonant c, there exists some absolute vowel position v within at most 2 characters, noninclusive."**

## Short Discussion

This conjecture serves as a validation and completion rule rather than a primary detection method. After all explicit vowel patterns have been identified, any consonants that remain without an associated absolute vowel position within the 2-character threshold indicate locations where hidden vowels must exist.

The conjecture helps ensure complete vowel coverage but requires careful application as a final-pass rule to avoid false positives during initial pattern matching phases.

## Application Scope

- **Timing**: Final-pass analysis only
- **Purpose**: Hidden vowel position identification
- **Constraint**: Distance < 2 characters (noninclusive)
- **Reference**: Absolute vowel positions as defined in Voraritskul Conjecture

## Related Work

- **Companion Conjecture**: [Voraritskul Conjecture](./voraritskul_conjecture_revised.md)
- **Dependency**: Requires absolute vowel position identification first

---

*A completion rule ensuring systematic vowel coverage in Thai text analysis.*