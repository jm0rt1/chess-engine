"""
Unit tests for BoardManager class.

Tests the core board management functionality including move validation,
state management, and board operations.
"""

import unittest
import chess
from src.chess_engine.board_manager import BoardManager


class TestBoardManager(unittest.TestCase):
    """Test cases for BoardManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.board_manager = BoardManager()

    def test_initialization(self):
        """Test that BoardManager initializes correctly with starting position."""
        # Check that board is initialized
        self.assertIsNotNone(self.board_manager.get_board_state())
        
        # Check starting position FEN
        expected_fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        actual_fen = self.board_manager.get_fen()
        self.assertTrue(actual_fen.startswith(expected_fen_start))

    def test_make_legal_move(self):
        """Test making a legal move."""
        # Make e4 move (e2 to e4)
        move = chess.Move.from_uci("e2e4")
        result = self.board_manager.make_move(move)
        self.assertTrue(result)
        
        # Verify move was made
        self.assertEqual(len(self.board_manager.move_history), 1)

    def test_reset(self):
        """Test resetting the board."""
        # Make some moves
        self.board_manager.make_move(chess.Move.from_uci("e2e4"))
        self.board_manager.make_move(chess.Move.from_uci("e7e5"))
        
        # Reset
        self.board_manager.reset()
        
        # Verify back to starting position
        expected_fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.assertTrue(self.board_manager.get_fen().startswith(expected_fen_start))
        self.assertEqual(len(self.board_manager.move_history), 0)


if __name__ == '__main__':
    unittest.main()
