#!/usr/bin/env python3
"""
Quick test script for the labeling system
"""

import sys
import os
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analyzer():
    """Test the Thai analyzer directly"""
    try:
        from thai_reading_order import ThaiReadingOrderAnalyzer

        analyzer = ThaiReadingOrderAnalyzer(
            "res/foundation/foundation.json",
            "thai_vowels_tagged_9-21-2025-2-31-pm.json"
        )

        # Test simple word
        result = analyzer.findThaiGraphemeOrderDomain("ยา")
        print(f"Test 'ยา': {result}")

        return True
    except Exception as e:
        print(f"Analyzer test failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    try:
        from database.query_utilities import ThaiGraphemeQuery

        query = ThaiGraphemeQuery()
        tags = query.get_all_tags()
        print(f"Database has {len(tags)} tags")

        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def main():
    print("Testing Thai Labeling System Components")
    print("=" * 50)

    analyzer_ok = test_analyzer()
    print(f"Analyzer: {'[OK]' if analyzer_ok else '[FAIL]'}")

    database_ok = test_database()
    print(f"Database: {'[OK]' if database_ok else '[FAIL]'}")

    if analyzer_ok and database_ok:
        print("\n[OK] All tests passed. System should work correctly.")
    else:
        print("\n[FAIL] Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()