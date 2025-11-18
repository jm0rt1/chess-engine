# Manual Board Orientation Selection Feature

## Overview

This feature allows users to manually specify the board orientation when loading and processing chess board images. This is particularly useful when automatic orientation detection fails or when the user knows in advance whether the image was captured from white's or black's perspective.

## Problem Statement

Users reported being unable to correctly process images captured with "black on bottom" (from black's perspective). The automatic orientation detection sometimes fails, and even after using the "Flip Board Orientation" button, the board position could not be fully corrected.

### Root Cause

The automatic orientation detection uses heuristics (square colors and piece positions) to determine if the image shows white or black at the bottom. However, these heuristics can fail in certain scenarios:
- Non-standard board colors or lighting
- Incomplete piece positions (mid-game positions)
- Images with artifacts or poor quality

When the automatic detection fails, the data is processed in the wrong orientation, leading to an incorrect FEN representation.

## Solution

Added a manual orientation selector in the Control Panel that allows users to explicitly specify the expected board orientation **before** processing the image.

### User Interface Changes

#### Control Panel - Board Orientation Section

Added a dropdown menu labeled "Expected:" with three options:

1. **Auto-detect** (default)
   - System automatically determines orientation using existing heuristics
   - If black pieces are detected at bottom, data is automatically flipped during processing
   - Best for standard board images with good quality

2. **White on Bottom**
   - User explicitly declares that white pieces are at the bottom of the image
   - System processes the image as-is without flipping
   - Use this when you know the image is from white's perspective

3. **Black on Bottom**
   - User explicitly declares that black pieces are at the bottom of the image
   - System automatically flips the board data during processing to normalize it
   - Use this when you know the image is from black's perspective

### Technical Implementation

#### Data Normalization

The chess engine expects board data in a normalized form:
- **Row 0** = Rank 8 (black's back rank in standard starting position)
- **Row 7** = Rank 1 (white's back rank in standard starting position)

This normalized form allows the FEN generator to work correctly.

#### Processing Flow

When an image is processed:

1. **Image Loaded**: User loads a chess board image

2. **Orientation Preference Check**: System reads the dropdown selection

3. **Automatic Detection Path** (if "Auto-detect" selected):
   ```
   - Detect orientation using heuristics
   - If 'black' detected at bottom:
     - Flip board squares (180° rotation)
     - Flip recognition results
   - Set orientation = 'white' (normalized)
   ```

4. **Manual White Path** (if "White on Bottom" selected):
   ```
   - Skip automatic detection
   - Process data as-is (no flipping needed)
   - Set orientation = 'white'
   ```

5. **Manual Black Path** (if "Black on Bottom" selected):
   ```
   - Skip automatic detection
   - Flip board squares (180° rotation)
   - Flip recognition results
   - Set orientation = 'white' (normalized)
   ```

6. **FEN Generation**: Generate FEN from normalized data

7. **Display**: Show board with white perspective (user can still flip using the flip button)

#### Key Code Changes

**src/gui_pyside6/widgets/control_panel.py**
```python
# Added orientation selector dropdown
self.orientation_selector = QComboBox()
self.orientation_selector.addItem("Auto-detect", "auto")
self.orientation_selector.addItem("White on Bottom", "white")
self.orientation_selector.addItem("Black on Bottom", "black")

# Added getter method
def get_orientation_preference(self) -> str:
    return self.orientation_selector.currentData()
```

**src/gui_pyside6/main_window.py**
```python
# Modified process_image() to respect user preference
orientation_pref = self.control_panel.get_orientation_preference()

if orientation_pref == 'auto':
    detected = self.board_detector.detect_board_orientation(...)
    if detected == 'black':
        # Auto-flip if black detected at bottom
        self.board_squares = self.board_detector.flip_board(...)
        # ... flip recognition results ...
elif orientation_pref == 'black':
    # Manual black selection - flip data
    self.board_squares = self.board_detector.flip_board(...)
    # ... flip recognition results ...
# else: white orientation - no flip needed

self.board_orientation = 'white'  # Always normalize to white
```

## Usage Guide

### Basic Workflow

1. **Launch the Application**
   ```bash
   python run_pyside6.py
   ```

2. **Select Orientation (Optional)**
   - If you know your image orientation, select it from the "Expected:" dropdown
   - Leave as "Auto-detect" if unsure

3. **Load Image**
   - Click "Load Image..." button
   - Select your chess board image

4. **Process Image**
   - Click "Process Image" button
   - System will automatically handle orientation based on your selection
   - Review the board reconstruction

5. **Verify & Adjust**
   - If orientation is still incorrect:
     - Change the "Expected:" dropdown setting
     - Click "Process Image" again (no need to reload)
   - If you want to view from black's perspective:
     - Use "Flip Board Orientation" button after processing

6. **Analyze**
   - Once board is correct, click "Run Engine Analysis"

### Example Scenarios

#### Scenario 1: Auto-detect Success
```
Image: Standard board with white on bottom
Setting: Auto-detect
Result: ✓ Correctly processed without flipping
```

#### Scenario 2: Auto-detect Failure
```
Image: Photo from black's perspective
Setting: Auto-detect
Result: ✗ Incorrectly detected as white orientation

Solution:
1. Change "Expected:" to "Black on Bottom"
2. Click "Process Image" again
Result: ✓ Correctly processed with automatic flip
```

#### Scenario 3: Known Orientation
```
Image: You know it's from black's perspective
Setting: Black on Bottom (selected before loading)
Result: ✓ Correctly processed, skips unreliable auto-detection
```

### Tips

- **Set orientation before processing**: While you can change it after, it's best to set the expected orientation before clicking "Process Image"

- **No need to reload**: If you change the orientation setting, just click "Process Image" again - the system will reprocess the already-loaded image

- **Use manual selection for consistency**: If you have a batch of images all from the same perspective, use manual selection to ensure consistent processing

- **Flip button still available**: After processing, you can still use the "Flip Board Orientation" button to toggle between viewing from white's and black's perspectives

## Testing

### Unit Tests

**tests/gui_pyside6/test_manual_orientation.py**
- Tests orientation selector functionality
- Verifies default is "Auto-detect"
- Tests all three orientation options
- Verifies reset behavior

### Manual Testing

**examples/test_orientation_correction.py**
- Demonstrates automatic detection behavior
- Shows how manual selection solves detection failures
- Provides visual examples of board states

Run the demo:
```bash
python examples/test_orientation_correction.py
```

## Files Modified

- `src/gui_pyside6/widgets/control_panel.py` - Added orientation selector UI
- `src/gui_pyside6/main_window.py` - Updated processing logic to respect orientation preference

## Files Added

- `tests/gui_pyside6/test_manual_orientation.py` - Unit tests for the feature
- `examples/test_orientation_correction.py` - Demonstration script
- `MANUAL_ORIENTATION_FEATURE.md` - This documentation

## Backward Compatibility

This feature is fully backward compatible:
- Default behavior is "Auto-detect" which matches the original automatic detection
- Existing functionality is unchanged when auto-detect is used
- No breaking changes to APIs or existing code

## Future Enhancements

Potential improvements for future releases:

1. **Remember Preference**: Save user's orientation preference across sessions
2. **Per-Image Setting**: Allow different orientations for different loaded images
3. **Visual Indicator**: Add a visual indicator showing current orientation in the board display
4. **Batch Processing**: Allow setting orientation for batch processing multiple images
5. **Better Auto-Detection**: Improve automatic detection algorithms using machine learning

## Related Issues

- Original issue: "Unable to fix orientation of loaded images if they are from the perspective of black on bottom"
- Related: Board Orientation Coordinate Label Feature (BOARD_ORIENTATION_FEATURE.md)

## Troubleshooting

### Problem: Board still shows incorrect orientation after selection

**Solution**: Make sure to click "Process Image" after changing the orientation setting. The setting only takes effect during processing.

### Problem: Pieces are upside-down

**Solution**: Use the "Flip Board Orientation" button to rotate the view 180 degrees.

### Problem: FEN is incorrect

**Solution**: 
1. Verify the board reconstruction visually matches your image
2. Try a different orientation setting
3. Use piece correction to fix any misrecognized pieces
4. Process again after corrections

## Summary

The Manual Board Orientation Selection feature provides users with full control over board orientation, ensuring that images captured from any perspective can be correctly processed. By allowing manual override of automatic detection, users can now reliably work with images that previously failed to process correctly.
