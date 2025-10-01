#!/usr/bin/env python3
"""
Flask server for Thai Grapheme Highlighting Tool
Provides API endpoints for grapheme classification and AVP detection
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import vowel detector (optional for now)
detector = None
try:
    from conjecture_based_vowel_detector import ConjectureBasedVowelDetector
    VOWEL_JSON_PATH = "thai_vowels_tagged_9-21-2025-2-31-pm.json"
    detector = ConjectureBasedVowelDetector(VOWEL_JSON_PATH)
    print(f"✓ Loaded vowel detector from {VOWEL_JSON_PATH}")
except ImportError:
    print(f"⚠ Warning: conjecture_based_vowel_detector not found - AVP detection disabled")
except Exception as e:
    print(f"⚠ Warning: Could not load vowel detector: {e}")

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the main HTML file"""
    # HTML file is in the parent directory (project root)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(parent_dir, 'thai_grapheme_highlighter.html')

@app.route('/api/classify', methods=['POST'])
def classify_text():
    """
    Classify Thai text into grapheme categories

    Request JSON:
    {
        "text": "ประเทศไทย"
    }

    Response JSON:
    {
        "text": "ประเทศไทย",
        "classifications": [
            {"index": 0, "char": "ป", "class": "tan", "avp": false},
            {"index": 1, "char": "ร", "class": "tan", "avp": false},
            ...
        ],
        "avps": [3, 7, 10]  // AVP positions
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Classify each character
        classifications = []
        avps = []

        # Get vowel positions using detector
        vowel_data = {}
        if detector:
            try:
                vowel_data = detector.find_vowels(text)
            except Exception as e:
                print(f"Vowel detection error: {e}")

        # Classify each character
        for i, char in enumerate(text):
            classification = classify_character(char, i, text, vowel_data)
            classifications.append({
                "index": i,
                "char": char,
                "class": classification["class"],
                "avp": classification["avp"]
            })

            if classification["avp"]:
                avps.append(i)

        return jsonify({
            "text": text,
            "classifications": classifications,
            "avps": avps
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def classify_character(char, index, text, vowel_data):
    """
    Classify a single character into grapheme categories

    Returns:
    {
        "class": "tan" | "sara" | "yuk" | "kho_yok_waen" | "unsure",
        "avp": boolean
    }
    """

    # Thai character ranges
    THAI_CONSONANTS = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
    THAI_TONE_MARKS = "่้๊๋"
    THAI_DIACRITICS = "์็ํ"
    # Vowels (excluding tone marks and diacritics which are checked first)
    THAI_VOWELS = "ะัาำิีึืุูเแโใไฯ"

    # Exception characters (อ and ว)
    EXCEPTIONS = "อว"

    classification = {
        "class": "unsure",
        "avp": False
    }

    # 1. Check tone marks and diacritics first (ยุกต์/yuk)
    if char in THAI_TONE_MARKS or char in THAI_DIACRITICS:
        classification["class"] = "yuk"
        return classification

    # 2. Check vowels (สระ/sara)
    if char in THAI_VOWELS:
        classification["class"] = "sara"
        # AVP detection disabled for now
        classification["avp"] = False
        return classification

    # 3. Check consonants (ฐาน/tan)
    if char in THAI_CONSONANTS:
        # Check if it's an exception character - leave as unsure for now
        if char in EXCEPTIONS:
            classification["class"] = "unsure"
        else:
            classification["class"] = "tan"
        return classification

    # 4. Everything else is unsure
    return classification

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "detector_loaded": detector is not None
    })

@app.route('/api/restart', methods=['POST'])
def restart():
    """Restart the Flask server"""
    import sys
    import threading

    def shutdown():
        # Wait a moment to send response
        import time
        time.sleep(0.5)
        # Exit with code 42 to signal restart
        sys.exit(42)

    # Start shutdown in background thread
    thread = threading.Thread(target=shutdown)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "restarting"})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Thai Grapheme Highlighting Tool - Flask Server")
    print("="*60)
    print("\nServer starting...")
    print(f"Vowel detector: {'✓ Loaded' if detector else '✗ Not loaded'}")
    print("\n" + "="*60)
    print("Open in browser: http://127.0.0.1:5001")
    print("="*60 + "\n")

    app.run(debug=True, port=5001, use_reloader=True)
