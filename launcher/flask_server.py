#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
flask_server.py

Flask-based server for Thai classifier web app.
More reliable than SimpleHTTPServer with better port handling.
"""

import os
import sys
from pathlib import Path
import time

# Check if Flask is installed, if not try to install it
try:
    from flask import Flask, send_from_directory, send_file, request, jsonify
except ImportError:
    print("Flask not found. Installing Flask...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        from flask import Flask, send_from_directory, send_file
        print("Flask installed successfully!")
    except Exception as e:
        print(f"Failed to install Flask: {e}")
        print("Please install Flask manually: pip install flask")
        sys.exit(1)

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)

    # Get project root directory
    project_root = Path(__file__).parent.parent

    @app.route('/')
    def index():
        """Redirect to classifier"""
        return send_file(project_root / 'tools' / 'thai_classifier_improved.html')

    @app.route('/tools/<path:filename>')
    def tools(filename):
        """Serve files from tools directory"""
        return send_from_directory(project_root / 'tools', filename)

    @app.route('/res/<path:filename>')
    def resources(filename):
        """Serve files from res directory"""
        return send_from_directory(project_root / 'res', filename)

    @app.route('/progress/<path:filename>')
    def progress(filename):
        """Serve files from progress directory"""
        progress_dir = project_root / 'progress'
        if not progress_dir.exists():
            progress_dir.mkdir(exist_ok=True)
        return send_from_directory(progress_dir, filename)

    @app.route('/api/save-progress', methods=['POST'])
    def save_progress():
        """Save progress data to server"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Create progress directory if it doesn't exist
            progress_dir = project_root / 'progress'
            progress_dir.mkdir(exist_ok=True)

            # Generate readable filename
            import datetime
            now = datetime.datetime.now()
            months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december']
            month = months[now.month - 1]
            day = now.day
            year = now.year
            hour = now.hour
            minute = f"{now.minute:02d}"
            ampm = 'pm' if hour >= 12 else 'am'
            hour12 = hour % 12 or 12

            readable_timestamp = f"{month}_{day}_{year}_at_{hour12}_{minute}_{ampm}"
            filename = f"save_{readable_timestamp}.json"
            filepath = progress_dir / filename

            # Write the data
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return jsonify({
                'success': True,
                'filename': filename,
                'path': str(filepath)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/restart-server', methods=['POST'])
    def restart_server():
        """Restart the Flask server"""
        try:
            # Use Flask's built-in shutdown if available, otherwise force exit
            def shutdown():
                import time
                time.sleep(1)  # Give time for response to be sent
                try:
                    # Try graceful shutdown first
                    import signal
                    import os
                    os.kill(os.getpid(), signal.SIGTERM)
                except:
                    # Force exit if graceful shutdown fails
                    import os
                    os._exit(1)  # Exit with code 1 to trigger restart

            import threading
            thread = threading.Thread(target=shutdown)
            thread.daemon = True
            thread.start()

            return jsonify({'success': True, 'message': 'Server restarting...'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/update-source-json', methods=['POST'])
    def update_source_json():
        """Update the original source JSON files"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            data_type = data.get('dataType')
            patterns = data.get('patterns')

            if not data_type or not patterns:
                return jsonify({'error': 'Missing dataType or patterns'}), 400

            # Determine the correct file path
            if data_type == 'vowels':
                file_path = project_root / 'res' / 'sara' / 'sara_combos.json'
            elif data_type == 'foundations':
                file_path = project_root / 'res' / 'foundation' / 'foundation.json'
            elif data_type == 'exceptions':
                # Exceptions are hardcoded, but we could allow custom ones
                return jsonify({'error': 'Exceptions cannot be modified via file update'}), 400
            else:
                return jsonify({'error': f'Unknown data type: {data_type}'}), 400

            # Create backup before modifying
            import shutil
            import datetime
            backup_path = file_path.with_suffix(f'.backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            if file_path.exists():
                shutil.copy2(file_path, backup_path)

            # Update the file
            import json
            if data_type == 'foundations':
                # Foundation file has a different structure
                file_data = {"foundation": patterns}
            else:
                # Vowels file is just an array
                file_data = patterns

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)

            return jsonify({
                'success': True,
                'filename': file_path.name,
                'backup': backup_path.name,
                'patterns_count': len(patterns)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/save-temp-session', methods=['POST'])
    def save_temp_session():
        """Save temporary session data"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Create temp directory if it doesn't exist
            temp_dir = project_root / 'progress' / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Always save to the same temp file (overwrites previous)
            temp_file = temp_dir / 'latest_session.json'

            # Write the data
            import json
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return jsonify({
                'success': True,
                'message': 'Temporary session saved'
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/get-temp-session', methods=['GET'])
    def get_temp_session():
        """Get temporary session data"""
        try:
            temp_dir = project_root / 'progress' / 'temp'
            temp_file = temp_dir / 'latest_session.json'

            if not temp_file.exists():
                return jsonify({'error': 'No temporary session found'}), 404

            # Read the temp session
            import json
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Delete the temp file after reading (one-time use)
            temp_file.unlink()

            return jsonify(data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

def find_free_port(start_port=8000):
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

def main():
    """Main function"""
    print("Thai Character Pattern Classifier (Flask Server)")
    print("=" * 50)

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    try:
        os.chdir(project_root)
        print(f"Project root: {project_root}")
    except Exception as e:
        print(f"Error changing directory: {e}")
        return

    # Check required files
    html_file = project_root / 'tools' / 'thai_classifier_improved.html'
    if not html_file.exists():
        print(f"ERROR: {html_file} not found!")
        return

    res_dir = project_root / 'res'
    if not res_dir.exists():
        print(f"WARNING: {res_dir} not found!")

    # Find free port
    port = find_free_port()
    if port is None:
        print("ERROR: No free ports found!")
        return

    # Create Flask app
    app = create_app()

    # Display server info
    timestamp = int(time.time())
    url = f'http://localhost:{port}/?v={timestamp}'

    print()
    print("=" * 60)
    print("SERVER READY!")
    print("=" * 60)
    print("Open this link in your browser:")
    print(f"   {url}")
    print("=" * 60)
    print("Server running! Press Ctrl+C to stop.")
    print("=" * 60)
    print()

    try:
        # Run Flask server
        app.run(host='localhost', port=port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()