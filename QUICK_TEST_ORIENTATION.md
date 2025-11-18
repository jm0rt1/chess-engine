# Quick Test Guide: Manual Board Orientation Feature

## Quick Start

To test the new manual orientation selection feature:

### 1. Run the Demo Script (No GUI needed)

```bash
python examples/test_orientation_correction.py
```

This demonstrates:
- How automatic detection can fail
- How manual selection solves the problem
- Data flow and normalization process

### 2. Run the GUI Application

```bash
python run_pyside6.py
```

## Test Scenarios

### Scenario A: Auto-detect with White on Bottom (Default)

**Steps:**
1. Launch GUI: `python run_pyside6.py`
2. Leave orientation selector on "Auto-detect" (default)
3. Load a chess board image with white pieces at bottom
4. Click "Process Image"
5. **Expected**: Board displays correctly without flipping

**Success Criteria:**
✓ White pieces appear at bottom of display  
✓ Rank labels show 1 at bottom, 8 at top  
✓ File labels show a-h from left to right  
✓ FEN string correctly represents the position

---

### Scenario B: Auto-detect FAILS with Black on Bottom (The Original Problem)

**Steps:**
1. Launch GUI: `python run_pyside6.py`
2. Leave orientation selector on "Auto-detect"
3. Load a chess board image with black pieces at bottom
4. Click "Process Image"
5. **Observe**: Board might display incorrectly if auto-detect fails

**If auto-detect fails:**
- ✗ Black pieces might be shown as rank 1 (wrong!)
- ✗ Coordinate labels might be incorrect
- ✗ FEN might be inverted

**Solution → Try Scenario C**

---

### Scenario C: Manual "Black on Bottom" (FIX for the problem)

**Steps:**
1. Launch GUI: `python run_pyside6.py`
2. **BEFORE processing**: Change orientation selector to "Black on Bottom"
3. Load a chess board image with black pieces at bottom
4. Click "Process Image"
5. **Expected**: Board displays correctly WITH automatic flip

**Success Criteria:**
✓ Data is automatically normalized (flipped 180°)  
✓ Black pieces shown at rank 8 position  
✓ White pieces shown at rank 1 position  
✓ Coordinate labels are correct  
✓ FEN string correctly represents the position  
✓ Can still use "Flip Board Orientation" button to toggle view

---

### Scenario D: Re-process with Different Orientation (No Reload Needed)

**Steps:**
1. Load an image and process it
2. If orientation is wrong, change the dropdown setting
3. Click "Process Image" **again** (image is already loaded)
4. **Expected**: Image is re-processed with new orientation setting

**Success Criteria:**
✓ No need to reload the image  
✓ Processing respects new orientation setting  
✓ Can try different settings until satisfied

---

### Scenario E: Manual "White on Bottom" (Explicit Control)

**Steps:**
1. Launch GUI: `python run_pyside6.py`
2. Change orientation selector to "White on Bottom"
3. Load any chess board image
4. Click "Process Image"
5. **Expected**: Board processed without flipping, regardless of auto-detect

**Success Criteria:**
✓ System skips automatic detection  
✓ No flipping occurs during processing  
✓ User has explicit control over orientation

---

## Visual Test Checklist

When the board is displayed correctly, you should see:

```
Rank 8 (top):    ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜  (Black's back rank)
Rank 7:          ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟  (Black pawns)
Rank 6:          . . . . . . . .
Rank 5:          . . . . . . . .
Rank 4:          . . . . . . . .
Rank 3:          . . . . . . . .
Rank 2:          ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙  (White pawns)
Rank 1 (bottom): ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖  (White's back rank)
                 a  b  c  d  e  f  g  h
```

### Key Visual Indicators

✓ **White pieces at bottom** = Rank 1  
✓ **Black pieces at top** = Rank 8  
✓ **Files a-h left to right**  
✓ **Ranks 1-8 bottom to top**

If you see black pieces at bottom with Rank 1 label → **Wrong orientation!**

---

## Common Issues & Solutions

### Issue: "Board is upside-down after processing"

**Cause**: Wrong orientation setting selected

**Solution**:
1. Change orientation dropdown to opposite setting
2. Click "Process Image" again (no reload needed)
3. OR use "Flip Board Orientation" button

---

### Issue: "Pieces are in wrong positions in FEN"

**Cause**: Data wasn't normalized correctly

**Solution**:
1. Check which orientation was selected during processing
2. Try "Black on Bottom" if image has black at bottom
3. Re-process the image

---

### Issue: "Auto-detect keeps failing"

**Solution**: 
✓ **Use manual selection instead**  
✓ Select "White on Bottom" or "Black on Bottom" explicitly  
✓ Don't rely on auto-detect for problematic images

---

## Testing Without Real Images

If you don't have chess board images, run the demo script:

```bash
python examples/test_orientation_correction.py
```

This simulates the issue and shows how the fix works.

---

## Expected Test Results

### Before This Fix
- ✗ Images with black on bottom couldn't be corrected
- ✗ Auto-detect failures were not recoverable
- ✗ Users were stuck with wrong orientation

### After This Fix
- ✓ Manual orientation selection available
- ✓ Users can override auto-detect
- ✓ All orientations can be handled
- ✓ Re-processing without reload
- ✓ Full control over board orientation

---

## Performance Test

The feature should not impact performance:

- **No extra computation** for default "Auto-detect"
- **Single flip operation** when manual "Black on Bottom" selected
- **Instant orientation switch** in dropdown
- **Fast re-processing** (no reload needed)

---

## Regression Test

Verify existing functionality still works:

1. **Flip Board Button**: Should still work after processing
2. **Coordinate Labels**: Should still flip with orientation
3. **Engine Analysis**: Should work with any orientation
4. **Piece Correction**: Should work regardless of orientation
5. **Auto-detect**: Should still work when selected

---

## Success Criteria Summary

The feature is working correctly if:

✓ Manual orientation selector appears in Control Panel  
✓ Three options available: Auto-detect, White on Bottom, Black on Bottom  
✓ Manual selection overrides auto-detect  
✓ Black-on-bottom images process correctly with manual selection  
✓ Can re-process without reloading image  
✓ FEN generation is correct after normalization  
✓ All existing features still work  
✓ No performance degradation

---

## Need Help?

If you encounter issues:

1. Check the detailed documentation: `MANUAL_ORIENTATION_FEATURE.md`
2. Run the demo: `python examples/test_orientation_correction.py`
3. Check test files for examples:
   - `tests/gui_pyside6/test_manual_orientation.py`
   - `tests/integration/test_manual_orientation_integration.py`

---

## Quick Command Reference

```bash
# Run GUI application
python run_pyside6.py

# Run demo (no GUI needed)
python examples/test_orientation_correction.py

# Run unit tests
python -m pytest tests/gui_pyside6/test_manual_orientation.py -v

# Run integration tests
python -m pytest tests/integration/test_manual_orientation_integration.py -v

# Run all tests
./test.sh
```

---

**Feature Status**: ✅ Ready for Testing
