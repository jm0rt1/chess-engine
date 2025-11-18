"""
Integration test for board flip functionality.

Tests the complete workflow of detecting, recognizing, and flipping a board.
"""

import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType, RecognitionResult
from src.chess_engine.board_manager import BoardManager


class TestBoardFlipIntegration(unittest.TestCase):
    """Integration test for board flipping workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BoardDetector()
        self.recognizer = PieceRecognizer()
        self.board_manager = BoardManager()
    
    def test_flip_workflow_with_starting_position(self):
        """Test complete flip workflow with starting position."""
        # Create a mock starting position recognition results
        # Row 0 = Rank 8 (black pieces), Row 7 = Rank 1 (white pieces)
        results = []
        
        # Rank 8 (black back rank)
        rank_8 = [
            RecognitionResult(PieceType.BLACK_ROOK, 0.95),
            RecognitionResult(PieceType.BLACK_KNIGHT, 0.93),
            RecognitionResult(PieceType.BLACK_BISHOP, 0.92),
            RecognitionResult(PieceType.BLACK_QUEEN, 0.94),
            RecognitionResult(PieceType.BLACK_KING, 0.96),
            RecognitionResult(PieceType.BLACK_BISHOP, 0.91),
            RecognitionResult(PieceType.BLACK_KNIGHT, 0.92),
            RecognitionResult(PieceType.BLACK_ROOK, 0.94),
        ]
        results.append(rank_8)
        
        # Rank 7 (black pawns)
        rank_7 = [RecognitionResult(PieceType.BLACK_PAWN, 0.90) for _ in range(8)]
        results.append(rank_7)
        
        # Ranks 6-3 (empty)
        for _ in range(4):
            empty_rank = [RecognitionResult(PieceType.EMPTY, 0.99) for _ in range(8)]
            results.append(empty_rank)
        
        # Rank 2 (white pawns)
        rank_2 = [RecognitionResult(PieceType.WHITE_PAWN, 0.91) for _ in range(8)]
        results.append(rank_2)
        
        # Rank 1 (white back rank)
        rank_1 = [
            RecognitionResult(PieceType.WHITE_ROOK, 0.94),
            RecognitionResult(PieceType.WHITE_KNIGHT, 0.92),
            RecognitionResult(PieceType.WHITE_BISHOP, 0.93),
            RecognitionResult(PieceType.WHITE_QUEEN, 0.95),
            RecognitionResult(PieceType.WHITE_KING, 0.97),
            RecognitionResult(PieceType.WHITE_BISHOP, 0.92),
            RecognitionResult(PieceType.WHITE_KNIGHT, 0.93),
            RecognitionResult(PieceType.WHITE_ROOK, 0.95),
        ]
        results.append(rank_1)
        
        # Generate FEN from original results
        original_fen = self.recognizer.results_to_fen(results)
        
        # Set board position
        self.assertTrue(self.board_manager.set_position_from_fen(original_fen))
        
        # Verify it's the starting position
        self.assertEqual(
            original_fen.split()[0],  # Get just the position part
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        )
        
        # Now flip the results
        flipped_results = []
        for row in reversed(results):
            flipped_row = list(reversed(row))
            flipped_results.append(flipped_row)
        
        # Generate FEN from flipped results
        flipped_fen = self.recognizer.results_to_fen(flipped_results)
        
        # Set board position with flipped FEN
        self.assertTrue(self.board_manager.set_position_from_fen(flipped_fen))
        
        # After flipping the starting position, the FEN should be different
        # because we're viewing from the opposite perspective
        # The board is upside down: white pieces are now on rank 8, black on rank 1
        # But flipping also reverses columns (king and queen swap sides)
        self.assertNotEqual(original_fen.split()[0], flipped_fen.split()[0])
        
        # Verify the flipped FEN is valid
        self.assertIsNotNone(flipped_fen)
    
    def test_flip_workflow_with_asymmetric_position(self):
        """Test flip workflow with an asymmetric position to verify orientation change."""
        # Create a simple asymmetric position: white pawn on e4
        results = []
        
        # All empty except for one pawn
        for row in range(8):
            row_results = []
            for col in range(8):
                # White pawn on e4 (row 4, col 4 in our grid)
                if row == 4 and col == 4:
                    piece = PieceType.WHITE_PAWN
                else:
                    piece = PieceType.EMPTY
                result = RecognitionResult(piece, 0.95)
                row_results.append(result)
            results.append(row_results)
        
        # Generate FEN
        original_fen = self.recognizer.results_to_fen(results)
        
        # Flip results
        flipped_results = []
        for row in reversed(results):
            flipped_row = list(reversed(row))
            flipped_results.append(flipped_row)
        
        # Generate flipped FEN
        flipped_fen = self.recognizer.results_to_fen(flipped_results)
        
        # The FENs should be different (pawn moved to different square after flip)
        # Original: pawn at row 4, col 4 (e4)
        # Flipped: pawn at row 3, col 3 (d5)
        self.assertNotEqual(original_fen.split()[0], flipped_fen.split()[0])
    
    def test_double_flip_returns_original(self):
        """Test that flipping twice returns the original FEN."""
        # Create a random position
        results = []
        np.random.seed(42)  # For reproducibility
        
        piece_types = [
            PieceType.WHITE_PAWN, PieceType.WHITE_KNIGHT, PieceType.WHITE_BISHOP,
            PieceType.WHITE_ROOK, PieceType.WHITE_QUEEN, PieceType.WHITE_KING,
            PieceType.BLACK_PAWN, PieceType.BLACK_KNIGHT, PieceType.BLACK_BISHOP,
            PieceType.BLACK_ROOK, PieceType.BLACK_QUEEN, PieceType.BLACK_KING,
            PieceType.EMPTY, PieceType.EMPTY, PieceType.EMPTY  # More empty squares
        ]
        
        for row in range(8):
            row_results = []
            for col in range(8):
                piece = np.random.choice(piece_types)
                result = RecognitionResult(piece, 0.9)
                row_results.append(result)
            results.append(row_results)
        
        # Generate original FEN
        original_fen = self.recognizer.results_to_fen(results)
        
        # Flip once
        flipped_once = []
        for row in reversed(results):
            flipped_row = list(reversed(row))
            flipped_once.append(flipped_row)
        
        # Flip twice
        flipped_twice = []
        for row in reversed(flipped_once):
            flipped_row = list(reversed(row))
            flipped_twice.append(flipped_row)
        
        # Generate FEN after double flip
        double_flip_fen = self.recognizer.results_to_fen(flipped_twice)
        
        # Should match original (modulo turn and other metadata)
        self.assertEqual(original_fen.split()[0], double_flip_fen.split()[0])


if __name__ == '__main__':
    unittest.main()
