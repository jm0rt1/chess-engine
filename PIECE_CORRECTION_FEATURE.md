# Interactive Piece Correction Feature

## Overview

The Interactive Piece Correction feature allows users to manually correct or confirm piece recognition results in the PySide6 Chess Engine GUI. This feature enables:

- **Immediate Correction**: Fix misrecognized pieces with a simple click
- **Feedback Collection**: Automatically store corrections for model improvement
- **Interactive Learning**: Build a dataset for future ML model training

## User Guide

### Enabling Correction Mode

1. Process a chess board image using the application
2. Navigate to the "Board Reconstruction" tab
3. Click the "Enable Piece Correction" button
4. Squares become clickable with yellow hover effects

### Correcting a Piece

1. **Click on a square** that you want to correct
2. A dialog appears showing:
   - Square name (e.g., "E4")
   - Current recognition (e.g., "White Pawn")
   - Confidence score (e.g., "65%")
3. **Select the correct piece** from the organized options:
   - White Pieces section (6 pieces)
   - Black Pieces section (6 pieces)
   - "Empty Square" option
4. **Click "Confirm Selection"** or press Enter
5. The board updates immediately with your correction

### Visual Feedback

- **Hover Effect**: Yellow highlight appears when hovering over squares
- **Confidence Updates**: Corrected squares show 100% confidence
- **Status Messages**: Status bar shows correction count
- **Board Refresh**: Board and FEN notation update automatically

## Technical Details

### Architecture

#### Components

1. **PieceCorrectionDialog** (`src/gui_pyside6/widgets/piece_correction_dialog.py`)
   - Modal dialog for piece selection
   - Organized by piece color
   - Pre-selects current piece
   - Emits signal on confirmation

2. **ClickableSquare** (in `board_widget.py`)
   - Custom QGraphicsRectItem
   - Handles mouse events
   - Provides hover effects
   - Triggers correction dialog

3. **BoardReconstructionWidget** (enhanced)
   - Toggle for correction mode
   - Signal emission for corrections
   - Updates display after correction

4. **FeedbackManager** (`src/computer_vision/feedback_manager.py`)
   - Stores correction data
   - Persists to JSON file
   - Provides statistics
   - Supports export

5. **MainWindow** (enhanced)
   - Coordinates correction flow
   - Updates recognition results
   - Shows feedback statistics

#### Data Flow

```
User clicks square
    ↓
ClickableSquare.mousePressEvent()
    ↓
BoardReconstructionWidget.on_square_clicked()
    ↓
PieceCorrectionDialog.show()
    ↓
User selects piece
    ↓
Dialog emits piece_selected signal
    ↓
BoardReconstructionWidget emits piece_corrected signal
    ↓
MainWindow.on_piece_corrected()
    ↓
1. Store feedback (FeedbackManager)
2. Update recognition results
3. Regenerate FEN
4. Refresh board display
5. Show confirmation message
```

### Feedback Data Structure

```json
[
  {
    "square_name": "e4",
    "original_prediction": "WHITE_PAWN",
    "original_confidence": 0.65,
    "user_correction": "WHITE_KNIGHT",
    "timestamp": "2024-01-15T10:30:45.123456"
  }
]
```

### File Locations

- **Feedback Storage**: `output/piece_recognition_feedback.json`
- **Dialog Component**: `src/gui_pyside6/widgets/piece_correction_dialog.py`
- **Feedback Manager**: `src/computer_vision/feedback_manager.py`
- **Board Widget**: `src/gui_pyside6/widgets/board_widget.py` (enhanced)
- **Main Window**: `src/gui_pyside6/main_window.py` (enhanced)

## Developer Guide

### Using FeedbackManager Programmatically

```python
from src.computer_vision.feedback_manager import FeedbackManager
from src.computer_vision.piece_recognizer import PieceType

# Initialize manager
manager = FeedbackManager()

# Add feedback
manager.add_feedback(
    square_name='e4',
    original_prediction=PieceType.WHITE_PAWN,
    original_confidence=0.65,
    user_correction=PieceType.WHITE_KNIGHT
)

# Get statistics
stats = manager.get_correction_statistics()
print(f"Total corrections: {stats['total_corrections']}")
print(f"By piece type: {stats['by_piece_type']}")
print(f"Avg confidence: {stats['avg_original_confidence']:.2%}")

# Export feedback
from pathlib import Path
manager.export_feedback(Path('exported_feedback.json'))

# Clear all feedback
manager.clear_feedback()
```

### Extending the Dialog

To add custom piece types or modify the dialog:

```python
# In piece_correction_dialog.py

# Add custom pieces to the dialog
custom_pieces = [
    ('🏴', 'Custom', CustomPieceType.CUSTOM_PIECE),
]

for i, (symbol, name, piece_type) in enumerate(custom_pieces):
    btn = QPushButton(f"{symbol}\n{name}")
    # ... configuration ...
```

### Signals and Slots

**BoardReconstructionWidget Signals**:
- `piece_corrected(str, int, int, object)`: Emitted when piece is corrected
  - Args: square_name, row, col, PieceType

**PieceCorrectionDialog Signals**:
- `piece_selected(object)`: Emitted when user confirms selection
  - Args: PieceType or None

### Testing

Run the feedback manager tests:

```bash
python -m pytest tests/computer_vision/test_feedback_manager.py -v
```

Tests cover:
- Feedback creation and serialization
- Manager initialization and persistence
- Adding and retrieving feedback
- Statistics calculation
- Export functionality
- Clearing feedback

## Use Cases

### 1. Manual Correction Workflow
**Scenario**: User loads a blurry image with low recognition confidence

**Steps**:
1. Load and process image
2. Review board reconstruction
3. Enable correction mode
4. Click on low-confidence squares
5. Correct misrecognized pieces
6. Run engine analysis on corrected position

### 2. Building Training Dataset
**Scenario**: Developer wants to improve the recognition model

**Steps**:
1. Collect diverse chess board images
2. Process each image through the application
3. Users correct any mistakes
4. Export feedback data
5. Use feedback as ground truth for ML training

### 3. Quality Assurance
**Scenario**: Testing recognition accuracy on known positions

**Steps**:
1. Process images with known positions
2. Enable correction mode
3. Verify each piece is correct
4. Review statistics to identify problematic pieces
5. Focus improvement efforts on common errors

## Best Practices

### For Users
1. **Always verify** low-confidence squares (< 70%)
2. **Enable correction mode** before making analysis decisions
3. **Check the entire board** systematically (rank by rank)
4. **Use keyboard shortcuts** for faster correction

### For Developers
1. **Monitor feedback statistics** to identify improvement areas
2. **Regularly export feedback** for backup and analysis
3. **Use feedback data** to retrain models periodically
4. **Document correction patterns** for debugging

## Troubleshooting

### Dialog Not Appearing
- **Check**: Correction mode is enabled (button shows "Disable Piece Correction")
- **Verify**: Clicking on the square itself, not margins

### Corrections Not Saving
- **Check**: Output directory exists and is writable
- **Verify**: `output/piece_recognition_feedback.json` is created
- **Review**: Log messages for any errors

### Board Not Updating
- **Check**: Valid FEN is generated after correction
- **Verify**: Recognition results array is properly updated
- **Try**: Restart application and reload image

## Future Improvements

1. **Bulk Correction Mode**: Select and correct multiple squares at once
2. **Confidence Threshold Filtering**: Only show squares below certain confidence
3. **Undo/Redo**: Revert corrections if needed
4. **Correction History**: View all corrections made in a session
5. **ML Model Integration**: Use feedback to automatically retrain models
6. **Collaborative Feedback**: Share feedback across users for better training
7. **Smart Suggestions**: Suggest likely corrections based on board context
8. **Keyboard Shortcuts**: Quick piece selection with keys

## Performance Considerations

- **Memory**: Feedback is stored in memory and persisted to disk
- **File Size**: JSON file grows with corrections (~200 bytes per entry)
- **UI Responsiveness**: Dialog creation is instant (< 50ms)
- **Feedback Saving**: Asynchronous to avoid blocking UI

## Security & Privacy

- **Local Storage**: All feedback stored locally in `output/` directory
- **No External Transmission**: Feedback is never sent to external servers
- **User Control**: Users can clear feedback at any time
- **Anonymous Data**: No personally identifiable information collected

## Credits

Developed as part of the Chess Engine with Computer Vision project.

## License

Same license as the main chess-engine project.
