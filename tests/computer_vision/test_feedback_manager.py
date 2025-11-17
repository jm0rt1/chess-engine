"""
Unit tests for FeedbackManager.

Tests feedback collection and storage functionality.
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.computer_vision.feedback_manager import FeedbackManager, PieceFeedback
from src.computer_vision.piece_recognizer import PieceType


class TestPieceFeedback(unittest.TestCase):
    """Test PieceFeedback data class."""
    
    def test_feedback_creation(self):
        """Test creating a PieceFeedback object."""
        feedback = PieceFeedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT
        )
        
        self.assertEqual(feedback.square_name, 'e4')
        self.assertEqual(feedback.original_prediction, PieceType.WHITE_PAWN)
        self.assertEqual(feedback.original_confidence, 0.6)
        self.assertEqual(feedback.user_correction, PieceType.WHITE_KNIGHT)
        self.assertIsNotNone(feedback.timestamp)
    
    def test_feedback_to_dict(self):
        """Test converting feedback to dictionary."""
        feedback = PieceFeedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT
        )
        
        data = feedback.to_dict()
        
        self.assertEqual(data['square_name'], 'e4')
        self.assertEqual(data['original_prediction'], 'WHITE_PAWN')
        self.assertEqual(data['user_correction'], 'WHITE_KNIGHT')
        self.assertEqual(data['original_confidence'], 0.6)
    
    def test_feedback_from_dict(self):
        """Test creating feedback from dictionary."""
        data = {
            'square_name': 'e4',
            'original_prediction': 'WHITE_PAWN',
            'original_confidence': 0.6,
            'user_correction': 'WHITE_KNIGHT',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        feedback = PieceFeedback.from_dict(data)
        
        self.assertEqual(feedback.square_name, 'e4')
        self.assertEqual(feedback.original_prediction, PieceType.WHITE_PAWN)
        self.assertEqual(feedback.user_correction, PieceType.WHITE_KNIGHT)
        self.assertEqual(feedback.original_confidence, 0.6)


class TestFeedbackManager(unittest.TestCase):
    """Test FeedbackManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_path.exists():
            self.temp_path.unlink()
    
    def test_manager_initialization(self):
        """Test FeedbackManager initialization."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        self.assertEqual(manager.feedback_file, self.temp_path)
        self.assertEqual(len(manager.feedback_data), 0)
    
    def test_add_feedback(self):
        """Test adding feedback."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT
        )
        
        self.assertEqual(manager.get_feedback_count(), 1)
    
    def test_feedback_persistence(self):
        """Test that feedback is saved and loaded correctly."""
        # Create manager and add feedback
        manager1 = FeedbackManager(feedback_file=self.temp_path)
        manager1.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT
        )
        
        # Create new manager and check feedback was loaded
        manager2 = FeedbackManager(feedback_file=self.temp_path)
        self.assertEqual(manager2.get_feedback_count(), 1)
        
        feedback = manager2.feedback_data[0]
        self.assertEqual(feedback.square_name, 'e4')
        self.assertEqual(feedback.original_prediction, PieceType.WHITE_PAWN)
        self.assertEqual(feedback.user_correction, PieceType.WHITE_KNIGHT)
    
    def test_correction_statistics(self):
        """Test getting correction statistics."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        manager.add_feedback('e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT)
        manager.add_feedback('e5', PieceType.BLACK_PAWN, 0.7, PieceType.BLACK_KNIGHT)
        manager.add_feedback('d4', PieceType.WHITE_ROOK, 0.5, PieceType.WHITE_KNIGHT)
        
        stats = manager.get_correction_statistics()
        
        self.assertEqual(stats['total_corrections'], 3)
        self.assertEqual(stats['by_piece_type']['WHITE_KNIGHT'], 2)
        self.assertEqual(stats['by_piece_type']['BLACK_KNIGHT'], 1)
        self.assertAlmostEqual(stats['avg_original_confidence'], 0.6, places=2)
    
    def test_clear_feedback(self):
        """Test clearing feedback."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        manager.add_feedback('e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT)
        self.assertEqual(manager.get_feedback_count(), 1)
        
        manager.clear_feedback()
        self.assertEqual(manager.get_feedback_count(), 0)
        self.assertFalse(self.temp_path.exists())
    
    def test_export_feedback(self):
        """Test exporting feedback."""
        manager = FeedbackManager(feedback_file=self.temp_path)
        
        manager.add_feedback('e4', PieceType.WHITE_PAWN, 0.6, PieceType.WHITE_KNIGHT)
        
        # Export to different file
        export_path = self.temp_path.parent / 'export_test.json'
        try:
            manager.export_feedback(export_path)
            
            self.assertTrue(export_path.exists())
            
            # Verify exported content
            with open(export_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['square_name'], 'e4')
        finally:
            if export_path.exists():
                export_path.unlink()


if __name__ == '__main__':
    unittest.main()
