#!/usr/bin/env python3
"""
Demo script showcasing the session tracking and deduplication features.

This script demonstrates:
1. How sessions work
2. How deduplication handles multiple corrections
3. How to analyze feedback with the new features
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.computer_vision.feedback_manager import FeedbackManager
from src.computer_vision.piece_recognizer import PieceType


def create_mock_images():
    """Create mock chess board images for demonstration."""
    # Image 1: Normal board
    image1 = np.ones((800, 800, 3), dtype=np.uint8) * 128
    
    # Image 2: Different board (brighter)
    image2 = np.ones((800, 800, 3), dtype=np.uint8) * 180
    
    # Square images
    square = np.ones((100, 100, 3), dtype=np.uint8) * 150
    
    return image1, image2, square


def demo_basic_deduplication():
    """Demonstrate basic deduplication functionality."""
    print("=" * 70)
    print("DEMO 1: BASIC DEDUPLICATION")
    print("=" * 70)
    print()
    
    # Create a temporary feedback file
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    feedback_file = output_dir / 'deduplication_demo_feedback.json'
    
    # Initialize manager
    manager = FeedbackManager(
        feedback_file=feedback_file,
        session_id='demo_session_1'
    )
    
    # Create mock images
    image1, _, square = create_mock_images()
    
    # Set current image
    print("Loading chess board image...")
    manager.set_current_image(image1)
    print(f"✓ Image hash: {manager.current_image_hash[:16]}...")
    print()
    
    # User makes first correction
    print("User corrects e4 as WHITE_KNIGHT:")
    manager.add_feedback(
        square_name='e4',
        original_prediction=PieceType.WHITE_PAWN,
        original_confidence=0.6,
        user_correction=PieceType.WHITE_KNIGHT,
        square_image=square
    )
    print("  ✓ Correction saved (active)")
    print()
    
    # User realizes mistake and corrects again
    print("User realizes mistake, corrects e4 as WHITE_BISHOP:")
    manager.add_feedback(
        square_name='e4',
        original_prediction=PieceType.WHITE_KNIGHT,
        original_confidence=1.0,
        user_correction=PieceType.WHITE_BISHOP,
        square_image=square
    )
    print("  ✓ New correction saved (active)")
    print("  ✓ Previous correction marked as superseded (inactive)")
    print()
    
    # Show statistics
    stats = manager.get_correction_statistics()
    print("Statistics:")
    print(f"  • Total corrections: {stats['total_corrections']}")
    print(f"  • Active corrections: {stats['active_corrections']}")
    print(f"  • Superseded corrections: {stats['superseded_corrections']}")
    print()
    
    # Show training data
    training_data = manager.get_training_data()
    print("Training Data:")
    print(f"  • Number of samples: {len(training_data)}")
    print(f"  • Labels: {[label.name for _, label in training_data]}")
    print()
    
    print("✅ Result: Only the latest correction (WHITE_BISHOP) is in training data!")
    print()
    
    return manager


def demo_multiple_images():
    """Demonstrate that same square in different images is NOT deduplicated."""
    print("=" * 70)
    print("DEMO 2: DIFFERENT IMAGES ARE NOT DEDUPLICATED")
    print("=" * 70)
    print()
    
    # Create a temporary feedback file
    output_dir = Path(__file__).parent.parent / 'output'
    feedback_file = output_dir / 'deduplication_demo_feedback2.json'
    
    manager = FeedbackManager(
        feedback_file=feedback_file,
        session_id='demo_session_2'
    )
    
    image1, image2, square = create_mock_images()
    
    # Correct e4 in first image
    print("Processing first chess board:")
    manager.set_current_image(image1)
    print(f"  Image hash: {manager.current_image_hash[:16]}...")
    manager.add_feedback(
        square_name='e4',
        original_prediction=PieceType.WHITE_PAWN,
        original_confidence=0.6,
        user_correction=PieceType.WHITE_KNIGHT,
        square_image=square
    )
    print("  ✓ Corrected e4 as WHITE_KNIGHT")
    print()
    
    # Correct e4 in second image
    print("Processing second chess board (different game):")
    manager.set_current_image(image2)
    print(f"  Image hash: {manager.current_image_hash[:16]}...")
    manager.add_feedback(
        square_name='e4',
        original_prediction=PieceType.BLACK_PAWN,
        original_confidence=0.6,
        user_correction=PieceType.BLACK_KNIGHT,
        square_image=square
    )
    print("  ✓ Corrected e4 as BLACK_KNIGHT")
    print()
    
    # Show results
    stats = manager.get_correction_statistics()
    training_data = manager.get_training_data()
    
    print("Statistics:")
    print(f"  • Total corrections: {stats['total_corrections']}")
    print(f"  • Active corrections: {stats['active_corrections']}")
    print(f"  • Superseded corrections: {stats['superseded_corrections']}")
    print()
    
    print("Training Data:")
    print(f"  • Number of samples: {len(training_data)}")
    labels = [label.name for _, label in training_data]
    print(f"  • Labels: {labels}")
    print()
    
    print("✅ Result: Both corrections kept (different images)!")
    print()


def demo_session_tracking():
    """Demonstrate session tracking across multiple sessions."""
    print("=" * 70)
    print("DEMO 3: SESSION TRACKING")
    print("=" * 70)
    print()
    
    output_dir = Path(__file__).parent.parent / 'output'
    feedback_file = output_dir / 'deduplication_demo_feedback3.json'
    
    image1, _, square = create_mock_images()
    
    # Session 1: Morning labeling session
    print("Session 1: Morning labeling session")
    session1 = FeedbackManager(
        feedback_file=feedback_file,
        session_id='session_morning_20241121'
    )
    session1.set_current_image(image1)
    
    for square_name, piece in [('e4', PieceType.WHITE_KNIGHT), ('d4', PieceType.WHITE_QUEEN)]:
        session1.add_feedback(
            square_name=square_name,
            original_prediction=None,
            original_confidence=0.5,
            user_correction=piece,
            square_image=square
        )
    print(f"  ✓ Added 2 corrections in session: {session1.session_id}")
    print()
    
    # Session 2: Afternoon labeling session
    print("Session 2: Afternoon labeling session")
    session2 = FeedbackManager(
        feedback_file=feedback_file,
        session_id='session_afternoon_20241121'
    )
    session2.set_current_image(image1)
    
    for square_name, piece in [('c3', PieceType.BLACK_KNIGHT), ('f5', PieceType.EMPTY)]:
        session2.add_feedback(
            square_name=square_name,
            original_prediction=None,
            original_confidence=0.5,
            user_correction=piece,
            square_image=square
        )
    print(f"  ✓ Added 2 corrections in session: {session2.session_id}")
    print()
    
    # Load and analyze all sessions
    print("Analyzing all sessions:")
    manager = FeedbackManager(feedback_file=feedback_file)
    
    summary = manager.get_session_summary()
    print(f"  • Total sessions: {len(summary)}")
    for session_id, info in summary.items():
        print(f"\n  Session: {session_id}")
        print(f"    - Active corrections: {info['active_count']}")
        print(f"    - Total corrections: {info['total_count']}")
    print()
    
    # Get statistics by session
    stats = manager.get_correction_statistics()
    print("Corrections by session:")
    for session, count in stats['by_session'].items():
        print(f"  • {session}: {count} corrections")
    print()
    
    print("✅ Result: Each session's contributions are tracked separately!")
    print()


def demo_complex_scenario():
    """Demonstrate a complex real-world scenario."""
    print("=" * 70)
    print("DEMO 4: COMPLEX REAL-WORLD SCENARIO")
    print("=" * 70)
    print()
    
    output_dir = Path(__file__).parent.parent / 'output'
    feedback_file = output_dir / 'deduplication_demo_feedback4.json'
    
    manager = FeedbackManager(
        feedback_file=feedback_file,
        session_id='complex_demo_session'
    )
    
    image1, _, square = create_mock_images()
    manager.set_current_image(image1)
    
    print("User goes through a chess board making corrections:")
    print()
    
    # Simulated correction sequence with changes of mind
    corrections = [
        ('e4', PieceType.WHITE_PAWN, "Initial attempt"),
        ('d4', PieceType.WHITE_PAWN, "Another square"),
        ('e4', PieceType.WHITE_KNIGHT, "Changed mind on e4"),
        ('e5', PieceType.BLACK_PAWN, "New square"),
        ('e4', PieceType.WHITE_BISHOP, "Changed mind again on e4"),
        ('f4', PieceType.WHITE_QUEEN, "Another square"),
        ('e4', PieceType.EMPTY, "Final decision on e4"),
    ]
    
    for i, (square_name, piece, note) in enumerate(corrections, 1):
        print(f"{i}. Correct {square_name} as {piece.name}: {note}")
        manager.add_feedback(
            square_name=square_name,
            original_prediction=None,
            original_confidence=0.5,
            user_correction=piece,
            square_image=square
        )
    
    print()
    
    # Show final state
    stats = manager.get_correction_statistics()
    training_data = manager.get_training_data()
    
    print("Final Statistics:")
    print(f"  • Total corrections made: {stats['total_corrections']}")
    print(f"  • Active (used for training): {stats['active_corrections']}")
    print(f"  • Superseded (old versions): {stats['superseded_corrections']}")
    print()
    
    print("Training Data:")
    print(f"  • Number of samples: {len(training_data)}")
    print(f"  • Unique squares: {stats['active_corrections']}")
    print()
    
    print("Piece type breakdown (active only):")
    for piece_type, count in stats['by_piece_type'].items():
        print(f"  • {piece_type}: {count}")
    print()
    
    print("✅ Result: Clean training data despite multiple changes!")
    print(f"   e4 had 4 corrections, but only the final one (EMPTY) is used.")
    print()


def main():
    """Run all demos."""
    print()
    print("=" * 70)
    print("SESSION TRACKING AND DEDUPLICATION DEMO")
    print("=" * 70)
    print()
    
    # Run demos
    demo_basic_deduplication()
    input("Press Enter to continue to Demo 2...")
    print()
    
    demo_multiple_images()
    input("Press Enter to continue to Demo 3...")
    print()
    
    demo_session_tracking()
    input("Press Enter to continue to Demo 4...")
    print()
    
    demo_complex_scenario()
    
    print("=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("1. The system automatically handles duplicate corrections")
    print("2. Same square in different images are kept separate")
    print("3. Session tracking helps analyze which sessions were most useful")
    print("4. Only the latest correction for each square is used for training")
    print("5. All corrections are kept for audit/history purposes")
    print()
    print("For more details, see: docs/training-pipeline.md")
    print()


if __name__ == '__main__':
    main()
