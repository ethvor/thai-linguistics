#!/usr/bin/env python3
"""
migrate_database.py

Migrates existing database to new schema with validation support.
"""

import sqlite3
from pathlib import Path


def migrate_database(db_path="thai_syllable_labels.db"):
    """Add new columns and tables to existing database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Migrating database: {db_path}")

    try:
        # Add validity_status column to interpretations table
        cursor.execute("""
            ALTER TABLE interpretations
            ADD COLUMN validity_status TEXT DEFAULT 'unlabeled'
        """)
        print("[OK] Added validity_status column to interpretations table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  - validity_status column already exists")
        else:
            raise

    try:
        # Add synonymous_with_id column
        cursor.execute("""
            ALTER TABLE interpretations
            ADD COLUMN synonymous_with_id INTEGER REFERENCES interpretations(id)
        """)
        print("[OK] Added synonymous_with_id column to interpretations table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("  - synonymous_with_id column already exists")
        else:
            raise

    # Create invalid_components table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invalid_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interpretation_id INTEGER REFERENCES interpretations(id) ON DELETE CASCADE,
            component_type TEXT NOT NULL,
            component_value TEXT NOT NULL,
            invalid_reason TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (component_type IN ('foundation', 'vowel', 'final', 'pattern', 'cluster'))
        )
    """)
    print("[OK] Created invalid_components table")

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interpretations_validity ON interpretations(validity_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invalid_components_interp ON invalid_components(interpretation_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invalid_components_type ON invalid_components(component_type)")
    print("[OK] Created indexes")

    conn.commit()

    # Verify migration
    cursor.execute("PRAGMA table_info(interpretations)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nInterpretations table columns: {columns}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"All tables: {tables}")

    conn.close()
    print("\n[SUCCESS] Migration completed successfully!")


if __name__ == "__main__":
    migrate_database()