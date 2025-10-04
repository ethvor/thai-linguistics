# Initial Foundation Terminal Conjecture (IFTC)

## Extended Statement (✅ Confirmed 2025-10-03)
**If any consonant `c` has a vowel part OR tone mark (yuk), then `c` is a terminal initial-foundation consonant.**

## Original Statement
If any consonant `c` has any tone mark, then `c` is the last character in an initial foundation for that syllable.

## Explanation
A consonant bearing a vowel part or tone mark signals the boundary/terminus of the syllable's initial consonant cluster. This can be used to identify syllable boundaries in Thai text.

The **Extended IFTC** has been empirically validated and is now the primary form of this conjecture. The original formulation (tone marks only) is a subset of the extended version.

## Examples

### Extended IFTC Examples (Vowel Parts OR Tone Marks)

#### Tone Mark Examples (Original IFTC)
- **`ปร้าว`** → `ร` has tone mark `้` → `ร` is terminal in initial foundation `ปร`
- **`กล่าว`** → `ล` has tone mark `่` → `ล` is terminal in initial foundation `กล`
- **`ครั่ง`** → `ร` has tone mark `่` → `ร` is terminal in initial foundation `คร`

#### Vowel Part Examples (Extended IFTC)
- **`ครู`** → `ร` has vowel part `ู` below → `ร` is terminal in initial foundation `คร`
- **`เมือง`** → `ม` has vowel part `เ` to its left → `ม` is terminal
- **`เชียง`** → `ช` has vowel part `เ` to its left → `ช` is terminal

### Negative Examples (No Markers)
- **`ประเทศ`** → `ป` has no vowel part or tone mark → `ป` is not terminal (cluster is `ปร`)
- **`กรุง`** → `ก` has no vowel part or tone mark → `ก` is not terminal (cluster is `กร`)

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
**✅ CONFIRMED** - Extended IFTC empirically validated (2025-10-03)

### Confirmation Details
- **Original IFTC**: Confirmed as valid (tone marks only)
- **Extended IFTC**: Confirmed as valid (vowel parts OR tone marks)
- **Current Standard**: Extended IFTC is the primary formulation
- **Exception Count**: One small exception class (disregarded for algorithmic purposes)

## Investigation: Extended IFTC

### Extended IFTC (✅ Confirmed)
**Extended IFTC:** "If any consonant `c` has a vowel part OR tone mark (yuk), then `c` is a terminal initial-foundation consonant."

### Rationale
Vowel parts serve the same boundary-marking function as tone marks. This provides a more comprehensive rule for syllable boundary detection.

### Investigation Results
- **Documentation:** See [Extended IFTC Investigation](./extended_iftc_investigation.md)
- **Status:** ✅ Confirmed through empirical testing
- **Implementation**: Being updated in `projects/highlight_algorithm/src/renderer.py`

### Impact
The Extended IFTC significantly improves:
1. Syllable boundary detection accuracy
2. Foundation container identification
3. Vowel pattern matching reliability
4. Text segmentation for Thai linguistic analysis

## Date Added
2025-10-03

## Date Confirmed
2025-10-03

## Last Updated
2025-10-03 - Extended IFTC confirmed and promoted to primary status
