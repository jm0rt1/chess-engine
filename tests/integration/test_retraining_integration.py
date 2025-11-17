"""
Integration test for the retraining and orientation detection workflow.

Tests the complete flow from feedback collection to retraining.
"""

import unittest
import tempfile
import numpy as np
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.computer_vision.feedback_manager import FeedbackManager
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType
from src.computer_vision.board_detector import BoardDetector


class TestRetrainingIntegration(unittest.TestCase):
    """Test complete retraining workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary feedback file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
        self.temp_dir = self.temp_path.parent
        
        # Initialize components
        self.feedback_manager = FeedbackManager(feedback_file=self.temp_path)
        self.piece_recognizer = PieceRecognizer()
        self.board_detector = BoardDetector()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_path.exists():
            self.temp_path.unlink()
        
        # Clean up training images
        images_dir = self.temp_dir / 'training_images'
        if images_dir.exists():
            for img_file in images_dir.glob('*.png'):
                img_file.unlink()
            images_dir.rmdir()
    
    def test_complete_workflow(self):
        """Test the complete workflow from feedback to retraining."""
        # Step 1: Create mock board and detect orientation
        squares = self._create_mock_board()
        orientation = self.board_detector.detect_board_orientation(squares)
        self.assertIn(orientation, ['white', 'black'])
        
        # Step 2: Simulate piece corrections with images
        corrections = [
            (squares[0][0], 'a8', PieceType.BLACK_ROOK, PieceType.BLACK_ROOK, 0.9),
            (squares[3][4], 'e5', PieceType.BLACK_PAWN, PieceType.BLACK_BISHOP, 0.6),
            (squares[6][4], 'e2', PieceType.WHITE_PAWN, PieceType.WHITE_PAWN, 0.85),
        ]
        
        for square_img, square_name, original, corrected, confidence in corrections:
            self.feedback_manager.add_feedback(
                square_name=square_name,
                original_prediction=original,
                original_confidence=confidence,
                user_correction=corrected,
                square_image=square_img,
                board_orientation=orientation
            )
        
        # Verify feedback was collected
        self.assertEqual(self.feedback_manager.get_feedback_count(), 3)
        
        # Step 3: Get training data
        training_data = self.feedback_manager.get_training_data()
        self.assertEqual(len(training_data), 3)
        
        # Step 4: Retrain recognizer
        result = self.piece_recognizer.retrain_from_feedback(training_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['samples_processed'], 3)
        self.assertGreater(result['piece_types_trained'], 0)
        
        # Step 5: Verify training statistics
        stats = self.piece_recognizer.get_training_statistics()
        self.assertTrue(stats['trained'])
        self.assertGreater(stats['num_piece_types'], 0)
        
        # Step 6: Get feedback statistics
        feedback_stats = self.feedback_manager.get_correction_statistics()
        self.assertEqual(feedback_stats['total_corrections'], 3)
        self.assertGreater(feedback_stats['avg_original_confidence'], 0)
    
    def test_orientation_with_flipping(self):
        """Test orientation detection and board flipping."""
        # Create board
        squares = self._create_mock_board()
        
        # Detect orientation
        orientation1 = self.board_detector.detect_board_orientation(squares)
        
        # Flip board
        flipped_squares = self.board_detector.flip_board(squares)
        
        # Verify structure is preserved
        self.assertEqual(len(flipped_squares), 8)
        self.assertEqual(len(flipped_squares[0]), 8)
        
        # Verify corners are flipped
        self.assertTrue(np.array_equal(squares[0][0], flipped_squares[7][7]))
        self.assertTrue(np.array_equal(squares[7][7], flipped_squares[0][0]))
    
    def test_misclassification_analysis(self):
        """Test analysis of misclassifications."""
        # Add some feedback with misclassifications
        square_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        # Correct prediction
        self.feedback_manager.add_feedback(
            'a1', PieceType.WHITE_ROOK, 0.9, PieceType.WHITE_ROOK,
            square_img, 'white'
        )
        
        # Misclassifications
        self.feedback_manager.add_feedback(
            'e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT,
            square_img, 'white'
        )
        self.feedback_manager.add_feedback(
            'e5', PieceType.BLACK_PAWN, 0.65, PieceType.BLACK_BISHOP,
            square_img, 'white'
        )
        
        # Analyze misclassifications
        misclassified = self.feedback_manager.get_misclassified_feedback()
        
        self.assertEqual(len(misclassified), 2)
        for fb in misclassified:
            self.assertNotEqual(fb.original_prediction, fb.user_correction)
    
    def _create_mock_board(self):
        """Create a mock 8x8 board with checkerboard pattern."""
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Checkerboard pattern
                if (row + col) % 2 == 0:
                    square = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Light
                else:
                    square = np.ones((100, 100, 3), dtype=np.uint8) * 50   # Dark
                row_squares.append(square)
            squares.append(row_squares)
        return squares


if __name__ == '__main__':
    unittest.main()
