#!/usr/bin/env python3
"""Runner for Thai reading order algorithm with new data format"""

import sys
import io
from src.thai_reading_order import ThaiReadingOrderAnalyzer

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize the analyzer
analyzer = ThaiReadingOrderAnalyzer(
    "res/foundation/foundation.json",
    "data/thai_vowels_tagged_9-21-2025-2-31-pm.json"
)

# Test cases
thai1 = "ยา"
thai2 = "เด็ก"
thai3 = "คน"
thai4 = "เลว"
thaihard1 = "เกรียน"
thaihard2 = "เอา"
thaihard3 = "อย่า"
thaihard4 = "เอือม"
thaihard5 = "ไกล"

test_cases = [
    thai1,
    thai2,
    thai3,
    thai4,
    thaihard1,
    thaihard2,
    thaihard3,
    thaihard4,
    thaihard5
]

# Run tests and print results with new format
for text in test_cases:
    print(f"\n{text}")
    print("-" * 40)

    result = analyzer.findThaiGraphemeOrderDomain(text)

    if not result['readings']:
        print("No readings found")
    else:
        for i, reading in enumerate(result['readings'], 1):
            if len(result['readings']) > 1:
                print(f"Reading {i}:")

            for syllable in reading['syllables']:
                parts = []

                # Foundation (with tone if present)
                if syllable['foundation']:
                    foundation = syllable['foundation']
                    foundation_str = analyzer.render_foundation(foundation)
                    parts.append(f"foundation={foundation_str}")

                # Vowel
                if syllable['vowel']:
                    parts.append(f"vowel={syllable['vowel']}")

                # Final (with tone if present)
                if syllable['final']:
                    final_str = analyzer.render_foundation(syllable['final'])
                    parts.append(f"final={final_str}")

                # Pattern
                parts.append(f"pattern={syllable['pattern']}")

                print(f"  ({', '.join(parts)})")

            # Show reading order
            print(f"  Reading order: {' '.join(reading['reading_order'])}")

    # Show ambiguity status
    if result['is_ambiguous']:
        print(f"  Status: AMBIGUOUS ({len(result['readings'])} interpretations)")