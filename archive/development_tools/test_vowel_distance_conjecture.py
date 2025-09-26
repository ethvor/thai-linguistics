#!/usr/bin/env python3
"""
Test the conjecture: For any consonant c in a Thai string,
some vowel part p is AT MOST 2 characters away (inclusive).
"""

import sys
import io

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Character sets
CONSONANTS = {
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
    'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
    'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
    'ส', 'ห', 'ฬ', 'อ', 'ฮ'
}

VOWEL_MARKS = {
    'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู',
    'เ', 'แ', 'โ', 'ใ', 'ไ', '็', '์'  # Including ์ (cancellation mark) as it's vowel-related
}

TONE_MARKS = {'่', '้', '๊', '๋'}

def find_nearest_vowel_distance(text, pos):
    """Find distance to nearest vowel mark from position pos"""
    min_distance = float('inf')

    # Check characters before and after
    for i in range(len(text)):
        if text[i] in VOWEL_MARKS:
            distance = abs(i - pos)
            min_distance = min(min_distance, distance)
            if min_distance == 0:  # Adjacent vowel found
                break

    return min_distance

def test_conjecture(text):
    """Test if every consonant has a vowel within 2 characters"""
    violations = []
    consonant_distances = []

    for i, char in enumerate(text):
        if char in CONSONANTS:
            distance = find_nearest_vowel_distance(text, i)
            consonant_distances.append((i, char, distance))

            if distance > 2:
                violations.append((i, char, distance))

    return consonant_distances, violations

def analyze_text(text, name=""):
    """Analyze a text for the conjecture"""
    print(f"\nAnalyzing: {name}")
    print(f"Text: '{text}'")
    print("-" * 50)

    # Show character breakdown
    print("Character breakdown:")
    for i, char in enumerate(text):
        char_type = "?"
        if char in CONSONANTS:
            char_type = "C"
        elif char in VOWEL_MARKS:
            char_type = "V"
        elif char in TONE_MARKS:
            char_type = "T"
        print(f"  [{i}] {char} : {char_type}")

    # Test conjecture
    consonant_distances, violations = test_conjecture(text)

    print(f"\nConsonant → Nearest Vowel distances:")
    for pos, consonant, distance in consonant_distances:
        status = "✓" if distance <= 2 else "✗"
        print(f"  [{pos}] {consonant} → distance {distance} {status}")

    if violations:
        print(f"\nCONJECTURE VIOLATED! {len(violations)} violations found:")
        for pos, consonant, distance in violations:
            print(f"  Position {pos}: '{consonant}' has nearest vowel at distance {distance}")
    else:
        print(f"\nCONJECTURE HOLDS! All {len(consonant_distances)} consonants have vowels within distance 2")

    return len(violations) == 0

def main():
    """Test the conjecture on various Thai texts"""

    test_cases = [
        ("ยา", "Simple CV"),
        ("เด็ก", "Pre-positioned vowel"),
        ("คน", "Hidden vowel word"),
        ("ประเทศไทย", "Country name"),
        ("สวัสดี", "Greeting"),
        ("กรม", "Consonant cluster with hidden vowel"),
        ("สตรี", "Cluster str-"),
        ("ครับ", "Polite particle"),
        ("ความ", "khwaam (abstract noun prefix)"),
        ("พระ", "Honorific prefix"),
        ("กรรม", "Word with rrm cluster"),
        ("สามารถ", "Can/able"),
        ("ธรรม", "Dharma"),
        ("จักรวาล", "Universe"),
    ]

    print("=" * 70)
    print("TESTING VOWEL DISTANCE CONJECTURE")
    print("Conjecture: Every consonant has a vowel mark within 2 characters")
    print("=" * 70)

    results = []
    for text, description in test_cases:
        holds = analyze_text(text, description)
        results.append((text, description, holds))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, _, holds in results if holds)
    total = len(results)

    print(f"Conjecture held for {passed}/{total} test cases")

    if passed < total:
        print("\nViolating cases:")
        for text, desc, holds in results:
            if not holds:
                print(f"  - {text} ({desc})")

    # Additional analysis
    print("\n" + "-" * 50)
    print("OBSERVATION:")
    print("Words with hidden vowels (like คน, กรม) may violate the conjecture")
    print("because they have no explicit vowel marks. The conjecture seems to")
    print("apply specifically to words with explicit vowel marks.")

if __name__ == "__main__":
    main()