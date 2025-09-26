#!/usr/bin/env python3
"""
Add pattern IDs to the vowel database
Corrected format:
- Abbreviated: a_s_o, ai_s_c_jg_1
- Long: a_short_open, ai_short_closed_jglide_1
"""

import json
import sys
import io
from collections import defaultdict
import shutil
from datetime import datetime

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_pattern_ids(pattern, tags):
    """Generate both abbreviated and long IDs for a pattern"""

    # Extract components from tags
    sound = next((t.replace('sound_', '') for t in tags if t.startswith('sound_')), 'X')
    length = next((t.replace('length_', '') for t in tags if t.startswith('length_')), 'X')
    openness = next((t.replace('vowel_', '') for t in tags if t.startswith('vowel_')), 'X')

    # Detect glides
    has_jglide = 'glide_j' in tags or pattern.endswith('ย')
    has_wglide = 'glide_w' in tags or pattern.endswith('ว')

    # Build abbreviated ID with underscores
    abbrev_parts = [sound]
    abbrev_parts.append(length[0] if length != 'X' else 'X')
    abbrev_parts.append(openness[0] if openness != 'X' else 'X')

    if has_jglide:
        abbrev_parts.append('jg')
    elif has_wglide:
        abbrev_parts.append('wg')

    abbrev_base = '_'.join(abbrev_parts)

    # Build long ID - clean format without verbose labels
    long_parts = [sound]
    long_parts.append(length if length != 'X' else 'X')
    long_parts.append(openness if openness != 'X' else 'X')

    if has_jglide:
        long_parts.append('jglide')
    elif has_wglide:
        long_parts.append('wglide')

    long_base = '_'.join(long_parts)

    return abbrev_base, long_base

def add_ids_to_database(input_file, output_file=None):
    """Add IDs to all patterns in the database"""

    # If no output file specified, update in place with backup
    if output_file is None:
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = input_file.replace('.json', f'_backup_{timestamp}.json')
        shutil.copy2(input_file, backup_file)
        print(f"Created backup: {backup_file}")
        output_file = input_file

    # Load the database
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Track duplicates for numbering
    abbrev_counts = defaultdict(int)
    long_counts = defaultdict(int)

    # Process each pattern
    patterns_processed = 0
    for pattern, info in data['patterns'].items():
        tags = info.get('tags', [])

        # Generate base IDs
        abbrev_base, long_base = generate_pattern_ids(pattern, tags)

        # Handle duplicates for abbreviated
        abbrev_counts[abbrev_base] += 1
        if abbrev_counts[abbrev_base] > 1:
            abbrev_id = f"{abbrev_base}_{abbrev_counts[abbrev_base]}"
        else:
            abbrev_id = abbrev_base

        # Handle duplicates for long
        long_counts[long_base] += 1
        if long_counts[long_base] > 1:
            long_id = f"{long_base}_{long_counts[long_base]}"
        else:
            long_id = long_base

        # Add IDs to pattern info
        info['abbrev_id'] = abbrev_id
        info['long_id'] = long_id

        patterns_processed += 1

    # Save updated database
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nProcessed {patterns_processed} patterns")
    print(f"Database updated: {output_file}")

    # Report on duplicates
    duplicate_abbrevs = {k: v for k, v in abbrev_counts.items() if v > 1}
    duplicate_longs = {k: v for k, v in long_counts.items() if v > 1}

    if duplicate_abbrevs:
        print(f"\nAbbreviated ID duplicates ({len(duplicate_abbrevs)}):")
        for base, count in duplicate_abbrevs.items():
            print(f"  {base}: {count} patterns")
            # Find and display the patterns
            patterns_with_this_base = []
            for pattern, info in data['patterns'].items():
                if info['abbrev_id'].startswith(base):
                    patterns_with_this_base.append(f"{pattern} → {info['abbrev_id']}")
            for p in patterns_with_this_base[:3]:  # Show first 3
                print(f"    {p}")

    return data

def verify_ids(database_file):
    """Verify that all IDs are unique and properly formatted"""

    with open(database_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    abbrev_ids = {}
    long_ids = {}

    for pattern, info in data['patterns'].items():
        abbrev_id = info.get('abbrev_id')
        long_id = info.get('long_id')

        if abbrev_id:
            if abbrev_id in abbrev_ids:
                print(f"ERROR: Duplicate abbrev_id '{abbrev_id}' for patterns: {abbrev_ids[abbrev_id]} and {pattern}")
            else:
                abbrev_ids[abbrev_id] = pattern

        if long_id:
            if long_id in long_ids:
                print(f"ERROR: Duplicate long_id '{long_id}' for patterns: {long_ids[long_id]} and {pattern}")
            else:
                long_ids[long_id] = pattern

    print(f"\nVerification complete:")
    print(f"  Unique abbreviated IDs: {len(abbrev_ids)}")
    print(f"  Unique long IDs: {len(long_ids)}")
    print(f"  Total patterns: {len(data['patterns'])}")

def main():
    """Add IDs to the vowel database"""

    database_file = "thai_vowels_tagged_9-21-2025-2-31-pm.json"

    print("=" * 70)
    print("ADDING PATTERN IDS TO DATABASE")
    print("=" * 70)

    # Add IDs to database
    updated_data = add_ids_to_database(database_file)

    # Show examples
    print("\n" + "-" * 50)
    print("SAMPLE PATTERN IDS")
    print("-" * 50)

    samples = ["xา", "xาย", "xาว", "ใx", "ไxย", "เx็f", "xัว", "xอย", "xัf", "xรรf"]
    for pattern in samples:
        if pattern in updated_data['patterns']:
            info = updated_data['patterns'][pattern]
            abbrev = info.get('abbrev_id', 'N/A')
            long_id = info.get('long_id', 'N/A')
            print(f"{pattern:8} → Abbrev: {abbrev:15} | Long: {long_id}")

    # Verify uniqueness
    print("\n" + "-" * 50)
    print("VERIFICATION")
    print("-" * 50)
    verify_ids(database_file)

if __name__ == "__main__":
    main()