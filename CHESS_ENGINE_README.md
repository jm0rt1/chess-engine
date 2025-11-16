# Chess Engine with Computer Vision

A complete chess engine written in Python with computer vision capabilities for analyzing chess positions from screenshots.

## Overview

This chess engine provides:
- **Computer Vision**: Automatically detect and recognize chess boards from screenshots
- **Position Analysis**: Analyze threats, hanging pieces, and tactical patterns
- **Move Suggestions**: Get the best move recommendations with detailed explanations
- **Graphical Interface**: User-friendly GUI built with Tkinter
- **Modular Design**: Clean OOP architecture following SOLID principles

## Features

### 1. Image Recognition
- Load screenshots of any digital chess game
- Automatic board detection and square extraction
- Piece recognition using computer vision techniques
- User confirmation workflow for recognized positions

### 2. Chess Engine
- Full move validation and generation
- Checkmate, stalemate, and check detection
- Material and positional evaluation
- Legal move calculation

### 3. Threat Analysis
- Identify all threats on the board
- Detect hanging (undefended) pieces
- Find checks and checkmates
- Analyze pins, forks, and other tactical patterns

### 4. Move Suggestions
- Calculate best moves with evaluation scores
- Provide detailed explanations for each move
- Identify tactical themes (captures, checks, forks, etc.)
- Compare multiple move options

### 5. Graphical User Interface
- Load and display chess board screenshots
- Interactive position confirmation
- Tabbed interface for different analyses
- ASCII board visualization
- Real-time analysis updates

## Installation

### Prerequisites
- Python 3.11 or higher
- System packages: python3-tk (for GUI)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/jm0rt1/chess-engine.git
cd chess-engine
```

2. **Initialize virtual environment**
```bash
./init-venv.sh
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install system packages (Linux)**
```bash
sudo apt-get install python3-tk
```

## Usage

### Running the Application

#### Method 1: Using the launcher script
```bash
python run.py
```

#### Method 2: Direct execution
```bash
python -m src.main
```

#### Method 3: Using VS Code debugger
1. Open the project in VS Code
2. Select "run.py" from the debug configuration dropdown
3. Click the green play button

### Using the Chess Engine

#### 1. Load a Chess Board Screenshot
- Click "Load Screenshot" button
- Select an image file containing a chess board
- The image will be displayed in the interface

#### 2. Recognize the Position
- Click "Detect & Recognize" to automatically detect and recognize pieces
- Review the recognized position in the "Board State" tab
- The system will ask for confirmation

#### 3. Confirm or Edit Position
- If the recognition is correct, click "Confirm Position"
- If incorrect, manually edit the FEN string and click "Set Position"
- You can also enter positions manually using FEN notation

#### 4. Analyze the Position
- Click "Analyze Threats" to see:
  - All threats and attacks
  - Hanging pieces
  - Checks and tactical patterns
  
- Click "Suggest Best Moves" to get:
  - Top 5 best moves
  - Evaluation scores
  - Detailed explanations
  - Tactical themes

### Manual Position Entry

You can enter positions directly using FEN (Forsyth-Edwards Notation):

1. Enter FEN string in the "FEN String" field
2. Click "Set Position"
3. The board will update with your position

Example FEN:
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

## Project Structure

```
chess-engine/
├── src/
│   ├── chess_engine/          # Core chess engine logic
│   │   ├── board_manager.py   # Board state and move validation
│   │   ├── threat_analyzer.py # Threat detection and analysis
│   │   └── move_suggester.py  # Best move calculation
│   ├── computer_vision/       # CV modules
│   │   ├── board_detector.py  # Board detection from images
│   │   └── piece_recognizer.py # Piece recognition
│   ├── gui/                   # GUI components
│   │   └── chess_app.py       # Main Tkinter application
│   └── main.py               # Application entry point
├── tests/                     # Unit tests
│   └── chess_engine/
│       └── test_board_manager.py
├── requirements.txt           # Python dependencies
├── run.py                     # Application launcher
└── README.md                  # This file
```

## Architecture

The project follows a modular, object-oriented design with clear separation of concerns:

### Chess Engine Module
- **BoardManager**: Encapsulates board state, move validation, and game rules
- **ThreatAnalyzer**: Analyzes tactical threats and patterns
- **MoveSuggester**: Evaluates positions and suggests optimal moves

### Computer Vision Module
- **BoardDetector**: Detects chess boards in images and extracts squares
- **PieceRecognizer**: Recognizes pieces using computer vision techniques

### GUI Module
- **ChessEngineGUI**: Main application interface with event handling

## Dependencies

Core libraries:
- `python-chess`: Chess logic and move generation
- `opencv-python`: Computer vision for image processing
- `Pillow`: Image handling and display
- `numpy`: Numerical operations
- `tkinter`: GUI framework (system package)

Development tools:
- `pytest`: Testing framework
- `autopep8`: Code formatting

## Testing

Run the test suite:
```bash
# Run all tests
./test.sh

# Run specific test module
python -m pytest tests/chess_engine/test_board_manager.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

## API Reference

### BoardManager

```python
from src.chess_engine.board_manager import BoardManager

# Initialize board
board = BoardManager()

# Make moves
move = chess.Move.from_uci("e2e4")
board.make_move(move)

# Get FEN position
fen = board.get_fen()

# Check game state
if board.is_checkmate():
    print("Checkmate!")
```

### ThreatAnalyzer

```python
from src.chess_engine.threat_analyzer import ThreatAnalyzer

# Analyze threats
analyzer = ThreatAnalyzer(board_manager)
analysis = analyzer.analyze_position()

# Get hanging pieces
hanging = analyzer.find_hanging_pieces(chess.WHITE)

# Get threat summary
summary = analyzer.get_threat_summary()
```

### MoveSuggester

```python
from src.chess_engine.move_suggester import MoveSuggester

# Get best moves
suggester = MoveSuggester(board_manager)
best_moves = suggester.get_best_moves(num_moves=3)

# Get single best move with explanation
move, explanation = suggester.get_best_move_with_explanation()
```

## Code Quality

This project follows Python best practices:
- **PEP 8**: Code style compliance
- **PEP 257**: Comprehensive docstrings for all classes and methods
- **Type Hints**: Type annotations for better code clarity
- **Comments**: Detailed inline comments explaining logic
- **SOLID Principles**: Single responsibility, proper encapsulation
- **Modular Design**: Clear separation of concerns

## Limitations and Future Improvements

### Current Limitations
- Computer vision piece recognition is heuristic-based (not ML-based)
- Board detection works best with clear, high-contrast images
- Evaluation function is simplified (not as strong as Stockfish)

### Potential Improvements
- Train ML model for more accurate piece recognition
- Implement more sophisticated evaluation (PST, king safety, pawn structure)
- Add support for chess variants
- Implement opening book and endgame tablebases
- Add UCI protocol support for external engine integration
- Improve board detection with deep learning
- Add game database and PGN support

## References

- [Chess Programming Wiki](https://www.chessprogramming.org/Main_Page) - Comprehensive chess programming resource
- [python-chess Documentation](https://python-chess.readthedocs.io/)
- [OpenCV Documentation](https://docs.opencv.org/)

## License

This project is licensed under the terms specified in the repository.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All classes and methods have PEP 257 compliant docstrings
- Comprehensive comments explain complex logic
- Tests are included for new features
- Modular design principles are maintained

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.
