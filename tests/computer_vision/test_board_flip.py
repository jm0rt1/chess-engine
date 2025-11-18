"""
Unit tests for board flipping functionality.

Tests the board flip feature that allows users to rotate the board 180 degrees.
"""

import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType, RecognitionResult


class TestBoardFlip(unittest.TestCase):
    """Test board flipping functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BoardDetector()
        self.recognizer = PieceRecognizer()
    
    def test_flip_board_squares(self):
        """Test that flipping board squares rotates 180 degrees correctly."""
        # Create a test pattern with unique values
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Each square has a unique identifier
                value = row * 8 + col
                square = np.ones((10, 10, 3), dtype=np.uint8) * value
                row_squares.append(square)
            squares.append(row_squares)
        
        # Flip the board
        flipped = self.detector.flip_board(squares)
        
        # Verify dimensions are preserved
        self.assertEqual(len(flipped), 8)
        for row in flipped:
            self.assertEqual(len(row), 8)
        
        # Verify corners are swapped correctly
        # Top-left (0,0) should become bottom-right (7,7)
        self.assertTrue(np.array_equal(squares[0][0], flipped[7][7]))
        # Top-right (0,7) should become bottom-left (7,0)
        self.assertTrue(np.array_equal(squares[0][7], flipped[7][0]))
        # Bottom-left (7,0) should become top-right (0,7)
        self.assertTrue(np.array_equal(squares[7][0], flipped[0][7]))
        # Bottom-right (7,7) should become top-left (0,0)
        self.assertTrue(np.array_equal(squares[7][7], flipped[0][0]))
    
    def test_flip_board_twice_returns_original(self):
        """Test that flipping twice returns the original board."""
        # Create a test pattern
        squares = []
        for row in range(8):
            row_squares = []
            for col in range(8):
                value = row * 8 + col
                square = np.ones((10, 10, 3), dtype=np.uint8) * value
                row_squares.append(square)
            squares.append(row_squares)
        
        # Flip twice
        flipped_once = self.detector.flip_board(squares)
        flipped_twice = self.detector.flip_board(flipped_once)
        
        # Should match original
        for row in range(8):
            for col in range(8):
                self.assertTrue(np.array_equal(squares[row][col], flipped_twice[row][col]))
    
    def test_flip_recognition_results(self):
        """Test that flipping recognition results works correctly."""
        # Create recognition results grid
        results = []
        for row in range(8):
            row_results = []
            for col in range(8):
                # Create a simple pattern: row number determines piece type
                if row == 0:
                    piece = PieceType.WHITE_ROOK
                elif row == 7:
                    piece = PieceType.BLACK_ROOK
                else:
                    piece = PieceType.EMPTY
                
                result = RecognitionResult(piece_type=piece, confidence=0.9)
                row_results.append(result)
            results.append(row_results)
        
        # Flip results (same logic as board flip)
        flipped_results = []
        for row in reversed(results):
            flipped_row = list(reversed(row))
            flipped_results.append(flipped_row)
        
        # Verify dimensions
        self.assertEqual(len(flipped_results), 8)
        for row in flipped_results:
            self.assertEqual(len(row), 8)
        
        # Verify corners are swapped
        # Top-left white rook should be at bottom-right after flip
        self.assertEqual(results[0][0].piece_type, PieceType.WHITE_ROOK)
        self.assertEqual(flipped_results[7][7].piece_type, PieceType.WHITE_ROOK)
        
        # Bottom-left black rook should be at top-right after flip
        self.assertEqual(results[7][0].piece_type, PieceType.BLACK_ROOK)
        self.assertEqual(flipped_results[0][7].piece_type, PieceType.BLACK_ROOK)
    
    def test_flip_preserves_piece_types(self):
        """Test that all piece types are preserved during flip."""
        # Create a board with different piece types
        piece_types = [
            PieceType.WHITE_KING, PieceType.WHITE_QUEEN, PieceType.WHITE_ROOK,
            PieceType.WHITE_BISHOP, PieceType.WHITE_KNIGHT, PieceType.WHITE_PAWN,
            PieceType.BLACK_KING, PieceType.BLACK_QUEEN, PieceType.EMPTY
        ]
        
        results = []
        type_idx = 0
        for row in range(8):
            row_results = []
            for col in range(8):
                piece = piece_types[type_idx % len(piece_types)]
                result = RecognitionResult(piece_type=piece, confidence=1.0)
                row_results.append(result)
                type_idx += 1
            results.append(row_results)
        
        # Count piece types before flip
        original_counts = {}
        for row in results:
            for result in row:
                piece_name = result.piece_type.name if result.piece_type else "None"
                original_counts[piece_name] = original_counts.get(piece_name, 0) + 1
        
        # Flip results
        flipped_results = []
        for row in reversed(results):
            flipped_row = list(reversed(row))
            flipped_results.append(flipped_row)
        
        # Count piece types after flip
        flipped_counts = {}
        for row in flipped_results:
            for result in row:
                piece_name = result.piece_type.name if result.piece_type else "None"
                flipped_counts[piece_name] = flipped_counts.get(piece_name, 0) + 1
        
        # Counts should be identical
        self.assertEqual(original_counts, flipped_counts)


if __name__ == '__main__':
    unittest.main()
