#!/usr/bin/env python3
"""
Import Thai grapheme data from JSON files into the database
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional

class ThaiDataImporter:
    def __init__(self, db_path="database/thai_voraritskul_graphemes.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}. Run init_databases.py first.")

    def get_or_create_category(self, conn, category_name: str) -> int:
        """Get category ID, creating if necessary"""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        conn.commit()
        return cursor.lastrowid

    def get_or_create_tag(self, conn, tag_name: str) -> int:
        """Get tag ID, creating if necessary"""
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = cursor.fetchone()

        if result:
            return result[0]

        cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
        conn.commit()
        return cursor.lastrowid

    def import_vowel_patterns(self, json_file: str) -> Dict:
        """Import vowel patterns with tags from JSON file"""
        json_path = Path(json_file)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        print(f"Importing vowel patterns from {json_file}...")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get vowel_pattern category ID
        category_id = self.get_or_create_category(conn, 'vowel_pattern')

        stats = {'patterns': 0, 'tags': 0, 'links': 0}

        # Import patterns and their tags
        patterns_data = data.get('patterns', {})
        for pattern, tags in patterns_data.items():
            # Insert or get character
            cursor.execute("""
                INSERT OR IGNORE INTO characters (category_id, sequence, is_cluster)
                VALUES (?, ?, 0)
            """, (category_id, pattern))

            cursor.execute("""
                SELECT id FROM characters
                WHERE category_id = ? AND sequence = ?
            """, (category_id, pattern))
            char_id = cursor.fetchone()[0]
            stats['patterns'] += 1

            # Link tags to character
            for tag_name in tags:
                tag_id = self.get_or_create_tag(conn, tag_name)
                cursor.execute("""
                    INSERT OR IGNORE INTO character_tags (character_id, tag_id)
                    VALUES (?, ?)
                """, (char_id, tag_id))
                stats['links'] += 1

            stats['tags'] = len(set(tag for tags in patterns_data.values() for tag in tags))

        conn.commit()
        conn.close()

        print(f"[OK] Imported {stats['patterns']} vowel patterns")
        print(f"[OK] Created/linked {stats['tags']} unique tags")
        print(f"[OK] Created {stats['links']} character-tag associations")
        return stats

    def import_foundations(self, json_file: str) -> Dict:
        """Import foundation consonants from JSON file"""
        json_path = Path(json_file)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        print(f"Importing foundations from {json_file}...")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get foundation category ID
        category_id = self.get_or_create_category(conn, 'foundation')

        stats = {'foundations': 0}

        # Import foundations
        foundations = data.get('foundation', [])
        for foundation in foundations:
            cursor.execute("""
                INSERT OR IGNORE INTO characters (category_id, sequence, is_cluster)
                VALUES (?, ?, 0)
            """, (category_id, foundation))
            stats['foundations'] += 1

        conn.commit()
        conn.close()

        print(f"[OK] Imported {stats['foundations']} foundation consonants")
        return stats

    def import_valid_clusters(self, clusters: List[Dict]) -> Dict:
        """Import valid consonant clusters

        Args:
            clusters: List of dicts with 'cluster' and optionally 'components' and 'usage_position'
                     e.g., [{'cluster': 'คร', 'components': ['ค', 'ร'], 'usage_position': 'initial'}]
        """
        print(f"Importing {len(clusters)} valid clusters...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {'clusters': 0}

        for cluster_data in clusters:
            cluster = cluster_data.get('cluster')
            components = cluster_data.get('components', list(cluster))
            usage_position = cluster_data.get('usage_position', None)
            notes = cluster_data.get('notes', None)

            cursor.execute("""
                INSERT OR REPLACE INTO valid_clusters (cluster, components, usage_position, notes)
                VALUES (?, ?, ?, ?)
            """, (cluster, json.dumps(components), usage_position, notes))
            stats['clusters'] += 1

            # Also add to characters table as foundation with is_cluster=1
            category_id = self.get_or_create_category(conn, 'foundation')
            cursor.execute("""
                INSERT OR IGNORE INTO characters (category_id, sequence, is_cluster)
                VALUES (?, ?, 1)
            """, (category_id, cluster))

        conn.commit()
        conn.close()

        print(f"[OK] Imported {stats['clusters']} valid clusters")
        return stats

    def verify_import(self) -> Dict:
        """Verify database contents after import"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count statistics
        stats = {}

        cursor.execute("SELECT COUNT(*) FROM categories")
        stats['categories'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM characters")
        stats['total_characters'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM characters WHERE is_cluster = 0")
        stats['single_characters'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM characters WHERE is_cluster = 1")
        stats['clusters'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tags")
        stats['tags'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM character_tags")
        stats['character_tag_links'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM valid_clusters")
        stats['valid_clusters'] = cursor.fetchone()[0]

        conn.close()

        print("\nDatabase Statistics:")
        print("-" * 40)
        for key, value in stats.items():
            print(f"{key:.<30} {value}")

        return stats

def main():
    """Example usage"""
    importer = ThaiDataImporter()

    # Import vowel patterns with tags
    try:
        importer.import_vowel_patterns("thai_vowels_tagged_9-21-2025-2-31-pm.json")
    except FileNotFoundError as e:
        print(f"Warning: {e}")

    # Import foundations
    try:
        importer.import_foundations("res/foundation/foundation.json")
    except FileNotFoundError as e:
        print(f"Warning: {e}")

    # Example: Import some valid clusters (you would provide your actual list)
    example_clusters = [
        {'cluster': 'กร', 'components': ['ก', 'ร'], 'usage_position': 'initial'},
        {'cluster': 'กล', 'components': ['ก', 'ล'], 'usage_position': 'initial'},
        {'cluster': 'คร', 'components': ['ค', 'ร'], 'usage_position': 'initial'},
        {'cluster': 'คล', 'components': ['ค', 'ล'], 'usage_position': 'initial'},
        {'cluster': 'ปร', 'components': ['ป', 'ร'], 'usage_position': 'initial'},
        {'cluster': 'ปล', 'components': ['ป', 'ล'], 'usage_position': 'initial'},
        {'cluster': 'พร', 'components': ['พ', 'ร'], 'usage_position': 'initial'},
        {'cluster': 'พล', 'components': ['พ', 'ล'], 'usage_position': 'initial'},
        {'cluster': 'ตร', 'components': ['ต', 'ร'], 'usage_position': 'initial'},
    ]
    # Uncomment when you have your actual cluster list
    # importer.import_valid_clusters(example_clusters)

    # Verify the import
    importer.verify_import()

if __name__ == "__main__":
    main()