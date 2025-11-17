# Piece Recognition Retraining Guide

This guide explains how to use the new retraining and board orientation detection features to improve piece recognition accuracy over time.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Board Orientation Detection](#board-orientation-detection)
4. [Collecting Training Data](#collecting-training-data)
5. [Retraining the Model](#retraining-the-model)
6. [Analyzing Feedback](#analyzing-feedback)
7. [Best Practices](#best-practices)
8. [Programmatic Usage](#programmatic-usage)
9. [Troubleshooting](#troubleshooting)

## Overview

The chess engine now includes intelligent features that learn from your corrections:

- **Automatic Orientation Detection**: Determines if the board is viewed from white's or black's perspective
- **Feedback Collection**: Saves square images when you make corrections
- **Model Retraining**: Adjusts recognition parameters based on your corrections
- **Analytics**: Tracks which pieces are often misidentified

## Quick Start

### Using the GUI

1. **Load and process a chess board image**
   - File → Load Image
   - Process → Process Image

2. **Make corrections** (if needed)
   - Click "Enable Piece Correction" in Board Reconstruction tab
   - Click on any incorrect square
   - Select the correct piece
   - Images are automatically saved for training

3. **Retrain the model**
   - Training → Retrain from Feedback
   - Confirm the operation
   - Review the training statistics

4. **View your progress**
   - Training → View Feedback Statistics
   - See which pieces need more corrections

### First-Time Setup

No setup required! The system automatically:
- Creates the `output/` directory
- Stores feedback in `output/piece_recognition_feedback.json`
- Saves training images to `output/training_images/`

## Board Orientation Detection

### How It Works

The system automatically detects board orientation using two methods:

1. **Square Color Analysis**
   - Analyzes corner square brightness
   - Standard boards: a1 (dark), a8 (light)
   - Determines which side faces the user

2. **Piece Position Analysis**
   - Looks for white/black pieces in ranks
   - Uses starting position patterns
   - More reliable for initial positions

### Viewing Orientation

The orientation is logged during processing:
```
INFO: Board orientation: WHITE at bottom
```

### Manual Flipping

If orientation is detected incorrectly, the system provides a flip function:

```python
from src.computer_vision.board_detector import BoardDetector

detector = BoardDetector()
flipped_squares = detector.flip_board(squares)
```

## Collecting Training Data

### What Gets Saved

When you correct a piece, the system saves:
- **Square Image**: PNG file of the chess square
- **Original Prediction**: What the AI thought it was
- **User Correction**: What you said it actually is
- **Confidence Score**: How confident the original prediction was
- **Board Orientation**: Which way the board faced
- **Timestamp**: When the correction was made

### Storage Location

```
output/
├── piece_recognition_feedback.json     # Metadata
└── training_images/                     # Square images
    ├── e4_20240115_103045_123456.png
    ├── d4_20240115_103047_234567.png
    └── ...
```

### Minimum Recommendations

For effective retraining:
- **Minimum**: 3-5 corrections per piece type
- **Recommended**: 10-20 corrections per piece type
- **Best**: 30+ corrections covering various lighting/angles

## Retraining the Model

### From the GUI

1. **Menu**: Training → Retrain from Feedback
2. **Confirm**: Click "Yes" to proceed
3. **Review**: Check the training statistics

**Training Statistics Include:**
- Number of samples processed
- Piece types trained
- Count per piece type

### What Retraining Does

The system:
1. Analyzes features from corrected images
2. Calculates average characteristics per piece
3. Adjusts recognition thresholds
4. Stores learned parameters for future use

### When to Retrain

- After collecting 5-10 corrections
- When you notice recurring errors
- After processing images from a new setup
- Before important analysis sessions

## Analyzing Feedback

### View Statistics (GUI)

**Training → View Feedback Statistics**

Shows:
- Total corrections made
- Average original confidence
- Misclassification rate
- Breakdown by piece type

### Programmatic Analysis

```python
from src.computer_vision.feedback_manager import FeedbackManager

manager = FeedbackManager()
stats = manager.get_correction_statistics()

print(f"Total: {stats['total_corrections']}")
print(f"Avg confidence: {stats['avg_original_confidence']:.1%}")
print(f"By piece: {stats['by_piece_type']}")
```

### Finding Problem Areas

**Get Misclassifications:**
```python
misclassified = manager.get_misclassified_feedback()
for fb in misclassified:
    print(f"{fb.square_name}: {fb.original_prediction} → {fb.user_correction}")
```

**Filter by Piece Type:**
```python
knight_feedback = manager.get_feedback_by_piece_type(PieceType.WHITE_KNIGHT)
print(f"Knight corrections: {len(knight_feedback)}")
```

## Best Practices

### For Best Results

1. **Consistent Lighting**
   - Collect corrections from various lighting conditions
   - Include bright, dim, and shadowed squares

2. **Camera Angles**
   - Correct pieces from different viewing angles
   - Include both straight and angled shots

3. **Piece Styles**
   - If you use multiple chess sets, correct from each
   - The model learns set-specific features

4. **Regular Retraining**
   - Retrain after every 10-15 corrections
   - Don't wait until you have hundreds of corrections

5. **Verify Results**
   - After retraining, process a test image
   - Check if accuracy improved

### Common Mistakes to Avoid

❌ **Don't**:
- Retrain with only 1-2 corrections
- Clear feedback data frequently
- Only correct one type of piece
- Ignore orientation information

✅ **Do**:
- Collect diverse corrections
- Keep feedback data long-term
- Correct all types of errors
- Review statistics regularly

## Programmatic Usage

### Complete Workflow Example

```python
from pathlib import Path
import cv2
from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType
from src.computer_vision.feedback_manager import FeedbackManager

# Initialize components
detector = BoardDetector()
recognizer = PieceRecognizer()
manager = FeedbackManager()

# Process image
image = cv2.imread('chessboard.png')
board_image, squares = detector.detect_board(image)

# Detect orientation
orientation = detector.detect_board_orientation(squares)
print(f"Orientation: {orientation}")

# Recognize pieces
results = recognizer.recognize_board(squares)

# Simulate correction (in practice, this comes from user)
manager.add_feedback(
    square_name='e4',
    original_prediction=results[3][4].piece_type,
    original_confidence=results[3][4].confidence,
    user_correction=PieceType.WHITE_KNIGHT,
    square_image=squares[3][4],
    board_orientation=orientation
)

# Retrain when ready
training_data = manager.get_training_data()
if len(training_data) >= 5:
    result = recognizer.retrain_from_feedback(training_data)
    print(f"Training result: {result['status']}")
    print(f"Samples: {result['samples_processed']}")
```

### Exporting Data

```python
# Export feedback for external use
export_path = Path('exported_training_data.json')
manager.export_feedback(export_path)

# Clear feedback (use with caution!)
# manager.clear_feedback()
```

## Troubleshooting

### "No Training Data" Error

**Problem**: Trying to retrain with no feedback

**Solution**:
- Make at least 3-5 piece corrections first
- Ensure corrections include square images
- Check that `output/training_images/` has PNG files

### Orientation Always Defaults

**Problem**: Can't confidently detect orientation

**Solutions**:
- Ensure clear checkerboard pattern visible
- Check if pieces are in recognizable positions
- Manually flip if needed: `detector.flip_board(squares)`

### Training Images Not Saved

**Problem**: No images in `output/training_images/`

**Solutions**:
- Check write permissions on `output/` directory
- Ensure square images are provided when adding feedback
- Verify cv2 is installed correctly

### Poor Improvement After Retraining

**Problem**: Recognition still inaccurate after retraining

**Solutions**:
- Collect more diverse corrections (10+ per piece type)
- Include corrections from various lighting/angles
- Ensure feedback includes actual misclassifications, not just confirmations
- Try retraining with fresher, more relevant data

### Memory/Disk Space Issues

**Problem**: Too many training images

**Solutions**:
- Export feedback periodically: `manager.export_feedback(path)`
- Clear old feedback: `manager.clear_feedback()`
- Retrain before clearing (to preserve learning)
- Archive exported JSON files externally

## Advanced Topics

### Custom Thresholds

After retraining, you can adjust the minimum confidence:

```python
recognizer = PieceRecognizer(min_confidence=0.6)  # Stricter
# or
recognizer = PieceRecognizer(min_confidence=0.4)  # More lenient
```

### Batch Processing

Process multiple images and collect feedback:

```python
from pathlib import Path

image_dir = Path('chess_images/')
for img_path in image_dir.glob('*.png'):
    image = cv2.imread(str(img_path))
    # ... process and collect feedback
    
# Retrain once after processing all
training_data = manager.get_training_data()
recognizer.retrain_from_feedback(training_data)
```

### Integration with ML Pipelines

Export feedback for external ML training:

```python
# Get training data
training_data = manager.get_training_data()

# Convert to ML framework format
X = np.array([img for img, _ in training_data])
y = np.array([label.value[0] for _, label in training_data])

# Use with your ML framework
# model.fit(X, y)
```

## Support

For issues or questions:
- Check the main README.md
- Review PIECE_CORRECTION_FEATURE.md
- See examples/retraining_demo.py for code samples
- Open an issue on GitHub

## Version History

- **v1.1.0** - Added retraining and orientation detection features
- **v1.0.0** - Initial piece correction feedback system
