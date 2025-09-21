#!/usr/bin/env python3
"""
make_foundation_json.py

Reads a plaintext file (not actually parsed in this version),
and outputs a JSON file with the "foundation" list of Thai consonants.
"""

import json
from pathlib import Path

FOUNDATION = [
    "ก","ข","ฃ","ค","ฅ","ฆ","ง","จ","ฉ","ช","ซ","ฌ","ญ",
    "ฎ","ฏ","ฐ","ฑ","ฒ","ณ","ด","ต","ถ","ท","ธ","น","บ",
    "ป","ผ","ฝ","พ","ฟ","ภ","ม","ย","ร","ล","ว","ศ","ษ",
    "ส","ห","ฬ","ฮ"
]

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("plaintext_file", help="Input plaintext file (not parsed here, just a placeholder)")
    ap.add_argument("output_json", help="Output JSON file for foundation consonants")
    args = ap.parse_args()

    # In case you want to verify file exists, even though not used
    _ = Path(args.plaintext_file).read_text(encoding="utf-8")

    data = {"foundation": FOUNDATION}

    Path(args.output_json).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Wrote {len(FOUNDATION)} foundation consonants to {args.output_json}")
