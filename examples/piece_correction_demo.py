#!/usr/bin/env python3
"""
Demo script for the piece correction and feedback collection feature.

This script demonstrates how the feedback system works without requiring
a full GUI environment.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.computer_vision.feedback_manager import FeedbackManager, PieceFeedback
from src.computer_vision.piece_recognizer import PieceType


def main():
    """Run the piece correction demo."""
    
    print("=" * 60)
    print("Chess Piece Correction & Feedback Collection Demo")
    print("=" * 60)
    print()
    
    # Initialize feedback manager
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    feedback_file = output_dir / 'demo_feedback.json'
    
    print(f"Initializing FeedbackManager...")
    print(f"Feedback file: {feedback_file}")
    manager = FeedbackManager(feedback_file=feedback_file)
    print(f"✓ Manager initialized with {manager.get_feedback_count()} existing entries")
    print()
    
    # Simulate some piece corrections
    print("Simulating piece corrections...")
    print("-" * 60)
    
    corrections = [
        {
            'square': 'e4',
            'original': PieceType.WHITE_PAWN,
            'confidence': 0.65,
            'corrected': PieceType.WHITE_KNIGHT,
            'description': 'Pawn misidentified as knight due to lighting'
        },
        {
            'square': 'e5',
            'original': PieceType.BLACK_PAWN,
            'confidence': 0.72,
            'corrected': PieceType.BLACK_BISHOP,
            'description': 'Pawn misidentified as bishop due to angle'
        },
        {
            'square': 'd4',
            'original': PieceType.EMPTY,
            'confidence': 0.55,
            'corrected': PieceType.WHITE_QUEEN,
            'description': 'Empty square actually had a queen'
        },
        {
            'square': 'a8',
            'original': PieceType.BLACK_ROOK,
            'confidence': 0.45,
            'corrected': PieceType.BLACK_ROOK,
            'description': 'User confirmed low-confidence correct prediction'
        },
    ]
    
    for i, corr in enumerate(corrections, 1):
        print(f"\nCorrection {i}:")
        print(f"  Square: {corr['square'].upper()}")
        print(f"  Original prediction: {corr['original'].name}")
        print(f"  Confidence: {corr['confidence']:.1%}")
        print(f"  User correction: {corr['corrected'].name}")
        print(f"  Note: {corr['description']}")
        
        manager.add_feedback(
            square_name=corr['square'],
            original_prediction=corr['original'],
            original_confidence=corr['confidence'],
            user_correction=corr['corrected']
        )
        print(f"  ✓ Feedback saved")
    
    print()
    print("-" * 60)
    print()
    
    # Display statistics
    print("Feedback Statistics:")
    print("-" * 60)
    stats = manager.get_correction_statistics()
    
    print(f"Total corrections: {stats['total_corrections']}")
    print(f"Average original confidence: {stats['avg_original_confidence']:.1%}")
    print()
    print("Corrections by piece type:")
    for piece_type, count in sorted(stats['by_piece_type'].items()):
        print(f"  - {piece_type}: {count}")
    
    print()
    print("-" * 60)
    print()
    
    # Show how to use feedback for analysis
    print("Analyzing correction patterns...")
    print("-" * 60)
    
    # Find pieces with low confidence that were corrected
    low_conf_corrections = [
        fb for fb in manager.feedback_data 
        if fb.original_confidence < 0.7
    ]
    
    print(f"\nLow confidence corrections (< 70%): {len(low_conf_corrections)}")
    for fb in low_conf_corrections:
        print(f"  - {fb.square_name}: {fb.original_prediction.name if fb.original_prediction else 'None'} "
              f"→ {fb.user_correction.name} (conf: {fb.original_confidence:.1%})")
    
    # Find confirmed correct predictions
    confirmed = [
        fb for fb in manager.feedback_data
        if fb.original_prediction == fb.user_correction
    ]
    
    print(f"\nConfirmed correct predictions: {len(confirmed)}")
    for fb in confirmed:
        print(f"  - {fb.square_name}: {fb.original_prediction.name} (conf: {fb.original_confidence:.1%})")
    
    print()
    print("-" * 60)
    print()
    
    # Show export functionality
    print("Exporting feedback...")
    export_file = output_dir / 'exported_demo_feedback.json'
    manager.export_feedback(export_file)
    print(f"✓ Feedback exported to: {export_file}")
    
    print()
    print("=" * 60)
    print("Demo complete!")
    print(f"Feedback saved to: {feedback_file}")
    print("This data can be used to train or fine-tune recognition models.")
    print("=" * 60)


if __name__ == '__main__':
    main()
