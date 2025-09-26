#!/usr/bin/env python3
"""Analyze uniqueness of vowel patterns using different tag combinations"""

import json
import sys
import io
from collections import defaultdict

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the vowel patterns
with open('thai_vowels_tagged_9-21-2025-2-31-pm.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

patterns_by_id = defaultdict(list)
pattern_details = {}

for pattern, info in data['patterns'].items():
    tags = info.get('tags', [])

    # Extract tag components
    sound = [t.replace('sound_', '') for t in tags if t.startswith('sound_')]
    length = [t.replace('length_', '') for t in tags if t.startswith('length_')]
    vowel_type = [t for t in tags if t in ['monophthong', 'diphthong', 'triphthong']]
    openness = [t.replace('vowel_', '') for t in tags if t.startswith('vowel_')]

    # Try different ID schemes
    id1 = f"{sound[0] if sound else 'X'}_{length[0][0] if length else 'X'}"  # e.g., "a_s" for short a
    id2 = f"{sound[0] if sound else 'X'}_{length[0] if length else 'X'}_{vowel_type[0][0] if vowel_type else 'X'}"  # e.g., "a_short_m"
    id3 = f"{sound[0] if sound else 'X'}_{length[0][0] if length else 'X'}_{openness[0][0] if openness else 'X'}"  # e.g., "a_s_o" for short open a

    # Store for analysis
    patterns_by_id[id1].append(pattern)
    pattern_details[pattern] = {
        'sound': sound[0] if sound else None,
        'length': length[0] if length else None,
        'type': vowel_type[0] if vowel_type else None,
        'openness': openness[0] if openness else None,
        'id1': id1,
        'id2': id2,
        'id3': id3
    }

# Analyze each ID scheme
print("=" * 70)
print("VOWEL PATTERN IDENTIFIER ANALYSIS")
print("=" * 70)
print(f"\nTotal patterns: {len(data['patterns'])}")

# Check ID scheme 1: sound + length
print("\n" + "-" * 50)
print("ID Scheme 1: sound_length (e.g., 'a_s' for short a)")
print("-" * 50)

duplicates1 = {k: v for k, v in patterns_by_id.items() if len(v) > 1}
print(f"Unique IDs: {len(patterns_by_id)}")
print(f"Duplicate IDs: {len(duplicates1)}")

if duplicates1:
    print("\nDuplicate examples:")
    for id_key, patterns in list(duplicates1.items())[:10]:
        print(f"\n  {id_key}: {patterns}")
        for p in patterns:
            details = pattern_details[p]
            print(f"    {p}: open={details['openness']}, type={details['type']}")

# Check for patterns with same literal pattern but different tags
print("\n" + "-" * 50)
print("ID Scheme 2: Adding vowel type (monophthong/diphthong)")
print("-" * 50)

patterns_by_id2 = defaultdict(list)
for pattern, details in pattern_details.items():
    patterns_by_id2[details['id2']].append(pattern)

duplicates2 = {k: v for k, v in patterns_by_id2.items() if len(v) > 1}
print(f"Unique IDs: {len(patterns_by_id2)}")
print(f"Duplicate IDs: {len(duplicates2)}")

if duplicates2:
    print("\nRemaining duplicates:")
    for id_key, patterns in list(duplicates2.items())[:5]:
        print(f"  {id_key}: {patterns}")

# Check ID scheme 3: sound + length + openness
print("\n" + "-" * 50)
print("ID Scheme 3: Adding open/closed distinction")
print("-" * 50)

patterns_by_id3 = defaultdict(list)
for pattern, details in pattern_details.items():
    patterns_by_id3[details['id3']].append(pattern)

duplicates3 = {k: v for k, v in patterns_by_id3.items() if len(v) > 1}
print(f"Unique IDs: {len(patterns_by_id3)}")
print(f"Duplicate IDs: {len(duplicates3)}")

if duplicates3:
    print("\nRemaining duplicates:")
    for id_key, patterns in list(duplicates3.items())[:5]:
        print(f"  {id_key}: {patterns}")

# Suggest best approach
print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)

if len(duplicates3) == 0:
    print("✓ ID Scheme 3 (sound_length_openness) provides unique identifiers!")
elif len(duplicates3) < 5:
    print("ID Scheme 3 is nearly unique. Consider:")
    print("1. Using the pattern itself as ID for duplicates")
    print("2. Adding an index suffix (a_s_o_1, a_s_o_2)")
else:
    print("Consider using the actual pattern as the primary key")
    print("with the ID as a human-readable alias")

# Show some example IDs
print("\n" + "-" * 50)
print("Example Pattern IDs:")
print("-" * 50)
examples = list(pattern_details.items())[:10]
for pattern, details in examples:
    print(f"{pattern:10} -> {details['id3']:10} (sound={details['sound']}, len={details['length']}, open={details['openness']})")