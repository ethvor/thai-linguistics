# Voraritskul Conjecture for Thai Segmentation
## A Non-ML Approach to Multi-Syllable Thai Word Analysis

### Date: September 26, 2025

---

## Core Insight

Thai orthographic structure, while complex in appearance, follows strict phonological rules that can be exploited for deterministic syllable segmentation. The key observation is that **each syllable contains exactly one vowel pattern**, creating natural segmentation boundaries that can be identified through systematic analysis.

## The Conjecture

**For any Thai text sequence S = s₁s₂s₃...sₙ consisting of syllables, each syllable sᵢ can be deterministically identified by:**

1. Locating all vowel patterns V = {v₁, v₂, v₃, ..., vₖ} in the text
2. Recognizing that each vowel vᵢ belongs to exactly one syllable sᵢ
3. Working bidirectionally from each vowel to establish syllable boundaries
4. Validating boundaries against Thai phonotactic constraints

## Fundamental Syllable Structure

Every Thai syllable **MUST** contain:

### 1. Initial Foundation (Required)
- **Single consonant**: From the set of 44 Thai consonants
- **Consonant cluster**: From a finite set of valid initial clusters (กร, กล, ขร, ขล, คร, คล, etc.)
- **Constraint**: Not all consonants can form clusters
- **Domain**: Explicitly definable set of valid initial formations

### 2. Vowel Pattern (Required)
- **Exactly one** vowel pattern per syllable
- **Position-variable**: Can appear before, after, above, below, or around the initial
- **Pattern constraints**: Some vowels cannot combine with certain initials
- **Critical property**: **No syllable can exist without a vowel pattern**

### 3. Final Foundation (Optional)
- **Single consonant**: From a restricted set of final consonants
- **Consonant cluster**: Rare but possible (e.g., -รถ, -นธ์)
- **Domain**: Smaller than initial consonant domain
- **Constraint**: Many consonants cannot appear in final position

## The Vowel Anchor Principle

**Key Innovation**: Vowels serve as **anchors** for syllable identification.

Given a text sequence:
```
[consonants] [vowel₁] [consonants] [vowel₂] [consonants] [vowel₃]
```

We can deduce:
- Syllable 1 contains vowel₁
- Syllable 2 contains vowel₂
- Syllable 3 contains vowel₃

**Critical insight**: The transition from syllable k to syllable k+1 **must occur** between vowel_k and vowel_k+1.

## Segmentation Algorithm (Enhanced with Two-Vowel Consideration)

### Phase 1: Vowel Identification
```
1. Scan text for all vowel patterns
2. Mark positions: V = [(v₁, pos₁), (v₂, pos₂), ...]
3. Each vowel marks a syllable core
```

### Phase 2: Boundary Determination (Three-Vowel Window Analysis)
For determining syllable n's boundaries, consider vowels n-1, n, and n+1 simultaneously:

```
For vowel vₙ with neighbors vₙ₋₁ and vₙ₊₁:

1. LEFT BOUNDARY (consider vₙ₋₁ and vₙ):
   - If vₙ has pre-positioned characters (เ, แ, โ, ใ, ไ):
     - Syllable n MUST start at the pre-positioned character
     - This provides definitive left boundary for syllable n

2. RIGHT BOUNDARY (consider vₙ and vₙ₊₁):
   - If vₙ₊₁ has pre-positioned characters:
     - Syllable n MUST end before the pre-positioned character
     - This provides definitive right boundary for syllable n

3. EDGE CASES:
   - FIRST SYLLABLE: The first consonant in the text is always the initial consonant
     - No left ambiguity for syllable 1
     - Only need to find right boundary using v₂

   - LAST SYLLABLE: All remaining consonants belong to final syllable
     - No right ambiguity for final syllable
     - Only need to find left boundary using vₙ₋₁

4. Example: "ประเทศไทย"
   - Syllable 1 (ประ): First consonant ป is initial, v₂ starts with เ → ends before เ
   - Syllable 2 (เทศ): Starts at เ (pre-positioned), v₃ starts with ไ → ends before ไ
   - Syllable 3 (ไทย): Starts at ไ (pre-positioned), no v₄ → takes remaining text

5. This three-vowel window provides maximum orthographic constraints,
   using both forward and backward lookahead to disambiguate boundaries
```

### Phase 3: Bidirectional Validation
From each vowel vᵢ:

**Backward scan**:
```
- Identify initial consonant/cluster
- Validate against vowel compatibility rules
- Confirm no overlap with syllable i-1
```

**Forward scan**:
```
- Identify optional final consonant
- Validate against phonotactic rules
- Confirm no overlap with syllable i+1
```

## Advantages Over Pure Pattern Matching

1. **Reduced Search Space**: Instead of testing all possible segmentations, we only test boundaries between vowels

2. **Natural Constraints**: The one-vowel-per-syllable rule eliminates impossible segmentations

3. **Deterministic Anchors**: Vowels provide fixed reference points

4. **Scalable Complexity**: O(n × v × c) where:
   - n = text length
   - v = vowels found
   - c = average consonants between vowels

## Handling Ambiguous Cases

### Case 1: Ambiguous Vowel Characters (อ, ว, ย)
- When these appear between explicit vowels, test both interpretations:
  - As consonant (part of cluster or final)
  - As vowel component
- Validate each interpretation against phonotactic rules

### Case 2: Hidden Vowels
- Some syllables have implicit vowels (e.g., คน has hidden โ-ะ)
- Solution: Treat consonant sequences without explicit vowels as potential syllables
- Validate against known patterns

### Case 3: Overlapping Patterns
- When vowel patterns could theoretically overlap
- Apply precedence rules based on pattern length and frequency

## Implementation Strategy

### Data Requirements
1. **Valid initial consonants/clusters** - Complete enumeration
2. **Valid final consonants** - Complete enumeration
3. **Vowel-initial compatibility matrix** - Which vowels can follow which initials
4. **Pattern precedence rules** - For resolving ambiguities

### Algorithm Flow
```python
def segment_thai_text(text):
    # Phase 1: Find all vowel anchors
    vowel_positions = identify_vowels(text)

    # Phase 2: Establish boundaries
    boundaries = []
    for i in range(len(vowel_positions) - 1):
        boundary = find_optimal_boundary(
            text,
            vowel_positions[i],
            vowel_positions[i+1]
        )
        boundaries.append(boundary)

    # Phase 3: Build syllables
    syllables = []
    for i, vowel in enumerate(vowel_positions):
        syllable = construct_syllable(
            text,
            vowel,
            boundaries[i-1] if i > 0 else 0,
            boundaries[i] if i < len(boundaries) else len(text)
        )
        syllables.append(syllable)

    return syllables
```

## Validation Through Examples

### Example 1: "ประเทศไทย" (Thailand)
- Vowels identified: ระ, เ◌ศ, ไ◌ย
- Syllable 1: ประ (pr-a)
- Syllable 2: เทศ (tʰêːt)
- Syllable 3: ไทย (tʰāj)
- Boundaries naturally fall between vowel patterns

### Example 2: "สวัสดีครับ" (Hello)
- Vowels identified: ◌ั, ◌ี, ◌ั
- Syllable 1: สวัส (sà-wàt)
- Syllable 2: ดี (dīː)
- Syllable 3: ครับ (kʰráp)
- Final consonants validated against rules

## Theoretical Advantages

1. **No Training Required**: Pure rule-based approach
2. **Explainable Results**: Every decision traceable to linguistic rules
3. **Language Preservation**: Respects Thai orthographic principles
4. **Extensible**: New patterns can be added without retraining

## Practical Considerations

### Challenges
1. **Compound words**: May need morphological analysis
2. **Foreign loanwords**: May violate standard patterns
3. **Abbreviations**: Often omit vowels entirely
4. **Sacred/Royal language**: Uses archaic patterns

### Solutions
1. **Exception dictionary**: For known irregular words
2. **Fallback patterns**: For unmatched sequences
3. **Confidence scoring**: Rate segmentation quality
4. **User validation**: Allow manual correction

## The Two-Character Proximity Conjecture
*Also known as: The Vowel Proximity Conjecture*

### Statement
**"For any consonant c in Thai text, a vowel component (explicit or hidden) exists within a distance of at most 2 characters (inclusive)."**

### Corollary
If no explicit vowel mark is found within 2 characters of a consonant, a hidden vowel MUST be present at that location.

### Implications
1. **Hidden Vowel Detection**: Consonants isolated from vowel marks (distance > 2) definitively indicate hidden vowels
2. **Search Space Reduction**: Pattern matching needs only examine a 5-character window (position ± 2)
3. **Systematic Coverage**: Every consonant in Thai text belongs to exactly one vowel pattern, either explicit or hidden

### Examples
- **Explicit**: "ประเทศ" - Every consonant has a vowel mark within 2 positions
- **Hidden**: "คน" → ค[โ-ะ]น - No vowel marks, therefore hidden vowel after ค
- **Mixed**: "สตรี" → ส[ะ]ตรี - ส is >2 from ี, therefore hidden ะ after ส

## Conclusion

The Voraritskul Conjecture, enhanced by the Two-Character Proximity Conjecture, presents a deterministic, linguistically-grounded approach to Thai syllable segmentation. By recognizing that **vowels are mandatory syllable components** and using them as anchors, combined with the proximity rule for detecting hidden vowels, we can achieve complete vowel coverage and dramatically reduce the complexity of multi-syllable segmentation while maintaining high accuracy.

This approach:
- Leverages Thai phonological structure
- Avoids the black-box nature of ML models
- Provides explainable, reproducible results
- Scales linearly with text length (not exponentially)

The conjecture awaits formal implementation and validation against large Thai corpora, but initial analysis suggests it could provide a robust foundation for Thai NLP applications without requiring machine learning infrastructure.

---

*"The structure is in the language; we need only observe it carefully."*
*- Voraritskul Conjecture, 2025*