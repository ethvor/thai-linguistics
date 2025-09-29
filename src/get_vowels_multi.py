#!/usr/bin/env python3
"""
Multi-interpretation Thai vowel pattern matcher.
Finds all possible vowel pattern interpretations and groups by vowel position.
"""

import json
import os
import sys
import io
from typing import List, Dict, Tuple, Optional

# Set UTF-8 encoding for Windows console (skip in Jupyter)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Thai consonants (all 44)
CONSONANTS = {
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
    'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
    'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
    'ส', 'ห', 'ฬ', 'อ', 'ฮ'
}

# Thai vowel marks
VOWEL_MARKS = {
    'า', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ั', 'ำ', 'ะ', '็'
}

# Thai tone marks (to be ignored during pattern matching)
TONE_MARKS = {
    '่', '้', '๊', '๋'
}

# Predefined consonant clusters (initially empty, can be populated)
INITIAL_CLUSTERS = set()  # e.g., {'กร', 'คล', 'สตร', 'คร', 'ปล'}
FINAL_CLUSTERS = set()    # e.g., {'นธ์', 'รณ์'}


def strip_tone_marks(text: str) -> Tuple[str, List[Tuple[int, str]]]:
    """
    Remove tone marks from text for pattern matching.
    Returns (stripped_text, tone_mark_positions)
    """
    stripped = []
    tone_positions = []

    for i, char in enumerate(text):
        if char in TONE_MARKS:
            tone_positions.append((i, char))
        else:
            stripped.append(char)

    return ''.join(stripped), tone_positions


def restore_original_positions(match_info: Dict, original_text: str, stripped_text: str, tone_positions: List[Tuple[int, str]]) -> Dict:
    """
    Restore original text positions accounting for tone marks.
    """
    if not tone_positions:
        return match_info

    # Map stripped positions back to original positions
    stripped_to_original = {}
    original_idx = 0
    stripped_idx = 0

    for original_pos, tone_char in tone_positions:
        # Map indices up to this tone mark
        while original_idx < original_pos:
            stripped_to_original[stripped_idx] = original_idx
            stripped_idx += 1
            original_idx += 1
        # Skip the tone mark in original
        original_idx += 1

    # Map remaining characters
    while stripped_idx < len(stripped_text):
        stripped_to_original[stripped_idx] = original_idx
        stripped_idx += 1
        original_idx += 1

    # Update match_info positions
    new_match_info = match_info.copy()

    if match_info['start_pos'] in stripped_to_original:
        new_match_info['start_pos'] = stripped_to_original[match_info['start_pos']]

    if match_info['end_pos'] in stripped_to_original:
        new_match_info['end_pos'] = stripped_to_original[match_info['end_pos']]
    elif match_info['end_pos'] >= len(stripped_text):
        new_match_info['end_pos'] = len(original_text) - 1

    # Update matched_text to use original text
    start = new_match_info['start_pos']
    end = new_match_info['end_pos']
    new_match_info['matched_text'] = original_text[start:end+1]

    return new_match_info


def load_patterns(patterns_file: str) -> List[Dict]:
    """Load vowel patterns from JSON file."""
    if not os.path.exists(patterns_file):
        raise FileNotFoundError(f"Patterns file not found: {patterns_file}")

    with open(patterns_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract patterns from the JSON structure
    if isinstance(data, dict) and 'patterns' in data:
        patterns_dict = data['patterns']
        # Convert from {pattern: data} to [{pattern: ..., data}, ...]
        patterns_list = []
        for pattern, pattern_data in patterns_dict.items():
            pattern_entry = {'pattern': pattern}
            pattern_entry.update(pattern_data)
            patterns_list.append(pattern_entry)
        return patterns_list
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Unexpected JSON structure in {patterns_file}")


def get_all_pattern_interpretations(text: str, pattern_data: Dict, pos: int) -> List[Dict]:
    """
    Get all possible interpretations of a pattern at a position.
    Returns list of all valid interpretations.
    """
    pattern = pattern_data.get('pattern', '')
    if not pattern:
        return []

    interpretations = []

    # Generate all possible x and f combinations
    x_options = []
    f_options = []

    # Find x positions in pattern
    x_count = pattern.count('x')
    f_count = pattern.count('f')

    if x_count == 0 and f_count == 0:
        # No x or f, pattern must match literally
        interpretation = try_literal_pattern(text, pattern_data, pos)
        if interpretation:
            return [interpretation]
        return []

    # Try all combinations of x and f lengths
    if x_count > 0:
        x_options = get_foundation_options(text, pattern, pos)
    else:
        x_options = [None]

    if f_count > 0:
        # For each x option, try different f options
        for x_opt in x_options:
            f_options_for_x = get_final_options(text, pattern, pos, x_opt)
            for f_opt in f_options_for_x:
                interp = try_pattern_with_options(text, pattern_data, pos, x_opt, f_opt)
                if interp:
                    interpretations.append(interp)
    else:
        # No f in pattern, just try x options
        for x_opt in x_options:
            interp = try_pattern_with_options(text, pattern_data, pos, x_opt, None)
            if interp:
                interpretations.append(interp)

    return interpretations


def get_foundation_options(text: str, pattern: str, pos: int) -> List[Dict]:
    """Get all possible foundation (x) interpretations at position."""
    options = []
    x_idx = pattern.index('x')

    # Calculate where x should be in the text
    text_x_pos = pos + x_idx

    if text_x_pos >= len(text):
        return []

    # Try single consonant
    if text[text_x_pos] in CONSONANTS:
        options.append({
            'start': text_x_pos,
            'end': text_x_pos,
            'text': text[text_x_pos],
            'length': 1
        })

    # Try two-consonant sequence
    if text_x_pos + 1 < len(text):
        two_char = text[text_x_pos:text_x_pos+2]
        if all(c in CONSONANTS for c in two_char):
            options.append({
                'start': text_x_pos,
                'end': text_x_pos + 1,
                'text': two_char,
                'length': 2
            })

    return options


def get_final_options(text: str, pattern: str, pos: int, x_option: Dict) -> List[Dict]:
    """Get all possible final (f) interpretations given an x option."""
    if not x_option:
        return [None]

    options = []
    f_idx = pattern.index('f')

    # Calculate where f should be in the text
    # Account for x's actual length
    x_idx = pattern.index('x')
    text_offset = pos + f_idx
    if x_idx < f_idx:
        text_offset += (x_option['length'] - 1)

    if text_offset >= len(text):
        return [None]

    # Try single consonant
    if text[text_offset] in CONSONANTS:
        options.append({
            'start': text_offset,
            'end': text_offset,
            'text': text[text_offset],
            'length': 1
        })

    # Try two-consonant sequence
    if text_offset + 1 < len(text):
        two_char = text[text_offset:text_offset+2]
        if all(c in CONSONANTS for c in two_char):
            options.append({
                'start': text_offset,
                'end': text_offset + 1,
                'text': two_char,
                'length': 2
            })

    return options if options else [None]


def try_pattern_with_options(text: str, pattern_data: Dict, pos: int,
                            x_option: Optional[Dict], f_option: Optional[Dict]) -> Optional[Dict]:
    """Try to match pattern with specific x and f options."""
    pattern = pattern_data.get('pattern', '')

    text_idx = pos
    pattern_idx = 0
    match_info = {
        'pattern': pattern,
        'abbrev_id': pattern_data.get('abbrev_id', ''),
        'long_id': pattern_data.get('long_id', ''),
        'tags': pattern_data.get('tags', []),  # Include tags for database
        'start_pos': pos,
        'end_pos': pos,
        'x_text': None,
        'f_text': None,
        'matched_text': ''
    }

    while pattern_idx < len(pattern) and text_idx < len(text):
        pattern_char = pattern[pattern_idx]

        if pattern_char == 'x':
            if not x_option:
                return None

            # Verify x is at expected position
            if text_idx != x_option['start']:
                return None

            match_info['x_text'] = x_option['text']
            text_idx = x_option['end'] + 1
            pattern_idx += 1

        elif pattern_char == 'f':
            if not f_option:
                return None

            # Verify f is at expected position
            if text_idx != f_option['start']:
                return None

            match_info['f_text'] = f_option['text']
            text_idx = f_option['end'] + 1
            pattern_idx += 1

        else:
            # Literal character - must match exactly
            if text_idx >= len(text) or text[text_idx] != pattern_char:
                return None

            text_idx += 1
            pattern_idx += 1

    # Check if we matched the entire pattern
    if pattern_idx != len(pattern):
        return None

    match_info['end_pos'] = text_idx - 1
    match_info['matched_text'] = text[pos:text_idx]

    return match_info


def try_literal_pattern(text: str, pattern_data: Dict, pos: int) -> Optional[Dict]:
    """Try to match a pattern with no x or f variables."""
    pattern = pattern_data.get('pattern', '')

    if pos + len(pattern) > len(text):
        return None

    if text[pos:pos+len(pattern)] == pattern:
        return {
            'pattern': pattern,
            'abbrev_id': pattern_data.get('abbrev_id', ''),
            'long_id': pattern_data.get('long_id', ''),
            'tags': pattern_data.get('tags', []),  # Include tags for database
            'start_pos': pos,
            'end_pos': pos + len(pattern) - 1,
            'x_text': None,
            'f_text': None,
            'matched_text': pattern
        }

    return None


def group_interpretations_by_vowel(all_matches: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Group pattern matches by actual vowel mark positions, respecting the Voraritskul Conjecture.
    Each vowel mark in the text gets its own group. Patterns are only grouped if they
    contain the same vowel mark (same vowel character at the same position).
    Returns dict: {vowel_number: [interpretations]}
    """
    if not all_matches:
        return {}

    # Thai vowel marks for identification
    vowel_marks = {'า', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ั', 'ำ', 'ะ', '็'}

    # Map each match to the vowel mark positions it contains
    match_to_vowel_positions = {}

    for i, match in enumerate(all_matches):
        vowel_positions = set()
        match_text = match['matched_text']
        start_pos = match['start_pos']

        # Find all vowel mark positions within this match
        for j, char in enumerate(match_text):
            if char in vowel_marks:
                vowel_positions.add(start_pos + j)

        match_to_vowel_positions[i] = vowel_positions

    # Group matches that share the same vowel mark positions
    vowel_groups = {}
    vowel_num = 1
    used_matches = set()

    for i, match in enumerate(all_matches):
        if i in used_matches:
            continue

        vowel_positions = match_to_vowel_positions[i]
        if not vowel_positions:
            # Pattern with no vowel marks - skip or handle separately
            continue

        # Start a new group
        current_group = [match]
        used_matches.add(i)

        # Find other matches that share the same vowel mark positions
        for j, other_match in enumerate(all_matches):
            if j in used_matches or j <= i:
                continue

            other_vowel_positions = match_to_vowel_positions[j]

            # Group if they share any vowel mark positions
            if vowel_positions & other_vowel_positions:
                current_group.append(other_match)
                used_matches.add(j)

        vowel_groups[vowel_num] = current_group
        vowel_num += 1

    return vowel_groups


def overlaps(region1: Tuple[int, int], region2: Tuple[int, int]) -> bool:
    """Check if two regions overlap."""
    return not (region1[1] < region2[0] or region2[1] < region1[0])


def get_vowels_multi(text: str, patterns_file: str = "data/thai_vowels_tagged_9-21-2025-2-31-pm.json") -> Dict[int, List[Dict]]:
    """
    Find all vowel pattern interpretations in Thai text.
    Tone marks are ignored during pattern matching but preserved in results.
    Returns a dictionary where keys are vowel numbers (1, 2, 3...)
    and values are lists of all possible interpretations for that vowel.
    """
    patterns = load_patterns(patterns_file)
    all_matches = []

    # Strip tone marks for pattern matching
    stripped_text, tone_positions = strip_tone_marks(text)

    # Try each pattern at each position and get all interpretations
    for pos in range(len(stripped_text)):
        for pattern_data in patterns:
            interpretations = get_all_pattern_interpretations(stripped_text, pattern_data, pos)

            # Restore original positions and text for each interpretation
            for interp in interpretations:
                restored_interp = restore_original_positions(interp, text, stripped_text, tone_positions)
                all_matches.append(restored_interp)

    # Group by vowel position
    vowel_groups = group_interpretations_by_vowel(all_matches)

    return vowel_groups


def display_vowel_groups(text: str, vowel_groups: Dict[int, List[Dict]]) -> None:
    """Display vowel groups with all interpretations."""
    print(f"Text: '{text}'")
    print(f"Found {len(vowel_groups)} vowel positions")
    print("=" * 70)

    for vowel_num in sorted(vowel_groups.keys()):
        interpretations = vowel_groups[vowel_num]
        print(f"\nVowel {vowel_num}: ({len(interpretations)} interpretations)")
        print("-" * 70)

        for i, interp in enumerate(interpretations, 1):
            print(f"  [{i}] Pattern: {interp['pattern']:<12} ID: {interp['abbrev_id']:<15}")
            print(f"      Text: '{interp['matched_text']}'  Pos: {interp['start_pos']}-{interp['end_pos']}")
            if interp['x_text']:
                print(f"      x='{interp['x_text']}'", end="")
            if interp['f_text']:
                print(f"  f='{interp['f_text']}'", end="")
            if interp['x_text'] or interp['f_text']:
                print()  # New line after x/f info


def main():
    """Example usage."""
    test_texts = [
        "คนสตรี",     # Should show multiple interpretations for รี
        "เด็ก",       # Multiple patterns
        "กรุงเทพ",    # Cluster possibilities
    ]

    for text in test_texts:
        print(f"\n{'='*70}")
        vowels = get_vowels_multi(text)
        display_vowel_groups(text, vowels)


if __name__ == "__main__":
    main()