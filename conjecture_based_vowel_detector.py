#!/usr/bin/env python3
"""
Conjecture-Based Vowel Detector
Uses Voraritskul Conjecture and Two-Character Proximity Conjecture as axioms
Modular, rule-based architecture for extensibility
"""

import json
import sys
import io
from typing import Dict, List, Tuple, Set, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Set UTF-8 encoding (skip for Jupyter notebooks)
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class VowelType(Enum):

    """Type of vowel detected"""
    EXPLICIT = "explicit"      # Visible vowel mark
    HIDDEN = "hidden"          # Inferred from proximity rule
    AMBIGUOUS = "ambiguous"    # Could be either (ว, ย, อ)

@dataclass
class VowelCandidate:
    """A potential vowel occurrence"""
    vowel_type: VowelType
    pattern: str              # Pattern template (e.g., "xา", "HIDDEN_xf")
    abbrev_id: str           # Pattern ID
    start_pos: int           # Start position in text
    end_pos: int             # End position in text
    foundation_pos: Optional[int] = None
    final_pos: Optional[int] = None
    evidence: List[str] = field(default_factory=list)  # Why we think this is a vowel

    def __str__(self):
        """Human-readable string representation"""
        pos_info = f"[{self.start_pos}:{self.end_pos}]"
        return f"{self.pattern} ({self.abbrev_id}) {pos_info} - {self.vowel_type.value}"

    def display(self, text: str = None):
        """Detailed human-readable display"""
        print(f"Pattern: {self.pattern}")
        print(f"ID: {self.abbrev_id}")
        print(f"Position: {self.start_pos}-{self.end_pos}")
        print(f"Type: {self.vowel_type.value}")
        if text:
            segment = text[self.start_pos:self.end_pos+1]
            print(f"Text: '{segment}'")
        if self.foundation_pos is not None:
            print(f"Foundation: pos {self.foundation_pos}")
        if self.final_pos is not None:
            print(f"Final: pos {self.final_pos}")
        if self.evidence:
            print(f"Evidence:")
            for i, ev in enumerate(self.evidence, 1):
                print(f"   {i}. {ev}")

    def _repr_html_(self):
        """Jupyter notebook HTML representation"""
        type_color = {
            VowelType.EXPLICIT: "#2e7d32",    # Green
            VowelType.HIDDEN: "#d32f2f",      # Red
            VowelType.AMBIGUOUS: "#f57c00"    # Orange
        }
        color = type_color.get(self.vowel_type, "#666666")

        html = f"""
        <div style="border: 1px solid {color}; border-radius: 8px; padding: 10px; margin: 5px 0; background-color: {color}15;">
            <div style="font-weight: bold; color: {color}; font-size: 14px;">
                {self.pattern} ({self.abbrev_id})
            </div>
            <div style="color: #666; font-size: 12px; margin-top: 4px;">
                Position: {self.start_pos}-{self.end_pos} | Type: {self.vowel_type.value}
            </div>
            {f'<div style="font-size: 11px; color: #888; margin-top: 2px;">Evidence: {"; ".join(self.evidence)}</div>' if self.evidence else ''}
        </div>
        """
        return html

@dataclass
class VowelData:
    """Complete data for a vowel position"""
    vowel_number: int
    candidates: List[VowelCandidate]  # All possible interpretations
    best_candidate: VowelCandidate    # Most likely interpretation
    text_span: Tuple[int, int]        # Overall position range

    def __str__(self):
        """Human-readable string representation"""
        best = f"{self.best_candidate.pattern} ({self.best_candidate.abbrev_id})"
        alt_count = len(self.candidates) - 1
        alt_info = f" +{alt_count} alternatives" if alt_count > 0 else ""
        return f"Vowel {self.vowel_number}: {best}{alt_info}"

    def display(self, text: str = None, show_alternatives: bool = True):
        """Detailed human-readable display"""
        print(f"VOWEL {self.vowel_number}")
        print(f"Span: {self.text_span[0]}-{self.text_span[1]}")
        if text:
            segment = text[self.text_span[0]:self.text_span[1]+1]
            print(f"Text: '{segment}'")

        print(f"\nBEST CANDIDATE:")
        self.best_candidate.display(text)

        if show_alternatives and len(self.candidates) > 1:
            print(f"\nALTERNATIVES ({len(self.candidates)-1}):")
            for i, candidate in enumerate(self.candidates):
                if candidate != self.best_candidate:
                    print(f"   Alternative {i+1}:")
                    candidate.display(text)
                    print()

    def _repr_html_(self):
        """Jupyter notebook HTML representation"""
        best_html = self.best_candidate._repr_html_()

        html = f"""
        <div style="border: 2px solid #1976d2; border-radius: 12px; padding: 15px; margin: 10px 0; background-color: #e3f2fd;">
            <div style="font-weight: bold; color: #1976d2; font-size: 16px; margin-bottom: 10px;">
                Vowel {self.vowel_number} (Span: {self.text_span[0]}-{self.text_span[1]})
            </div>
            <div style="margin-bottom: 8px; font-weight: bold; color: #333;">Best Candidate:</div>
            {best_html}
        """

        if len(self.candidates) > 1:
            html += f"""
            <div style="margin-top: 10px; font-weight: bold; color: #333;">
                Alternatives ({len(self.candidates)-1}):
            </div>
            """
            for candidate in self.candidates:
                if candidate != self.best_candidate:
                    html += candidate._repr_html_()

        html += "</div>"
        return html

class RuleEngine:
    """Modular rule engine for processing vowel detection rules"""

    def __init__(self):
        self.pre_rules = []    # Rules before main detection
        self.detect_rules = [] # Main detection rules
        self.post_rules = []   # Rules after detection (filtering, validation)

    def add_pre_rule(self, rule: Callable, name: str):
        """Add a preprocessing rule"""
        self.pre_rules.append((name, rule))

    def add_detect_rule(self, rule: Callable, name: str):
        """Add a detection rule"""
        self.detect_rules.append((name, rule))

    def add_post_rule(self, rule: Callable, name: str):
        """Add a post-processing rule"""
        self.post_rules.append((name, rule))


class ConjectureBasedVowelDetector:
    """Main vowel detector using conjectures as axioms"""

    def __init__(self, patterns_file: str):
        """Initialize with pattern database"""
        with open(patterns_file, 'r', encoding='utf-8') as f:
            self.pattern_data = json.load(f)

        # Character sets
        self.consonants = {
            'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
            'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
            'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
            'ส', 'ห', 'ฬ', 'อ', 'ฮ'
        }

        self.vowel_marks = {
            'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู',
            'เ', 'แ', 'โ', 'ใ', 'ไ', '็'
        }

        self.pre_vowels = {'เ', 'แ', 'โ', 'ใ', 'ไ'}  # Vowels that come before consonant
        self.tone_marks = {'่', '้', '๊', '๋'}
        self.ambiguous_chars = {'ว', 'ย', 'อ'}  # Can be consonant or vowel

        # Initialize rule engine
        self.rules = RuleEngine()
        self._register_default_rules()

        # Cache for pattern lookups
        self._build_pattern_index()

    def _build_pattern_index(self):
        """Build indices for fast pattern lookup"""
        self.patterns_by_start = {}  # Patterns grouped by starting character
        self.patterns_by_vowel = {}  # Patterns containing specific vowel marks

        for pattern, info in self.pattern_data['patterns'].items():
            # Index by first character
            if pattern[0] != 'x':
                first_char = pattern[0]
                if first_char not in self.patterns_by_start:
                    self.patterns_by_start[first_char] = []
                self.patterns_by_start[first_char].append((pattern, info))

            # Index by vowel marks contained
            for char in pattern:
                if char in self.vowel_marks:
                    if char not in self.patterns_by_vowel:
                        self.patterns_by_vowel[char] = []
                    self.patterns_by_vowel[char].append((pattern, info))

    def _register_default_rules(self):
        """Register the default rules based on our conjectures"""

        # DETECTION RULES

        # Rule 1: Explicit vowel detection
        self.rules.add_detect_rule(self._detect_explicit_vowels,
                                  "explicit_vowel_detection")

        # Rule 2: Hidden vowel detection (Two-Character Proximity)
        self.rules.add_detect_rule(self._detect_hidden_vowels,
                                  "hidden_vowel_proximity")

        # Rule 3: Ambiguous character resolution
        self.rules.add_detect_rule(self._detect_ambiguous_vowels,
                                  "ambiguous_character_resolution")

        # POST-PROCESSING RULES

        # Rule 4: Remove overlapping candidates
        self.rules.add_post_rule(self._merge_overlapping_candidates,
                               "merge_overlapping")



    def find_vowels(self, text: str) -> Dict[int, VowelData]:
        """
        Main entry point: Find all vowels using conjecture-based rules
        Returns: Dict with 1-based indexing
        """
        candidates = []

        # Apply detection rules
        for rule_name, rule in self.rules.detect_rules:
            new_candidates = rule(text)
            candidates.extend(new_candidates)

        # Apply post-processing rules
        for rule_name, rule in self.rules.post_rules:
            candidates = rule(text, candidates)


        # Group candidates and create final structure
        vowel_groups = self._group_candidates(candidates)

        # Convert to numbered structure (1-based)
        result = {}
        for idx, (span, group_candidates) in enumerate(vowel_groups, start=1):
            # Select first candidate (they're all equally valid without confidence)
            best = group_candidates[0]

            result[idx] = VowelData(
                vowel_number=idx,
                candidates=group_candidates,
                best_candidate=best,
                text_span=span
            )

        return result

    # === DETECTION RULES ===

    def _detect_explicit_vowels(self, text: str) -> List[VowelCandidate]:
        """Rule: Detect explicit vowel marks and their patterns"""
        candidates = []

        # Scan for vowel marks
        for i, char in enumerate(text):
            if char in self.vowel_marks:
                # Get patterns that could contain this vowel
                possible_patterns = self.patterns_by_vowel.get(char, [])

                # Try to match each pattern around this position
                for pattern, info in possible_patterns:
                    matched = self._try_match_pattern(text, i, pattern, char)
                    if matched:
                        candidate = VowelCandidate(
                            vowel_type=VowelType.EXPLICIT,
                            pattern=pattern,
                            abbrev_id=info.get('abbrev_id', 'unknown'),
                            start_pos=matched['start'],
                            end_pos=matched['end'],
                            foundation_pos=matched.get('foundation_pos'),
                            final_pos=matched.get('final_pos'),
                            evidence=[f"Explicit vowel mark '{char}' at position {i}"]
                        )
                        candidates.append(candidate)

        return candidates

    def _detect_hidden_vowels(self, text: str) -> List[VowelCandidate]:
        """Rule: Detect hidden vowels using Two-Character Proximity"""
        candidates = []

        # Find consonants with no nearby vowels
        for i, char in enumerate(text):
            if char in self.consonants:
                # Check 2-character window
                has_nearby_vowel = False
                for j in range(max(0, i-2), min(len(text), i+3)):
                    if j != i and text[j] in self.vowel_marks:
                        has_nearby_vowel = True
                        break

                if not has_nearby_vowel:
                    # Hidden vowel detected!
                    # Determine pattern based on context
                    pattern = self._infer_hidden_pattern(text, i)

                    candidate = VowelCandidate(
                        vowel_type=VowelType.HIDDEN,
                        pattern=pattern,
                        abbrev_id="o_s_c",  # Default: short 'o' sound
                        start_pos=i,
                        end_pos=i,
                        foundation_pos=i,
                        evidence=[f"No vowel within 2 chars of consonant '{char}' at {i}"]
                    )
                    candidates.append(candidate)

        return candidates

    def _detect_ambiguous_vowels(self, text: str) -> List[VowelCandidate]:
        """Rule: Handle ambiguous characters (ว, ย, อ)"""
        candidates = []

        for i, char in enumerate(text):
            if char in self.ambiguous_chars:
                # Determine if this is likely a vowel based on context
                is_vowel_context = self._check_ambiguous_context(text, i, char)

                if is_vowel_context:
                    # Find patterns containing this character
                    pattern = self._find_ambiguous_pattern(text, i, char)

                    if pattern:
                        candidate = VowelCandidate(
                            vowel_type=VowelType.AMBIGUOUS,
                            pattern=pattern['pattern'],
                            abbrev_id=pattern['abbrev_id'],
                            start_pos=pattern['start'],
                            end_pos=pattern['end'],
                            foundation_pos=pattern.get('foundation_pos'),
                            evidence=[f"Ambiguous '{char}' at {i} in vowel context"]
                        )
                        candidates.append(candidate)

        return candidates

    # === POST-PROCESSING RULES ===

    def _merge_overlapping_candidates(self, text: str,
                                     candidates: List[VowelCandidate]) -> List[VowelCandidate]:
        """Rule: Merge overlapping candidates into groups"""
        if not candidates:
            return candidates

        # Sort by start position
        candidates.sort(key=lambda c: c.start_pos)

        # Keep all candidates but mark relationships
        # This preserves options while showing they're related
        # (Full merging logic would be more complex)
        return candidates




    # === HELPER METHODS ===

    def _try_match_pattern(self, text: str, vowel_pos: int,
                          pattern: str, vowel_char: str) -> Optional[Dict]:
        """Try to match a pattern containing a vowel at given position"""
        # Find where vowel appears in pattern
        vowel_indices = [i for i, c in enumerate(pattern) if c == vowel_char]

        for vowel_idx in vowel_indices:
            # Calculate where pattern would start
            start_pos = vowel_pos - vowel_idx

            if start_pos < 0 or start_pos + len(pattern) > len(text):
                continue

            # Try to match
            match_info = self._match_pattern_at_position(text, start_pos, pattern)
            if match_info:
                return match_info

        return None

    def _match_pattern_at_position(self, text: str, start: int,
                                  pattern: str) -> Optional[Dict]:
        """Match a specific pattern at a specific position"""
        result = {
            'start': start,
            'end': start + len(pattern) - 1,
            'foundation_pos': None,
            'final_pos': None
        }

        text_idx = start
        for p_char in pattern:
            if text_idx >= len(text):
                return None

            if p_char == 'x':
                # Must be consonant
                if text[text_idx] not in self.consonants:
                    return None
                result['foundation_pos'] = text_idx
                text_idx += 1
                # Skip tone if present
                if text_idx < len(text) and text[text_idx] in self.tone_marks:
                    text_idx += 1

            elif p_char == 'f':
                # Must be consonant (final)
                if text[text_idx] not in self.consonants:
                    return None
                result['final_pos'] = text_idx
                text_idx += 1

            else:
                # Must match exact character
                if text[text_idx] != p_char:
                    return None
                text_idx += 1

        result['end'] = text_idx - 1
        return result

    def _infer_hidden_pattern(self, text: str, pos: int) -> str:
        """Infer the hidden vowel pattern type"""
        # Look ahead to see if there's a final consonant
        if pos + 1 < len(text) and text[pos + 1] in self.consonants:
            # Next char is also consonant - could be cluster or C[V]C pattern
            # Need more sophisticated analysis here
            return "HIDDEN_xf"
        else:
            # Isolated consonant or end of word
            return "HIDDEN_x"

    def _check_ambiguous_context(self, text: str, pos: int, char: str) -> bool:
        """Check if ambiguous character is in vowel context"""
        # Simplified heuristics
        if char == 'ว':
            # After consonant, likely vowel
            if pos > 0 and text[pos-1] in self.consonants:
                return True
        elif char == 'ย':
            # At end or after า/ั, likely vowel
            if pos == len(text) - 1 or (pos > 0 and text[pos-1] in 'าั'):
                return True
        elif char == 'อ':
            # Before vowel mark, likely vowel carrier
            if pos < len(text) - 1 and text[pos+1] in self.vowel_marks:
                return True
        return False

    def _find_ambiguous_pattern(self, text: str, pos: int, char: str) -> Optional[Dict]:
        """Find pattern for ambiguous character"""
        # This would need pattern database lookup
        # Simplified version for now
        if char == 'ว':
            return {
                'pattern': 'xว',
                'abbrev_id': 'ua_s_o_wg',
                'start': pos - 1 if pos > 0 else pos,
                'end': pos,
                'foundation_pos': pos - 1 if pos > 0 else None
            }
        return None

    def _group_candidates(self, candidates: List[VowelCandidate]) -> List[Tuple]:
        """Group overlapping candidates"""
        if not candidates:
            return []

        # Sort by start position
        candidates.sort(key=lambda c: c.start_pos)

        groups = []
        current_group = []
        current_span = None

        for candidate in candidates:
            cand_span = (candidate.start_pos, candidate.end_pos)

            if current_span is None:
                current_span = cand_span
                current_group = [candidate]
            elif self._spans_overlap(current_span, cand_span):
                # Extend group
                current_group.append(candidate)
                current_span = (
                    min(current_span[0], cand_span[0]),
                    max(current_span[1], cand_span[1])
                )
            else:
                # New group
                groups.append((current_span, current_group))
                current_span = cand_span
                current_group = [candidate]

        # Add last group
        if current_group:
            groups.append((current_span, current_group))

        return groups

    def _spans_overlap(self, span1: Tuple, span2: Tuple) -> bool:
        """Check if two spans overlap"""
        return not (span1[1] < span2[0] or span2[1] < span1[0])

    # === PUBLIC API FOR ADDING CUSTOM RULES ===

    def add_custom_rule(self, rule_func: Callable, name: str,
                       rule_type: str = "post"):
        """
        Add a custom rule to the engine

        Args:
            rule_func: Function that processes candidates
            name: Name of the rule
            rule_type: "pre", "detect", or "post"
        """
        if rule_type == "pre":
            self.rules.add_pre_rule(rule_func, name)
        elif rule_type == "detect":
            self.rules.add_detect_rule(rule_func, name)
        elif rule_type == "post":
            self.rules.add_post_rule(rule_func, name)
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")


def main():
    """Test the conjecture-based detector"""

    detector = ConjectureBasedVowelDetector("thai_vowels_tagged_9-21-2025-2-31-pm.json")

    test_cases = [
        "ยา",
        "เด็ก",
        "คน",      # Hidden vowel
        "สตรี",    # Hidden vowel in first syllable
        "ประเทศไทย",
        "สวัสดีครับ",
    ]

    print("=" * 70)
    print("CONJECTURE-BASED VOWEL DETECTOR")
    print("=" * 70)

    for text in test_cases:
        print(f"\nText: '{text}'")
        print("-" * 50)

        vowels = detector.find_vowels(text)

        for idx in sorted(vowels.keys()):
            data = vowels[idx]
            print(f"\nVowel {idx}:")
            print(f"  Best: {data.best_candidate.pattern} ({data.best_candidate.vowel_type.value})")
            print(f"  Position: {data.text_span}")
            print(f"  Evidence: {data.best_candidate.evidence}")

            if len(data.candidates) > 1:
                print(f"  Alternatives: {len(data.candidates) - 1}")


# Utility functions for data analysis in notebooks

def analyze_text(text: str, patterns_file: str = "thai_vowels_tagged_9-21-2025-2-31-pm.json"):
    """Quick analysis of Thai text with rich display"""
    detector = ConjectureBasedVowelDetector(patterns_file)
    vowels = detector.find_vowels(text)

    print(f"Analyzing: '{text}'")
    print(f"Found {len(vowels)} vowels")
    print("-" * 50)

    for i in sorted(vowels.keys()):
        vowels[i].display(text, show_alternatives=False)
        print("-" * 30)

    return vowels

def compare_texts(texts: List[str], patterns_file: str = "thai_vowels_tagged_9-21-2025-2-31-pm.json"):
    """Compare vowel detection across multiple texts"""
    detector = ConjectureBasedVowelDetector(patterns_file)

    results = []
    for text in texts:
        vowels = detector.find_vowels(text)
        results.append((text, vowels))

    # Summary table
    print("COMPARISON SUMMARY")
    print(f"{'Text':<15} {'Vowels':<8} {'Hidden':<8} {'Explicit':<8} {'Ambiguous':<10}")
    print("-" * 60)

    for text, vowels in results:
        hidden = sum(1 for v in vowels.values() if v.best_candidate.vowel_type == VowelType.HIDDEN)
        explicit = sum(1 for v in vowels.values() if v.best_candidate.vowel_type == VowelType.EXPLICIT)
        ambiguous = sum(1 for v in vowels.values() if v.best_candidate.vowel_type == VowelType.AMBIGUOUS)

        print(f"{text:<15} {len(vowels):<8} {hidden:<8} {explicit:<8} {ambiguous:<10}")

    return results

def vowel_stats(vowels_dict: Dict[int, VowelData]):
    """Generate statistics about vowel detection results"""
    if not vowels_dict:
        print("No vowels to analyze")
        return

    total = len(vowels_dict)
    by_type = {}
    patterns_used = {}

    for v_data in vowels_dict.values():
        vowel_type = v_data.best_candidate.vowel_type
        pattern = v_data.best_candidate.pattern

        by_type[vowel_type] = by_type.get(vowel_type, 0) + 1
        patterns_used[pattern] = patterns_used.get(pattern, 0) + 1

    print(f"VOWEL ANALYSIS ({total} vowels)")
    print("-" * 30)

    print("By Type:")
    for vowel_type, count in by_type.items():
        percentage = (count/total)*100
        print(f"  {vowel_type.value:>10}: {count:>2} ({percentage:4.1f}%)")

    print("\nMost Common Patterns:")
    sorted_patterns = sorted(patterns_used.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:5]:
        percentage = (count/total)*100
        print(f"  {pattern:>10}: {count:>2} ({percentage:4.1f}%)")

    print(f"\nAverage alternatives per vowel: {sum(len(v.candidates) for v in vowels_dict.values()) / total:.1f}")

def display_vowel_grid(vowels_dict: Dict[int, VowelData], text: str = None):
    """Display vowels in a compact grid format"""
    if not vowels_dict:
        print("No vowels to display")
        return

    print("VOWEL GRID")
    print("-" * 60)

    header = f"{'#':>3} {'Pattern':<12} {'ID':<15} {'Type':<10} {'Pos':<8}"
    if text:
        header += " Text"
    print(header)
    print("-" * 60)

    for i in sorted(vowels_dict.keys()):
        v_data = vowels_dict[i]
        best = v_data.best_candidate

        # Type symbol
        type_symbol = {
            VowelType.EXPLICIT: "E",
            VowelType.HIDDEN: "H",
            VowelType.AMBIGUOUS: "A"
        }[best.vowel_type]

        pos_str = f"{best.start_pos}-{best.end_pos}"
        row = f"{i:>3} {best.pattern:<12} {best.abbrev_id:<15} {type_symbol}{best.vowel_type.value:<9} {pos_str:<8}"

        if text:
            segment = text[v_data.text_span[0]:v_data.text_span[1]+1]
            row += f" '{segment}'"

        print(row)


if __name__ == "__main__":
    main()