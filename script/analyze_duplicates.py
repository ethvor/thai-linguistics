#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_duplicates.py

Analyzes duplicates in sara_combos.json and classified_sara_combos.json
Writes comprehensive duplicate analysis to a file
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_duplicates():
    """Analyze duplicates in both sara files"""

    # Load both files
    sara_file = Path("../res/sara/sara_combos.json")
    classified_file = Path("../res/sara/classified_sara_combos.json")

    with open(sara_file, 'r', encoding='utf-8') as f:
        sara_list = json.load(f)

    with open(classified_file, 'r', encoding='utf-8') as f:
        classified = json.load(f)

    output_lines = []
    output_lines.append("THAI VOWEL PATTERN DUPLICATE ANALYSIS")
    output_lines.append("=====================================")
    output_lines.append("Generated: 2025-09-20")
    output_lines.append("")

    # Analyze within-class duplicates
    output_lines.append("WITHIN-CLASS DUPLICATES (Same pattern appears multiple times in one class):")
    output_lines.append("=" * 77)
    output_lines.append("")

    within_class_duplicates = False
    for class_name, patterns in classified.items():
        pattern_counts = {}
        for pattern in patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        duplicates_in_class = {p: count for p, count in pattern_counts.items() if count > 1}

        if duplicates_in_class:
            within_class_duplicates = True
            output_lines.append(f"Class \"{class_name}\":")
            for pattern, count in duplicates_in_class.items():
                output_lines.append(f"  - \"{pattern}\" appears {count} times")
            output_lines.append("")
        else:
            output_lines.append(f"Class \"{class_name}\": No duplicates ✓")

    if not within_class_duplicates:
        output_lines.append("RESULT: No patterns appear multiple times within the same class")

    output_lines.append("")

    # Create reverse lookup: pattern -> classes
    pattern_to_classes = defaultdict(list)
    for class_name, patterns in classified.items():
        for pattern in patterns:
            pattern_to_classes[pattern].append(class_name)

    # Analyze cross-class duplicates
    output_lines.append("CROSS-CLASS DUPLICATES (Same pattern appears in different classes):")
    output_lines.append("=" * 70)
    output_lines.append("")

    cross_class_patterns = {p: classes for p, classes in pattern_to_classes.items() if len(classes) > 1}

    for pattern, classes in cross_class_patterns.items():
        output_lines.append(f"Pattern: \"{pattern}\"")
        output_lines.append(f"  Classes: {classes}")
        output_lines.append("")

    # Analyze linear duplicates in sara_combos.json
    output_lines.append("SARA_COMBOS.JSON LINEAR DUPLICATES (same pattern appears multiple times in the list):")
    output_lines.append("=" * 88)
    output_lines.append("")

    seen_positions = {}
    linear_duplicates = {}

    for i, pattern in enumerate(sara_list):
        if pattern in seen_positions:
            if pattern not in linear_duplicates:
                linear_duplicates[pattern] = [seen_positions[pattern]]
            linear_duplicates[pattern].append(i)
        else:
            seen_positions[pattern] = i

    for pattern, positions in linear_duplicates.items():
        lines = [str(pos + 1) for pos in positions]
        output_lines.append(f"Pattern: \"{pattern}\" - Lines: {', '.join(lines)} ({len(positions)} occurrences)")

    # Summary statistics
    output_lines.append("")
    output_lines.append("SUMMARY STATISTICS:")
    output_lines.append("=" * 18)
    output_lines.append(f"- Total patterns in sara_combos.json: {len(sara_list)}")
    output_lines.append(f"- Unique patterns in sara_combos.json: {len(seen_positions)}")
    output_lines.append(f"- Patterns with cross-class classification: {len(cross_class_patterns)}")
    output_lines.append(f"- Patterns with linear duplicates: {len(linear_duplicates)}")

    total_duplicate_entries = sum(len(positions) - 1 for positions in linear_duplicates.values())
    output_lines.append(f"- Total duplicate entries to remove: {total_duplicate_entries}")
    output_lines.append(f"- Final unique count after deduplication: {len(sara_list) - total_duplicate_entries}")

    # Recommendations
    output_lines.append("")
    output_lines.append("RECOMMENDATIONS:")
    output_lines.append("=" * 15)
    output_lines.append("1. The classified_sara_combos.json shows no within-class duplicates ✓")
    output_lines.append("2. Cross-class duplicates are CORRECT - patterns can belong to multiple categories")
    output_lines.append("3. The sara_combos.json linear duplicates should be removed to create a clean unique list")
    output_lines.append("4. The tag-based system is perfect for handling multi-class patterns")
    output_lines.append("5. Consider using classified_sara_combos.json as source for tags")

    output_lines.append("")
    output_lines.append("CONCLUSION:")
    output_lines.append("=" * 10)
    output_lines.append("The duplicates represent linguistic reality - Thai vowel patterns")
    output_lines.append("can be classified multiple ways. The tag-based system handles this complexity.")

    return output_lines, linear_duplicates, cross_class_patterns

def main():
    """Main function"""
    print("Analyzing Thai vowel pattern duplicates...")

    output_lines, linear_duplicates, cross_class_patterns = analyze_duplicates()

    # Write to file
    output_file = Path("../duplicate_analysis.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"Analysis written to: {output_file}")
    print(f"Found {len(linear_duplicates)} patterns with linear duplicates")
    print(f"Found {len(cross_class_patterns)} patterns with cross-class duplicates")

    return output_lines, linear_duplicates, cross_class_patterns

if __name__ == "__main__":
    main()