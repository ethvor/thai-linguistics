# Initial Foundation Terminal Conjecture (IFTC)

## Statement
If any consonant `c` has any tone mark, then `c` is the last character in an initial foundation for that syllable.

## Explanation
A consonant bearing a tone mark signals the boundary/terminus of the syllable's initial consonant cluster. This can be used to identify syllable boundaries in Thai text.

## Examples

### Positive Examples (Conjecture Holds)
- **`ปร้าว`** → `ร` has tone mark `้` → `ร` is the last consonant in the initial foundation `ปร`
- **`กล่าว`** → `ล` has tone mark `่` → `ล` is the last consonant in the initial foundation `กล`
- **`ครั่ง`** → `ร` has tone mark `่` → `ร` is the last consonant in the initial foundation `คร`

### Negative Examples (Consonant Without Tone Mark)
- **`ประเทศ`** → `ป` has no tone mark → `ป` is not the last in cluster (cluster is `ปร`)
- **`กรุง`** → `ก` has no tone mark → `ก` is not the last in cluster (cluster is `กร`)

## Applications
- **Syllable boundary detection**: Identify where initial consonant clusters end
- **Text segmentation**: Use tone marks as markers for syllable structure
- **Reading order analysis**: Determine foundation container boundaries

## Related Concepts
- Foundation consonants (ฐาน/tan)
- Tone marks (่ ้ ๊ ๋)
- Syllable structure in Thai
- Initial consonant clusters

## Status
**Conjecture** - Needs empirical validation across Thai corpus

## Investigation: Possible Extension

### Proposed Extension
A possible extension to IFTC is under investigation:

**Extended IFTC:** "If any consonant `c` has a vowel part OR tone mark (yuk), then `c` is a terminal initial-foundation consonant."

### Rationale
Vowel parts may serve the same boundary-marking function as tone marks. This would provide a more comprehensive rule for syllable boundary detection.

### Investigation Status
- **Documentation:** See [Extended IFTC Investigation](./extended_iftc_investigation.md)
- **Test Script:** `projects/highlight_algorithm/tests/test_extended_iftc.py`
- **Status:** Investigation pending

### Next Steps
1. Run test script on diverse Thai corpus
2. Manually verify consonants with vowel parts
3. Look for counterexamples
4. Document findings in extended_iftc_investigation.md
5. Update conjecture if evidence supports extension

## Date Added
2025-10-03

## Last Updated
2025-10-03
