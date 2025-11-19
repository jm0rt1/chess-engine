# Square Name Calculation Bug Fix

## Issue

When users viewed a chess board from black's perspective (after using the "Flip Board Orientation" button), clicking on squares to correct pieces would save feedback data with incorrect square names.

### Example of the Problem

**Scenario:**
1. User loads an image with black pieces at bottom
2. System processes and normalizes the data
3. User clicks "Flip Board Orientation" to view from black's perspective
4. Board displays with H1 at top-left (correct for black's view)
5. User clicks on the top-left square to correct the piece
6. **BUG**: System saves feedback with square name "a8" instead of "h1"

### Root Cause

The `ClickableSquare.mousePressEvent` method always calculated square names using the white orientation formula:
```python
square_name = chess.square_name(chess.square(col, 7 - row))
```

This formula assumes:
- Row 0 = Rank 8 (top of board)
- Col 0 = File A (left side)

However, when viewing from black's perspective:
- Row 0 should = Rank 1 (top of board)
- Col 0 should = File H (left side)

## Solution

Modified the square name calculation to respect the `board_orientation` setting:

```python
if self.widget.board_orientation == 'white':
    # White perspective: row 0 = rank 8, col 0 = file a
    square_name = chess.square_name(chess.square(col, 7 - row))
else:
    # Black perspective: row 0 = rank 1, col 0 = file h
    square_name = chess.square_name(chess.square(7 - col, row))
```

### Formula Explanation

**White Orientation (default view):**
```
    a  b  c  d  e  f  g  h
8   .  .  .  .  .  .  .  .  8  ← row 0
7   .  .  .  .  .  .  .  .  7  ← row 1
6   .  .  .  .  .  .  .  .  6  ← row 2
5   .  .  .  .  .  .  .  .  5  ← row 3
4   .  .  .  .  .  .  .  .  4  ← row 4
3   .  .  .  .  .  .  .  .  3  ← row 5
2   .  .  .  .  .  .  .  .  2  ← row 6
1   .  .  .  .  .  .  .  .  1  ← row 7
    a  b  c  d  e  f  g  h
    ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
  col0 1  2  3  4  5  6  7

Formula: square(col, 7 - row)
- Top-left (row=0, col=0): square(0, 7) = a8 ✓
- Bottom-right (row=7, col=7): square(7, 0) = h1 ✓
```

**Black Orientation (after flip):**
```
    h  g  f  e  d  c  b  a
1   .  .  .  .  .  .  .  .  1  ← row 0
2   .  .  .  .  .  .  .  .  2  ← row 1
3   .  .  .  .  .  .  .  .  3  ← row 2
4   .  .  .  .  .  .  .  .  4  ← row 3
5   .  .  .  .  .  .  .  .  5  ← row 4
6   .  .  .  .  .  .  .  .  6  ← row 5
7   .  .  .  .  .  .  .  .  7  ← row 6
8   .  .  .  .  .  .  .  .  8  ← row 7
    h  g  f  e  d  c  b  a
    ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
  col0 1  2  3  4  5  6  7

Formula: square(7 - col, row)
- Top-left (row=0, col=0): square(7, 0) = h1 ✓
- Bottom-right (row=7, col=7): square(0, 7) = a8 ✓
```

## Impact

### Before Fix
- Feedback data saved with incorrect square names when viewing from black's perspective
- Made retraining difficult as square images didn't match their labeled square names
- Confusion when reviewing feedback data

### After Fix
- Square names always match what the user sees on screen
- Feedback data is accurate regardless of viewing orientation
- Enables correct retraining from user corrections

## Files Changed

- `src/gui_pyside6/widgets/board_widget.py`:
  - Modified `ClickableSquare.mousePressEvent()` to check board_orientation
  - Modified `_update_confidence_display()` to check board_orientation
- `tests/gui_pyside6/test_board_orientation_square_names.py`:
  - Added comprehensive tests for both orientations
  - Verifies all 64 squares map correctly

## Testing

### Manual Test
1. Load an image and process it
2. Click "Flip Board Orientation" to view from black's perspective
3. Click on the top-left square (should show as h1)
4. Verify the piece correction dialog shows "Square: h1"
5. Make a correction and check feedback.json - should show "square_name": "h1"

### Automated Tests
```bash
python -m unittest tests.gui_pyside6.test_board_orientation_square_names -v
```

Tests verify:
- White orientation square names (all corners and center)
- Black orientation square names (all corners and center)
- All 64 squares are uniquely mapped in both orientations
- Both orientations cover the complete set of squares

## Related Issues

This fix is critical for the feedback collection and retraining feature. Without it, feedback data collected while viewing from black's perspective would have:
- Square names that don't match the visual position
- Training data with incorrect labels
- Potential for model confusion during retraining

## Commit

Fixed in commit: `c7ef341`

## Backward Compatibility

This fix is 100% backward compatible:
- White orientation behavior unchanged (most common case)
- Black orientation now works correctly (was broken before)
- No changes to data structures or APIs
- Existing feedback data structure unchanged
