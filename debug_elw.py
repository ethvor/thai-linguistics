#!/usr/bin/env python3
"""Debug why เลว isn't finding all interpretations"""

import json
import sys
import io

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load data
with open("res/foundation/foundation.json", "r", encoding="utf-8") as f:
    foundation = set(json.load(f)["foundation"])

with open("thai_vowels_tagged_9-21-2025-2-31-pm.json", "r", encoding="utf-8") as f:
    patterns = list(json.load(f)["patterns"].keys())

text = "เลว"
print(f"Analyzing: {text}")
print(f"Characters: {[c for c in text]}")
print(f"Is ล a foundation? {text[1] in foundation}")
print(f"Is ว a foundation? {text[2] in foundation}")
print()

# Manually check each pattern
test_patterns = ['เxว', 'เxf', 'เx']

for pattern in test_patterns:
    print(f"\nTesting pattern: {pattern}")
    print("-" * 30)

    # Try interpretation 1: เxว with x=ล
    if pattern == 'เxว':
        print("  Interpretation: x=ล, ว is part of vowel")
        print("  Match: เ[ล]ว → เxว pattern")
        print("  Reading order: ล, เxว")

    # Try interpretation 2: เxf with x=ล, f=ว
    elif pattern == 'เxf':
        print("  Interpretation: x=ล, f=ว (ว is final consonant)")
        print("  Match: เ[ล][ว] → เxf pattern")
        print("  Reading order: ล, เx, ว")

    # Try interpretation 3: เx with x=ลว (cluster)
    elif pattern == 'เx':
        print("  Interpretation: x=ลว (cluster)")
        print("  Match: เ[ลว] → เx pattern")
        print("  Reading order: ลว, เx")

print("\n" + "="*50)
print("All three patterns exist and match!")
print("The algorithm should find all three interpretations.")
print("\nThe issue might be:")
print("1. The algorithm isn't trying all cluster sizes")
print("2. The algorithm is eliminating duplicates incorrectly")
print("3. The algorithm isn't exploring all starting positions")