# PySide6 Chess Engine GUI Documentation

## Overview

The PySide6 Chess Engine GUI provides a comprehensive, interactive interface for visualizing chess board image processing and engine analysis. This implementation offers superior visualization capabilities compared to the original Tkinter version, with a focus on educational transparency and step-by-step pipeline visualization.

## Features

### 1. Verbose Image Processing Pipeline Visualization

The GUI displays every stage of the image processing workflow:

- **Raw Image Input**: Original loaded image
- **Preprocessing**: 
  - Grayscale conversion
  - Gaussian blur
  - Adaptive thresholding
- **Edge & Contour Detection**:
  - Canny edge detection
  - Contour visualization with overlays
- **Board Region Extraction**: Isolated chess board
- **Square Segmentation**: 8x8 grid with visual boundaries
- **Piece Recognition**: Individual squares with confidence scores

### 2. Board Reconstruction & Verification

- **Visual Chess Board**: High-quality rendering with Unicode chess pieces (♔♕♖♗♘♙)
- **Coordinate Labels**: Files (a-h) and ranks (1-8)
- **Confidence Indicators**: Color-coded confidence scores for each recognized piece
  - Green: High confidence (>80%)
  - Orange: Medium confidence (50-80%)
  - Red: Low confidence (<50%)
- **Interactive Piece Correction**: Click on any square to correct recognized pieces
  - Toggle correction mode with "Enable Piece Correction" button
  - Visual hover effects show clickable squares
  - Piece selection dialog for easy correction
  - Automatic feedback collection for model improvement
- **FEN Notation Display**: Complete FEN string for the position
- **Board State Information**: Turn, check status, game status
- **Recognition Summary**: Overall confidence statistics and warnings

### 3. Chess Engine Integration

#### Threat Map Visualization
- **Color-coded Attack Visualization**:
  - Light Red: Squares attacked by White
  - Dark Red: Squares attacked by Black
  - Purple: Squares attacked by both colors
- **Hanging Piece Detection**: Red circles around undefended pieces
- **Interactive Display**: Clear visual representation of all threats

#### Best Move Analysis
- **Visual Move Arrows**: Color-coded arrows showing top 5 moves
  - Green (#1): Best move
  - Blue (#2): Second best
  - Yellow (#3): Third best
  - Orange (#4): Fourth best
  - Purple (#5): Fifth best
- **Move Rankings**: Numbered labels on destination squares
- **Detailed Explanations**: 
  - Move notation (UCI format)
  - Evaluation scores
  - Tactical themes
  - Strategic explanations

### 4. Interactive Controls

#### Control Panel
- **Load Image**: Open file dialog to select chess board images
- **Process Image**: Run complete pipeline automatically
- **Step Through Pipeline**: Navigate through processing stages one-by-one
- **Run Engine Analysis**: Execute threat analysis and move suggestions
- **Manual FEN Entry**: Direct position input for testing
- **Reset Application**: Clear all data and start fresh

#### Menu Bar
- **File Menu**:
  - Load Image (Ctrl+O)
  - Exit (Ctrl+Q)
- **Process Menu**:
  - Process Image (Ctrl+P)
  - Step Through Pipeline (Ctrl+S)
- **Analysis Menu**:
  - Run Engine Analysis (Ctrl+E)
- **Help Menu**:
  - About dialog

## Installation

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# System dependencies (Linux)
sudo apt-get install libgl1-mesa-glx libegl1 libxkbcommon-x11-0
```

### Install Dependencies

```bash
# Navigate to project directory
cd chess-engine

# Install requirements
pip install -r requirements.txt

# This will install:
# - PySide6 (GUI framework)
# - opencv-python (image processing)
# - python-chess (chess logic)
# - numpy (numerical operations)
# - Pillow (image handling)
```

## Running the Application

### Launch GUI

```bash
# From project root directory
python run_pyside6.py

# Or
python3 run_pyside6.py
```

## Usage Guide

### Basic Workflow

1. **Load Image**
   - Click "Load Image..." button
   - Select a chess board image (PNG, JPG, BMP)
   - Image appears in pipeline visualization

2. **Process Image**
   - Click "Process Image" for automatic processing
   - OR click "Step Through Pipeline" to see each stage
   - Review each processing stage in the pipeline widget

3. **Verify Board Position**
   - Switch to "Board Reconstruction" tab
   - Check the visual board matches your image
   - Review confidence scores for each piece
   - Verify FEN notation is correct

4. **Correct Pieces (Optional)**
   - Click "Enable Piece Correction" button in Board Reconstruction tab
   - Click on any square that was incorrectly recognized
   - Select the correct piece from the dialog
   - Board updates automatically with your correction
   - Feedback is saved for future model training

5. **Run Analysis**
   - Click "Run Engine Analysis"
   - Switch to "Engine Analysis" tab
   - View threat map (shows attacked squares)
   - View best moves (with arrows and explanations)

### Step-by-Step Pipeline Mode

1. Click "Step Through Pipeline"
2. Use dropdown or Next/Previous buttons
3. Examine each stage:
   - See intermediate processing results
   - Understand how detection works
   - Identify potential issues

### Manual Position Entry

If automatic recognition fails:
1. Enter FEN string in "Manual Position Entry"
2. Click anywhere to confirm
3. Board updates immediately
4. Proceed with analysis

### Interactive Piece Correction

The piece correction feature allows you to improve recognition accuracy:

1. **Enable Correction Mode**
   - In the "Board Reconstruction" tab, click "Enable Piece Correction"
   - Instruction message appears: "Click on any square to correct the piece"
   - All squares become interactive with hover effects

2. **Correct a Piece**
   - Click on a square that was incorrectly recognized
   - A dialog appears showing:
     - The square name (e.g., "E4")
     - Current recognition result
     - Confidence score
   - Select the correct piece from:
     - White pieces (King, Queen, Rook, Bishop, Knight, Pawn)
     - Black pieces (King, Queen, Rook, Bishop, Knight, Pawn)
     - Empty Square
   - Click "Confirm Selection" or "Cancel"

3. **After Correction**
   - Board position updates immediately
   - FEN notation is regenerated
   - Confidence score changes to 100% for corrected square
   - Correction count is displayed in status bar
   - Feedback is automatically saved to `output/piece_recognition_feedback.json`

4. **Using Feedback**
   - All corrections are saved persistently
   - Feedback includes: square name, original prediction, confidence, and user correction
   - This data can be used to retrain or fine-tune the recognition model
   - Feedback is preserved across application sessions

## Architecture

### Module Structure

```
src/gui_pyside6/
├── __init__.py                 # Package initialization
├── main_window.py             # Main application window
└── widgets/                   # Custom widgets
    ├── __init__.py
    ├── control_panel.py       # Action buttons and controls
    ├── pipeline_widget.py     # Image processing visualization
    ├── board_widget.py        # Board reconstruction display
    └── analysis_widget.py     # Engine analysis display
```

### Design Principles

1. **Separation of Concerns**: Each widget handles a specific responsibility
2. **Signal-Slot Architecture**: Qt's signal-slot mechanism for communication
3. **Modular Components**: Widgets can be tested and modified independently
4. **Clean Interfaces**: Clear APIs between components
5. **Educational Focus**: Every step visible and understandable

## Widget Details

### MainWindow
- Coordinates all components
- Manages application state
- Handles menu actions
- Orchestrates workflow

### ControlPanelWidget
- Provides action buttons
- Manages workflow state
- Emits signals for actions
- Displays status information

### PipelineVisualizationWidget
- Displays processing stages
- Supports step-by-step navigation
- Shows multiple images per stage
- Allows stage selection

### BoardReconstructionWidget
- Renders chess board visually
- Displays Unicode chess pieces
- Shows confidence indicators
- Displays FEN and board state

### EngineAnalysisWidget
- Visualizes threat maps
- Draws move arrows
- Shows detailed analysis text
- Supports multiple tabs

## Customization

### Changing Board Colors

Edit `board_widget.py` or `analysis_widget.py`:

```python
# Light squares
light_color = QColor(240, 217, 181)

# Dark squares
dark_color = QColor(181, 136, 99)
```

### Adjusting Confidence Thresholds

Edit `board_widget.py`:

```python
if confidence > 0.8:  # High confidence
    conf_text.setDefaultTextColor(QColor(0, 200, 0))
elif confidence > 0.5:  # Medium confidence
    conf_text.setDefaultTextColor(QColor(255, 165, 0))
else:  # Low confidence
    conf_text.setDefaultTextColor(QColor(255, 0, 0))
```

### Modifying Arrow Colors

Edit `analysis_widget.py`:

```python
colors = [
    QColor(0, 200, 0, 200),      # Best move
    QColor(100, 150, 255, 180),  # Second
    QColor(255, 200, 0, 160),    # Third
    # Add more colors...
]
```

## Troubleshooting

### Application Won't Start

**Issue**: `ImportError: libEGL.so.1: cannot open shared object file`

**Solution**:
```bash
# Linux
sudo apt-get install libegl1-mesa libgles2-mesa

# Or set environment variable for software rendering
export QT_QPA_PLATFORM=offscreen
```

### Images Not Displaying

**Issue**: Images show as blank or corrupted

**Solution**:
- Check image format is supported (PNG, JPG, BMP)
- Verify image is not corrupted
- Try converting to PNG format
- Check file permissions

### Board Detection Fails

**Issue**: "Could not detect chess board"

**Solution**:
- Ensure board is clearly visible
- Good lighting conditions
- Board fills significant portion of image
- Try manual FEN entry as fallback

### Low Recognition Confidence

**Issue**: Piece recognition has low confidence

**Solution**:
- Use higher resolution images
- Ensure good contrast between pieces and board
- Check pieces are standard design
- Manually verify and correct using FEN entry

### GUI Appears Frozen

**Issue**: Application becomes unresponsive

**Solution**:
- Large images take time to process
- Check terminal for progress messages
- Consider resizing very large images
- Close and restart application

## Performance Optimization

### Image Size
- Recommended: 800x800 to 1200x1200 pixels
- Larger images take longer to process
- Resize very large images before loading

### Processing Speed
- Raw processing: ~2-5 seconds per image
- Engine analysis: ~0.5-1 second
- GUI rendering: Real-time

### Memory Usage
- Base application: ~100-150 MB
- With loaded image: +20-50 MB
- Total: ~200 MB typical usage

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Load Image |
| Ctrl+P | Process Image |
| Ctrl+S | Step Through Pipeline |
| Ctrl+E | Run Engine Analysis |
| Ctrl+Q | Exit Application |

## Comparison with Tkinter Version

| Feature | Tkinter | PySide6 |
|---------|---------|---------|
| Image Processing Visualization | Basic | **Comprehensive** |
| Board Display | ASCII/Simple | **Visual with Unicode** |
| Threat Visualization | Text Only | **Color-coded Map** |
| Move Display | Text List | **Visual Arrows** |
| Step-by-Step Mode | No | **Yes** |
| Confidence Display | No | **Yes** |
| Professional Look | Basic | **Modern** |
| Customization | Limited | **Extensive** |

## Feedback & Model Training

The application collects user feedback on piece recognition to enable future model improvements:

### Feedback Storage
- **Location**: `output/piece_recognition_feedback.json`
- **Format**: JSON array of feedback entries
- **Data Collected**:
  - Square name (e.g., 'e4')
  - Original prediction and confidence
  - User's correction
  - Timestamp

### Using Feedback for Training
The collected feedback can be used to:
1. **Identify weak spots**: Find which pieces are frequently misrecognized
2. **Build training dataset**: Use corrections as ground truth labels
3. **Fine-tune model**: Retrain recognition algorithms with real-world corrections
4. **Improve accuracy**: Target specific piece types that need improvement

### Viewing Feedback Statistics
After making corrections, the application displays:
- Total number of corrections in the session
- Count by piece type
- Average confidence of corrected predictions

### Exporting Feedback
Developers can programmatically export feedback:
```python
from src.computer_vision.feedback_manager import FeedbackManager

manager = FeedbackManager()
stats = manager.get_correction_statistics()
print(f"Total corrections: {stats['total_corrections']}")
manager.export_feedback(Path('my_feedback.json'))
```

## Future Enhancements

### Potential Additions
1. **3D Board Visualization**: Perspective view of the board
2. **Animation**: Smooth transitions between moves
3. **Game Replay**: Step through move history
4. **Position Editor**: Manual piece placement
5. **Database Integration**: Save and load positions
6. **Multiple Engine Support**: Connect to Stockfish, etc.
7. **Opening Book**: Display opening names
8. **Export Capabilities**: Save analysis as images/PDF
9. **Machine Learning Integration**: Use collected feedback to train a neural network for piece recognition
10. **Batch Correction**: Correct multiple pieces at once

## Technical Details

### Qt Version
- PySide6 6.5.0 or higher
- Qt 6.x framework
- Python bindings for Qt

### Threading
- Image processing on main thread
- Potential for background processing
- UI remains responsive

### Graphics
- QGraphicsScene/QGraphicsView for board rendering
- Vector-based drawing for scalability
- High-quality rendering

## Contributing

To contribute to the PySide6 GUI:

1. Follow existing widget patterns
2. Use Qt signal-slot mechanism
3. Document all public methods
4. Test on multiple platforms
5. Maintain separation of concerns

## Support

For issues or questions:
- Check this documentation
- Review the code comments
- Check GitHub issues
- Open a new issue with details

## License

Same license as the main chess-engine project.

## Credits

- Built with PySide6 (Qt for Python)
- Chess logic: python-chess library
- Image processing: OpenCV
- Unicode chess symbols: Standard Unicode set
