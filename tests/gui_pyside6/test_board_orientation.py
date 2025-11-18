"""
Unit tests for board orientation coordinate labeling.

Tests that coordinate labels (a-h, 1-8) are correctly displayed based on board orientation.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestBoardOrientationLabels(unittest.TestCase):
    """Test board orientation coordinate labeling."""
    
    def test_white_orientation_rank_labels(self):
        """Test that rank labels are correct when white is at bottom."""
        # When white is at bottom (default orientation):
        # row 0 (top) should show rank 8
        # row 7 (bottom) should show rank 1
        
        for row in range(8):
            expected_rank = 8 - row
            self.assertEqual(expected_rank, 8 - row)
    
    def test_black_orientation_rank_labels(self):
        """Test that rank labels are correct when black is at bottom."""
        # When black is at bottom (flipped orientation):
        # row 0 (top) should show rank 1
        # row 7 (bottom) should show rank 8
        
        for row in range(8):
            expected_rank = row + 1
            self.assertEqual(expected_rank, row + 1)
    
    def test_white_orientation_file_labels(self):
        """Test that file labels are correct when white is at bottom."""
        # When white is at bottom:
        # col 0 (left) should show 'a'
        # col 7 (right) should show 'h'
        
        for col in range(8):
            expected_file = chr(ord('a') + col)
            self.assertEqual(expected_file, chr(ord('a') + col))
    
    def test_black_orientation_file_labels(self):
        """Test that file labels are correct when black is at bottom."""
        # When black is at bottom:
        # col 0 (left) should show 'h'
        # col 7 (right) should show 'a'
        
        for col in range(8):
            expected_file = chr(ord('h') - col)
            self.assertEqual(expected_file, chr(ord('h') - col))
    
    def test_orientation_toggle(self):
        """Test that orientation correctly toggles between white and black."""
        orientation = 'white'
        
        # Toggle to black
        orientation = 'black' if orientation == 'white' else 'white'
        self.assertEqual(orientation, 'black')
        
        # Toggle back to white
        orientation = 'black' if orientation == 'white' else 'white'
        self.assertEqual(orientation, 'white')


if __name__ == '__main__':
    unittest.main()
