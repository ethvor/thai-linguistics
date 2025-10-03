#!/usr/bin/env python3
"""
Initialize Thai AVP Graphemes and Thai Syllable Labels databases
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class ThaiDatabaseInitializer:
    def __init__(self, db_directory="database"):
        self.db_dir = Path(db_directory)
        self.db_dir.mkdir(exist_ok=True)

        self.graphemes_db_path = self.db_dir / "thai_avp_graphemes.db"
        self.labels_db_path = self.db_dir / "thai_syllable_labels.db"

    def init_graphemes_database(self):
        """Initialize the Thai AVP Graphemes database"""
        print(f"Initializing {self.graphemes_db_path}...")

        conn = sqlite3.connect(self.graphemes_db_path)
        cursor = conn.cursor()

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                sequence TEXT NOT NULL,
                is_cluster BOOLEAN DEFAULT 0,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category_id, sequence)
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Character-Tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_tags (
                character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
                tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                confidence REAL DEFAULT 1.0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (character_id, tag_id)
            )
        """)

        # Valid clusters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS valid_clusters (
                cluster TEXT PRIMARY KEY,
                components JSON NOT NULL,
                usage_position TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default categories
        default_categories = [
            ('foundation', 'Thai consonants that serve as bases for vowel patterns'),
            ('vowel_pattern', 'Thai vowel patterns that attach to foundations'),
            ('dependent', 'Tone marks and diacritics that cannot exist independently')
        ]

        for name, desc in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description)
                VALUES (?, ?)
            """, (name, desc))

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_category ON characters(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_tags_char ON character_tags(character_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_tags_tag ON character_tags(tag_id)")

        conn.commit()
        conn.close()
        print(f"[OK] Graphemes database initialized at {self.graphemes_db_path}")

    def init_labels_database(self):
        """Initialize the Thai Syllable Labels database"""
        print(f"Initializing {self.labels_db_path}...")

        conn = sqlite3.connect(self.labels_db_path)
        cursor = conn.cursor()

        # Labeling sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labeling_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                source TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Interpretations table - MODIFIED: added validity_status and synonymous_with_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpretations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
                interpretation_json JSON NOT NULL,
                validity_status TEXT DEFAULT 'unlabeled',  -- valid, invalid, synonymous, unlabeled
                synonymous_with_id INTEGER REFERENCES interpretations(id),
                algorithm_version TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (validity_status IN ('valid', 'invalid', 'synonymous', 'unlabeled'))
            )
        """)

        # NEW TABLE: Invalid components tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invalid_components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interpretation_id INTEGER REFERENCES interpretations(id) ON DELETE CASCADE,
                component_type TEXT NOT NULL,  -- foundation, vowel, final, pattern, cluster
                component_value TEXT NOT NULL,  -- the actual character(s)
                invalid_reason TEXT,  -- invalid_cluster, cannot_be_final, wrong_vowel_pattern, etc.
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (component_type IN ('foundation', 'vowel', 'final', 'pattern', 'cluster'))
            )
        """)

        # Labels table - MODIFIED: Now tracks batch labeling sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
                session_id INTEGER REFERENCES labeling_sessions(id),
                selected_interpretation_id INTEGER REFERENCES interpretations(id),
                is_custom BOOLEAN DEFAULT 0,
                custom_interpretation JSON,
                notes TEXT,
                labeler TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Extracted patterns table for rule discovery
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_rule TEXT,
                pattern_data JSON,
                support_count INTEGER,
                confidence REAL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Algorithm feedback table (for tracking missing interpretations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS algorithm_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER REFERENCES words(id),
                missing_interpretation JSON,
                feedback_type TEXT,
                notes TEXT,
                reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes - ADDED: indexes for new tables
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interpretations_word ON interpretations(word_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interpretations_validity ON interpretations(validity_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invalid_components_interp ON invalid_components(interpretation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invalid_components_type ON invalid_components(component_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_labels_word ON labels(word_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_labels_session ON labels(session_id)")

        conn.commit()
        conn.close()
        print(f"[OK] Labels database initialized at {self.labels_db_path}")

    def initialize_all(self):
        """Initialize both databases"""
        print("Initializing Thai database system...")
        print("-" * 50)
        self.init_graphemes_database()
        self.init_labels_database()
        print("-" * 50)
        print("[OK] All databases initialized successfully!")
        return {
            'graphemes_db': str(self.graphemes_db_path),
            'labels_db': str(self.labels_db_path)
        }

def main():
    initializer = ThaiDatabaseInitializer()
    paths = initializer.initialize_all()

    print("\nDatabase paths:")
    for name, path in paths.items():
        print(f"  {name}: {path}")

if __name__ == "__main__":
    main()