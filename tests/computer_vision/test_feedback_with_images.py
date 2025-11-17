"""
Unit tests for FeedbackManager with image support.

Tests the enhanced feedback collection with square images.
"""

import unittest
import tempfile
import numpy as np
from pathlib import Path
import sys
import os
import cv2

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.computer_vision.feedback_manager import FeedbackManager, PieceFeedback
from src.computer_vision.piece_recognizer import PieceType


class TestFeedbackWithImages(unittest.TestCase):
    """Test FeedbackManager with image support."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
        
        # Create temp directory for images
        self.temp_dir = Path(self.temp_file.name).parent
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_path.exists():
            self.temp_path.unlink()
        
        # Clean up training images directory
        images_dir = self.temp_dir / 'training_images'
        if images_dir.exists():
            for img_file in images_dir.glob('*.png'):
                img_file.unlink()
            images_dir.rmdir()
    
    def test_add_feedback_with_image(self):
        """Test adding feedback with square image."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        # Create a test image
        test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=test_image,
            board_orientation='white'
        )
        
        self.assertEqual(manager.get_feedback_count(), 1)
        
        # Check that image was saved
        feedback = manager.feedback_data[0]
        self.assertIsNotNone(feedback.square_image_path)
        self.assertEqual(feedback.board_orientation, 'white')
        
        # Verify image file exists
        image_path = self.temp_dir / feedback.square_image_path
        self.assertTrue(image_path.exists())
    
    def test_get_training_data(self):
        """Test retrieving training data from feedback."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        # Add feedback with images
        for i in range(3):
            test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            manager.add_feedback(
                square_name=f'e{i+4}',
                original_prediction=PieceType.WHITE_PAWN,
                original_confidence=0.6,
                user_correction=PieceType.WHITE_KNIGHT,
                square_image=test_image
            )
        
        # Get training data
        training_data = manager.get_training_data()
        
        self.assertEqual(len(training_data), 3)
        
        # Check structure
        for image, label in training_data:
            self.assertIsInstance(image, np.ndarray)
            self.assertEqual(label, PieceType.WHITE_KNIGHT)
    
    def test_add_feedback_without_image(self):
        """Test adding feedback without image (backward compatibility)."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT
        )
        
        self.assertEqual(manager.get_feedback_count(), 1)
        
        feedback = manager.feedback_data[0]
        self.assertIsNone(feedback.square_image_path)
        self.assertIsNone(feedback.board_orientation)
    
    def test_feedback_persistence_with_images(self):
        """Test that feedback with images persists correctly."""
        # Create manager and add feedback with image
        manager1 = FeedbackManager(feedback_file=self.temp_path)
        test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        manager1.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=test_image,
            board_orientation='black'
        )
        
        image_path = manager1.feedback_data[0].square_image_path
        
        # Create new manager and verify data loaded
        manager2 = FeedbackManager(feedback_file=self.temp_path)
        self.assertEqual(manager2.get_feedback_count(), 1)
        
        feedback = manager2.feedback_data[0]
        self.assertEqual(feedback.square_name, 'e4')
        self.assertEqual(feedback.square_image_path, image_path)
        self.assertEqual(feedback.board_orientation, 'black')
    
    def test_get_feedback_by_piece_type(self):
        """Test filtering feedback by piece type."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        # Add different piece types
        manager.add_feedback('e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT)
        manager.add_feedback('e5', PieceType.BLACK_PAWN, 0.7, PieceType.BLACK_KNIGHT)
        manager.add_feedback('d4', PieceType.WHITE_ROOK, 0.5, PieceType.WHITE_KNIGHT)
        
        # Filter by WHITE_KNIGHT
        knight_feedback = manager.get_feedback_by_piece_type(PieceType.WHITE_KNIGHT)
        self.assertEqual(len(knight_feedback), 2)
        
        # Filter by BLACK_KNIGHT
        black_knight_feedback = manager.get_feedback_by_piece_type(PieceType.BLACK_KNIGHT)
        self.assertEqual(len(black_knight_feedback), 1)
    
    def test_get_misclassified_feedback(self):
        """Test getting misclassified feedback."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        # Add correct prediction (confirmed)
        manager.add_feedback('a1', PieceType.WHITE_ROOK, 0.8, PieceType.WHITE_ROOK)
        
        # Add misclassifications
        manager.add_feedback('e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT)
        manager.add_feedback('e5', PieceType.BLACK_PAWN, 0.7, PieceType.BLACK_BISHOP)
        
        # Get misclassified
        misclassified = manager.get_misclassified_feedback()
        self.assertEqual(len(misclassified), 2)
        
        # Verify they are all different from original
        for fb in misclassified:
            self.assertNotEqual(fb.original_prediction, fb.user_correction)


if __name__ == '__main__':
    unittest.main()
