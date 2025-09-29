#!/usr/bin/env python3
"""
Thai Syllable Database
Simple one-liner interface for tracking Thai syllable patterns.
Auto-manages SQLite connections and stores full pattern data.
"""

import sqlite3
import json
import sys
import io
from dataclasses import dataclass, asdict
from typing import Optional, List, Tuple, Set
from pathlib import Path

# Set UTF-8 encoding for Windows console (skip in Jupyter)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@dataclass
class PatternData:
    """Data structure for Thai vowel patterns."""
    pattern: str                    # Raw pattern like 'เx็f'
    foundation: Optional[str]       # The 'x' text: 'ด', 'ตร', etc.
    final: Optional[str]           # The 'f' text: 'ก', 'รณ์', etc.
    syllable: str                  # Full syllable text: 'เด็ก'
    pattern_id: Optional[str] = None  # ID like 'e_s_c'
    tags: Optional[List[str]] = None  # Tags from pattern database


# Global database path
DB_PATH = Path("thai_syllables.db")


def _get_connection():
    """Get or create database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name

    # Create tables if first time
    cursor = conn.cursor()

    # Main syllables table with JSON fields for complex data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS syllables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            foundation TEXT,
            final TEXT,
            syllable TEXT NOT NULL,
            pattern_id TEXT,
            tags TEXT,  -- JSON array of tags
            foundation_type TEXT,
            final_type TEXT,
            occurrence_count INTEGER DEFAULT 1,
            pattern_data TEXT,  -- JSON serialized full PatternData
            UNIQUE(pattern, foundation, final, syllable)
        )
    ''')

    # Indexes for performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_pattern_foundation_final
        ON syllables(pattern, foundation, final)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_syllable
        ON syllables(syllable)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tags
        ON syllables(tags)
    ''')

    conn.commit()
    return conn


def _classify_text(text: Optional[str]) -> str:
    """Classify text as single, cluster, or none."""
    if text is None:
        return 'none'
    elif len(text) == 1:
        return 'single'
    elif len(text) == 2:
        return 'cluster'
    else:
        return f'cluster_{len(text)}'


def syllable_query(pattern_data: PatternData) -> Tuple[int, bool]:
    """
    Query or add a syllable to the database. Simple one-liner interface.

    Args:
        pattern_data: PatternData object with pattern info

    Returns:
        Tuple of (syllable_id, is_new)

    Example:
        >>> data = PatternData(
        ...     pattern="เx็f",
        ...     foundation="ด",
        ...     final="ก",
        ...     syllable="เด็ก",
        ...     pattern_id="e_s_c",
        ...     tags=["short", "closed"]
        ... )
        >>> id, is_new = syllable_query(data)
    """
    conn = _get_connection()
    cursor = conn.cursor()

    try:
        # Check if exists
        cursor.execute('''
            SELECT id, occurrence_count FROM syllables
            WHERE pattern = ? AND foundation IS ? AND final IS ? AND syllable = ?
        ''', (pattern_data.pattern, pattern_data.foundation, pattern_data.final, pattern_data.syllable))

        result = cursor.fetchone()

        if result:
            # Exists - increment count
            syllable_id = result['id']
            cursor.execute('''
                UPDATE syllables SET occurrence_count = occurrence_count + 1
                WHERE id = ?
            ''', (syllable_id,))
            conn.commit()
            return syllable_id, False

        else:
            # New - insert
            foundation_type = _classify_text(pattern_data.foundation)
            final_type = _classify_text(pattern_data.final)
            tags_json = json.dumps(pattern_data.tags) if pattern_data.tags else None
            pattern_json = json.dumps(asdict(pattern_data))

            cursor.execute('''
                INSERT INTO syllables
                (pattern, foundation, final, syllable, pattern_id, tags,
                 foundation_type, final_type, pattern_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern_data.pattern,
                pattern_data.foundation,
                pattern_data.final,
                pattern_data.syllable,
                pattern_data.pattern_id,
                tags_json,
                foundation_type,
                final_type,
                pattern_json
            ))

            conn.commit()
            return cursor.lastrowid, True

    finally:
        conn.close()


def get_syllable(syllable_id: int) -> Optional[PatternData]:
    """
    Retrieve a syllable by ID.

    Args:
        syllable_id: The database ID

    Returns:
        PatternData object or None if not found
    """
    conn = _get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT pattern_data FROM syllables WHERE id = ?', (syllable_id,))
        result = cursor.fetchone()

        if result and result['pattern_data']:
            data = json.loads(result['pattern_data'])
            return PatternData(**data)
        return None

    finally:
        conn.close()


def find_syllables(**criteria) -> List[Tuple[int, PatternData]]:
    """
    Find syllables matching criteria.

    Args:
        pattern: Match specific pattern
        foundation: Match specific foundation
        syllable: Match specific syllable text
        has_tags: List of tags that must be present
        foundation_type: 'single', 'cluster', etc.

    Returns:
        List of (id, PatternData) tuples
    """
    conn = _get_connection()
    cursor = conn.cursor()

    try:
        conditions = []
        params = []

        if 'pattern' in criteria:
            conditions.append('pattern = ?')
            params.append(criteria['pattern'])

        if 'foundation' in criteria:
            conditions.append('foundation = ?')
            params.append(criteria['foundation'])

        if 'syllable' in criteria:
            conditions.append('syllable = ?')
            params.append(criteria['syllable'])

        if 'foundation_type' in criteria:
            conditions.append('foundation_type = ?')
            params.append(criteria['foundation_type'])

        if 'has_tags' in criteria:
            for tag in criteria['has_tags']:
                conditions.append('tags LIKE ?')
                params.append(f'%"{tag}"%')

        query = 'SELECT id, pattern_data FROM syllables'
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            if row['pattern_data']:
                data = json.loads(row['pattern_data'])
                results.append((row['id'], PatternData(**data)))

        return results

    finally:
        conn.close()


def get_statistics() -> dict:
    """Get database statistics."""
    conn = _get_connection()
    cursor = conn.cursor()

    try:
        stats = {}

        # Total count
        cursor.execute('SELECT COUNT(*) as count FROM syllables')
        stats['total'] = cursor.fetchone()['count']

        # By foundation type
        cursor.execute('''
            SELECT foundation_type, COUNT(*) as count
            FROM syllables GROUP BY foundation_type
        ''')
        stats['by_foundation_type'] = {row['foundation_type']: row['count']
                                       for row in cursor.fetchall()}

        # By pattern
        cursor.execute('''
            SELECT pattern, COUNT(*) as count
            FROM syllables GROUP BY pattern
            ORDER BY count DESC LIMIT 10
        ''')
        stats['top_patterns'] = [(row['pattern'], row['count'])
                                 for row in cursor.fetchall()]

        # Most common syllables
        cursor.execute('''
            SELECT syllable, occurrence_count
            FROM syllables
            ORDER BY occurrence_count DESC LIMIT 10
        ''')
        stats['top_syllables'] = [(row['syllable'], row['occurrence_count'])
                                  for row in cursor.fetchall()]

        return stats

    finally:
        conn.close()


def display_database(limit: int = 20):
    """Display database contents in readable format."""
    conn = _get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f'''
            SELECT id, pattern, foundation, final, syllable, pattern_id, occurrence_count
            FROM syllables
            ORDER BY id
            LIMIT {limit}
        ''')

        print(f"{'ID':<5} {'Pattern':<10} {'Foundation':<10} {'Final':<8} {'Syllable':<12} {'Pattern-ID':<15} {'Count':<7}")
        print("-" * 85)

        for row in cursor.fetchall():
            foundation = row['foundation'] or '-'
            final = row['final'] or '-'
            pattern_id = row['pattern_id'] or '-'

            print(f"{row['id']:<5} {row['pattern']:<10} {foundation:<10} "
                  f"{final:<8} {row['syllable']:<12} {pattern_id:<15} "
                  f"{row['occurrence_count']:<7}")

    finally:
        conn.close()


# Convenience function for processing vowel groups from get_vowels_multi
def process_vowel_groups(vowel_groups: dict) -> dict:
    """
    Process output from get_vowels_multi and store in database.

    Args:
        vowel_groups: Output from get_vowels_multi()

    Returns:
        Dict mapping vowel numbers to lists of syllable IDs
    """
    result = {}

    for vowel_num, interpretations in vowel_groups.items():
        syllable_ids = []

        for interp in interpretations:
            # Extract tags if available (would need to be passed from pattern database)
            tags = None  # TODO: Get from pattern database

            pattern_data = PatternData(
                pattern=interp['pattern'],
                foundation=interp.get('x_text'),
                final=interp.get('f_text'),
                syllable=interp['matched_text'],
                pattern_id=interp.get('abbrev_id'),
                tags=tags
            )

            syllable_id, _ = syllable_query(pattern_data)
            syllable_ids.append(syllable_id)

        result[vowel_num] = syllable_ids

    return result


def main():
    """Example usage."""
    # Test with some sample data
    test_cases = [
        PatternData(
            pattern="xี",
            foundation="ร",
            final=None,
            syllable="รี",
            pattern_id="i_l_o",
            tags=["long", "open", "monophthong"]
        ),
        PatternData(
            pattern="xี",
            foundation="ตร",
            final=None,
            syllable="ตรี",
            pattern_id="i_l_o",
            tags=["long", "open", "monophthong"]
        ),
        PatternData(
            pattern="เx็f",
            foundation="ด",
            final="ก",
            syllable="เด็ก",
            pattern_id="e_s_c",
            tags=["short", "closed"]
        ),
        PatternData(
            pattern="xี",
            foundation="ร",
            final=None,
            syllable="รี",
            pattern_id="i_l_o",
            tags=["long", "open", "monophthong"]
        ),  # Duplicate to test counting
    ]

    print("Testing syllable_query with PatternData:")
    print("=" * 50)

    for data in test_cases:
        syll_id, is_new = syllable_query(data)
        status = "NEW" if is_new else "EXISTS"
        print(f"{status:8} ID={syll_id:3} : {data.syllable} ({data.pattern})")

    print("\n" + "=" * 50)
    print("DATABASE CONTENTS:")
    display_database()

    print("\n" + "=" * 50)
    print("STATISTICS:")
    stats = get_statistics()
    print(f"Total syllables: {stats['total']}")
    print(f"By foundation type: {stats['by_foundation_type']}")
    print(f"Top patterns: {stats['top_patterns'][:5]}")
    print(f"Most frequent syllables: {stats['top_syllables'][:5]}")

    # Test retrieval
    print("\n" + "=" * 50)
    print("RETRIEVING SYLLABLE ID 1:")
    retrieved = get_syllable(1)
    if retrieved:
        print(f"  Pattern: {retrieved.pattern}")
        print(f"  Foundation: {retrieved.foundation}")
        print(f"  Syllable: {retrieved.syllable}")
        print(f"  Tags: {retrieved.tags}")

    # Test search
    print("\n" + "=" * 50)
    print("SEARCHING FOR pattern='xี':")
    results = find_syllables(pattern="xี")
    for syll_id, data in results:
        print(f"  ID {syll_id}: {data.syllable} (foundation={data.foundation})")


if __name__ == "__main__":
    main()