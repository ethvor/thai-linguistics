# Immediate Next Steps

## 1. Add 5th Class for Non-Tone-Mark Diacritics
**Goal:** Split the `yuk` class into two classes:
- **`yuk`** (tone marks only): `่ ้ ๊ ๋`
- **New class** (diacritics): `์ ็ ํ`

**Rationale:** Tone marks have different linguistic function than other diacritics. Separating them enables more precise analysis.

**Implementation:**
- Update `src/server.py` classification logic
- Add new CSS class and glow color
- Add toggle checkbox in HTML
- Update legend

---

## 2. Investigate Extended Terminal Initial-Foundation Conjecture
**Current IFTC:** "If any consonant c has any tone mark, then c is the last character in an initial foundation for that syllable."

**Proposed Extension:** "If any consonant c has a vowel part OR tone mark (yuk), then c is a terminal initial-foundation consonant."

**Investigation Tasks:**
- [ ] Collect examples where consonants have vowel parts attached
- [ ] Test if these consonants are always terminal in their cluster
- [ ] Look for counterexamples
- [ ] Document findings in `conjectures/` directory
- [ ] Update IFTC if evidence supports extension

**Why:** Vowel parts may serve same boundary-marking function as tone marks.

---

## 3. Vowel Pattern Identification Algorithm
**Goal:** Use intermediate step classifications to identify complete vowel patterns from our tagged vowel database.

**Test Text:** เมืองเชียงใหม่เรียนรู้เกี่ยวกับครูแชมป์
- Complex example with all character classes
- Multiple vowel patterns to identify

**Algorithm Approach:**
- Start with intermediate classifications (tan → a/x, yuk removed, sara preserved)
- Match sara sequences against known vowel patterns from `thai_vowels_tagged_9-21-2025-2-31-pm.json`
- Use position information (left/right/above/below) to identify pattern structure
- Handle multi-part vowels (e.g., เ...า, ไ, ใ)

**Data Structure Needed:**
- Groups with base character and attached sara
- Left/right context for each character
- Access to vowel pattern database

**Success Criteria:**
- Correctly identify all vowel patterns in test text
- Generate intermediate step output showing pattern boundaries
- Validate against known Thai syllable structure

---

## Notes
- These steps build on the classification work completed in the highlight algorithm
- Step 1 is prerequisite for accurate Step 2 investigation
- Step 3 is the major algorithmic challenge - vowel pattern matching
- Later, we will use step 3 to identify AVPs for each pattern identified - multiple interpretations could be troublesome though.
- After that, we can use the AVPs to segment the string into syllables
