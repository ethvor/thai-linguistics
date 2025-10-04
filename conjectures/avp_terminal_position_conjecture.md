# AVP Terminal Position Conjecture

## Statement
**Absolute Vowel Positions (AVPs) are ALWAYS directly after terminal initial-foundation consonants.**

## Formal Definition
For any Thai syllable S with initial foundation F and Absolute Vowel Position V:
- If F consists of consonant(s) c₁, c₂, ..., cₙ where n ≤ 2
- And cₙ is the terminal (last) consonant in F
- Then V occurs immediately after cₙ in the phonetic realization

## Explanation
This conjecture establishes a deterministic relationship between terminal initial-foundation consonants and AVP locations. The AVP - the position where the vowel is phonetically realized - always follows the last consonant of the initial foundation, whether that foundation is:
1. A single consonant
2. A two-consonant cluster

This provides a reliable anchor point for vowel pattern detection and syllable segmentation.

## Examples

### Single Consonant Foundation
- **มา** (ma):
  - Initial foundation: ม (single consonant, terminal by default)
  - AVP: directly after ม
  - Vowel pattern: xา

### Two-Consonant Cluster Foundation
- **ครู** (khru):
  - Initial foundation: คร (cluster)
  - Terminal consonant: ร
  - AVP: directly after ร
  - Vowel pattern: xู (where x represents the คร cluster)

### Left-Anchored Vowel
- **เมือง** (mueang):
  - Initial foundation: ม (terminal)
  - AVP: directly after ม (even though เ appears before)
  - Vowel pattern: เxือ

## Implications

### For Extended IFTC
- Consonants marked as 'x' (with tone marks or vowels) are guaranteed terminal positions
- AVP is always immediately after these 'x' markers
- Provides validation for Extended IFTC marking

### For Unmarked Terminals
- Not all terminal consonants have tone marks or vowel attachments
- These unmarked terminals still have AVP directly after
- Algorithm must identify these through other means (cluster analysis, vowel proximity)

### For Pattern Matching
- Once terminal is identified, AVP location is deterministic
- Simplifies vowel pattern boundary detection
- Enables accurate syllable segmentation

## Relationship to Other Conjectures

### With Extended IFTC
Extended IFTC identifies SOME terminal positions (those with markers). This conjecture states that ALL terminals (marked or unmarked) have AVP directly after.

### With Absolute Vowel Position Conjecture
The original AVP conjecture states each syllable has exactly one AVP. This conjecture specifies WHERE that AVP is located relative to the foundation.

### With Proximity Conjecture
The two-character proximity rule helps find unmarked terminals by locating consonants that must have nearby AVPs.

## Foundation Clarifications

### Initial Foundation Types
1. **Single consonant**: The consonant IS the terminal
2. **Two-consonant cluster**: The second consonant is terminal
3. **No three-consonant clusters exist in Thai**

### Marked vs Unmarked Terminals
- **Marked**: Has tone mark (yuk) OR vowel part (sara) → becomes 'x' in intermediate
- **Unmarked**: No markers → remains 'a' in intermediate, but still terminal if no following cluster member

## Algorithm Applications

### Finding Unmarked Terminals
```
For each 'a' in intermediate form:
  1. Check if next character can cluster with it
  2. If no valid cluster → 'a' is terminal
  3. AVP is directly after this 'a'
```

### Validating Vowel Patterns
```
For each identified terminal position:
  1. AVP is immediately after
  2. Vowel pattern components surround this position
  3. Pattern boundaries cannot cross AVP points
```

## Status
**Discovered**: 2025-10-04
**Status**: New conjecture requiring validation
**Evidence**: Derived from Extended IFTC and Thai phonetic structure

## Testing Required
1. Verify across Thai corpus that AVP always follows terminal
2. Test with various cluster types
3. Validate with unmarked terminal positions
4. Check edge cases (loan words, compounds)

## Related Documents
- [Extended IFTC Investigation](./extended_iftc_investigation.md)
- [Absolute Vowel Position Conjecture](./absolute_vowel_position_conjecture.md)
- [Proximity Conjecture](./proximity_conjecture.md)

---

*A fundamental insight linking foundation structure to vowel realization in Thai phonetics.*