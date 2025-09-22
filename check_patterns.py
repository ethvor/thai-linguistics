#!/usr/bin/env python3
"""Check what patterns we have for เลว"""

import json
import sys
import io

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load patterns
with open('thai_vowels_tagged_9-21-2025-2-31-pm.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

patterns = list(data['patterns'].keys())

print("Patterns that could match เลว:")
print("-" * 40)

# Find patterns with เ
e_patterns = [p for p in patterns if 'เ' in p]
print(f"\nPatterns containing เ: {len(e_patterns)}")

# Specifically look for patterns that could match เลว
target_patterns = ['เx', 'เxf', 'เxว']
for pattern in target_patterns:
    if pattern in patterns:
        print(f"  ✓ {pattern} EXISTS")
    else:
        print(f"  ✗ {pattern} NOT FOUND")

print("\nAll patterns with เx:")
for p in e_patterns:
    if 'เx' in p:
        print(f"  {p}")

print("\nFor เลว to be fully ambiguous, we need:")
print("  1. เxว (ล + vowel pattern where ว is part of vowel) - EXISTS" if 'เxว' in patterns else "  1. เxว - NOT FOUND")
print("  2. เxf (ล + vowel, ว as final consonant) - EXISTS" if 'เxf' in patterns else "  2. เxf - NOT FOUND")
print("  3. เx (ลว cluster + open vowel) - EXISTS" if 'เx' in patterns else "  3. เx - NOT FOUND")