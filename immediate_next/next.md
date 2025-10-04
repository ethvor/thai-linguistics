# Immediate Next Steps

## Core Algorithm Approach
**Foundation Insight:** Terminal initial-foundation consonants → AVP positions → Vowel pattern interpretation

Our algorithm must follow this sequence:
1. **Identify ALL terminal initial-foundation consonants** (both marked 'x' and unmarked 'a')
2. **Locate AVPs** (always directly after terminals - new conjecture)
3. **Interpret vowel patterns** using AVP as anchor point

---

## Phase 1: Terminal Detection Infrastructure

### 1.1 Compile Thai Cluster Lists
**Goal:** Create definitive lists for cluster validation

**Initial Clusters (2-consonant max):**
- Common: คร, กร, ปร, ตร, กล, ปล, คล, ขล
- With ว: กว, คว, ขว, ทว
- Need: Complete exhaustive list from linguistic resources

**Final Clusters (different valid set):**
- Need: Research and compile valid final clusters
- Note: Rare but important for disambiguation

**Implementation:**
- Create JSON files in `res/clusters/`
- Include frequency data if available
- Build validation functions

---

### 1.2 Design Comprehensive Terminal Detection Algorithm
**Goal:** Find ALL terminal positions, not just marked ones

**Algorithm Components:**
```python
def find_all_terminals(intermediate_text):
    terminals = []

    # Step 1: Mark all 'x' positions (Extended IFTC)
    # These are guaranteed terminals

    # Step 2: Find unmarked terminals among 'a' positions
    for each 'a':
        if next_char cannot_cluster_with(a):
            mark a as terminal
        elif no_vowel_within_proximity(a):
            check if a could be terminal

    # Step 3: Validate using pattern constraints
    # Every syllable must have exactly one terminal

    return terminals
```

**Key Challenges:**
- Disambiguating `aa` sequences
- Identifying syllable boundaries without markers
- Handling exception characters (อ ว ย)

---

## Phase 2: AVP-Based Pattern Detection

### 2.1 AVP Localization
**Goal:** Mark all AVP positions using terminal positions

**Implementation:**
```python
def locate_avps(text, terminals):
    avps = []
    for terminal_pos in terminals:
        avp_pos = terminal_pos + 1  # Always directly after
        avps.append(avp_pos)
    return avps
```

**Validation:**
- Every syllable has exactly one AVP
- AVPs cannot be inside clusters
- AVPs align with vowel patterns

---

### 2.2 Foundation Grouping Algorithm
**Goal:** Group consonants into foundations based on terminals

**Process:**
1. For each terminal position:
   - Look backward for cluster members
   - If valid cluster found: group as 2-consonant foundation
   - Else: single-consonant foundation
2. Mark foundation boundaries
3. Assign foundation IDs for pattern matching

**Example:**
```
Text: ครู
Intermediate: axู
Terminal: position 1 (x)
Look back: 'a' at position 0
Check: คร is valid cluster
Result: Foundation = คร (positions 0-1)
```

---

### 2.3 Foundation-Based Pattern Matching
**Goal:** Match vowel patterns using foundations as units

**Key Innovation:**
- Pattern database uses 'x' for foundation placeholder
- Our foundations (1-2 consonants) map directly to 'x'
- Exact matching becomes possible

**Algorithm:**
```python
def match_vowel_patterns(text, foundations, avps):
    patterns = []

    for foundation in foundations:
        # Get vowel components around foundation
        left_vowels = get_left_vowels(foundation)
        right_vowels = get_right_vowels(foundation)

        # Build pattern string
        pattern_key = build_pattern_key(left_vowels, 'x', right_vowels)

        # Direct database lookup
        match = database.get_pattern(pattern_key)
        if match:
            patterns.append({
                'foundation': foundation,
                'pattern': pattern_key,
                'avp': avps[foundation.id],
                'match_data': match
            })

    return patterns
```

---

## Phase 3: Complex Cases and Validation

### 3.1 Exception Character Handling
**Characters:** อ ว ย (can be consonants OR vowel parts)

**Context Rules:**
- As initial consonant: อาหาร (อ is consonant)
- As vowel part: เมือง (อ is part of เ-ือ pattern)
- As final consonant: ชาว (ว is final)
- As vowel part: แมว (ว is part of แ-ว pattern)

**Resolution Strategy:**
- Check pattern database first
- Use positional heuristics
- Apply frequency-based disambiguation

---

### 3.2 Test Suite Development
**Test Text:** เมืองเชียงใหม่เรียนรู้เกี่ยวกับครูแชมป์

**Expected Outputs:**
```
Intermediate: เxือaเxียaใaxเxียaxูเxียวxัaaxูแaaa

Terminals: [positions of all x's + unmarked terminals]
AVPs: [positions directly after each terminal]
Foundations: [grouped consonants with boundaries]
Patterns: [matched vowel patterns with confidence scores]
```

**Validation Criteria:**
- All syllables have exactly one AVP
- All vowel patterns match database entries
- No overlapping patterns
- Complete text coverage

---

## Implementation Priority

### Week 1: Terminal Detection
1. Compile cluster lists
2. Implement unmarked terminal detection
3. Validate on test corpus

### Week 2: AVP and Foundation
1. Implement AVP localization
2. Build foundation grouping
3. Test cluster validation

### Week 3: Pattern Matching
1. Adapt pattern matcher for foundations
2. Handle exception characters
3. Complete test suite

### Week 4: Refinement
1. Edge case handling
2. Performance optimization
3. Documentation

---

## Success Metrics

1. **Terminal Detection Accuracy:** >95% of all terminals identified
2. **AVP Localization:** 100% correct (deterministic from terminals)
3. **Pattern Matching:** >90% of patterns correctly identified
4. **Syllable Segmentation:** >85% correct boundaries

---

## Key Insights to Remember

1. **'x' represents foundations (1-2 consonants), not single consonants**
2. **Not all terminals are marked - many remain as 'a'**
3. **AVPs are ALWAYS directly after terminal initial-foundation consonants**
4. **Pattern database 'x' aligns with our foundation concept**
5. **Clusters have 2-consonant maximum in Thai**

---

## Dependencies

- `docs/thai_linguistics_reference.md` - Authoritative definitions
- `conjectures/avp_terminal_position_conjecture.md` - New AVP rule
- `conjectures/extended_iftc_investigation.md` - Confirmed marking rules
- `data/thai_vowels_tagged_9-21-2025-2-31-pm.json` - Pattern database
- (Needed) `res/clusters/initial_clusters.json` - Valid initial clusters
- (Needed) `res/clusters/final_clusters.json` - Valid final clusters