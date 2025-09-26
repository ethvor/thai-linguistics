#!/usr/bin/env python3
"""
Flask application for Thai syllable labeling system
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import os

# Check if Flask is installed, if not try to install it
try:
    from flask import Flask, render_template, jsonify, request, send_from_directory, redirect
    from flask_cors import CORS
except ImportError:
    print("Flask not found. Installing Flask and Flask-CORS...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        from flask import Flask, render_template, jsonify, request, send_from_directory, redirect
        from flask_cors import CORS
        print("Flask installed successfully!")
    except Exception as e:
        print(f"Failed to install Flask: {e}")
        print("Please install Flask manually: pip install flask flask-cors")
        sys.exit(1)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from thai_reading_order import ThaiReadingOrderAnalyzer
from database.query_utilities import ThaiGraphemeQuery

app = Flask(__name__)
CORS(app)

# Database paths - use absolute paths to avoid working directory issues
import os
from pathlib import Path

script_dir = Path(__file__).parent
GRAPHEMES_DB = script_dir / "database" / "thai_voraritskul_graphemes.db"
LABELS_DB = script_dir / "database" / "thai_syllable_labels.db"

print(f"Looking for graphemes DB at: {GRAPHEMES_DB}")
print(f"DB exists: {GRAPHEMES_DB.exists()}")

# Initialize analyzer
try:
    analyzer = ThaiReadingOrderAnalyzer(
        str(script_dir / "res" / "foundation" / "foundation.json"),
        str(script_dir / "thai_vowels_tagged_9-21-2025-2-31-pm.json")
    )
    print("✓ Analyzer initialized successfully")
except Exception as e:
    print(f"✗ Analyzer initialization failed: {e}")
    raise

# Initialize query utility
try:
    query_util = ThaiGraphemeQuery(str(GRAPHEMES_DB))
    print("✓ Query utility initialized successfully")
except Exception as e:
    print(f"✗ Query utility initialization failed: {e}")
    raise

@app.route('/')
def index():
    """Redirect to the labeling interface"""
    return redirect('/thai_syllable_labeler.html')

@app.route('/thai_syllable_labeler.html')
def serve_labeler():
    """Serve the labeling interface with dynamic port injection"""
    try:
        with open('thai_syllable_labeler.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Get the current port from request host
        port = request.host.split(':')[1] if ':' in request.host else '5001'

        # Replace hardcoded localhost:5001 with dynamic port
        html_content = html_content.replace('http://localhost:5001', f'http://localhost:{port}')

        return html_content
    except Exception as e:
        return f"Error loading labeler: {e}", 500

@app.route('/api/generate-interpretations', methods=['POST'])
def generate_interpretations():
    """Generate all possible interpretations for a word"""
    data = request.json
    word = data.get('word', '')

    if not word:
        return jsonify({'error': 'No word provided'}), 400

    try:
        print(f"Analyzing word: {word}")

        # Generate interpretations using the analyzer
        result = analyzer.findThaiGraphemeOrderDomain(word)
        print(f"Raw result: {result}")

        if not result or 'readings' not in result:
            return jsonify({'error': 'No readings generated', 'word': word, 'interpretations': []}), 200

        # Format interpretations for UI
        interpretations = []
        for i, reading in enumerate(result.get('readings', [])):
            interp = {
                'id': f'interp_{i+1}',
                'syllables': []
            }

            for syllable in reading['syllables']:
                syl_data = {
                    'foundation': syllable['foundation'],
                    'vowel': syllable['vowel'],
                    'final': syllable['final'],
                    'pattern': syllable['pattern'],
                    'reading_order': []
                }

                # Build reading order - handle foundation object properly
                if syllable['foundation']:
                    foundation_data = syllable['foundation']
                    print(f"  Foundation data type: {type(foundation_data)}")
                    print(f"  Foundation data: {foundation_data}")

                    # Extract consonants from foundation object
                    if isinstance(foundation_data, dict) and 'consonants' in foundation_data:
                        foundation_chars = foundation_data['consonants']
                        syl_data['foundation'] = foundation_chars
                        foundation_str = ''.join(foundation_chars)
                    else:
                        foundation_str = str(foundation_data)
                        syl_data['foundation'] = [foundation_str]

                    syl_data['reading_order'].append(foundation_str)

                if syllable['vowel']:
                    syl_data['reading_order'].append(syllable['vowel'])

                if syllable['final']:
                    final_data = syllable['final']
                    if isinstance(final_data, dict) and 'consonants' in final_data:
                        final_chars = final_data['consonants']
                        syl_data['final'] = final_chars
                        final_str = ''.join(final_chars)
                    else:
                        final_str = str(final_data)
                        syl_data['final'] = [final_str]
                    syl_data['reading_order'].append(final_str)

                interp['syllables'].append(syl_data)

            # Validate interpretation
            try:
                print(f"Validating interpretation {i+1} for word '{word}'")
                syllable_to_validate = interp['syllables'][0] if interp['syllables'] else {}
                print(f"  Syllable data: {syllable_to_validate}")
                validation = query_util.validate_interpretation(syllable_to_validate)
                print(f"  Validation result: {validation}")
                interp['validation'] = validation
            except Exception as val_error:
                print(f"  Validation failed: {val_error}")
                interp['validation'] = {'is_valid': False, 'issues': [f'Validation error: {val_error}'], 'character_info': {}}

            interpretations.append(interp)

        # Store word and interpretations in database - MODIFIED: now returns interpretation IDs
        word_id, interpretation_ids = store_word_and_interpretations(word, interpretations)

        # Add database IDs to interpretations for frontend tracking
        for i, interp in enumerate(interpretations):
            interp['db_id'] = interpretation_ids[i]
            interp['validity_status'] = 'unlabeled'  # Add status to response

        return jsonify({
            'word': word,
            'word_id': word_id,
            'interpretations': interpretations,
            'is_ambiguous': result['is_ambiguous'],
            'count': len(interpretations)
        })

    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'word': word
        }
        print(f"ERROR in generate_interpretations:")
        print(f"  Word: {word}")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        print(f"  Full traceback:\n{traceback.format_exc()}")
        return jsonify(error_details), 500

@app.route('/api/save-interpretation-validations', methods=['POST'])
def save_interpretation_validations():
    """Save batch validation labels for all interpretations of a word"""
    data = request.json

    try:
        conn = sqlite3.connect(LABELS_DB)
        cursor = conn.cursor()

        # Get or create session
        session_id = data.get('session_id')
        if not session_id:
            cursor.execute("""
                INSERT INTO labeling_sessions (session_name, description)
                VALUES (?, ?)
            """, (f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}", "Batch validation session"))
            session_id = cursor.lastrowid

        word_id = data.get('word_id')
        validations = data.get('validations', [])

        # Process each interpretation validation
        for validation in validations:
            interp_id = validation.get('interpretation_id')
            validity_status = validation.get('validity_status')
            synonymous_with = validation.get('synonymous_with_id')

            # Update interpretation validity status
            cursor.execute("""
                UPDATE interpretations
                SET validity_status = ?, synonymous_with_id = ?
                WHERE id = ?
            """, (validity_status, synonymous_with, interp_id))

            # If invalid, store the invalid components
            if validity_status == 'invalid':
                invalid_components = validation.get('invalid_components', [])
                for component in invalid_components:
                    cursor.execute("""
                        INSERT INTO invalid_components (
                            interpretation_id, component_type, component_value,
                            invalid_reason, notes
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        interp_id,
                        component.get('type'),
                        component.get('value'),
                        component.get('reason'),
                        component.get('notes', '')
                    ))

        # Create a label entry for this batch validation session
        cursor.execute("""
            INSERT INTO labels (
                word_id, session_id, notes, labeler
            ) VALUES (?, ?, ?, ?)
        """, (
            word_id,
            session_id,
            f"Batch validation: {len(validations)} interpretations labeled",
            data.get('labeler', 'user')
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'validations_saved': len(validations)
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/save-label', methods=['POST'])
def save_label():
    """Save a labeling decision"""
    data = request.json

    try:
        conn = sqlite3.connect(LABELS_DB)
        cursor = conn.cursor()

        # Get or create session
        session_id = data.get('session_id')
        if not session_id:
            cursor.execute("""
                INSERT INTO labeling_sessions (session_name, description)
                VALUES (?, ?)
            """, (f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""))
            session_id = cursor.lastrowid

        # Save label
        cursor.execute("""
            INSERT INTO labels (
                word_id, session_id, selected_interpretation_id,
                is_custom, custom_interpretation, notes, labeler
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['word_id'],
            session_id,
            data.get('interpretation_id'),
            data.get('is_custom', False),
            json.dumps(data.get('custom_interpretation')) if data.get('custom_interpretation') else None,
            data.get('notes', ''),
            data.get('labeler', 'user')
        ))

        label_id = cursor.lastrowid

        # If custom interpretation, add to algorithm feedback
        if data.get('is_custom'):
            cursor.execute("""
                INSERT INTO algorithm_feedback (
                    word_id, missing_interpretation, feedback_type, notes
                ) VALUES (?, ?, ?, ?)
            """, (
                data['word_id'],
                json.dumps(data.get('custom_interpretation')),
                'missing_interpretation',
                'User provided custom interpretation not found by algorithm'
            ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'label_id': label_id,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-tags', methods=['POST'])
def get_tags():
    """Get tags for characters dynamically"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        characters = data.get('characters', {})
        print(f"Getting tags for characters: {characters}")

        result = {}
        for char_type, char_value in characters.items():
            if char_value:
                try:
                    if isinstance(char_value, list):
                        # Handle clusters
                        char_str = ''.join(char_value)
                    else:
                        char_str = char_value

                    print(f"  Looking up tags for {char_type}: '{char_str}'")
                    tags = query_util.get_character_tags(char_str)
                    print(f"  Found tags: {tags}")

                    result[char_type] = {
                        'character': char_str,
                        'tags': tags
                    }
                except Exception as char_error:
                    print(f"  Error getting tags for {char_type} '{char_value}': {char_error}")
                    result[char_type] = {
                        'character': str(char_value),
                        'tags': [],
                        'error': str(char_error)
                    }

        return jsonify(result)

    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        print(f"ERROR in get_tags:")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        print(f"  Full traceback:\n{traceback.format_exc()}")
        return jsonify(error_details), 500

@app.route('/api/get-session-stats', methods=['GET'])
def get_session_stats():
    """Get statistics for current labeling session"""
    session_id = request.args.get('session_id')

    conn = sqlite3.connect(LABELS_DB)
    cursor = conn.cursor()

    # Get session stats
    cursor.execute("""
        SELECT COUNT(*) as total_labels,
               SUM(CASE WHEN is_custom = 1 THEN 1 ELSE 0 END) as custom_labels,
               COUNT(DISTINCT word_id) as unique_words
        FROM labels
        WHERE session_id = ?
    """, (session_id,))

    stats = cursor.fetchone()
    conn.close()

    return jsonify({
        'total_labels': stats[0] if stats else 0,
        'custom_labels': stats[1] if stats else 0,
        'unique_words': stats[2] if stats else 0
    })

@app.route('/api/load-word-batch', methods=['POST'])
def load_word_batch():
    """Load a batch of words for labeling"""
    data = request.json
    words = data.get('words', [])

    results = []
    for word in words:
        # Check if already labeled
        conn = sqlite3.connect(LABELS_DB)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
        existing = cursor.fetchone()

        results.append({
            'word': word,
            'is_labeled': existing is not None
        })

        conn.close()

    return jsonify({'words': results})

@app.route('/api/restart-server', methods=['POST'])
def restart_server():
    """Restart the Flask server - system independent approach"""
    try:
        def shutdown():
            import time
            import os
            import sys

            time.sleep(1)  # Give time for response to be sent

            # System-independent restart approach
            try:
                # Check if we're running under a launcher that expects specific exit codes
                launcher_type = os.environ.get('LAUNCHER_TYPE', 'direct')

                # Method 1: Try graceful shutdown with different signals based on OS
                if sys.platform.startswith('win'):
                    # Windows: Use taskkill or direct exit
                    try:
                        import signal
                        os.kill(os.getpid(), signal.SIGTERM)
                    except:
                        # Exit with code 1 to trigger restart in batch/shell launcher
                        os._exit(1)
                else:
                    # Unix-like systems (Mac, Linux): Try multiple approaches
                    try:
                        import signal
                        # First try SIGTERM (works well with shell scripts)
                        os.kill(os.getpid(), signal.SIGTERM)
                    except:
                        try:
                            # If SIGTERM fails, try SIGINT (Ctrl+C equivalent)
                            os.kill(os.getpid(), signal.SIGINT)
                        except:
                            # Force exit with code 1 to trigger restart in launcher
                            os._exit(1)
            except Exception:
                # Ultimate fallback: force exit with code 1 to trigger restart in launcher
                os._exit(1)

        import threading
        thread = threading.Thread(target=shutdown)
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'message': 'Server restarting...'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def store_word_and_interpretations(word, interpretations):
    """Store word and its interpretations in database"""
    conn = sqlite3.connect(LABELS_DB)
    cursor = conn.cursor()

    # Insert or get word
    cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
    existing = cursor.fetchone()

    if existing:
        word_id = existing[0]
    else:
        cursor.execute("INSERT INTO words (word) VALUES (?)", (word,))
        word_id = cursor.lastrowid

    # Store interpretations with new validity_status field
    interpretation_ids = []
    for interp in interpretations:
        cursor.execute("""
            INSERT INTO interpretations (
                word_id, interpretation_json, validity_status, algorithm_version
            ) VALUES (?, ?, ?, ?)
        """, (
            word_id,
            json.dumps(interp),
            "unlabeled",  # All new interpretations start as unlabeled
            "v1.0"  # Version tracking
        ))
        interpretation_ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()

    return word_id, interpretation_ids

def find_free_port(start_port=5001):
    """Find a free port starting from start_port"""
    import socket
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    import time

    print("Thai Syllable Labeling System")
    print("=" * 50)

    # Find available port
    port = find_free_port(5001)
    if port is None:
        print("ERROR: No free ports found between 5001-5010!")
        sys.exit(1)

    # Create timestamp for cache busting
    timestamp = int(time.time())
    url = f'http://localhost:{port}/thai_syllable_labeler.html?v={timestamp}'

    print()
    print("=" * 60)
    print("SERVER READY!")
    print("=" * 60)
    print("Open this link in your browser:")
    print(f"   {url}")
    print("=" * 60)
    print(f"Server running on port {port}! Press Ctrl+C to stop.")
    print("=" * 60)
    print()

    # Store port in environment variable for HTML to read
    os.environ['LABELING_SERVER_PORT'] = str(port)

    try:
        app.run(host='localhost', port=port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"Server error: {e}")