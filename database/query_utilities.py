#!/usr/bin/env python3
"""
Utility functions for querying the Thai grapheme database
"""

import sqlite3
import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional, Set

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ThaiGraphemeQuery:
    def __init__(self, db_path="database/thai_voraritskul_graphemes.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")

    def get_character_tags(self, sequence, category: Optional[str] = None) -> List[str]:
        """Get all tags for a character sequence"""
        # Handle list input - convert to string
        if isinstance(sequence, list):
            sequence = ''.join(sequence)

        # Ensure it's a string
        sequence = str(sequence)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            query = """
                SELECT t.name FROM tags t
                JOIN character_tags ct ON t.id = ct.tag_id
                JOIN characters c ON ct.character_id = c.id
                JOIN categories cat ON c.category_id = cat.id
                WHERE c.sequence = ? AND cat.name = ?
            """
            cursor.execute(query, (sequence, category))
        else:
            query = """
                SELECT t.name FROM tags t
                JOIN character_tags ct ON t.id = ct.tag_id
                JOIN characters c ON ct.character_id = c.id
                WHERE c.sequence = ?
            """
            cursor.execute(query, (sequence,))

        tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tags

    def get_character_info(self, sequence) -> Optional[Dict]:
        """Get complete information about a character sequence"""
        # Handle list input - convert to string
        if isinstance(sequence, list):
            sequence = ''.join(sequence)

        # Ensure it's a string
        sequence = str(sequence)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT c.id, c.sequence, c.is_cluster, c.metadata,
                   cat.name as category,
                   GROUP_CONCAT(t.name) as tags
            FROM characters c
            JOIN categories cat ON c.category_id = cat.id
            LEFT JOIN character_tags ct ON c.id = ct.character_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            WHERE c.sequence = ?
            GROUP BY c.id
        """
        cursor.execute(query, (sequence,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'sequence': row[1],
            'is_cluster': bool(row[2]),
            'metadata': json.loads(row[3]) if row[3] else None,
            'category': row[4],
            'tags': row[5].split(',') if row[5] else []
        }

    def is_valid_cluster(self, cluster: str) -> bool:
        """Check if a consonant cluster is valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM valid_clusters WHERE cluster = ?", (cluster,))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    def get_cluster_components(self, cluster: str) -> Optional[List[str]]:
        """Get the components of a cluster"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT components FROM valid_clusters WHERE cluster = ?", (cluster,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def validate_interpretation(self, interpretation: Dict) -> Dict:
        """Validate an interpretation against the database

        Returns dict with:
        - is_valid: bool
        - issues: list of validation issues
        - character_info: dict of character information
        """
        issues = []
        char_info = {}

        # Check foundation (no cluster validation - that's for pruning, not UI validation)
        if 'foundation' in interpretation:
            foundations = interpretation['foundation']
            if isinstance(foundations, list):
                if len(foundations) > 1:
                    # It's a cluster - just get info, don't validate
                    cluster = ''.join(foundations)
                    char_info['foundation'] = self.get_character_info(cluster) or {'sequence': cluster, 'tags': []}
                else:
                    # Single foundation
                    char_info['foundation'] = self.get_character_info(foundations[0])
                    if not char_info['foundation']:
                        issues.append(f"Unknown foundation: {foundations[0]}")
            else:
                char_info['foundation'] = self.get_character_info(foundations)
                if not char_info['foundation']:
                    issues.append(f"Unknown foundation: {foundations}")

        # Check vowel (just get info, don't validate - algorithm generates these)
        if 'vowel' in interpretation and interpretation['vowel']:
            vowel_info = self.get_character_info(interpretation['vowel'])
            if vowel_info:
                char_info['vowel'] = vowel_info
            else:
                # Vowel not in database - that's ok, algorithm generated it
                char_info['vowel'] = {'sequence': interpretation['vowel'], 'tags': [], 'category': 'vowel_pattern'}

        # Check final
        if 'final' in interpretation and interpretation['final']:
            final_info = self.get_character_info(interpretation['final'])
            if final_info:
                char_info['final'] = final_info
            else:
                char_info['final'] = {'sequence': interpretation['final'], 'tags': [], 'category': 'foundation'}

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'character_info': char_info
        }

    def get_all_tags(self) -> List[str]:
        """Get all tags in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM tags ORDER BY name")
        tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tags

    def get_characters_by_tag(self, tag_name: str) -> List[Dict]:
        """Get all characters with a specific tag"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT c.sequence, cat.name as category
            FROM characters c
            JOIN categories cat ON c.category_id = cat.id
            JOIN character_tags ct ON c.id = ct.character_id
            JOIN tags t ON ct.tag_id = t.id
            WHERE t.name = ?
        """
        cursor.execute(query, (tag_name,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'sequence': row[0],
                'category': row[1]
            })

        conn.close()
        return results

def main():
    """Test the query utilities"""
    query = ThaiGraphemeQuery()

    # Test getting character info
    print("Testing character queries:")
    print("-" * 40)

    # Test a vowel pattern
    test_vowel = "า"
    info = query.get_character_info(test_vowel)
    if info:
        print(f"Character '{test_vowel}':")
        print(f"  Category: {info['category']}")
        print(f"  Tags: {info['tags']}")

    # Test a foundation
    test_foundation = "ค"
    info = query.get_character_info(test_foundation)
    if info:
        print(f"\nCharacter '{test_foundation}':")
        print(f"  Category: {info['category']}")
        print(f"  Tags: {info['tags']}")

    # Test validation
    print("\n\nTesting interpretation validation:")
    print("-" * 40)

    test_interpretation = {
        'foundation': ['ล'],
        'vowel': 'เ',
        'final': 'ว',
        'pattern': 'เxf'
    }

    validation = query.validate_interpretation(test_interpretation)
    print(f"Interpretation: {test_interpretation}")
    print(f"Valid: {validation['is_valid']}")
    if validation['issues']:
        print(f"Issues: {validation['issues']}")

    # Show all tags
    print("\n\nAll tags in database:")
    print("-" * 40)
    tags = query.get_all_tags()
    for tag in tags:
        print(f"  - {tag}")

if __name__ == "__main__":
    main()