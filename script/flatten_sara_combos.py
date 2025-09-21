#!/usr/bin/env python3
"""
flatten_sara_combinations.py

Take a JSON mapping of Thai vowel templates (dict of lists),
drop the keys, and combine all values into one big list.
Output as JSON.
"""

import json
from pathlib import Path

def flatten_json(json_path: str):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    combined = []
    for values in data.values():
        combined.extend(values)
    return combined

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file", help="Input JSON file with vowel templates")
    ap.add_argument("output_file", help="Output JSON file (flattened)")
    args = ap.parse_args()

    combined = flatten_json(args.json_file)
    Path(args.output_file).write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8"
    )
