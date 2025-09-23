# Thai Syllable Labeling System Documentation

## Overview
A web-based labeling interface for creating training data to improve Thai reading order algorithm. The system generates all possible interpretations for Thai words and allows you to label the correct one, building a dataset for pattern discovery.

## System Architecture

### Databases
- **`database/thai_voraritskul_graphemes.db`**: Stores Thai characters, patterns, tags, and valid clusters
- **`database/thai_syllable_labels.db`**: Stores labeling decisions, sessions, and extracted patterns

### Core Components
1. **Flask Server** (`thai_labeling_app.py`): Backend API server
2. **Web Interface** (`thai_syllable_labeler.html`): Visual labeling interface
3. **Pattern Extractor** (`database/extract_patterns.py`): Analyzes labeled data for patterns
4. **Database Tools** (`database/` folder): Initialize, import, and query utilities

## Installation & Setup

### First-Time Setup
```bash
# 1. Initialize databases
python database/init_databases.py

# 2. Import existing data
python database/import_thai_data.py

# 3. (Optional) Define valid clusters
# Edit import_thai_data.py to add your cluster list
```

### Running the Server

#### Option 1: Using Batch File (Windows) - RECOMMENDED
```bash
# Double-click or run:
launcher\syllable_label_server.bat
```

#### Option 2: Direct Python
```bash
python thai_labeling_app.py
```

### Port Configuration
✅ **AUTOMATIC PORT DETECTION**: The server now automatically finds an available port between 5001-5010.

The server will:
1. Try port 5001 first
2. If busy, automatically try 5002, 5003, etc. up to 5010
3. Display the URL with the correct port in the console
4. Dynamically inject the correct port into the HTML interface

No manual configuration needed!

## Using the Labeling Interface

### Basic Workflow

1. **Start Server**
   ```bash
   launcher\syllable_label_server.bat
   # OR
   python thai_labeling_app.py
   ```
   Server will display the URL with port (e.g., http://localhost:5001)

2. **Open Browser**
   - Click the URL shown in the console
   - The server automatically handles port injection

3. **Label Words**
   - Enter a Thai word in the input field
   - Click "Analyze" or press Enter
   - System shows all possible interpretations

4. **Select Interpretation**
   - **Option A**: Click an interpretation card to select it
   - **Option B**: Fill custom interpretation form if system missed the correct one

5. **Save Label**
   - Add optional notes
   - Click "Save Label"

### Batch Processing

1. **Load Multiple Words**
   - Use the Word Queue panel on the right
   - Enter words (one per line) in textarea
   - Click "Load Batch"
   - System will process words sequentially

2. **Navigate Queue**
   - Click any word in queue to jump to it
   - Green checkmark shows labeled words
   - Blue highlight shows current word

### Understanding Interpretations

Each interpretation card shows:
- **Reading Order**: Visual breakdown of components
  - Foundation (consonant base)
  - Vowel pattern
  - Final consonant (if any)
- **Pattern Template**: Like "xา" or "เxf" (x=foundation, f=final)
- **Validation Badge**:
  - Green "Valid" - All clusters are valid
  - Red "Has Issues" - Contains invalid clusters or unknown patterns
- **Tags**: Dynamically loaded from database (may show "Loading..." initially)

## Data Analysis

### Extract Patterns
After labeling several words, analyze patterns:
```bash
python database/extract_patterns.py
```

This will:
- Show tag combination patterns
- Identify ambiguity resolution preferences
- List algorithm gaps (custom interpretations)
- Save patterns to database

### Query Database
```bash
python database/query_utilities.py
```

Check specific character tags or validate interpretations.

## Testing the System

### Test Cases to Try

1. **Simple word** (unambiguous):
   - Input: "ยา"
   - Expected: Single interpretation
   - Foundation: ย, Vowel: า, Pattern: xา

2. **Ambiguous word**:
   - Input: "เลว"
   - Expected: Multiple interpretations
   - Tests cluster vs. final consonant handling

3. **Complex pattern**:
   - Input: "เด็ก"
   - Tests vowel wrapping (เ...็)
   - Pattern: เx็f

4. **Custom interpretation**:
   - Input any word
   - Don't select any interpretation
   - Fill custom form with new pattern
   - Tests algorithm gap detection

### Validation Checks

1. **Database Connection**:
   - Check interpretations load tags
   - Verify "Save Label" creates database entry
   - Run `extract_patterns.py` to confirm data saved

2. **Session Persistence**:
   - Label a word
   - Refresh page
   - Stats should persist via localStorage

3. **Cluster Validation**:
   - Add valid clusters to database
   - Test words with clusters
   - Invalid clusters should show "Has Issues"

## Troubleshooting

### Server Won't Start
- **All ports busy (5001-5010)**: Server will show error message. Wait for a port to free up
- **Module missing**: Server auto-installs Flask, but check with `pip install flask flask-cors`
- **Database missing**: Run `python database/init_databases.py`

### No Interpretations Generated
- Check `thai_reading_order.py` exists
- Verify vowel patterns file: `thai_vowels_tagged_9-21-2025-2-31-pm.json`
- Check foundation file: `res/foundation/foundation.json`

### Tags Not Loading
- Database might be disconnected
- Check browser console for errors
- Verify database has data: `python database/query_utilities.py`

### Labels Not Saving
- Check server console for errors
- Verify `thai_syllable_labels.db` exists
- Check browser Network tab for failed requests

## Customization

### Add Valid Clusters
Edit `database/import_thai_data.py`:
```python
clusters = [
    {'cluster': 'กร', 'components': ['ก', 'ร'], 'usage_position': 'initial'},
    {'cluster': 'กล', 'components': ['ก', 'ล'], 'usage_position': 'initial'},
    # Add more...
]
importer.import_valid_clusters(clusters)
```

### Change UI Layout
Edit `thai_syllable_labeler.html`:
- Styles are in `<style>` section
- Card layout: `.interpretation-card`
- Colors: Change hex values
- Fonts: Modify `font-family` in `.thai-input`, `.component-char`

### Add New Categories
Beyond foundation/vowel_pattern/dependent:
```python
# In database/import_thai_data.py
category_id = importer.get_or_create_category(conn, 'your_new_category')
```

## Important Notes

1. **Single Syllable Focus**: System assumes one syllable per word currently
2. **Dynamic Tags**: Tags are loaded from database, not stored with labels
3. **Custom Interpretations**: Indicate algorithm failures, valuable for improvement
4. **No Auto-Save**: Must click "Save Label" explicitly
5. **Session Storage**: Uses localStorage, clears on browser data clear

## API Endpoints

The Flask server provides:
- `GET /` - Serve main HTML interface
- `POST /api/generate-interpretations` - Generate all interpretations for a word
- `POST /api/save-label` - Save labeling decision
- `POST /api/get-tags` - Get tags for characters
- `GET /api/get-session-stats` - Get current session statistics
- `POST /api/load-word-batch` - Check which words are already labeled

## Next Development Steps

1. ✅ **Port Detection**: ~~Add automatic port finding (5001-5010)~~ COMPLETED
2. **Multi-Syllable**: Extend to handle word segmentation
3. **Context Tags**: Add semantic/frequency tags for disambiguation
4. **Export Features**: CSV/JSON export of labeled data
5. **Undo/Edit**: Allow editing previous labels
6. **Confidence Scores**: Add labeler confidence ratings
7. **Integration**: Connect pattern classifier tags directly to this database