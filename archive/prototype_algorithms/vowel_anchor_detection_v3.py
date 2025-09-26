#!/usr/bin/env python3
"""
Vowel Anchor Detection Algorithm v3
Uses IDs stored in database with corrected format:
- Abbreviated: a_s_o, ai_s_c_jg_1
- Long: a_short_open, ai_short_closed_jglide_1
"""

import json
import sys
import io
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class VowelAnchor:
    """Represents a detected vowel pattern in text"""
    pattern: str           # The vowel pattern (e.g., "xา", "เx็f")
    abbrev_id: str         # Abbreviated ID from database
    long_id: str           # Long ID from database
    start_pos: int         # Start position in text
    end_pos: int           # End position in text
    foundation_pos: int    # Position where foundation ('x') should be
    final_pos: Optional[int] = None  # Position where final ('f') should be if present
    confidence: float = 1.0  # Confidence score for ambiguous cases

@dataclass
class PatternInfo:
    """Metadata for a vowel pattern"""
    pattern: str
    abbrev_id: str
    long_id: str
    tags: List[str]
    priority: int  # For resolving conflicts (longer patterns have higher priority)

class VowelAnchorDetectorV3:
    """Detects vowel patterns in Thai text using database-stored IDs"""

    def __init__(self, vowel_patterns_file: str):
        """Initialize with vowel pattern data including IDs"""
        with open(vowel_patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Build pattern registry from database
        self.patterns = {}
        self.pattern_by_abbrev = {}
        self.pattern_by_long = {}

        for pattern, info in data['patterns'].items():
            # Get IDs from database
            abbrev_id = info.get('abbrev_id', 'UNKNOWN')
            long_id = info.get('long_id', 'UNKNOWN')
            tags = info.get('tags', [])

            # Store pattern info
            pattern_info = PatternInfo(
                pattern=pattern,
                abbrev_id=abbrev_id,
                long_id=long_id,
                tags=tags,
                priority=len(pattern)  # Longer patterns get higher priority
            )

            self.patterns[pattern] = pattern_info
            self.pattern_by_abbrev[abbrev_id] = pattern_info
            self.pattern_by_long[long_id] = pattern_info

        # Build character sets for quick filtering
        self.vowel_marks = {'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู',
                           'เ', 'แ', 'โ', 'ใ', 'ไ', '็', '่', '้', '๊', '๋'}
        self.ambiguous_chars = {'ว', 'ย', 'อ', 'ร'}  # Can be consonant or vowel component
        self.tone_marks = {'่', '้', '๊', '๋'}

        # Sort patterns by priority (longest first) for matching
        self.sorted_patterns = sorted(self.patterns.values(),
                                     key=lambda p: p.priority,
                                     reverse=True)

        print(f"Loaded {len(self.patterns)} vowel patterns with IDs from database")
        print(f"Sample IDs:")
        for pattern in ["xา", "xาย", "xาว", "ใx", "ไxย"]:
            if pattern in self.patterns:
                info = self.patterns[pattern]
                print(f"  {pattern}: {info.abbrev_id} / {info.long_id}")

    def detect_vowel_anchors(self, text: str) -> List[VowelAnchor]:
        """
        Detect all vowel patterns in Thai text.
        Returns list of VowelAnchor objects sorted by position.
        """
        anchors = []
        text_len = len(text)
        used_positions = set()

        # Scan through text
        for i in range(text_len):
            # Quick check: is there a potential vowel component here?
            if not self._has_vowel_potential(text, i):
                continue

            # Try to match patterns at this position
            matches = self._find_pattern_matches_at_position(text, i, used_positions)

            # Add best match if found
            if matches:
                best_match = matches[0]  # Already sorted by priority
                anchors.append(best_match)

                # Mark positions as used
                for pos in range(best_match.start_pos, best_match.end_pos + 1):
                    used_positions.add(pos)
                if best_match.foundation_pos is not None:
                    used_positions.add(best_match.foundation_pos)
                if best_match.final_pos is not None:
                    used_positions.add(best_match.final_pos)

        # Sort anchors by position
        anchors.sort(key=lambda a: a.start_pos)

        return anchors

    def _has_vowel_potential(self, text: str, pos: int) -> bool:
        """Check if position could be part of a vowel pattern"""
        if pos >= len(text):
            return False

        char = text[pos]

        # Explicit vowel mark (excluding tone marks for primary detection)
        if char in self.vowel_marks and char not in self.tone_marks:
            return True

        # Ambiguous character that might be part of vowel
        if char in self.ambiguous_chars:
            # Check context to determine if likely vowel component
            return self._check_ambiguous_context(text, pos)

        return False

    def _check_ambiguous_context(self, text: str, pos: int) -> bool:
        """Check if ambiguous character is likely part of vowel pattern"""
        char = text[pos]

        # Enhanced heuristics
        if char == 'ว':
            # Check if preceded by consonant (likely vowel)
            if pos > 0 and text[pos-1] not in self.vowel_marks:
                return True
            # Check if part of xัว pattern
            if pos > 1 and text[pos-1] == 'ั':
                return True

        if char == 'ย':
            # Check if at end or followed by space/punctuation (likely final)
            if pos == len(text) - 1 or (pos < len(text) - 1 and text[pos+1] in ' .,!?'):
                return True
            # Check if part of xาย, xัย patterns
            if pos > 1 and text[pos-1] in 'าั':
                return True

        if char == 'อ':
            # Check if followed by vowel mark (likely part of pattern)
            if pos < len(text) - 1 and text[pos+1] in self.vowel_marks:
                return True
            # Check if preceded by เ (เอ pattern)
            if pos > 0 and text[pos-1] == 'เ':
                return True

        return False

    def _find_pattern_matches_at_position(self, text: str, pos: int,
                                         used: Set[int]) -> List[VowelAnchor]:
        """Find all patterns that could match at or near this position"""
        matches = []

        for pattern_info in self.sorted_patterns:
            pattern = pattern_info.pattern

            # Try different alignment strategies
            # Strategy 1: Pattern starts at current position
            anchor = self._try_match_pattern(text, pos, pattern_info, used, 'start')
            if anchor:
                matches.append(anchor)

            # Strategy 2: Pattern's 'x' aligns with current position
            if 'x' in pattern:
                anchor = self._try_match_pattern(text, pos, pattern_info, used, 'foundation')
                if anchor:
                    matches.append(anchor)

            # Strategy 3: Pattern ends at current position
            anchor = self._try_match_pattern(text, pos, pattern_info, used, 'end')
            if anchor:
                matches.append(anchor)

        # Sort by confidence and priority
        matches.sort(key=lambda m: (m.confidence, self.patterns[m.pattern].priority),
                    reverse=True)

        return matches

    def _try_match_pattern(self, text: str, pos: int, pattern_info: PatternInfo,
                           used: Set[int], alignment: str) -> Optional[VowelAnchor]:
        """Try to match a pattern with specific alignment"""
        pattern = pattern_info.pattern

        # Calculate starting position based on alignment
        if alignment == 'start':
            start_pos = pos
        elif alignment == 'foundation':
            # Find where pattern starts if 'x' is at pos
            x_index = pattern.index('x') if 'x' in pattern else 0
            start_pos = pos - x_index
        elif alignment == 'end':
            start_pos = pos - len(pattern) + 1
        else:
            return None

        # Check bounds
        if start_pos < 0 or start_pos + len(pattern) > len(text):
            return None

        # Try to match pattern
        foundation_pos = None
        final_pos = None
        matched_positions = []

        pattern_idx = 0
        text_idx = start_pos

        while pattern_idx < len(pattern):
            p_char = pattern[pattern_idx]

            if p_char == 'x':
                # Foundation placeholder - skip consonant(s)
                foundation_pos = text_idx
                # For now, assume single consonant (can be enhanced for clusters)
                if text_idx < len(text) and text[text_idx] not in self.vowel_marks:
                    matched_positions.append(text_idx)
                    text_idx += 1
                    # Check for tone mark after consonant
                    if text_idx < len(text) and text[text_idx] in self.tone_marks:
                        text_idx += 1  # Skip tone mark but don't add to matched positions
                else:
                    return None

            elif p_char == 'f':
                # Final consonant placeholder
                final_pos = text_idx
                if text_idx < len(text) and text[text_idx] not in self.vowel_marks:
                    matched_positions.append(text_idx)
                    text_idx += 1
                else:
                    return None

            else:
                # Must match exact character
                if text_idx < len(text) and text[text_idx] == p_char:
                    matched_positions.append(text_idx)
                    text_idx += 1
                else:
                    return None

            pattern_idx += 1

        # Check if any positions are already used
        if any(pos in used for pos in matched_positions):
            return None

        # Create anchor with IDs from database
        return VowelAnchor(
            pattern=pattern,
            abbrev_id=pattern_info.abbrev_id,
            long_id=pattern_info.long_id,
            start_pos=min(matched_positions) if matched_positions else start_pos,
            end_pos=max(matched_positions) if matched_positions else start_pos,
            foundation_pos=foundation_pos,
            final_pos=final_pos,
            confidence=1.0  # Can be adjusted based on context
        )

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze Thai text and return vowel anchor analysis with database IDs.
        """
        anchors = self.detect_vowel_anchors(text)

        # Build analysis report
        analysis = {
            'text': text,
            'length': len(text),
            'anchors': [],
            'syllable_count_estimate': len(anchors),
            'coverage': 0.0
        }

        covered_positions = set()

        for anchor in anchors:
            anchor_info = {
                'pattern': anchor.pattern,
                'abbrev_id': anchor.abbrev_id,
                'long_id': anchor.long_id,
                'positions': f"[{anchor.start_pos}-{anchor.end_pos}]",
                'text_segment': text[anchor.start_pos:anchor.end_pos+1] if anchor.end_pos < len(text) else text[anchor.start_pos:],
                'foundation_at': anchor.foundation_pos,
                'final_at': anchor.final_pos
            }

            # Check for glides in tags
            pattern_info = self.patterns[anchor.pattern]
            if 'glide_j' in pattern_info.tags:
                anchor_info['glide'] = 'j-glide (ย)'
            elif 'glide_w' in pattern_info.tags:
                anchor_info['glide'] = 'w-glide (ว)'

            analysis['anchors'].append(anchor_info)

            # Track coverage
            for pos in range(anchor.start_pos, anchor.end_pos + 1):
                covered_positions.add(pos)
            if anchor.foundation_pos is not None:
                covered_positions.add(anchor.foundation_pos)
            if anchor.final_pos is not None:
                covered_positions.add(anchor.final_pos)

        # Calculate coverage
        if len(text) > 0:
            analysis['coverage'] = len(covered_positions) / len(text)

        return analysis


def main():
    """Test the vowel anchor detection with database IDs"""

    # Initialize detector
    detector = VowelAnchorDetectorV3("thai_vowels_tagged_9-21-2025-2-31-pm.json")

    # Test cases
    test_cases = [
        "ยา",           # Simple: foundation + vowel
        "เด็ก",         # Vowel before foundation
        "คน",           # Hidden vowel
        "เลว",          # Ambiguous ว
        "ไทย",          # With j-glide
        "ขาว",          # With w-glide
        "กาย",          # า + j-glide
        "ประเทศไทย",    # Multi-syllable
        "สวัสดีครับ",    # Common greeting
        "อย่างไร",      # Complex patterns
        "ไกล"           # ไ pattern
    ]

    print("\n" + "=" * 70)
    print("VOWEL ANCHOR DETECTION v3 - Database IDs")
    print("=" * 70)

    for text in test_cases:
        print(f"\nText: '{text}'")
        print("-" * 50)

        analysis = detector.analyze_text(text)

        print(f"Anchors found: {len(analysis['anchors'])}")
        print(f"Coverage: {analysis['coverage']:.1%}")

        for i, anchor in enumerate(analysis['anchors'], 1):
            print(f"\nAnchor {i}:")
            print(f"  Pattern: {anchor['pattern']}")
            print(f"  Abbrev: {anchor['abbrev_id']}")
            print(f"  Long: {anchor['long_id']}")
            print(f"  Segment: '{anchor['text_segment']}'")
            if 'glide' in anchor:
                print(f"  Glide: {anchor['glide']}")


if __name__ == "__main__":
    main()