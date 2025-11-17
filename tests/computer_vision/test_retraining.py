"""
Unit tests for piece recognizer retraining.

Tests the retraining functionality using feedback data.
"""

import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType


class TestRetraining(unittest.TestCase):
    """Test piece recognizer retraining functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recognizer = PieceRecognizer()
    
    def test_retrain_with_no_data(self):
        """Test retraining with empty dataset."""
        result = self.recognizer.retrain_from_feedback([])
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['reason'], 'no_data')
    
    def test_retrain_with_sample_data(self):
        """Test retraining with sample images."""
        # Create sample training data
        training_data = []
        
        # Add some white pawn samples
        for _ in range(5):
            image = np.random.randint(100, 200, (100, 100, 3), dtype=np.uint8)
            training_data.append((image, PieceType.WHITE_PAWN))
        
        # Add some black knight samples
        for _ in range(3):
            image = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
            training_data.append((image, PieceType.BLACK_KNIGHT))
        
        # Retrain
        result = self.recognizer.retrain_from_feedback(training_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['samples_processed'], 8)
        self.assertEqual(result['piece_types_trained'], 2)
        self.assertIn('piece_counts', result)
        self.assertEqual(result['piece_counts']['WHITE_PAWN'], 5)
        self.assertEqual(result['piece_counts']['BLACK_KNIGHT'], 3)
    
    def test_learned_features_stored(self):
        """Test that learned features are stored."""
        # Create sample training data
        training_data = []
        for _ in range(3):
            image = np.random.randint(100, 200, (100, 100, 3), dtype=np.uint8)
            training_data.append((image, PieceType.WHITE_QUEEN))
        
        # Before training
        stats_before = self.recognizer.get_training_statistics()
        self.assertFalse(stats_before['trained'])
        
        # Retrain
        self.recognizer.retrain_from_feedback(training_data)
        
        # After training
        stats_after = self.recognizer.get_training_statistics()
        self.assertTrue(stats_after['trained'])
        self.assertIn('WHITE_QUEEN', stats_after['piece_types'])
        self.assertEqual(stats_after['num_piece_types'], 1)
    
    def test_multiple_retraining_sessions(self):
        """Test multiple retraining sessions accumulate knowledge."""
        # First training session
        training_data_1 = [
            (np.random.randint(100, 200, (100, 100, 3), dtype=np.uint8), PieceType.WHITE_PAWN)
            for _ in range(2)
        ]
        self.recognizer.retrain_from_feedback(training_data_1)
        
        stats_1 = self.recognizer.get_training_statistics()
        self.assertEqual(len(stats_1['piece_types']), 1)
        
        # Second training session with new piece type
        training_data_2 = [
            (np.random.randint(100, 200, (100, 100, 3), dtype=np.uint8), PieceType.BLACK_ROOK)
            for _ in range(2)
        ]
        self.recognizer.retrain_from_feedback(training_data_2)
        
        stats_2 = self.recognizer.get_training_statistics()
        self.assertEqual(len(stats_2['piece_types']), 2)
    
    def test_retrain_with_empty_squares(self):
        """Test retraining with empty square samples."""
        training_data = []
        
        # Add empty square samples (uniform background)
        for _ in range(4):
            # Empty squares have low variance
            color = np.random.randint(150, 200)
            image = np.ones((100, 100, 3), dtype=np.uint8) * color
            training_data.append((image, PieceType.EMPTY))
        
        result = self.recognizer.retrain_from_feedback(training_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('EMPTY', result['piece_counts'])
        self.assertEqual(result['piece_counts']['EMPTY'], 4)


if __name__ == '__main__':
    unittest.main()
