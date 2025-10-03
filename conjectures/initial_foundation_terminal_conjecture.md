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

## Date Added
2025-10-03
