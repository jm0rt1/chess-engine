#!/usr/bin/env python3
"""
Demo script for the retraining and orientation detection features.

This script demonstrates:
1. Board orientation detection
2. Collecting feedback with square images
3. Retraining the piece recognizer
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.computer_vision.feedback_manager import FeedbackManager
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType
from src.computer_vision.board_detector import BoardDetector


def create_mock_square_images():
    """Create mock square images for demonstration."""
    images = {}
    
    # Create different types of squares with distinct features
    # White pawn - lighter, simple shape
    white_pawn_img = np.ones((100, 100, 3), dtype=np.uint8) * 180
    white_pawn_img[40:80, 45:55] = 150  # Simple vertical shape
    images['white_pawn'] = white_pawn_img
    
    # Black knight - darker, complex shape
    black_knight_img = np.ones((100, 100, 3), dtype=np.uint8) * 120
    black_knight_img[30:70, 30:70] = 60  # Complex shape
    black_knight_img[40:50, 40:50] = 40  # Add detail
    images['black_knight'] = black_knight_img
    
    # Empty square - uniform
    empty_img = np.ones((100, 100, 3), dtype=np.uint8) * 200
    images['empty'] = empty_img
    
    # White queen - light, very complex
    white_queen_img = np.ones((100, 100, 3), dtype=np.uint8) * 190
    white_queen_img[20:80, 35:65] = 140  # Complex crown shape
    white_queen_img[25:35, 30:70] = 130  # Crown details
    images['white_queen'] = white_queen_img
    
    return images


def demo_orientation_detection():
    """Demonstrate board orientation detection."""
    print("=" * 70)
    print("BOARD ORIENTATION DETECTION DEMO")
    print("=" * 70)
    print()
    
    detector = BoardDetector()
    
    # Create mock board with checkerboard pattern (white at bottom)
    print("Creating mock chess board (white pieces at bottom)...")
    squares = []
    for row in range(8):
        row_squares = []
        for col in range(8):
            # Checkerboard: a1 is dark (row 7, col 0)
            if (row + col) % 2 == 1:
                square = np.zeros((100, 100, 3), dtype=np.uint8)  # Dark
            else:
                square = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Light
            row_squares.append(square)
        squares.append(row_squares)
    
    orientation = detector.detect_board_orientation(squares)
    print(f"✓ Detected orientation: {orientation.upper()} at bottom")
    print()
    
    # Demonstrate flipping
    print("Flipping board orientation...")
    flipped_squares = detector.flip_board(squares)
    print("✓ Board flipped (rotated 180 degrees)")
    print()
    
    return squares, flipped_squares


def demo_feedback_collection():
    """Demonstrate feedback collection with images."""
    print("=" * 70)
    print("FEEDBACK COLLECTION WITH IMAGES DEMO")
    print("=" * 70)
    print()
    
    # Create temporary feedback manager
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    feedback_file = output_dir / 'retraining_demo_feedback.json'
    
    manager = FeedbackManager(feedback_file=feedback_file)
    
    # Get mock square images
    mock_images = create_mock_square_images()
    
    print("Simulating piece corrections with images...")
    print("-" * 70)
    
    corrections = [
        {
            'square': 'e4',
            'original': PieceType.WHITE_PAWN,
            'confidence': 0.62,
            'corrected': PieceType.WHITE_KNIGHT,
            'image': mock_images['white_pawn'],
            'orientation': 'white',
            'note': 'Pawn misidentified due to lighting'
        },
        {
            'square': 'e5',
            'original': PieceType.BLACK_PAWN,
            'confidence': 0.58,
            'corrected': PieceType.BLACK_KNIGHT,
            'image': mock_images['black_knight'],
            'orientation': 'white',
            'note': 'Knight features not detected properly'
        },
        {
            'square': 'd4',
            'original': PieceType.EMPTY,
            'confidence': 0.71,
            'corrected': PieceType.WHITE_QUEEN,
            'image': mock_images['white_queen'],
            'orientation': 'white',
            'note': 'Queen not detected in bright lighting'
        },
        {
            'square': 'd5',
            'original': PieceType.WHITE_ROOK,
            'confidence': 0.48,
            'corrected': PieceType.EMPTY,
            'image': mock_images['empty'],
            'orientation': 'white',
            'note': 'False positive on empty square'
        },
    ]
    
    for i, corr in enumerate(corrections, 1):
        print(f"\nCorrection {i}:")
        print(f"  Square: {corr['square'].upper()}")
        print(f"  Original: {corr['original'].name}")
        print(f"  Confidence: {corr['confidence']:.1%}")
        print(f"  Corrected: {corr['corrected'].name}")
        print(f"  Orientation: {corr['orientation']}")
        print(f"  Note: {corr['note']}")
        
        manager.add_feedback(
            square_name=corr['square'],
            original_prediction=corr['original'],
            original_confidence=corr['confidence'],
            user_correction=corr['corrected'],
            square_image=corr['image'],
            board_orientation=corr['orientation']
        )
        print(f"  ✓ Feedback saved with image data")
    
    print()
    print("-" * 70)
    print()
    
    return manager


def demo_retraining(feedback_manager):
    """Demonstrate retraining from feedback."""
    print("=" * 70)
    print("RETRAINING FROM FEEDBACK DEMO")
    print("=" * 70)
    print()
    
    recognizer = PieceRecognizer()
    
    # Show initial state
    print("Before retraining:")
    stats_before = recognizer.get_training_statistics()
    print(f"  Trained: {stats_before['trained']}")
    print()
    
    # Get training data
    print("Retrieving training data from feedback...")
    training_data = feedback_manager.get_training_data()
    print(f"✓ Retrieved {len(training_data)} training samples")
    print()
    
    # Perform retraining
    print("Retraining piece recognizer...")
    result = recognizer.retrain_from_feedback(training_data)
    
    if result['status'] == 'success':
        print("✓ Retraining successful!")
        print()
        print("Training Results:")
        print(f"  • Samples processed: {result['samples_processed']}")
        print(f"  • Piece types trained: {result['piece_types_trained']}")
        print(f"  • Piece counts:")
        for piece_type, count in result['piece_counts'].items():
            print(f"    - {piece_type}: {count}")
        print()
        
        # Show updated state
        print("After retraining:")
        stats_after = recognizer.get_training_statistics()
        print(f"  Trained: {stats_after['trained']}")
        print(f"  Piece types with learned features: {stats_after['num_piece_types']}")
        print()
    else:
        print(f"✗ Retraining failed: {result.get('reason', 'Unknown')}")
        print()


def demo_feedback_analysis(feedback_manager):
    """Demonstrate feedback analysis capabilities."""
    print("=" * 70)
    print("FEEDBACK ANALYSIS DEMO")
    print("=" * 70)
    print()
    
    # Overall statistics
    stats = feedback_manager.get_correction_statistics()
    print("Overall Statistics:")
    print(f"  • Total corrections: {stats['total_corrections']}")
    print(f"  • Average original confidence: {stats['avg_original_confidence']:.1%}")
    print()
    
    # By piece type
    print("Corrections by piece type:")
    for piece_type, count in sorted(stats['by_piece_type'].items()):
        print(f"  • {piece_type}: {count}")
    print()
    
    # Misclassifications
    misclassified = feedback_manager.get_misclassified_feedback()
    print(f"Misclassifications: {len(misclassified)}")
    for fb in misclassified:
        print(f"  • {fb.square_name}: {fb.original_prediction.name if fb.original_prediction else 'None'} "
              f"→ {fb.user_correction.name}")
    print()


def main():
    """Run the retraining demo."""
    print()
    print("=" * 70)
    print("CHESS PIECE RECOGNITION RETRAINING & ORIENTATION DEMO")
    print("=" * 70)
    print()
    
    # Demo 1: Orientation detection
    squares, flipped = demo_orientation_detection()
    
    # Demo 2: Feedback collection
    manager = demo_feedback_collection()
    
    # Demo 3: Retraining
    demo_retraining(manager)
    
    # Demo 4: Analysis
    demo_feedback_analysis(manager)
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key takeaways:")
    print("1. Board orientation can be detected automatically")
    print("2. Feedback is collected with square images for retraining")
    print("3. The recognizer can learn from user corrections")
    print("4. Training data is persisted and can be analyzed")
    print()
    print(f"Feedback data saved to: {manager.feedback_file}")
    print()


if __name__ == '__main__':
    main()
