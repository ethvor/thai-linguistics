#!/usr/bin/env python3
"""
analyze_validations.py

Query utilities for analyzing invalid interpretation patterns from validation data.
"""

import sqlite3
import json
from pathlib import Path
from collections import Counter, defaultdict


class ValidationAnalyzer:
    def __init__(self, db_path="database/thai_syllable_labels.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def get_invalid_component_stats(self):
        """Get statistics on invalid components marked by users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts by component type
        cursor.execute("""
            SELECT component_type, COUNT(*) as count
            FROM invalid_components
            GROUP BY component_type
            ORDER BY count DESC
        """)
        component_types = cursor.fetchall()

        # Get counts by invalid reason
        cursor.execute("""
            SELECT invalid_reason, COUNT(*) as count
            FROM invalid_components
            WHERE invalid_reason IS NOT NULL
            GROUP BY invalid_reason
            ORDER BY count DESC
        """)
        reasons = cursor.fetchall()

        # Get most problematic values
        cursor.execute("""
            SELECT component_type, component_value, COUNT(*) as count
            FROM invalid_components
            GROUP BY component_type, component_value
            ORDER BY count DESC
            LIMIT 20
        """)
        problematic_values = cursor.fetchall()

        conn.close()

        return {
            'component_types': component_types,
            'reasons': reasons,
            'problematic_values': problematic_values
        }

    def get_validation_summary(self):
        """Get overall validation statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total interpretations by status
        cursor.execute("""
            SELECT validity_status, COUNT(*) as count
            FROM interpretations
            WHERE validity_status != 'unlabeled'
            GROUP BY validity_status
        """)
        status_counts = dict(cursor.fetchall())

        # Total words processed
        cursor.execute("SELECT COUNT(DISTINCT word_id) FROM interpretations")
        total_words = cursor.fetchone()[0]

        # Average interpretations per word
        cursor.execute("""
            SELECT AVG(interp_count) FROM (
                SELECT word_id, COUNT(*) as interp_count
                FROM interpretations
                GROUP BY word_id
            )
        """)
        avg_interpretations = cursor.fetchone()[0] or 0

        # Invalid clusters analysis
        cursor.execute("""
            SELECT component_value, COUNT(*) as count
            FROM invalid_components
            WHERE component_type = 'cluster'
            GROUP BY component_value
            ORDER BY count DESC
            LIMIT 10
        """)
        invalid_clusters = cursor.fetchall()

        conn.close()

        return {
            'total_words': total_words,
            'avg_interpretations_per_word': round(avg_interpretations, 2),
            'validation_counts': status_counts,
            'top_invalid_clusters': invalid_clusters
        }

    def find_patterns_in_invalid_finals(self):
        """Analyze patterns in components marked as invalid finals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT component_value, COUNT(*) as occurrences
            FROM invalid_components
            WHERE component_type = 'final'
            GROUP BY component_value
            ORDER BY occurrences DESC
        """)

        invalid_finals = cursor.fetchall()
        conn.close()

        print("\n=== Invalid Final Consonants Analysis ===")
        print("Characters frequently marked as invalid in final position:")
        for final, count in invalid_finals[:10]:
            print(f"  {final}: {count} occurrences")

        return invalid_finals

    def analyze_vowel_pattern_errors(self):
        """Analyze vowel patterns that are frequently marked invalid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ic.component_value, COUNT(*) as error_count
            FROM invalid_components ic
            WHERE ic.component_type = 'vowel'
            GROUP BY ic.component_value
            ORDER BY error_count DESC
        """)

        invalid_vowels = cursor.fetchall()

        # Get pattern errors
        cursor.execute("""
            SELECT component_value, COUNT(*) as count
            FROM invalid_components
            WHERE component_type = 'pattern'
            GROUP BY component_value
            ORDER BY count DESC
        """)

        invalid_patterns = cursor.fetchall()

        conn.close()

        print("\n=== Vowel Pattern Analysis ===")
        print("Vowels frequently marked as invalid:")
        for vowel, count in invalid_vowels[:10]:
            print(f"  {vowel}: {count} errors")

        print("\nPatterns frequently marked as invalid:")
        for pattern, count in invalid_patterns[:10]:
            print(f"  {pattern}: {count} errors")

        return {
            'invalid_vowels': invalid_vowels,
            'invalid_patterns': invalid_patterns
        }

    def export_validation_data(self, output_file="validation_analysis.json"):
        """Export all validation data for external analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all validated interpretations with their components
        cursor.execute("""
            SELECT
                i.id,
                w.word,
                i.interpretation_json,
                i.validity_status,
                i.synonymous_with_id
            FROM interpretations i
            JOIN words w ON i.word_id = w.id
            WHERE i.validity_status != 'unlabeled'
        """)

        interpretations = []
        for row in cursor.fetchall():
            interp_id, word, interp_json, status, synonym_id = row
            interp_data = json.loads(interp_json)

            # Get invalid components if any
            invalid_components = []
            if status == 'invalid':
                cursor.execute("""
                    SELECT component_type, component_value, invalid_reason
                    FROM invalid_components
                    WHERE interpretation_id = ?
                """, (interp_id,))
                invalid_components = [
                    {'type': t, 'value': v, 'reason': r}
                    for t, v, r in cursor.fetchall()
                ]

            interpretations.append({
                'word': word,
                'interpretation': interp_data,
                'validity_status': status,
                'synonymous_with_id': synonym_id,
                'invalid_components': invalid_components
            })

        conn.close()

        # Save to JSON file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(interpretations, f, ensure_ascii=False, indent=2)

        print(f"\n=== Exported {len(interpretations)} validated interpretations to {output_file} ===")
        return len(interpretations)

    def generate_report(self):
        """Generate a comprehensive report of validation findings"""
        print("\n" + "=" * 60)
        print("THAI SYLLABLE VALIDATION ANALYSIS REPORT")
        print("=" * 60)

        # Summary statistics
        summary = self.get_validation_summary()
        print(f"\nTotal words processed: {summary['total_words']}")
        print(f"Average interpretations per word: {summary['avg_interpretations_per_word']}")
        print("\nValidation status breakdown:")
        for status, count in summary['validation_counts'].items():
            print(f"  {status}: {count}")

        # Invalid component analysis
        stats = self.get_invalid_component_stats()
        print("\n=== Invalid Components by Type ===")
        for comp_type, count in stats['component_types']:
            print(f"  {comp_type}: {count} errors")

        print("\n=== Top Problematic Values ===")
        for comp_type, value, count in stats['problematic_values'][:10]:
            print(f"  {comp_type} '{value}': {count} errors")

        # Specific pattern analyses
        self.find_patterns_in_invalid_finals()
        self.analyze_vowel_pattern_errors()

        print("\n" + "=" * 60)
        print("END OF REPORT")
        print("=" * 60)


def main():
    """Main function to run analysis"""
    analyzer = ValidationAnalyzer()

    # Generate full report
    analyzer.generate_report()

    # Export data for external analysis
    analyzer.export_validation_data()

    # Example query for specific invalid cluster analysis
    print("\n=== Custom Query Example ===")
    print("Finding all interpretations where 'กร' was marked as invalid cluster:")

    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM invalid_components
        WHERE component_type = 'cluster' AND component_value LIKE '%กร%'
    """)
    count = cursor.fetchone()[0]
    conn.close()

    print(f"Found {count} cases where 'กร' cluster was marked invalid")


if __name__ == "__main__":
    main()