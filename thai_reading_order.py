#!/usr/bin/env python3
"""
Thai Reading Order Algorithm with Foundation Container Model
Finds all possible canonical reading orders for Thai text.

Key concepts:
- Foundation: A container for consonant(s) + optional tone mark
- Patterns: Describe vowel arrangement around foundations (x = foundation, f = final)
- Tone marks: Attached to specific consonants within foundations
"""

import json
from typing import List, Dict, Set, Tuple, Optional

class ThaiReadingOrderAnalyzer:
    def __init__(self, foundation_file: str, vowel_patterns_file: str):
        """Initialize with Thai linguistic data."""
        # Load foundation consonants
        with open(foundation_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.foundation = set(data["foundation"])

        # Load vowel patterns
        with open(vowel_patterns_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.vowel_patterns = list(data["patterns"].keys())

        print(f"Loaded {len(self.foundation)} foundation consonants")
        print(f"Loaded {len(self.vowel_patterns)} vowel patterns")

        # Define tone marks
        self.tone_marks = {'่', '้', '๊', '๋'}

        # Characters that can cause ambiguity
        self.ambiguous_chars = {"ว", "ย", "อ"}

    def findThaiGraphemeOrderDomain(self, text: str) -> Dict:
        """
        Find ALL possible reading orders for Thai text using foundation container model.

        Returns: Dictionary with complete analysis including all possible readings
        """
        if not text:
            return {
                'text': text,
                'readings': [],
                'is_ambiguous': False,
                'unmatched': []
            }

        all_readings = []
        text_len = len(text)

        def explore_segmentations(pos: int, used: Set[int], current_reading: List):
            """Recursively explore all possible syllable segmentations."""

            # If all positions used, we have a complete reading
            # CONSTRAINT: Only accept single-syllable readings
            if len(used) == text_len:
                if len(current_reading) == 1:  # Only single syllable interpretations
                    all_readings.append(current_reading.copy())
                return

            # Find next unused position
            while pos < text_len and pos in used:
                pos += 1

            if pos >= text_len:
                return

            # Try all patterns that could match at or around this position
            found_any = False

            for pattern in self.vowel_patterns:
                # Try all possible ways this pattern could match
                matches = self.find_pattern_matches(text, pattern, used)

                for match in matches:
                    # Check if this match uses our current position
                    if pos in match['positions']:
                        syllable = {
                            'foundation': match['foundation'],
                            'vowel': match['vowel_text'],
                            'final': match['final'],
                            'pattern': match['pattern']
                        }
                        new_used = used | set(match['positions'])
                        new_reading = current_reading + [syllable]

                        # Continue exploring
                        explore_segmentations(0, new_used, new_reading)
                        found_any = True

        # Start exploration from position 0
        explore_segmentations(0, set(), [])

        # Remove duplicates and build result structure
        unique_readings = []
        seen = set()

        for reading in all_readings:
            reading_str = str(reading)
            if reading_str not in seen:
                seen.add(reading_str)

                # Build reading order for this interpretation
                reading_order = []
                matched_text_parts = []

                for syllable in reading:
                    # Add foundation with tone
                    foundation_text = self.render_foundation(syllable['foundation'])
                    if foundation_text:
                        reading_order.append(foundation_text)
                        matched_text_parts.append(foundation_text)

                    # Add vowel
                    if syllable['vowel']:
                        reading_order.append(syllable['vowel'])
                        matched_text_parts.append(syllable['vowel'])

                    # Add final
                    if syllable['final']:
                        final_text = self.render_foundation(syllable['final'])
                        reading_order.append(final_text)
                        matched_text_parts.append(final_text)

                unique_readings.append({
                    'syllables': reading,
                    'reading_order': reading_order,
                    'matched_text': ''.join(matched_text_parts)
                })

        return {
            'text': text,
            'readings': unique_readings,
            'is_ambiguous': len(unique_readings) > 1,
            'unmatched': []  # TODO: Track any unmatched characters
        }

    def find_pattern_matches(self, text: str, pattern: str, used: Set[int]) -> List[Dict]:
        """
        Find all ways this pattern could match in the text.
        Considers different cluster sizes for 'x' and handles tone marks.
        """
        matches = []

        # Analyze pattern structure
        has_x = 'x' in pattern
        has_f = 'f' in pattern

        # For each possible starting position (including negative for patterns that start before x)
        for start_pos in range(-5, len(text)):
            # For patterns with 'x', try different cluster sizes
            if has_x:
                # Try different cluster sizes (1-3 consonants typically)
                max_cluster = min(3, len(text))  # Limit cluster size
                for cluster_size in range(1, max_cluster + 1):
                    match = self.try_match_pattern_with_foundation(
                        text, start_pos, pattern, used, cluster_size
                    )
                    if match:
                        # Verify no conflicts with used positions
                        if not any(pos in used for pos in match['positions']):
                            matches.append(match)
            else:
                # No 'x' in pattern - direct match
                match = self.try_match_pattern_with_foundation(
                    text, start_pos, pattern, used, 0
                )
                if match and not any(pos in used for pos in match['positions']):
                    matches.append(match)

        return matches

    def try_match_pattern_with_foundation(self, text: str, start_pos: int, pattern: str,
                                         used: Set[int], cluster_size: int) -> Optional[Dict]:
        """
        Try to match a pattern where 'x' represents a complete foundation object
        (consonants + optional tone mark).

        Returns: Dict with match details including foundation objects, or None if no match
        """
        positions = []
        foundation = None
        final_foundation = None
        vowel_text = ""

        text_idx = start_pos
        pattern_idx = 0

        while pattern_idx < len(pattern):
            if text_idx < 0 or text_idx >= len(text):
                return None

            p_char = pattern[pattern_idx]

            if p_char == 'x':
                # Build complete foundation object with tone support
                foundation_result = self.match_foundation(text, text_idx, cluster_size)
                if not foundation_result:
                    return None

                foundation = foundation_result
                positions.extend(foundation['positions'])
                text_idx = foundation['positions'][-1] + 1 if foundation['positions'] else text_idx + 1

            elif p_char == 'f':
                # Match final consonant (single consonant, can have tone)
                final_result = self.match_foundation(text, text_idx, 1)
                if not final_result:
                    return None

                final_foundation = final_result
                positions.extend(final_foundation['positions'])
                text_idx = final_foundation['positions'][-1] + 1 if final_foundation['positions'] else text_idx + 1

            else:
                # Must match exact character (vowel mark)
                if text_idx >= 0 and text_idx < len(text) and text[text_idx] == p_char:
                    vowel_text += text[text_idx]
                    positions.append(text_idx)
                    text_idx += 1
                else:
                    return None

            pattern_idx += 1

        # Verify pattern completely matched
        if pattern_idx != len(pattern):
            return None

        return {
            'pattern': pattern,
            'foundation': foundation,
            'vowel_text': vowel_text,
            'final': final_foundation,
            'positions': positions
        }

    def match_foundation(self, text: str, start_pos: int, consonant_count: int) -> Optional[Dict]:
        """
        Match a foundation: consonant(s) with optional tone mark.

        Returns foundation object with consonants, tone, and positions.
        """
        if start_pos < 0 or start_pos >= len(text):
            return None

        foundation = {
            'consonants': [],
            'tone': None,
            'tone_owner': None,
            'positions': []
        }

        consonants_found = 0
        idx = start_pos

        while consonants_found < consonant_count and idx < len(text):
            # Check if it's a consonant
            if text[idx] not in self.foundation:
                return None

            foundation['consonants'].append(text[idx])
            foundation['positions'].append(idx)
            current_consonant_idx = consonants_found
            consonants_found += 1
            idx += 1

            # Check for tone mark immediately after this consonant
            if idx < len(text) and text[idx] in self.tone_marks:
                foundation['tone'] = text[idx]
                foundation['tone_owner'] = current_consonant_idx
                foundation['positions'].append(idx)
                idx += 1

        # Verify we found the required number of consonants
        if consonants_found != consonant_count:
            return None

        return foundation

    def render_foundation(self, foundation: Optional[Dict]) -> str:
        """
        Render a foundation object as a string with tone mark attached to the correct consonant.
        """
        if not foundation or not foundation.get('consonants'):
            return ""

        result = []
        for i, consonant in enumerate(foundation['consonants']):
            if foundation.get('tone') and foundation.get('tone_owner') == i:
                # Attach tone to this consonant
                result.append(consonant + foundation['tone'])
            else:
                result.append(consonant)

        return ''.join(result)

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze a Thai text and return all possible readings with ambiguity analysis.
        (Wrapper for compatibility)
        """
        return self.findThaiGraphemeOrderDomain(text)


def main():
    """Test the algorithm with provided test cases."""

    # Set UTF-8 encoding for output
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Initialize analyzer
    analyzer = ThaiReadingOrderAnalyzer(
        "res/foundation/foundation.json",
        "thai_vowels_tagged_9-21-2025-2-31-pm.json"
    )

    # Test cases
    test_cases = [
        ("ยา", "simple case"),
        ("เด็ก", "vowel before consonant"),
        ("คน", "hidden vowel"),
        ("เลว", "AMBIGUOUS: ว could be final OR part of cluster"),
        ("เกรียน", "cluster case"),
        ("เอา", "อ as silent initial"),
        ("อย่า", "อ with tone mark"),
        ("เอือม", "อ in complex pattern"),
        ("ไกล", "ไ before consonant")
    ]

    print("\n" + "="*70)
    print("THAI READING ORDER ANALYSIS - Foundation Model")
    print("="*70)

    for thai_text, description in test_cases:
        print(f"\n'{thai_text}' - {description}")
        print("-" * 50)

        result = analyzer.analyze_text(thai_text)

        if result['is_ambiguous']:
            print(f"  AMBIGUOUS - {len(result['readings'])} possible readings:")
            for i, reading in enumerate(result['readings'][:5], 1):
                print(f"  Reading {i}: {' '.join(reading['reading_order'])}")

            if len(result['readings']) > 5:
                print(f"  ... and {len(result['readings']) - 5} more")
        else:
            print(f"  UNAMBIGUOUS - Single reading:")
            if result['readings']:
                print(f"    {' '.join(result['readings'][0]['reading_order'])}")
            else:
                print("    No readings found")


if __name__ == "__main__":
    main()