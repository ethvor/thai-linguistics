# Thai Linguistics Reference Document

**Created:** 2025-10-04
**Purpose:** Permanent reference for Thai linguistic definitions and rules established in this project

---

## Core Linguistic Units

### Consonants vs Foundations

#### Consonant
- **Definition**: A single Thai letter from the 44 consonant characters
- **Example**: ค, ร, ม, ง (individual letters)
- **Symbol in patterns**: Not directly represented

#### Foundation (ฐาน)
- **Definition**: A linguistic unit of 1 or 2 consonants that serves as a base for vowel attachment
- **Types**:
  1. **Single consonant foundation**: One consonant (e.g., ม in มา)
  2. **Clustered foundation**: Two consonants forming a cluster (e.g., คร in ครู)
- **Symbol in patterns**:
  - `x` = placeholder for entire foundation (1 or 2 consonants)
  - `f` = placeholder for final foundation (1 or 2 consonants)
- **Key Rule**: Thai clusters have a MAXIMUM of 2 consonants (no 3-consonant clusters)

### Foundation Types by Position

#### Initial Foundation
- **Definition**: The foundation that begins a syllable
- **Occurrence**: ALWAYS present in every syllable
- **Composition**: 1 or 2 consonants (single or cluster)
- **Clusters**: Almost always appear here (rarely in final)
- **Examples**:
  - Single: ม in มา
  - Cluster: คร in ครู, กล in กลาง

#### Final Foundation
- **Definition**: The foundation that ends a syllable
- **Occurrence**: OPTIONAL (open syllables have no final foundation)
- **Composition**: 1 or 2 consonants
- **Clusters**: Rarely appear here (different valid cluster list than initial)
- **Examples**:
  - Single: ง in มาง
  - Absent: มา (open syllable)

---

## Terminal Positions and Markers

### Terminal Initial-Foundation Consonant
- **Definition**: The LAST consonant in an initial foundation
- **In single consonant**: The consonant itself is terminal
- **In cluster**: The second consonant is terminal
- **Significance**: Marks the boundary of the initial foundation

### Extended IFTC Marking (✅ Confirmed)
- **Rule**: If a consonant has a vowel part (sara) OR tone mark (yuk), it is terminal
- **Intermediate representation**:
  - `x` = terminal consonant (has vowel part OR tone mark)
  - `a` = ambiguous position consonant (no markers)
- **CRITICAL**: Not all terminal consonants are marked!
  - Many initial foundations have neither tone marks nor vowel attachments
  - These unmarked terminals remain as 'a' in intermediate form

### Absolute Vowel Position (AVP)
- **Definition**: The position where the vowel is phonetically realized
- **Location Rule**: ALWAYS directly after the terminal initial-foundation consonant
- **Significance**: Deterministic anchor point for vowel pattern detection

---

## Intermediate Form Transformation Rules

### Character Transformations

1. **Tone marks (yuk: ่ ้ ๊ ๋)**: REMOVED entirely
2. **Diacritics (์ ็ ํ)**: REMOVED entirely
3. **Vowels (sara)**: PRESERVED as-is
4. **Consonants with markers** → `x` (terminal)
5. **Consonants without markers** → `a` (ambiguous)
6. **Exception characters (อ ว ย)**: Preserved or marked based on context

### Reading the Intermediate Form

#### 'x' Marker
- **Represents**: Terminal initial-foundation consonant
- **Could be**:
  - Single consonant with vowel/tone mark
  - Second consonant in cluster with vowel/tone mark
- **Guarantees**: This position ends an initial foundation
- **AVP location**: Immediately after this position

#### 'a' Marker
- **Represents**: Ambiguous position consonant
- **Could be**:
  - First consonant in a cluster (if followed by another 'a' or 'x')
  - Unmarked terminal consonant
  - Final consonant of previous syllable
  - Initial consonant of next syllable
- **Resolution**: Requires cluster analysis and context

#### Vowel Characters (sara)
- **Preserved**: Exactly as in original text
- **Position types**:
  - Before base (left vowels): เ แ โ ไ ใ
  - After base (right vowels): า ี ื ู ะ ั
  - Above/below base (combining): ิ ุ ึ etc.

---

## Clustering Rules

### Initial Clusters
- **Maximum size**: 2 consonants
- **Common patterns**: คร, กร, ปร, ตร, กล, ปล, คล, etc.
- **Position**: Almost always in initial foundation
- **In intermediate**: Can appear as `aa`, `ax`, or `xa` patterns
- **Validation**: Must check against valid initial cluster list

### Final Clusters
- **Maximum size**: 2 consonants
- **Occurrence**: Rare
- **Valid patterns**: Different list from initial clusters
- **Position**: Only in final foundation
- **Validation**: Must check against valid final cluster list

### Cluster Detection in Intermediate Form
```
Pattern → Interpretation
aa     → Could be cluster (check validity)
ax     → 'a' clusters with 'x' if valid cluster
xa     → Not a cluster ('x' is terminal, can't cluster forward)
xx     → IMPOSSIBLE (terminals don't cluster)
```

---

## Vowel Pattern Structure

### Pattern Notation in Database

#### Base Placeholder
- **`x`**: Represents the entire initial foundation (1-2 consonants)
- **Never `a`**: Database uses only 'x' as placeholder
- **Position**: Where the actual foundation consonants go

#### Final Placeholder
- **`f`**: Represents the final foundation (if present)
- **Optional**: Not all patterns have final consonants

### Pattern Types by Structure

1. **Right-anchored**: `xา`, `xี`, `xู`
   - Vowel components after foundation

2. **Left-anchored**: `เx`, `แx`, `โx`
   - Vowel components before foundation

3. **Split/Wrap-around**: `เxา`, `เxีย`, `เxือ`
   - Vowel components both before and after foundation

4. **With finals**: `xาf`, `xีf`, `xอf`
   - Includes final consonant position

---

## Syllable Structure Rules

### Mandatory Components
1. **Initial foundation**: Always present (1-2 consonants)
2. **Vowel pattern**: Always present (may be implicit)
3. **AVP**: Exactly one per syllable

### Optional Components
1. **Final foundation**: May be absent (open syllable)
2. **Tone marks**: Not all syllables have tones
3. **Diacritics**: Special marks, not always present

### Syllable Types
- **Open**: No final consonant (e.g., มา, ที)
- **Closed**: Has final consonant (e.g., มาก, ทาง)
- **Clustered initial**: Initial foundation is cluster (e.g., คราว, กลาง)

---

## Algorithm Implications

### Finding Unmarked Terminals
Since not all terminal positions have markers:
1. Use cluster validity checking
2. Apply proximity conjecture
3. Look for vowel patterns that require terminals
4. Process of elimination with 'a' sequences

### Vowel Pattern Matching
1. Identify all 'x' positions (guaranteed terminals)
2. Find unmarked terminals among 'a' positions
3. Match patterns using foundation positions, not individual consonants
4. Validate against pattern database

### Critical Constraints
1. **One AVP per syllable** (original AVP conjecture)
2. **AVP directly after terminal** (new AVP Terminal Position conjecture)
3. **Maximum 2-consonant clusters**
4. **Vowel patterns are atomic** (don't split across syllables)
5. **Database uses 'x' for foundation placeholder**

---

## Examples with Full Analysis

### ครู (teacher)
- **Original**: ค + ร + ู
- **Foundation**: คร (valid initial cluster)
- **Terminal**: ร (second in cluster, has ู attached)
- **Intermediate**: `axู` or just `xู` if ร is marked
- **Pattern**: `xู` where x = คร foundation
- **AVP**: After ร

### เมือง (city)
- **Original**: เ + ม + ื + อ + ง
- **Foundation**: ม (single consonant)
- **Terminal**: ม (has เ attached)
- **Intermediate**: `เxือa`
- **Pattern**: `เxือ` where x = ม
- **Final**: ง (the final 'a')
- **AVP**: After ม

### กลาง (middle)
- **Original**: ก + ล + า + ง
- **Foundation**: กล (valid initial cluster)
- **Terminal**: ล (second in cluster)
- **Intermediate**: Would depend on whether ล has markers
- **Pattern**: `xาf` where x = กล, f = ง
- **AVP**: After ล

---

## Future Additions Needed

1. **Complete list of valid initial clusters**
2. **Complete list of valid final clusters**
3. **Algorithm for detecting unmarked terminals**
4. **Handling of exception characters (อ ว ย) in various contexts**
5. **Special rules for loan words and compounds**

---

*This document serves as the authoritative reference for Thai linguistic terminology and rules in this project.*