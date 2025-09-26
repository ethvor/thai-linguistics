#!/usr/bin/env python3
"""
Vowel Anchor Detection Algorithm v2
Enhanced with dual ID system (abbreviated and long forms)
Based on Voraritskul Conjecture for Thai Segmentation
"""

import json
import sys
import io
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class VowelAnchor:
    """Represents a detected vowel pattern in text"""
    pattern: str           # The vowel pattern (e.g., "xา", "เx็f")
    abbrev_id: str         # Abbreviated ID (e.g., "alo", "escjg")
    long_id: str           # Long ID (e.g., "a_lengthlong_vowelopen")
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
    sound: str
    length: str
    openness: str
    has_jglide: bool
    has_wglide: bool
    priority: int  # For resolving conflicts (longer patterns have higher priority)

class VowelAnchorDetectorV2:
    """Detects vowel patterns in Thai text using enhanced ID system"""

    def __init__(self, vowel_patterns_file: str):
        """Initialize with vowel pattern data"""
        with open(vowel_patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Build pattern registry with dual IDs
        self.patterns = {}
        self.pattern_by_abbrev = {}
        self.pattern_by_long = {}

        # Track duplicates for numbering
        abbrev_counts = defaultdict(int)
        long_counts = defaultdict(int)

        for pattern, info in data['patterns'].items():
            tags = info.get('tags', [])

            # Extract components
            sound = next((t.replace('sound_', '') for t in tags if t.startswith('sound_')), 'X')
            length = next((t.replace('length_', '') for t in tags if t.startswith('length_')), 'X')
            openness = next((t.replace('vowel_', '') for t in tags if t.startswith('vowel_')), 'X')

            # Detect glides
            has_jglide = 'glide_j' in tags or pattern.endswith('ย')
            has_wglide = 'glide_w' in tags or pattern.endswith('ว')

            # Build abbreviated ID
            abbrev_base = f"{sound}{length[0] if length != 'X' else 'X'}{openness[0] if openness != 'X' else 'X'}"
            if has_jglide:
                abbrev_base += "jg"
            elif has_wglide:
                abbrev_base += "wg"

            # Handle duplicates for abbreviated
            if abbrev_base in abbrev_counts:
                abbrev_counts[abbrev_base] += 1
                abbrev_id = f"{abbrev_base}{abbrev_counts[abbrev_base]}"
            else:
                abbrev_counts[abbrev_base] = 1
                abbrev_id = abbrev_base

            # Build long ID
            long_base = f"{sound}_length{length}_vowel{openness}"
            if has_jglide:
                long_base += "_jglide"
            elif has_wglide:
                long_base += "_wglide"

            # Handle duplicates for long form
            if long_base in long_counts:
                long_counts[long_base] += 1
                long_id = f"{long_base}_{long_counts[long_base]}"
            else:
                long_counts[long_base] = 1
                long_id = long_base

            # Store pattern info
            pattern_info = PatternInfo(
                pattern=pattern,
                abbrev_id=abbrev_id,
                long_id=long_id,
                sound=sound,
                length=length,
                openness=openness,
                has_jglide=has_jglide,
                has_wglide=has_wglide,
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

        print(f"Loaded {len(self.patterns)} vowel patterns")
        print(f"Unique abbreviated IDs: {len(set(p.abbrev_id for p in self.patterns.values()))}")
        print(f"Unique long IDs: {len(set(p.long_id for p in self.patterns.values()))}")

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

        # Create anchor with dual IDs
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
        Analyze Thai text and return vowel anchor analysis with dual IDs.
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

            # Add glide information
            pattern_info = self.patterns[anchor.pattern]
            if pattern_info.has_jglide:
                anchor_info['glide'] = 'j-glide (ย)'
            elif pattern_info.has_wglide:
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
    """Test the enhanced vowel anchor detection algorithm"""

    # Initialize detector
    detector = VowelAnchorDetectorV2("thai_vowels_tagged_9-21-2025-2-31-pm.json")

    # Test cases - include some with glides
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
    print("VOWEL ANCHOR DETECTION v2 - Enhanced ID System")
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
            print(f"  Abbrev ID: {anchor['abbrev_id']}")
            print(f"  Long ID: {anchor['long_id']}")
            print(f"  Positions: {anchor['positions']}")
            print(f"  Segment: '{anchor['text_segment']}'")
            if 'glide' in anchor:
                print(f"  Glide: {anchor['glide']}")
            if anchor['foundation_at'] is not None:
                print(f"  Foundation at: {anchor['foundation_at']}")
            if anchor['final_at'] is not None:
                print(f"  Final at: {anchor['final_at']}")

    # Show ID examples
    print("\n" + "=" * 70)
    print("SAMPLE ID MAPPINGS")
    print("=" * 70)

    sample_patterns = ["xา", "xาย", "xาว", "ใx", "ไxย", "เx็f", "xัว", "xอย"]
    for pattern in sample_patterns:
        if pattern in detector.patterns:
            info = detector.patterns[pattern]
            print(f"{pattern:8} → {info.abbrev_id:10} | {info.long_id}")
            if info.has_jglide:
                print(f"         ↳ Has J-glide")
            if info.has_wglide:
                print(f"         ↳ Has W-glide")


if __name__ == "__main__":
    main()