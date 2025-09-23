#!/usr/bin/env python3
"""
Debug script to examine tone mark handling in Thai analyzer
"""
import json
import sys
import io
from thai_reading_order import ThaiReadingOrderAnalyzer

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_word(word):
    """Analyze a word and print detailed character information"""
    print(f"\n=== Analyzing: {word} ===")

    # Print each character with Unicode info
    print("Character breakdown:")
    for i, char in enumerate(word):
        unicode_val = ord(char)
        unicode_name = f"U+{unicode_val:04X}"
        print(f"  {i}: '{char}' ({unicode_name})")

    # Run analyzer
    analyzer = ThaiReadingOrderAnalyzer(
        'res/foundation/foundation.json',
        'thai_vowels_tagged_9-21-2025-2-31-pm.json'
    )

    result = analyzer.findThaiGraphemeOrderDomain(word)

    print(f"\nFound {len(result.get('readings', []))} interpretations:")

    for i, reading in enumerate(result.get('readings', [])):
        print(f"\nInterpretation {i+1}:")
        for j, syllable in enumerate(reading['syllables']):
            print(f"  Syllable {j+1}:")
            print(f"    Foundation: {syllable['foundation']}")
            print(f"    Foundation type: {type(syllable['foundation'])}")

            if isinstance(syllable['foundation'], dict):
                if 'consonants' in syllable['foundation']:
                    consonants = syllable['foundation']['consonants']
                    print(f"    Consonants list: {consonants}")
                    for k, cons in enumerate(consonants):
                        print(f"      Consonant {k}: '{cons}' (length: {len(cons)})")
                        if len(cons) > 1:
                            print(f"        Multi-char breakdown:")
                            for l, char in enumerate(cons):
                                unicode_val = ord(char)
                                print(f"          {l}: '{char}' (U+{unicode_val:04X})")

            print(f"    Vowel: {syllable['vowel']}")
            print(f"    Final: {syllable['final']}")
            print(f"    Pattern: {syllable['pattern']}")

if __name__ == "__main__":
    # Test words with tone marks
    test_words = [
        "อย่า",  # Has tone mark ่ (U+0E48)
        "ยา",    # Simple word without tone marks
        "ก้อ"    # Another tone mark example
    ]

    for word in test_words:
        try:
            analyze_word(word)
        except Exception as e:
            print(f"Error analyzing {word}: {e}")
            import traceback
            traceback.print_exc()