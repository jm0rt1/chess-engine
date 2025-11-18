# Board Orientation Coordinate Label Feature

## Overview

This feature extends the existing board flip functionality to also flip coordinate labels (a-h, 1-8) when the board orientation is changed. This ensures that the coordinate labels always match the perspective of the flipped board.

## Background

Issue #6 requested: "Added the ability to flip where the pieces are, but I want to be able to flip the numbering on the board too if needed."

Previously:
- Board pieces could be flipped using the "Flip Board Orientation" button or Ctrl+F
- Coordinate labels remained static (always showing white's perspective)
- This created a mismatch between piece positions and coordinate labels after flipping

## Implementation

### Changes Made

1. **BoardReconstructionWidget** (`src/gui_pyside6/widgets/board_widget.py`)
   - Added `board_orientation` property (default: 'white')
   - Updated coordinate rendering logic to calculate labels based on orientation
   - Added `set_board_orientation()` method to update orientation

2. **EngineAnalysisWidget** (`src/gui_pyside6/widgets/analysis_widget.py`)
   - Added `board_orientation` property (default: 'white')
   - Updated coordinate rendering in threat map and best moves displays
   - Added `set_board_orientation()` method to update orientation

3. **MainWindow** (`src/gui_pyside6/main_window.py`)
   - Updated widget initialization to pass board orientation
   - Modified `flip_board_orientation()` to update widget orientations
   - Updated analysis and piece correction handlers to maintain orientation

### Coordinate Calculation Logic

#### White Orientation (default)
- **Ranks**: Row 0 = Rank 8, Row 7 = Rank 1 (formula: `8 - row`)
- **Files**: Col 0 = 'a', Col 7 = 'h' (formula: `chr(ord('a') + col)`)

```
     a  b  c  d  e  f  g  h
  8  . . . . . . . .  8
  7  . . . . . . . .  7
  6  . . . . . . . .  6
  5  . . . . . . . .  5
  4  . . . . . . . .  4
  3  . . . . . . . .  3
  2  . . . . . . . .  2
  1  . . . . . . . .  1
     a  b  c  d  e  f  g  h
```

#### Black Orientation (after flip)
- **Ranks**: Row 0 = Rank 1, Row 7 = Rank 8 (formula: `row + 1`)
- **Files**: Col 0 = 'h', Col 7 = 'a' (formula: `chr(ord('h') - col)`)

```
     h  g  f  e  d  c  b  a
  1  . . . . . . . .  1
  2  . . . . . . . .  2
  3  . . . . . . . .  3
  4  . . . . . . . .  4
  5  . . . . . . . .  5
  6  . . . . . . . .  6
  7  . . . . . . . .  7
  8  . . . . . . . .  8
     h  g  f  e  d  c  b  a
```

## Usage

### In the GUI

1. Run the PySide6 GUI:
   ```bash
   python run_pyside6.py
   ```

2. Load and process a chess board image

3. Flip the board orientation:
   - Click the "Flip Board Orientation" button
   - Or use keyboard shortcut: **Ctrl+F**

4. Observe that:
   - Piece positions are rotated 180 degrees
   - **Coordinate labels now also flip to match the new orientation**

### Running the Demo

To see a visual demonstration of the coordinate labeling:

```bash
python examples/board_orientation_demo.py
```

This will display ASCII art showing how coordinates change between white and black orientations.

## Testing

### Unit Tests

**`tests/gui_pyside6/test_board_orientation.py`**
- Tests coordinate calculation formulas for both orientations
- Verifies rank and file label calculations
- Tests orientation toggle logic

**`tests/gui_pyside6/test_orientation_coordinates.py`**
- Integration tests for widgets with orientation support
- Tests widget initialization and orientation changes
- Verifies orientation persistence across updates

Run tests:
```bash
./test.sh
# or
python -m pytest tests/gui_pyside6/test_board_orientation.py -v
```

### Manual Testing

See `examples/board_orientation_demo.py` for a visual demonstration that can be run without a GUI display.

## Files Modified

- `src/gui_pyside6/widgets/board_widget.py` - Added orientation support to board reconstruction widget
- `src/gui_pyside6/widgets/analysis_widget.py` - Added orientation support to analysis widget
- `src/gui_pyside6/main_window.py` - Pass orientation to widgets when updating

## Files Added

- `tests/gui_pyside6/test_board_orientation.py` - Unit tests for coordinate calculations
- `tests/gui_pyside6/test_orientation_coordinates.py` - Integration tests for widgets
- `examples/board_orientation_demo.py` - Visual demonstration script
- `BOARD_ORIENTATION_FEATURE.md` - This documentation

## Design Decisions

1. **Minimal Changes**: Only modified the coordinate rendering logic, leaving piece rendering unchanged
2. **Backward Compatible**: Default orientation is 'white', matching previous behavior
3. **Consistent State**: Orientation is set once and persists across widget updates
4. **Synchronized Updates**: All widgets (board, analysis, threats, moves) update together when orientation changes

## Future Enhancements

Potential improvements for future work:
- Remember user's preferred orientation across sessions
- Add visual indicator showing current orientation in the UI
- Support orientation preference per loaded image
- Add orientation to saved/exported board positions

## Related Issues

- Issue #6: "Add manual board orientation flip for post-processing correction"

## Security

CodeQL analysis completed with **0 alerts** - no security vulnerabilities introduced.
