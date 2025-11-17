# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/jm0rt1/chess-engine.git
cd chess-engine

# 2. Set up virtual environment
./init-venv.sh
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install system packages (Linux only)
sudo apt-get install python3-tk
```

## Run the Application

### Option 1: PySide6 GUI (Recommended - Enhanced Visualization)

```bash
# Launch PySide6 GUI with comprehensive visualization
python run_pyside6.py
```

### Option 2: Original Tkinter GUI

```bash
# Launch original Tkinter GUI
python run.py
```

**Note**: The PySide6 GUI provides superior visualization including:
- Step-by-step image processing pipeline
- Visual board reconstruction with confidence scores
- Color-coded threat maps
- Move suggestions with arrows
- Professional appearance

See `PYSIDE6_GUI_README.md` for detailed PySide6 documentation.

## Using the GUI (Step-by-Step)

### Option 1: Load Screenshot
1. Click **"Load Screenshot"**
2. Select an image with a chess board
3. Click **"Detect & Recognize"**
4. Review the position in "Board State" tab
5. Click **"Confirm Position"** if correct

### Option 2: Manual Entry
1. Enter FEN string in the text field
2. Click **"Set Position"**

### Analyze Position
1. Click **"Analyze Threats"** to see:
   - All threats and attacks
   - Hanging pieces
   - Checks
   
2. Click **"Suggest Best Moves"** to get:
   - Top 5 moves
   - Scores
   - Explanations

## Example: Command Line Usage

```bash
# Run example scripts
python examples/basic_usage.py
```

## Example: Python Code

```python
from src.chess_engine.board_manager import BoardManager
from src.chess_engine.move_suggester import MoveSuggester
import chess

# Create board
board = BoardManager()

# Make a move
board.make_move(chess.Move.from_uci("e2e4"))

# Get suggestions
suggester = MoveSuggester(board)
best_moves = suggester.get_best_moves(num_moves=3)

for move_eval in best_moves:
    print(f"{move_eval.move.uci()}: {move_eval.explanation}")
```

## Testing

```bash
# Run all tests
./test.sh

# Or with pytest
python -m pytest tests/ -v
```

## Troubleshooting

### "No module named tkinter"
```bash
# Linux
sudo apt-get install python3-tk

# macOS
brew install python-tk

# Windows
# Reinstall Python with tcl/tk option checked
```

### "Failed to load image"
- Ensure image is a valid format (PNG, JPG, BMP)
- Try different board detection parameters
- Use manual FEN entry as fallback

### "Invalid FEN string"
- Check FEN format is correct
- Example: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`

## Need Help?

- See **CHESS_ENGINE_README.md** for detailed documentation
- Check **examples/basic_usage.py** for code examples
- Review **IMPLEMENTATION_SUMMARY.md** for architecture details
