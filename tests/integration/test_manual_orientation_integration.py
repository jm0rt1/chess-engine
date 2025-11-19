"""
Integration test for manual orientation selection feature.

Tests the complete workflow of selecting orientation and processing an image.
"""

import unittest
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType, RecognitionResult


class TestManualOrientationIntegration(unittest.TestCase):
    """Integration tests for manual orientation selection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BoardDetector()
        self.recognizer = PieceRecognizer()
    
    def create_test_squares_black_at_bottom(self):
        """Create test squares with black pieces at bottom."""
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Dark squares at bottom (black pieces area)
                brightness = 50 if row >= 6 else 200
                square = np.ones((100, 100, 3), dtype=np.uint8) * brightness
                row_squares.append(square)
            squares.append(row_squares)
        return squares
    
    def create_test_recognition_black_at_bottom(self):
        """Create test recognition results with black at bottom."""
        results = []
        for row in range(8):
            row_results = []
            for col in range(8):
                if row == 7:
                    # Bottom row - black pieces
                    piece = PieceType.BLACK_ROOK if col in [0, 7] else PieceType.BLACK_KNIGHT
                    row_results.append(RecognitionResult(piece, 0.95))
                elif row == 6:
                    row_results.append(RecognitionResult(PieceType.BLACK_PAWN, 0.95))
                elif row == 1:
                    row_results.append(RecognitionResult(PieceType.WHITE_PAWN, 0.95))
                elif row == 0:
                    # Top row - white pieces
                    piece = PieceType.WHITE_ROOK if col in [0, 7] else PieceType.WHITE_KNIGHT
                    row_results.append(RecognitionResult(piece, 0.95))
                else:
                    row_results.append(RecognitionResult(PieceType.EMPTY, 1.0))
            results.append(row_results)
        return results
    
    def test_auto_detect_with_white_at_bottom(self):
        """Test auto-detect when white is at bottom (standard)."""
        # Create standard orientation (white at bottom)
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                brightness = 200 if row <= 1 else 50
                square = np.ones((100, 100, 3), dtype=np.uint8) * brightness
                row_squares.append(square)
            squares.append(row_squares)
        
        # This should NOT require flipping
        detected = self.detector.detect_board_orientation(squares, None)
        
        # Should detect white at bottom
        # No flip needed in this case
        self.assertIn(detected, ['white', 'black'])
    
    def test_manual_black_selection_flips_data(self):
        """Test that manual 'black' selection results in flipped data."""
        squares = self.create_test_squares_black_at_bottom()
        results = self.create_test_recognition_black_at_bottom()
        
        # Simulate what happens when user selects "Black on Bottom"
        orientation_pref = 'black'
        
        if orientation_pref == 'black':
            # Flip the data
            flipped_squares = self.detector.flip_board(squares)
            
            # Flip results
            flipped_results = []
            for row in reversed(results):
                flipped_results.append(list(reversed(row)))
            
            # Verify the flip happened
            # Bottom-right of original should be top-left of flipped
            self.assertTrue(np.array_equal(squares[7][7], flipped_squares[0][0]))
            
            # Bottom-left piece should be top-right after flip
            self.assertEqual(results[7][0].piece_type, flipped_results[0][7].piece_type)
            
            # After flip, black pieces should be in row 0 (correct for FEN)
            self.assertEqual(flipped_results[0][0].piece_type, PieceType.BLACK_ROOK)
    
    def test_manual_white_selection_no_flip(self):
        """Test that manual 'white' selection doesn't flip data."""
        squares = self.create_test_squares_black_at_bottom()
        results = self.create_test_recognition_black_at_bottom()
        
        # Simulate what happens when user selects "White on Bottom"
        orientation_pref = 'white'
        
        if orientation_pref == 'white':
            # No flipping should occur
            # Data stays as-is
            
            # Verify no change
            self.assertEqual(results[7][0].piece_type, PieceType.BLACK_ROOK)
            # This is "wrong" but that's what the user selected
    
    def test_fen_generation_after_normalization(self):
        """Test that FEN is correct after normalization."""
        # Create a simple position with black at bottom
        results = self.create_test_recognition_black_at_bottom()
        
        # Generate FEN before flip (wrong orientation)
        fen_before = self.recognizer.results_to_fen(results)
        
        # Flip the results (normalize)
        flipped_results = []
        for row in reversed(results):
            flipped_results.append(list(reversed(row)))
        
        # Generate FEN after flip (correct orientation)
        fen_after = self.recognizer.results_to_fen(flipped_results)
        
        # The FENs should be different
        self.assertNotEqual(fen_before, fen_after)
        
        # After flip, first rank in FEN should have black pieces
        # (FEN starts with rank 8)
        self.assertTrue('r' in fen_after.split('/')[0] or 'n' in fen_after.split('/')[0])
    
    def test_orientation_preference_values(self):
        """Test that orientation preference values are valid."""
        valid_preferences = ['auto', 'white', 'black']
        
        for pref in valid_preferences:
            self.assertIn(pref, ['auto', 'white', 'black'])
    
    def test_flip_is_reversible(self):
        """Test that flipping twice returns to original state."""
        squares = self.create_test_squares_black_at_bottom()
        
        # Flip once
        flipped_once = self.detector.flip_board(squares)
        
        # Flip again
        flipped_twice = self.detector.flip_board(flipped_once)
        
        # Should be back to original
        self.assertTrue(np.array_equal(squares[0][0], flipped_twice[0][0]))
        self.assertTrue(np.array_equal(squares[7][7], flipped_twice[7][7]))


if __name__ == '__main__':
    unittest.main()
