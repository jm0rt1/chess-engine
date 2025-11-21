# Training Data Management Pipeline

## Overview

This document explains how the chess piece recognition training pipeline manages user feedback, handles corrections, and ensures clean training data for improved piece detection.

## Key Features

### 1. Session Tracking
Every labeling session is assigned a unique session ID that groups all corrections made during that session.

**Benefits:**
- Track which corrections came from which session
- Analyze session-specific accuracy improvements
- Enable future filtering or rollback of specific sessions

**Session ID Format:**
```
session_YYYYMMDD_HHMMSS_XXXXXXXX
```
Example: `session_20241121_143025_a7b3f2e1`

### 2. Image-Based Deduplication
Each correction is uniquely identified by combining:
- **Image Hash**: SHA256 hash of the source chess board image
- **Square Name**: The chess square (e.g., 'e4', 'd4')

**Unique Key Format:**
```
{image_hash}_{square_name}
```

This ensures that corrections for the same square in the same image are properly deduplicated, while corrections for the same square in different images are kept separate.

### 3. Correction Superseding
When a user corrects the same square multiple times in the same image:
1. The old correction is marked as `is_active = False` (superseded)
2. The new correction is added with `is_active = True`
3. Both entries remain in the database for audit purposes
4. Only active corrections are used for training

**Example:**
```
User corrects e4 as "white knight"  → Entry 1 (active)
User changes mind, corrects e4 as "white bishop" → Entry 1 (inactive), Entry 2 (active)
```

## Architecture

### Data Flow

```
┌─────────────────────┐
│   User loads image  │
│   (GUI/main_window) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  FeedbackManager.set_current_   │
│  image(image)                    │
│  - Computes image hash           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  User makes correction           │
│  (click square in GUI)           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  FeedbackManager.add_feedback()  │
│  - Computes unique key           │
│  - Checks for existing entry     │
│  - Supersedes if found           │
│  - Saves new correction          │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Feedback persisted to JSON      │
│  - All fields saved              │
│  - Training images saved         │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  User triggers retraining        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  get_training_data(active_only=  │
│  True)                           │
│  - Returns only active entries   │
│  - Loads images                  │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  PieceRecognizer.retrain_from_   │
│  feedback()                      │
│  - Trains on clean data          │
│  - Updates recognition params    │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Improved piece recognition!     │
└─────────────────────────────────┘
```

### Data Schema

**PieceFeedback Object:**
```json
{
  "square_name": "e4",
  "original_prediction": "WHITE_PAWN",
  "original_confidence": 0.65,
  "user_correction": "WHITE_KNIGHT",
  "timestamp": "2024-11-21T14:30:45.123456",
  "square_image_path": "training_images/e4_20241121_143045_123456.png",
  "board_orientation": "white",
  "session_id": "session_20241121_143025_a7b3f2e1",
  "unique_key": "9a7f3e...d4f2_e4",
  "image_hash": "9a7f3e2b1c5d8f4a...",
  "is_active": true
}
```

## Usage

### Basic Workflow

1. **Load an image:**
   ```python
   manager = FeedbackManager()
   manager.set_current_image(image)
   ```

2. **Add corrections:**
   ```python
   manager.add_feedback(
       square_name='e4',
       original_prediction=PieceType.WHITE_PAWN,
       original_confidence=0.6,
       user_correction=PieceType.WHITE_KNIGHT,
       square_image=square_img
   )
   ```

3. **Get clean training data:**
   ```python
   training_data = manager.get_training_data()  # Only active corrections
   ```

4. **Retrain the model:**
   ```python
   recognizer = PieceRecognizer()
   result = recognizer.retrain_from_feedback(training_data)
   ```

### Correction Workflow

**Scenario: User changes their mind**

```python
# User's first attempt
manager.add_feedback(
    square_name='e4',
    original_prediction=PieceType.WHITE_PAWN,
    original_confidence=0.6,
    user_correction=PieceType.WHITE_KNIGHT,
    square_image=square_img
)

# User realizes mistake, corrects again
manager.add_feedback(
    square_name='e4',
    original_prediction=PieceType.WHITE_KNIGHT,
    original_confidence=1.0,
    user_correction=PieceType.WHITE_BISHOP,
    square_image=square_img
)

# Result: Only WHITE_BISHOP will be in training data
training_data = manager.get_training_data()
# training_data contains 1 entry with label WHITE_BISHOP
```

### Session Management

**Track multiple sessions:**

```python
# Session 1
session1 = FeedbackManager(session_id='session_morning')
session1.set_current_image(image1)
session1.add_feedback(...)

# Session 2
session2 = FeedbackManager(session_id='session_afternoon')
session2.set_current_image(image2)
session2.add_feedback(...)

# Analyze sessions
manager = FeedbackManager()
summary = manager.get_session_summary()
for session_id, info in summary.items():
    print(f"{session_id}: {info['active_count']} active corrections")
```

### Statistics

**Get detailed statistics:**

```python
stats = manager.get_correction_statistics()

print(f"Total corrections: {stats['total_corrections']}")
print(f"Active: {stats['active_corrections']}")
print(f"Superseded: {stats['superseded_corrections']}")
print(f"Average confidence: {stats['avg_original_confidence']:.2%}")

print("\nBy piece type:")
for piece_type, count in stats['by_piece_type'].items():
    print(f"  {piece_type}: {count}")

print("\nBy session:")
for session, count in stats['by_session'].items():
    print(f"  {session[:25]}...: {count}")
```

## Implementation Details

### Deduplication Logic

When `add_feedback()` is called:

1. Compute unique key: `{image_hash}_{square_name}`
2. Search for existing feedback with same unique key
3. If found and active: mark it as `is_active = False`
4. Add new feedback with `is_active = True`
5. Save to disk

### Image Hashing

Images are hashed using SHA256 of a resized 64×64 version:

```python
def _compute_image_hash(self, image: np.ndarray) -> str:
    small = cv2.resize(image, (64, 64))
    image_bytes = small.tobytes()
    return hashlib.sha256(image_bytes).hexdigest()
```

This provides:
- **Fast computation**: Small image size
- **Consistent results**: Same image always produces same hash
- **Collision resistance**: SHA256 is cryptographically secure

### Storage

**File Structure:**
```
output/
├── piece_recognition_feedback.json  # Metadata with all fields
└── training_images/                  # Square images
    ├── e4_20241121_143045_123456.png
    ├── d4_20241121_143047_234567.png
    └── ...
```

**Disk Space:**
- ~200 bytes per JSON entry
- ~10-50 KB per training image
- 100 corrections ≈ 1-5 MB total

## Best Practices

### For Users

1. **Review before correcting**: Make sure you're confident in the correction
2. **It's OK to change your mind**: The system handles multiple corrections gracefully
3. **Correct diverse examples**: Include various lighting, angles, and piece styles
4. **Retrain regularly**: After 10-20 corrections, trigger retraining

### For Developers

1. **Always call `set_current_image()`**: Before processing a new image
2. **Use `get_training_data()`**: Not `get_training_data(active_only=False)`
3. **Check statistics**: Monitor `superseded_corrections` to gauge correction quality
4. **Backup feedback data**: Before clearing or making major changes

### For Training

1. **Minimum corrections**: At least 3-5 per piece type
2. **Diversity matters**: Vary lighting, angles, and piece styles
3. **Clean data is better**: Better to have fewer high-quality corrections
4. **Monitor statistics**: Use `get_correction_statistics()` to find problem areas

## Troubleshooting

### "Training data seems noisy"

**Cause**: Old implementation without deduplication
**Solution**: Clear old feedback and recollect:
```python
manager.clear_feedback(clear_images=True)
```

### "Corrections not improving recognition"

**Possible causes:**
1. Not enough corrections per piece type
2. Corrections too similar (same lighting/angle)
3. Retraining not triggered

**Solutions:**
1. Collect 10-20 corrections per piece type
2. Use images with varied conditions
3. Manually trigger retraining: Training → Retrain from Feedback

### "Session IDs are all the same"

**Cause**: Reusing same FeedbackManager instance across images
**Solution**: Create new manager or generate new session ID:
```python
manager = FeedbackManager(session_id=None)  # Auto-generates new ID
```

### "Duplicate entries in training data"

**Cause**: Not calling `set_current_image()` before corrections
**Solution**: Always call when processing new image:
```python
manager.set_current_image(image)
# Now add corrections...
```

## API Reference

### FeedbackManager

**Constructor:**
```python
FeedbackManager(
    feedback_file: Optional[Path] = None,
    session_id: Optional[str] = None
)
```

**Methods:**

- `set_current_image(image: np.ndarray)`: Set current image and compute hash
- `add_feedback(...)`: Add correction with deduplication
- `get_training_data(active_only: bool = True)`: Get training samples
- `get_correction_statistics(active_only: bool = True)`: Get statistics
- `get_feedback_by_session(session_id: str)`: Filter by session
- `get_session_summary()`: Summary of all sessions
- `clear_feedback(clear_images: bool = True)`: Clear all data

### PieceFeedback

**Attributes:**

- `square_name`: Chess square (e.g., 'e4')
- `original_prediction`: Original AI prediction
- `original_confidence`: Confidence (0-1)
- `user_correction`: User's correction
- `timestamp`: ISO timestamp
- `square_image_path`: Path to saved image
- `board_orientation`: 'white' or 'black'
- `session_id`: Session identifier
- `unique_key`: Deduplication key
- `image_hash`: Source image hash
- `is_active`: Whether currently active (not superseded)

## Future Enhancements

### Planned Features

1. **Automatic deduplication cleanup**: Periodically remove old superseded entries
2. **Session comparison**: Compare accuracy across sessions
3. **Confidence-based filtering**: Focus retraining on low-confidence corrections
4. **Export for ML frameworks**: Direct export to TensorFlow/PyTorch formats
5. **Cloud sync**: Optional sync of feedback across installations

### Research Directions

1. **Active learning**: Suggest which squares most need correction
2. **Transfer learning**: Use corrections to fine-tune neural networks
3. **Anomaly detection**: Identify unusual corrections that might be errors
4. **Crowdsourcing**: Aggregate feedback from multiple users

## Change Log

### Version 1.2.0 (Current)
- ✅ Added session tracking with unique IDs
- ✅ Implemented image-based deduplication
- ✅ Added correction superseding mechanism
- ✅ Enhanced statistics with active/superseded counts
- ✅ Backward compatible with old feedback files

### Version 1.1.0
- Added retraining from feedback
- Added board orientation detection
- Added square image storage

### Version 1.0.0
- Initial feedback collection system

## Support

For issues or questions:
- Check existing tests: `tests/computer_vision/test_feedback_deduplication.py`
- Review integration tests: `tests/integration/test_feedback_training_pipeline.py`
- See examples: `examples/retraining_demo.py`
