"""
Tests for the PieceRecognizer module.

Ensures that RecognitionResult handles None piece_type correctly.
"""

import unittest
from src.computer_vision.piece_recognizer import (
    PieceRecognizer,
    RecognitionResult,
    PieceType
)


class TestRecognitionResult(unittest.TestCase):
    """Test cases for RecognitionResult class."""

    def test_str_with_none_piece_type(self):
        """Test that __str__ handles None piece_type without error."""
        result = RecognitionResult(
            piece_type=None,
            confidence=0.3
        )
        
        # Should not raise an error
        str_repr = str(result)
        self.assertIn("Unknown", str_repr)
        self.assertIn("0.30", str_repr)

    def test_str_with_empty_piece_type(self):
        """Test that __str__ handles EMPTY piece_type correctly."""
        result = RecognitionResult(
            piece_type=PieceType.EMPTY,
            confidence=0.9
        )
        
        str_repr = str(result)
        self.assertIn("Empty", str_repr)
        self.assertIn("0.90", str_repr)

    def test_str_with_valid_piece_type(self):
        """Test that __str__ handles valid piece_type correctly."""
        result = RecognitionResult(
            piece_type=PieceType.WHITE_PAWN,
            confidence=0.85
        )
        
        str_repr = str(result)
        self.assertIn("White Pawn", str_repr)
        self.assertIn("0.85", str_repr)

    def test_to_fen_char_with_none(self):
        """Test that to_fen_char handles None piece_type."""
        result = RecognitionResult(
            piece_type=None,
            confidence=0.3
        )
        
        fen_char = result.to_fen_char()
        self.assertEqual(fen_char, '.')

    def test_to_fen_char_with_empty(self):
        """Test that to_fen_char handles EMPTY piece_type."""
        result = RecognitionResult(
            piece_type=PieceType.EMPTY,
            confidence=0.9
        )
        
        fen_char = result.to_fen_char()
        self.assertEqual(fen_char, '.')

    def test_to_fen_char_with_valid_piece(self):
        """Test that to_fen_char handles valid piece_type."""
        result = RecognitionResult(
            piece_type=PieceType.WHITE_PAWN,
            confidence=0.85
        )
        
        fen_char = result.to_fen_char()
        self.assertEqual(fen_char, 'P')


if __name__ == '__main__':
    unittest.main()
