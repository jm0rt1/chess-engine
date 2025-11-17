"""
Unit tests for board orientation detection.

Tests the board orientation detection functionality.
"""

import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.computer_vision.board_detector import BoardDetector


class TestOrientationDetection(unittest.TestCase):
    """Test board orientation detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BoardDetector()
    
    def test_calculate_square_brightness(self):
        """Test brightness calculation."""
        # Create a dark square (all black)
        dark_square = np.zeros((100, 100, 3), dtype=np.uint8)
        brightness = self.detector._calculate_square_brightness(dark_square)
        self.assertAlmostEqual(brightness, 0.0, places=1)
        
        # Create a light square (all white)
        light_square = np.ones((100, 100, 3), dtype=np.uint8) * 255
        brightness = self.detector._calculate_square_brightness(light_square)
        self.assertAlmostEqual(brightness, 255.0, places=1)
    
    def test_detect_orientation_from_color(self):
        """Test orientation detection based on square colors."""
        # Create mock squares grid with dark bottom-left
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Checkerboard pattern: bottom-left is dark (like a1)
                if (row + col) % 2 == 1:  # Dark squares
                    square = np.zeros((100, 100, 3), dtype=np.uint8)
                else:  # Light squares
                    square = np.ones((100, 100, 3), dtype=np.uint8) * 200
                row_squares.append(square)
            squares.append(row_squares)
        
        orientation = self.detector.detect_board_orientation(squares)
        self.assertEqual(orientation, 'white')
    
    def test_flip_board(self):
        """Test board flipping functionality."""
        # Create a simple test pattern
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Each square has a unique value
                square = np.ones((10, 10, 3), dtype=np.uint8) * (row * 8 + col)
                row_squares.append(square)
            squares.append(row_squares)
        
        # Flip the board
        flipped = self.detector.flip_board(squares)
        
        # Check that corners are flipped
        self.assertTrue(np.array_equal(squares[0][0], flipped[7][7]))
        self.assertTrue(np.array_equal(squares[7][7], flipped[0][0]))
        self.assertTrue(np.array_equal(squares[0][7], flipped[7][0]))
        self.assertTrue(np.array_equal(squares[7][0], flipped[0][7]))
    
    def test_orientation_returns_valid_value(self):
        """Test that orientation detection always returns a valid value."""
        # Create random squares
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                square = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
                row_squares.append(square)
            squares.append(row_squares)
        
        orientation = self.detector.detect_board_orientation(squares)
        self.assertIn(orientation, ['white', 'black'])


if __name__ == '__main__':
    unittest.main()
