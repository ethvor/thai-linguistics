#!/usr/bin/env python3
"""
Thai Vowel Pattern Matcher

Matches sara (vowel) sequences against the vowel pattern database
to identify complete vowel patterns in Thai text.
"""

from typing import List, Dict, Tuple, Optional
from pattern_database import VowelPatternDatabase
from renderer import transform_intermediate_classifications


class VowelPatternMatcher:
    """
    Matches Thai vowel patterns using intermediate classifications

    Algorithm:
    1. Transform classifications to intermediate form (tan→a/x, remove yuk/diacritic)
    2. Extract sara sequences and their positions
    3. Match sequences against pattern database
    4. Return identified patterns with metadata
    """

    def __init__(self, pattern_db: VowelPatternDatabase = None):
        """
        Initialize matcher

        Args:
            pattern_db: VowelPatternDatabase instance (creates new if None)
        """
        self.db = pattern_db if pattern_db else VowelPatternDatabase()

    def find_patterns(self, classifications: List[Dict]) -> List[Dict]:
        """
        Find all vowel patterns in classified text

        Args:
            classifications: List of character classifications from server.classify_text()

        Returns:
            List of identified patterns with positions and metadata
        """
        # Transform to intermediate form
        intermediate = transform_intermediate_classifications(classifications)

        # Find potential pattern boundaries
        patterns = []
        i = 0

        while i < len(intermediate):
            char_info = intermediate[i]

            # Look for pattern starting points
            # Patterns can start with:
            # 1. Left vowels (sara before base)
            # 2. Base consonant followed by sara
            # 3. Exception characters that could be vowel parts

            if char_info['class'] == 'sara':
                # Left vowel - look for pattern like "เx..." or "แx..."
                pattern = self._try_match_left_vowel_pattern(intermediate, i)
                if pattern:
                    patterns.append(pattern)
                    i = pattern['end_index'] + 1
                    continue

            elif char_info['class'] in ('tan', 'kho_yok_waen'):
                # Base consonant - look for following sara
                pattern = self._try_match_base_pattern(intermediate, i)
                if pattern:
                    patterns.append(pattern)
                    i = pattern['end_index'] + 1
                    continue

            i += 1

        return patterns

    def _try_match_left_vowel_pattern(self, intermediate: List[Dict], start_index: int) -> Optional[Dict]:
        """
        Try to match a pattern starting with a left vowel

        Args:
            intermediate: Intermediate classifications
            start_index: Index of left vowel character

        Returns:
            Pattern dict if match found, None otherwise
        """
        # Collect left vowel(s)
        left_vowels = []
        i = start_index

        while i < len(intermediate) and intermediate[i]['class'] == 'sara':
            left_vowels.append(intermediate[i])
            i += 1

        # Must have a base consonant after left vowels
        if i >= len(intermediate) or intermediate[i]['class'] not in ('tan', 'kho_yok_waen'):
            return None

        base_index = i
        base_char = intermediate[i]
        i += 1

        # Collect right vowels (sara after base)
        right_vowels = []
        while i < len(intermediate) and intermediate[i]['class'] == 'sara':
            right_vowels.append(intermediate[i])
            i += 1

        # Build pattern string to match against database
        # Format: left_chars + 'x' + right_chars
        pattern_string = ''.join([v['char'] for v in left_vowels]) + 'x'
        if right_vowels:
            pattern_string += ''.join([v['char'] for v in right_vowels])

        # Try to find match in database
        matches = self._find_database_matches(pattern_string, left_vowels, right_vowels)

        if matches:
            best_match = matches[0]  # Use first match for now
            return {
                'pattern_key': best_match['key'],
                'pattern_data': best_match['data'],
                'start_index': start_index,
                'end_index': i - 1,
                'base_index': base_index,
                'left_vowels': left_vowels,
                'right_vowels': right_vowels,
                'base_char': base_char,
                'match_type': 'left_pattern'
            }

        return None

    def _try_match_base_pattern(self, intermediate: List[Dict], start_index: int) -> Optional[Dict]:
        """
        Try to match a pattern starting with a base consonant

        Args:
            intermediate: Intermediate classifications
            start_index: Index of base consonant

        Returns:
            Pattern dict if match found, None otherwise
        """
        base_index = start_index
        base_char = intermediate[start_index]
        i = start_index + 1

        # Collect right vowels after base
        right_vowels = []
        while i < len(intermediate) and intermediate[i]['class'] == 'sara':
            right_vowels.append(intermediate[i])
            i += 1

        # If no vowels found, not a pattern
        if not right_vowels:
            return None

        # Build pattern string: 'x' + right_chars
        pattern_string = 'x' + ''.join([v['char'] for v in right_vowels])

        # Try to find match in database
        matches = self._find_database_matches(pattern_string, [], right_vowels)

        if matches:
            best_match = matches[0]
            return {
                'pattern_key': best_match['key'],
                'pattern_data': best_match['data'],
                'start_index': start_index,
                'end_index': i - 1,
                'base_index': base_index,
                'left_vowels': [],
                'right_vowels': right_vowels,
                'base_char': base_char,
                'match_type': 'right_pattern'
            }

        return None

    def _find_database_matches(self, pattern_string: str, left_vowels: List, right_vowels: List) -> List[Dict]:
        """
        Find matching patterns in database

        Args:
            pattern_string: Pattern string like "เx", "xา", "เxา", etc.
            left_vowels: List of left vowel character info
            right_vowels: List of right vowel character info

        Returns:
            List of matching patterns from database
        """
        # Direct match
        direct_match = self.db.get_pattern(pattern_string)
        if direct_match:
            return [{
                'key': pattern_string,
                'data': direct_match,
                'match_quality': 'exact'
            }]

        # Try partial matches by structure
        matches = []

        # Determine structure type
        if left_vowels and right_vowels:
            struct_type = 'split'
        elif left_vowels:
            struct_type = 'left'
        elif right_vowels:
            struct_type = 'right'
        else:
            struct_type = 'simple'

        # Search by structure and first character
        first_char = None
        if left_vowels:
            first_char = left_vowels[0]['char']
        elif right_vowels:
            first_char = right_vowels[0]['char']

        if first_char:
            candidates = self.db.find_patterns_by_first_char(first_char)
            for candidate in candidates:
                if candidate['structure']['type'] == struct_type:
                    matches.append({
                        'key': candidate['key'],
                        'data': candidate['data'],
                        'match_quality': 'structural'
                    })

        return matches

    def format_pattern_results(self, patterns: List[Dict], original_text: str) -> str:
        """
        Format pattern results for display

        Args:
            patterns: List of identified patterns
            original_text: Original Thai text

        Returns:
            Formatted string with pattern information
        """
        output = []
        output.append(f"Found {len(patterns)} vowel patterns in text: {original_text}")
        output.append("")

        for i, pattern in enumerate(patterns, 1):
            output.append(f"Pattern {i}:")
            output.append(f"  Key: {pattern['pattern_key']}")
            output.append(f"  Type: {pattern['match_type']}")
            output.append(f"  Position: {pattern['start_index']}-{pattern['end_index']}")
            output.append(f"  Base consonant: {pattern['base_char']['char']} (index {pattern['base_index']})")

            if pattern['left_vowels']:
                left_chars = ''.join([v['char'] for v in pattern['left_vowels']])
                output.append(f"  Left vowels: {left_chars}")

            if pattern['right_vowels']:
                right_chars = ''.join([v['char'] for v in pattern['right_vowels']])
                output.append(f"  Right vowels: {right_chars}")

            # Add tags if available
            tags = pattern['pattern_data'].get('tags', [])
            if tags:
                output.append(f"  Tags: {', '.join(tags[:5])}")  # Show first 5 tags

            output.append("")

        return '\n'.join(output)


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os

    # Add src directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from server import classify_character

    print("Thai Vowel Pattern Matcher - Test Mode")
    print("=" * 80)

    # Initialize matcher
    matcher = VowelPatternMatcher()

    # Test text
    test_text = "เมืองเชียงใหม่เรียนรู้เกี่ยวกับครูแชมป์"
    print(f"\nTest text: {test_text}")

    # Classify text
    classifications = []
    for i, char in enumerate(test_text):
        classification = classify_character(char, i, test_text, {})
        classifications.append({
            "index": i,
            "char": char,
            "class": classification["class"],
            "avp": classification["avp"]
        })

    # Find patterns
    print("\nFinding vowel patterns...")
    patterns = matcher.find_patterns(classifications)

    # Display results
    print(matcher.format_pattern_results(patterns, test_text))

    print("=" * 80)
