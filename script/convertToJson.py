#!/usr/bin/env python3
"""
parse_thai_sara_table.py

Transform a plain-text mapping of Thai vowel/marker keys to their combination templates
into structured JSON.

Input format (each line):
<KEY>: [ITEM1; ITEM2; ... ITEMN]

Example:
ะ: [◌ะ; ◌ัวะ; เ◌ะ; เ◌อะ; เ◌าะ]

Features:
- Robust line parsing with regex
- Whitespace cleanup
- Dotted-circle handling modes:
    * keep   : leave U+25CC (◌) as-is
    * strip  : remove U+25CC (default)
    * replace: replace U+25CC with a given Thai carrier (e.g., อ or ก)
- Emits pretty-printed UTF-8 JSON

Usage:
    python parse_thai_sara_table.py INPUT.txt OUTPUT.json --dotted strip
    python parse_thai_sara_table.py INPUT.txt OUTPUT.json --dotted replace --carrier อ
    python parse_thai_sara_table.py INPUT.txt OUTPUT.json --dotted keep
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

DOT = "\u25CC"  # dotted circle ◌

LINE_RE = re.compile(r'^\s*(?P<key>[^:]+?)\s*:\s*\[(?P<vals>.*?)\]\s*$', re.UNICODE)

def process_item(s: str, dotted_mode: str, carrier: str) -> str:
    s = s.strip()
    if dotted_mode == "strip":
        return s.replace(DOT, "")
    elif dotted_mode == "replace":
        return s.replace(DOT, carrier)
    else:  # keep
        return s

def parse_lines(text: str, dotted_mode: str = "strip", carrier: str = "อ") -> Dict[str, List[str]]:
    data: Dict[str, List[str]] = {}
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m = LINE_RE.match(raw)
        if not m:
            # Skip lines that don't fit the pattern (or raise if you prefer)
            continue
        key = m.group("key").strip()
        vals_blob = m.group("vals")
        items = [process_item(x, dotted_mode, carrier) for x in vals_blob.split(";")]
        # Normalize empties (after stripping dots)
        items = [x for x in (i.strip() for i in items) if x != ""]
        key = process_item(key, dotted_mode, carrier)
        data[key] = items
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--dotted", choices=["keep","strip","replace"], default="strip",
                    help="How to handle dotted circle U+25CC (default: strip)")
    ap.add_argument("--carrier", default="อ",
                    help="Carrier used when --dotted replace (default: อ)")
    args = ap.parse_args()

    text = args.input.read_text(encoding="utf-8")
    data = parse_lines(text, dotted_mode=args.dotted, carrier=args.carrier)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
