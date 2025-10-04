#!/usr/bin/env python3
"""
Thai Vowel Pattern Database Loader

Loads and indexes Thai vowel patterns from the tagged JSON file
for use in vowel pattern matching algorithms.
"""

import json
import os
from typing import Dict, List, Set, Tuple


class VowelPatternDatabase:
    """
    Loads and provides access to Thai vowel patterns

    Pattern notation:
    - 'x' = foundation consonant position (tan)
    - 'a' = foundation consonant position without combining marks
    - 'f' = final consonant position
    - Other characters = actual vowel characters (sara)
    """

    def __init__(self, json_path: str = None):
        """
        Initialize the database

        Args:
            json_path: Path to vowel patterns JSON file
                      If None, uses default path relative to project root
        """
        if json_path is None:
            # Default path: data/thai_vowels_tagged_9-21-2025-2-31-pm.json
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(project_root, "data", "thai_vowels_tagged_9-21-2025-2-31-pm.json")

        self.json_path = json_path
        self.patterns = {}
        self.indexed_patterns = {
            'by_first_char': {},  # Index by first character of pattern
            'by_structure': {},    # Index by structure type (left, right, complex, etc.)
            'by_length': {},       # Index by number of components
        }

        self._load_patterns()
        self._build_indices()

    def _load_patterns(self):
        """Load patterns from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', {})
                print(f"Loaded {len(self.patterns)} vowel patterns from {self.json_path}")
        except FileNotFoundError:
            print(f"Warning: Pattern file not found: {self.json_path}")
            self.patterns = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            self.patterns = {}

    def _build_indices(self):
        """Build search indices for fast pattern lookup"""
        for pattern_key, pattern_data in self.patterns.items():
            # Parse pattern structure
            structure = self._analyze_pattern_structure(pattern_key)

            # Index by first character
            first_char = structure['first_char']
            if first_char:
                if first_char not in self.indexed_patterns['by_first_char']:
                    self.indexed_patterns['by_first_char'][first_char] = []
                self.indexed_patterns['by_first_char'][first_char].append({
                    'key': pattern_key,
                    'data': pattern_data,
                    'structure': structure
                })

            # Index by structure type
            struct_type = structure['type']
            if struct_type not in self.indexed_patterns['by_structure']:
                self.indexed_patterns['by_structure'][struct_type] = []
            self.indexed_patterns['by_structure'][struct_type].append({
                'key': pattern_key,
                'data': pattern_data,
                'structure': structure
            })

            # Index by length (number of components)
            length = structure['component_count']
            if length not in self.indexed_patterns['by_length']:
                self.indexed_patterns['by_length'][length] = []
            self.indexed_patterns['by_length'][length].append({
                'key': pattern_key,
                'data': pattern_data,
                'structure': structure
            })

    def _analyze_pattern_structure(self, pattern_key: str) -> Dict:
        """
        Analyze a pattern key to determine its structure

        Args:
            pattern_key: Pattern key like "xว", "เxา", "เxีย", etc.

        Returns:
            Dict with structure information
        """
        # Count components
        components = []
        positions = {
            'left': [],      # Characters before 'x'
            'above_below': [],  # Combining characters (would appear after 'x')
            'right': [],     # Characters after 'x' (non-combining)
            'final': False   # Whether pattern has 'f' for final consonant
        }

        # Parse pattern
        i = 0
        before_x = True

        while i < len(pattern_key):
            char = pattern_key[i]

            if char == 'x':
                before_x = False
                components.append(('base', 'x'))
            elif char == 'f':
                positions['final'] = True
                components.append(('final', 'f'))
            elif char == 'a':
                # Alternative base notation
                components.append(('base', 'a'))
                before_x = False
            else:
                # Actual vowel character
                if before_x:
                    positions['left'].append(char)
                    components.append(('left', char))
                else:
                    # Determine if combining or not
                    # This is a simplification - actual combining detection
                    # would need Unicode analysis
                    positions['right'].append(char)
                    components.append(('right', char))

            i += 1

        # Determine structure type
        if positions['left'] and positions['right']:
            struct_type = 'split'  # Vowel parts on both sides
        elif positions['left']:
            struct_type = 'left'
        elif positions['right']:
            struct_type = 'right'
        else:
            struct_type = 'simple'

        # Get first actual character (not x, f, or a)
        first_char = None
        for comp_type, char in components:
            if comp_type in ('left', 'right') and char not in ('x', 'f', 'a'):
                first_char = char
                break

        return {
            'type': struct_type,
            'positions': positions,
            'components': components,
            'component_count': len([c for c in components if c[0] != 'base']),
            'first_char': first_char,
            'has_final': positions['final']
        }

    def find_patterns_by_first_char(self, char: str) -> List[Dict]:
        """Find all patterns that start with a specific character"""
        return self.indexed_patterns['by_first_char'].get(char, [])

    def find_patterns_by_structure(self, struct_type: str) -> List[Dict]:
        """
        Find patterns by structure type

        Args:
            struct_type: 'left', 'right', 'split', or 'simple'
        """
        return self.indexed_patterns['by_structure'].get(struct_type, [])

    def find_patterns_by_length(self, length: int) -> List[Dict]:
        """Find patterns with specific number of components"""
        return self.indexed_patterns['by_length'].get(length, [])

    def get_pattern(self, key: str) -> Dict:
        """Get a specific pattern by its key"""
        return self.patterns.get(key)

    def get_all_patterns(self) -> Dict:
        """Get all patterns"""
        return self.patterns

    def search_patterns(self, **criteria) -> List[Dict]:
        """
        Search patterns by multiple criteria

        Args:
            tags: List of tags to match (e.g., ['sound_a', 'length_short'])
            struct_type: Structure type filter
            min_length: Minimum number of components
            max_length: Maximum number of components

        Returns:
            List of matching patterns
        """
        results = []

        tags = criteria.get('tags', [])
        struct_type = criteria.get('struct_type')
        min_length = criteria.get('min_length', 0)
        max_length = criteria.get('max_length', float('inf'))

        for pattern_key, pattern_data in self.patterns.items():
            structure = self._analyze_pattern_structure(pattern_key)

            # Check structure type
            if struct_type and structure['type'] != struct_type:
                continue

            # Check length
            comp_count = structure['component_count']
            if comp_count < min_length or comp_count > max_length:
                continue

            # Check tags
            if tags:
                pattern_tags = set(pattern_data.get('tags', []))
                required_tags = set(tags)
                if not required_tags.issubset(pattern_tags):
                    continue

            results.append({
                'key': pattern_key,
                'data': pattern_data,
                'structure': structure
            })

        return results

    def get_statistics(self) -> Dict:
        """Get statistics about the loaded patterns"""
        return {
            'total_patterns': len(self.patterns),
            'by_structure': {k: len(v) for k, v in self.indexed_patterns['by_structure'].items()},
            'by_length': {k: len(v) for k, v in self.indexed_patterns['by_length'].items()},
            'unique_first_chars': len(self.indexed_patterns['by_first_char'])
        }


# Example usage and testing
if __name__ == "__main__":
    print("Loading Thai Vowel Pattern Database...")
    db = VowelPatternDatabase()

    print("\nDatabase Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nExample: Patterns starting with 'เ':")
    patterns = db.find_patterns_by_first_char('เ')
    for p in patterns[:5]:  # Show first 5
        print(f"  {p['key']}: {p['structure']['type']} structure")

    print("\nExample: Split structure patterns:")
    split_patterns = db.find_patterns_by_structure('split')
    for p in split_patterns[:5]:
        print(f"  {p['key']}")
