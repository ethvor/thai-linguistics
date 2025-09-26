#!/usr/bin/env python3
"""
Simple Vowel Finder Algorithm
Finds all possible vowel patterns in Thai text without optimization
Returns numbered data structure with 1-based indexing
"""

import json
import sys
import io
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class VowelMatch:
    """Single possible vowel pattern match"""
    pattern: str          # The pattern template (e.g., "xา", "เxf")
    abbrev_id: str        # Abbreviated ID
    start_pos: int        # Start position in original text
    end_pos: int          # End position in original text
    foundation_pos: int   # Where 'x' maps to
    final_pos: int = None # Where 'f' maps to if present

@dataclass
class VowelData:
    """All data for a single vowel position"""
    vowel_number: int                    # 1-based index
    possible_patterns: List[VowelMatch]  # All possible pattern matches
    text_positions: Tuple[int, int]      # Overall span in text

class VowelFinder:
    """Finds all vowel patterns in Thai text"""

    def __init__(self, patterns_file: str):
        """Load patterns database"""
        with open(patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.patterns = {}
        for pattern, info in data['patterns'].items():
            self.patterns[pattern] = {
                'abbrev_id': info.get('abbrev_id', 'unknown'),
                'tags': info.get('tags', [])
            }

        # Character sets
        self.vowel_chars = {'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู',
                           'เ', 'แ', 'โ', 'ใ', 'ไ', '็'}
        self.consonants = {
            'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
            'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
            'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
            'ส', 'ห', 'ฬ', 'อ', 'ฮ'
        }
        self.tone_marks = {'่', '้', '๊', '๋'}

    def find_vowels(self, text: str) -> Dict[int, VowelData]:
        """
        Find all vowel patterns in text
        Returns dict with 1-based indexing: {1: VowelData, 2: VowelData, ...}
        """
        all_matches = []

        # Try every pattern at every position (brute force)
        for pos in range(len(text)):
            for pattern in self.patterns:
                matches = self._try_pattern_at_position(text, pos, pattern)
                all_matches.extend(matches)

        # Group matches by their vowel components
        vowel_groups = self._group_by_vowel_position(all_matches)

        # Convert to numbered structure (1-based)
        result = {}
        for idx, (positions, matches) in enumerate(vowel_groups, start=1):
            result[idx] = VowelData(
                vowel_number=idx,
                possible_patterns=matches,
                text_positions=positions
            )

        return result

    def _try_pattern_at_position(self, text: str, pos: int, pattern: str) -> List[VowelMatch]:
        """Try to match a pattern starting at different alignments from pos"""
        matches = []

        # Try different alignments
        for alignment in ['pattern_start', 'x_at_pos', 'pattern_contains_pos']:
            match = self._match_pattern(text, pos, pattern, alignment)
            if match:
                matches.append(match)

        return matches

    def _match_pattern(self, text: str, pos: int, pattern: str, alignment: str) -> VowelMatch:
        """Match a specific pattern with given alignment"""

        # Calculate start position based on alignment
        if alignment == 'pattern_start':
            start = pos
        elif alignment == 'x_at_pos':
            if 'x' not in pattern:
                return None
            x_idx = pattern.index('x')
            start = pos - x_idx
        elif alignment == 'pattern_contains_pos':
            # Try to see if pattern could contain this position
            # For simplicity, skip this complex alignment for now
            return None
        else:
            return None

        # Check bounds
        if start < 0 or start + len(pattern) > len(text):
            return None

        # Try to match character by character
        text_idx = start
        pattern_idx = 0
        foundation_pos = None
        final_pos = None
        matched_positions = []

        while pattern_idx < len(pattern):
            if text_idx >= len(text):
                return None

            p_char = pattern[pattern_idx]
            t_char = text[text_idx]

            if p_char == 'x':
                # Must be consonant
                if t_char not in self.consonants:
                    return None
                foundation_pos = text_idx
                matched_positions.append(text_idx)
                text_idx += 1
                # Skip tone mark if present
                if text_idx < len(text) and text[text_idx] in self.tone_marks:
                    text_idx += 1

            elif p_char == 'f':
                # Must be consonant (final)
                if t_char not in self.consonants:
                    return None
                final_pos = text_idx
                matched_positions.append(text_idx)
                text_idx += 1

            else:
                # Must match exact character
                if t_char != p_char:
                    return None
                matched_positions.append(text_idx)
                text_idx += 1

            pattern_idx += 1

        # Success - create match
        if matched_positions:
            return VowelMatch(
                pattern=pattern,
                abbrev_id=self.patterns[pattern]['abbrev_id'],
                start_pos=min(matched_positions),
                end_pos=max(matched_positions),
                foundation_pos=foundation_pos,
                final_pos=final_pos
            )

        return None

    def _group_by_vowel_position(self, matches: List[VowelMatch]) -> List[Tuple[Tuple[int, int], List[VowelMatch]]]:
        """Group matches that represent the same vowel occurrence"""
        if not matches:
            return []

        # Sort by start position
        matches.sort(key=lambda m: m.start_pos)

        # Group overlapping matches
        groups = []
        current_group = []
        current_span = None

        for match in matches:
            match_span = (match.start_pos, match.end_pos)

            if current_span is None:
                # First match
                current_span = match_span
                current_group = [match]
            elif self._spans_overlap(current_span, match_span):
                # Overlaps with current group
                current_group.append(match)
                # Extend span
                current_span = (
                    min(current_span[0], match_span[0]),
                    max(current_span[1], match_span[1])
                )
            else:
                # New group
                groups.append((current_span, current_group))
                current_span = match_span
                current_group = [match]

        # Add last group
        if current_group:
            groups.append((current_span, current_group))

        return groups

    def _spans_overlap(self, span1: Tuple[int, int], span2: Tuple[int, int]) -> bool:
        """Check if two spans overlap"""
        return not (span1[1] < span2[0] or span2[1] < span1[0])


def main():
    """Test the vowel finder"""

    # Initialize finder
    finder = VowelFinder("thai_vowels_tagged_9-21-2025-2-31-pm.json")

    # Test cases
    test_cases = [
        "ยา",
        "เด็ก",
        "ประเทศไทย",
        "สวัสดีครับ",
        "อย่างไร"
    ]

    print("=" * 70)
    print("SIMPLE VOWEL FINDER")
    print("=" * 70)

    for text in test_cases:
        print(f"\nText: '{text}'")
        print("-" * 50)

        vowels = finder.find_vowels(text)

        for idx in sorted(vowels.keys()):
            data = vowels[idx]
            print(f"\nVowel {idx}:")
            print(f"  Text positions: {data.text_positions}")
            print(f"  Possible patterns ({len(data.possible_patterns)}):")

            for match in data.possible_patterns[:5]:  # Show first 5
                segment = text[match.start_pos:match.end_pos+1]
                print(f"    - {match.pattern} ({match.abbrev_id}) at [{match.start_pos}-{match.end_pos}]: '{segment}'")

            if len(data.possible_patterns) > 5:
                print(f"    ... and {len(data.possible_patterns) - 5} more")

        # Test indexing
        if 1 in vowels:
            print(f"\nAccessing vowels[1]: {vowels[1].vowel_number}, {len(vowels[1].possible_patterns)} patterns")


if __name__ == "__main__":
    main()