#!/usr/bin/env python3
"""
Example usage of vowel display methods for Jupyter notebooks
Copy these examples into notebook cells to see rich visualizations
"""

from conjecture_based_vowel_detector import ConjectureBasedVowelDetector, analyze_text, compare_texts, vowel_stats, display_vowel_grid

# Example 1: Basic analysis with rich display
def example_basic_analysis():
    """Example: Analyze a single word with detailed display"""
    text = "ประเทศไทย"
    vowels = analyze_text(text)
    return vowels

# Example 2: Individual vowel exploration
def example_individual_vowel(text="คน"):
    """Example: Explore individual vowel with all display options"""
    detector = ConjectureBasedVowelDetector("thai_vowels_tagged_9-21-2025-2-31-pm.json")
    vowels = detector.find_vowels(text)

    print(f"📝 Text: '{text}'")
    print(f"📊 Vowels found: {len(vowels)}")
    print("=" * 50)

    for i in sorted(vowels.keys()):
        v_data = vowels[i]

        # Different display methods
        print(f"\n🎯 METHOD 1 - Simple string representation:")
        print(f"   {v_data}")

        print(f"\n🎯 METHOD 2 - Detailed display:")
        v_data.display(text)

        print(f"\n🎯 METHOD 3 - Best candidate details:")
        v_data.best_candidate.display(text)

        # In Jupyter, this would show rich HTML:
        # v_data  # Just display the object directly

    return vowels

# Example 3: Compare multiple words
def example_comparison():
    """Example: Compare vowel patterns across words"""
    test_texts = ["คน", "ประเทศไทย", "สตรี", "กรม", "เด็ก"]
    results = compare_texts(test_texts)

    # Show statistics for each
    print("\n📊 DETAILED STATS PER TEXT:")
    print("=" * 50)

    for text, vowels in results:
        print(f"\n📝 '{text}':")
        vowel_stats(vowels)
        display_vowel_grid(vowels, text)

    return results

# Example 4: Pattern analysis
def example_pattern_analysis():
    """Example: Analyze patterns across different word types"""
    # Hidden vowel examples
    hidden_examples = ["คน", "สตรี", "กรม", "จริง", "ครบ"]

    # Complex vowel examples
    complex_examples = ["เด็ก", "เลว", "ไก่", "เกาะ", "เลือก"]

    print("🔍 HIDDEN VOWEL ANALYSIS")
    print("=" * 50)
    hidden_results = compare_texts(hidden_examples)

    print("\n\n🔍 COMPLEX VOWEL ANALYSIS")
    print("=" * 50)
    complex_results = compare_texts(complex_examples)

    return hidden_results, complex_results

# Jupyter notebook cells - copy these into separate cells:

notebook_cell_1 = '''
# Cell 1: Basic analysis with rich HTML display
from conjecture_based_vowel_detector import *

text = "ประเทศไทย"
vowels = analyze_text(text)

# Rich display in Jupyter (just execute the vowel object)
vowels[1]  # Shows first vowel with colors and formatting
'''

notebook_cell_2 = '''
# Cell 2: Compare different texts
texts = ["คน", "สตรี", "กรม", "เด็ก", "ไก่"]
results = compare_texts(texts)

# Show detailed stats
for text, vowels in results:
    print(f"\\n📝 Analysis of '{text}':")
    vowel_stats(vowels)
    print()
    display_vowel_grid(vowels, text)
    print("="*60)
'''

notebook_cell_3 = '''
# Cell 3: Interactive exploration
text = input("Enter Thai text to analyze: ")
detector = ConjectureBasedVowelDetector("thai_vowels_tagged_9-21-2025-2-31-pm.json")
vowels = detector.find_vowels(text)

print(f"\\n🔍 Analysis of '{text}':")
for i in sorted(vowels.keys()):
    vowels[i]  # Rich HTML display in Jupyter
'''

notebook_cell_4 = '''
# Cell 4: Detailed individual vowel analysis
text = "เลว"  # Ambiguous word
detector = ConjectureBasedVowelDetector("thai_vowels_tagged_9-21-2025-2-31-pm.json")
vowels = detector.find_vowels(text)

for i in sorted(vowels.keys()):
    v_data = vowels[i]

    print(f"📊 VOWEL {i} ANALYSIS:")
    v_data.display(text, show_alternatives=True)

    print(f"\\n🔄 All candidates:")
    for j, candidate in enumerate(v_data.candidates):
        print(f"   Candidate {j+1}:")
        print(f"      {candidate}")
        candidate.display(text)
        print()
'''

if __name__ == "__main__":
    print("🎯 VOWEL DISPLAY EXAMPLES")
    print("=" * 50)

    print("\\n1. Basic Analysis:")
    example_basic_analysis()

    print("\\n\\n2. Individual Vowel Exploration:")
    example_individual_vowel()

    print("\\n\\n3. Text Comparison:")
    example_comparison()

    print("\\n\\n4. Pattern Analysis:")
    example_pattern_analysis()

    print("\\n\\n📝 JUPYTER NOTEBOOK CELLS:")
    print("Copy these into separate Jupyter cells:")
    print("\\n" + notebook_cell_1)
    print("\\n" + notebook_cell_2)
    print("\\n" + notebook_cell_3)
    print("\\n" + notebook_cell_4)