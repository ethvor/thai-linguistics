#!/usr/bin/env python3
"""
unique_starters_to_json.py

Read a JSON mapping of Thai vowel templates and
extract the set of unique first characters from all entries.
Output as JSON.
"""

import json
from pathlib import Path

def unique_starters(json_path: str):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    starters = set()
    for values in data.values():
        for s in values:
            if s:  # non-empty string
                starters.add(s[0])
    return sorted(starters)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file", help="Input JSON file with vowel templates")
    ap.add_argument("output_file", help="Output JSON file for unique starters")
    args = ap.parse_args()

    chars = unique_starters(args.json_file)
    Path(args.output_file).write_text(
        json.dumps(chars, ensure_ascii=False, indent=2), encoding="utf-8"
    )
