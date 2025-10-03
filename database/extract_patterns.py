#!/usr/bin/env python3
"""
Extract patterns from labeled data to discover decision rules
"""

import sqlite3
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))
from database.query_utilities import ThaiGraphemeQuery

class PatternExtractor:
    def __init__(self, labels_db="database/thai_syllable_labels.db",
                 graphemes_db="database/thai_avp_graphemes.db"):
        self.labels_db_path = Path(labels_db)
        self.graphemes_db_path = Path(graphemes_db)
        self.query_util = ThaiGraphemeQuery(graphemes_db)

        if not self.labels_db_path.exists():
            raise FileNotFoundError(f"Labels database not found: {self.labels_db_path}")

    def get_labeled_data(self) -> List[Dict]:
        """Retrieve all labeled interpretations"""
        conn = sqlite3.connect(self.labels_db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                w.word,
                l.selected_interpretation_id,
                l.is_custom,
                l.custom_interpretation,
                i.interpretation_json
            FROM labels l
            JOIN words w ON l.word_id = w.id
            LEFT JOIN interpretations i ON l.selected_interpretation_id = i.id
            WHERE l.is_custom = 0  -- Focus on non-custom for pattern extraction
        """

        cursor.execute(query)
        results = []

        for row in cursor.fetchall():
            word = row[0]
            interp_json = json.loads(row[4]) if row[4] else None

            if interp_json:
                # Get the selected interpretation details
                syllable = interp_json['syllables'][0] if 'syllables' in interp_json else {}

                # Get tags for each component
                tags = self._get_interpretation_tags(syllable)

                results.append({
                    'word': word,
                    'interpretation': syllable,
                    'tags': tags,
                    'pattern': syllable.get('pattern', '')
                })

        conn.close()
        return results

    def _get_interpretation_tags(self, syllable: Dict) -> Dict:
        """Get tags for all components of an interpretation"""
        tags = {}

        # Foundation tags
        if syllable.get('foundation'):
            foundation = syllable['foundation']
            if isinstance(foundation, list):
                foundation_str = ''.join(foundation)
            else:
                foundation_str = foundation
            tags['foundation'] = self.query_util.get_character_tags(foundation_str)

        # Vowel tags
        if syllable.get('vowel'):
            tags['vowel'] = self.query_util.get_character_tags(syllable['vowel'])

        # Final tags
        if syllable.get('final'):
            final = syllable['final']
            if isinstance(final, list):
                final_str = ''.join(final)
            else:
                final_str = final
            tags['final'] = self.query_util.get_character_tags(final_str)

        return tags

    def extract_tag_patterns(self) -> Dict:
        """Extract patterns based on tag combinations"""
        labeled_data = self.get_labeled_data()

        # Pattern: (foundation_tags, vowel_tags, final_tags) -> pattern_template
        tag_patterns = defaultdict(Counter)

        for item in labeled_data:
            tags = item['tags']
            pattern = item['pattern']

            # Create tag signature
            foundation_tags = tuple(sorted(tags.get('foundation', [])))
            vowel_tags = tuple(sorted(tags.get('vowel', [])))
            final_tags = tuple(sorted(tags.get('final', [])))

            tag_signature = (foundation_tags, vowel_tags, final_tags)
            tag_patterns[tag_signature][pattern] += 1

        # Analyze patterns
        rules = []
        for tag_sig, pattern_counts in tag_patterns.items():
            foundation_tags, vowel_tags, final_tags = tag_sig
            total_count = sum(pattern_counts.values())

            if total_count >= 2:  # Minimum support
                most_common = pattern_counts.most_common(1)[0]
                pattern, count = most_common
                confidence = count / total_count

                rule = {
                    'foundation_tags': list(foundation_tags),
                    'vowel_tags': list(vowel_tags),
                    'final_tags': list(final_tags),
                    'pattern': pattern,
                    'support': count,
                    'confidence': confidence,
                    'total_cases': total_count
                }
                rules.append(rule)

        return {
            'rules': sorted(rules, key=lambda x: x['confidence'], reverse=True),
            'total_labeled': len(labeled_data)
        }

    def find_ambiguity_patterns(self) -> Dict:
        """Find patterns in how ambiguous cases are resolved"""
        conn = sqlite3.connect(self.labels_db_path)
        cursor = conn.cursor()

        # Get all words that have multiple interpretations
        query = """
            SELECT w.word, COUNT(DISTINCT i.id) as interp_count
            FROM words w
            JOIN interpretations i ON w.id = i.word_id
            GROUP BY w.id
            HAVING interp_count > 1
        """

        cursor.execute(query)
        ambiguous_words = cursor.fetchall()

        ambiguity_data = []
        for word, count in ambiguous_words:
            # Get the chosen interpretation for this word
            cursor.execute("""
                SELECT l.selected_interpretation_id, i.interpretation_json
                FROM labels l
                JOIN words w ON l.word_id = w.id
                JOIN interpretations i ON l.selected_interpretation_id = i.id
                WHERE w.word = ? AND l.is_custom = 0
            """, (word,))

            result = cursor.fetchone()
            if result:
                selected_id, selected_json = result
                ambiguity_data.append({
                    'word': word,
                    'interpretation_count': count,
                    'selected': json.loads(selected_json)
                })

        conn.close()

        # Analyze patterns in ambiguity resolution
        resolution_patterns = defaultdict(int)
        for item in ambiguity_data:
            syllable = item['selected']['syllables'][0] if 'syllables' in item['selected'] else {}
            pattern = syllable.get('pattern', '')
            resolution_patterns[pattern] += 1

        return {
            'ambiguous_words': len(ambiguous_words),
            'resolution_patterns': dict(resolution_patterns),
            'examples': ambiguity_data[:5]  # First 5 examples
        }

    def get_custom_interpretation_gaps(self) -> List[Dict]:
        """Identify algorithm gaps from custom interpretations"""
        conn = sqlite3.connect(self.labels_db_path)
        cursor = conn.cursor()

        query = """
            SELECT
                w.word,
                l.custom_interpretation,
                l.notes
            FROM labels l
            JOIN words w ON l.word_id = w.id
            WHERE l.is_custom = 1
        """

        cursor.execute(query)
        gaps = []

        for row in cursor.fetchall():
            word = row[0]
            custom = json.loads(row[1]) if row[1] else {}
            notes = row[2]

            gaps.append({
                'word': word,
                'custom_interpretation': custom,
                'notes': notes,
                'pattern': custom.get('pattern', '')
            })

        conn.close()
        return gaps

    def save_patterns_to_db(self, patterns: Dict):
        """Save extracted patterns to database"""
        conn = sqlite3.connect(self.labels_db_path)
        cursor = conn.cursor()

        for rule in patterns.get('rules', []):
            pattern_rule = f"Tags: F={rule['foundation_tags']}, V={rule['vowel_tags']}, Final={rule['final_tags']} → {rule['pattern']}"

            cursor.execute("""
                INSERT INTO extracted_patterns (
                    pattern_rule, pattern_data, support_count, confidence
                ) VALUES (?, ?, ?, ?)
            """, (
                pattern_rule,
                json.dumps(rule),
                rule['support'],
                rule['confidence']
            ))

        conn.commit()
        conn.close()

    def generate_report(self) -> str:
        """Generate a comprehensive pattern analysis report"""
        report = []
        report.append("=" * 60)
        report.append("Thai Syllable Labeling Pattern Analysis")
        report.append("=" * 60)

        # Extract patterns
        patterns = self.extract_tag_patterns()
        report.append(f"\nTotal labeled interpretations: {patterns['total_labeled']}")

        report.append("\nTop Patterns (by confidence):")
        report.append("-" * 40)

        for i, rule in enumerate(patterns['rules'][:10], 1):
            report.append(f"\n{i}. Pattern: {rule['pattern']}")
            report.append(f"   Foundation tags: {', '.join(rule['foundation_tags']) if rule['foundation_tags'] else 'none'}")
            report.append(f"   Vowel tags: {', '.join(rule['vowel_tags']) if rule['vowel_tags'] else 'none'}")
            report.append(f"   Final tags: {', '.join(rule['final_tags']) if rule['final_tags'] else 'none'}")
            report.append(f"   Support: {rule['support']} cases")
            report.append(f"   Confidence: {rule['confidence']:.1%}")

        # Ambiguity patterns
        ambiguity = self.find_ambiguity_patterns()
        report.append(f"\n\nAmbiguity Resolution:")
        report.append("-" * 40)
        report.append(f"Ambiguous words labeled: {ambiguity['ambiguous_words']}")

        if ambiguity['resolution_patterns']:
            report.append("\nPreferred patterns for ambiguous cases:")
            for pattern, count in ambiguity['resolution_patterns'].items():
                report.append(f"  {pattern}: {count} times")

        # Algorithm gaps
        gaps = self.get_custom_interpretation_gaps()
        if gaps:
            report.append(f"\n\nAlgorithm Gaps (Custom Interpretations):")
            report.append("-" * 40)
            report.append(f"Total custom interpretations: {len(gaps)}")

            for gap in gaps[:5]:
                report.append(f"\nWord: {gap['word']}")
                report.append(f"  Custom pattern: {gap['pattern']}")
                if gap['notes']:
                    report.append(f"  Notes: {gap['notes']}")

        return '\n'.join(report)

def main():
    """Run pattern extraction and display report"""
    extractor = PatternExtractor()

    try:
        report = extractor.generate_report()
        print(report)

        # Save patterns to database
        patterns = extractor.extract_tag_patterns()
        if patterns['rules']:
            extractor.save_patterns_to_db(patterns)
            print("\n\n[OK] Patterns saved to database")

    except Exception as e:
        print(f"Error during pattern extraction: {e}")

if __name__ == "__main__":
    main()