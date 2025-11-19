"""
Unit tests for board orientation-aware square name calculation.

Tests that square names are calculated correctly based on the board orientation.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PySide6.QtWidgets import QApplication
    import chess
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@unittest.skipIf(not PYSIDE6_AVAILABLE, "PySide6 not available")
class TestBoardOrientationSquareNames(unittest.TestCase):
    """Test board orientation-aware square name calculation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        if PYSIDE6_AVAILABLE:
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])
    
    def test_white_orientation_square_names(self):
        """Test square name calculation for white orientation."""
        # White orientation: row 0 = rank 8, col 0 = file a
        
        # Top-left corner should be a8
        row, col = 0, 0
        square_name = chess.square_name(chess.square(col, 7 - row))
        self.assertEqual(square_name, 'a8')
        
        # Top-right corner should be h8
        row, col = 0, 7
        square_name = chess.square_name(chess.square(col, 7 - row))
        self.assertEqual(square_name, 'h8')
        
        # Bottom-left corner should be a1
        row, col = 7, 0
        square_name = chess.square_name(chess.square(col, 7 - row))
        self.assertEqual(square_name, 'a1')
        
        # Bottom-right corner should be h1
        row, col = 7, 7
        square_name = chess.square_name(chess.square(col, 7 - row))
        self.assertEqual(square_name, 'h1')
    
    def test_black_orientation_square_names(self):
        """Test square name calculation for black orientation."""
        # Black orientation: row 0 = rank 1, col 0 = file h
        
        # Top-left corner should be h1
        row, col = 0, 0
        square_name = chess.square_name(chess.square(7 - col, row))
        self.assertEqual(square_name, 'h1')
        
        # Top-right corner should be a1
        row, col = 0, 7
        square_name = chess.square_name(chess.square(7 - col, row))
        self.assertEqual(square_name, 'a1')
        
        # Bottom-left corner should be h8
        row, col = 7, 0
        square_name = chess.square_name(chess.square(7 - col, row))
        self.assertEqual(square_name, 'h8')
        
        # Bottom-right corner should be a8
        row, col = 7, 7
        square_name = chess.square_name(chess.square(7 - col, row))
        self.assertEqual(square_name, 'a8')
    
    def test_orientation_consistency(self):
        """Test that both orientations map all squares correctly."""
        # Verify all 64 squares are unique in both orientations
        white_squares = set()
        black_squares = set()
        
        for row in range(8):
            for col in range(8):
                # White orientation
                white_square = chess.square_name(chess.square(col, 7 - row))
                white_squares.add(white_square)
                
                # Black orientation
                black_square = chess.square_name(chess.square(7 - col, row))
                black_squares.add(black_square)
        
        # Both should have exactly 64 unique squares
        self.assertEqual(len(white_squares), 64)
        self.assertEqual(len(black_squares), 64)
        
        # Both should cover the same set of squares
        self.assertEqual(white_squares, black_squares)


if __name__ == '__main__':
    unittest.main()
