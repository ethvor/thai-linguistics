#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deduplicate_sara.py

Removes duplicate patterns from sara_combos.json while preserving order
Creates backup of original file
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def deduplicate_sara_combos():
    """Remove duplicates from sara_combos.json while preserving first occurrence"""

    sara_file = Path("../res/sara/sara_combos.json")
    backup_file = Path("../res/sara/sara_combos_with_duplicates.json.bak")

    if not sara_file.exists():
        print(f"ERROR: {sara_file} not found!")
        return False

    # Create backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(f"../res/sara/sara_combos_backup_{timestamp}.json")

    print(f"Creating backup: {backup_file}")
    shutil.copy2(sara_file, backup_file)

    # Read original data
    with open(sara_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    print(f"Original data: {len(original_data)} patterns")

    # Remove duplicates while preserving order
    seen = set()
    unique_data = []
    duplicates_removed = []

    for i, pattern in enumerate(original_data):
        if pattern in seen:
            duplicates_removed.append({
                'pattern': pattern,
                'line': i + 1,
                'duplicate_of_line': original_data.index(pattern) + 1
            })
            first_line = original_data.index(pattern) + 1
            print(f"REMOVING duplicate at line {i + 1} (first at line {first_line})")
        else:
            seen.add(pattern)
            unique_data.append(pattern)

    print(f"\nDeduplication complete:")
    print(f"- Original count: {len(original_data)}")
    print(f"- Unique count: {len(unique_data)}")
    print(f"- Duplicates removed: {len(duplicates_removed)}")

    # Write deduplicated data
    with open(sara_file, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=2)

    print(f"\nDeduplicated data written to: {sara_file}")

    # Write deduplication report
    report_file = Path("../deduplication_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("SARA_COMBOS.JSON DEDUPLICATION REPORT\n")
        f.write("=====================================\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write(f"Original file: {sara_file}\n")
        f.write(f"Backup created: {backup_file}\n\n")

        f.write("STATISTICS:\n")
        f.write(f"- Original pattern count: {len(original_data)}\n")
        f.write(f"- Unique pattern count: {len(unique_data)}\n")
        f.write(f"- Duplicates removed: {len(duplicates_removed)}\n\n")

        f.write("REMOVED DUPLICATES:\n")
        f.write("===================\n")
        for dup in duplicates_removed:
            f.write(f"Line {dup['line']}: \"{dup['pattern']}\" (duplicate of line {dup['duplicate_of_line']})\n")

        f.write("\nRESULT:\n")
        f.write("=======\n")
        f.write("sara_combos.json now contains only unique patterns.\n")
        f.write("Order preserved - first occurrence of each pattern kept.\n")

    print(f"Deduplication report written to: {report_file}")

    return True

def main():
    """Main function"""
    print("Deduplicating sara_combos.json...")
    print("=" * 40)

    success = deduplicate_sara_combos()

    if success:
        print("\n✅ SUCCESS: Deduplication completed!")
        print("📁 Backup created")
        print("📊 Report generated")
        print("\nYour tag-based classifier will now work with clean, unique data!")
    else:
        print("\n❌ FAILED: Deduplication failed!")

if __name__ == "__main__":
    main()