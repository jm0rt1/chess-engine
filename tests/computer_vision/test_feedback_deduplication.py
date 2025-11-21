#!/usr/bin/env python3
"""
Tests for feedback deduplication and session tracking.

These tests verify that:
1. Multiple corrections for the same square in the same image are properly deduplicated
2. Session tracking works correctly
3. Only active feedback is used for training
4. Statistics accurately reflect active vs superseded entries
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from src.computer_vision.feedback_manager import FeedbackManager, PieceFeedback
from src.computer_vision.piece_recognizer import PieceType


class TestFeedbackDeduplication(unittest.TestCase):
    """Test deduplication of feedback entries."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test feedback
        self.test_dir = Path(tempfile.mkdtemp())
        self.feedback_file = self.test_dir / 'test_feedback.json'
        
        # Create a test image
        self.test_image = np.ones((800, 800, 3), dtype=np.uint8) * 128
        self.test_square = np.ones((100, 100, 3), dtype=np.uint8) * 150
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_session_id_generation(self):
        """Test that each manager instance gets a unique session ID."""
        manager1 = FeedbackManager(feedback_file=self.feedback_file)
        manager2 = FeedbackManager(feedback_file=self.feedback_file)
        
        self.assertIsNotNone(manager1.session_id)
        self.assertIsNotNone(manager2.session_id)
        self.assertNotEqual(manager1.session_id, manager2.session_id)
        self.assertTrue(manager1.session_id.startswith('session_'))
    
    def test_explicit_session_id(self):
        """Test that explicit session ID is used when provided."""
        custom_session = "custom_session_123"
        manager = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id=custom_session
        )
        
        self.assertEqual(manager.session_id, custom_session)
    
    def test_image_hash_computation(self):
        """Test that image hashing works correctly."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        
        # Set current image
        manager.set_current_image(self.test_image)
        
        # Hash should be set
        self.assertIsNotNone(manager.current_image_hash)
        self.assertEqual(len(manager.current_image_hash), 64)  # SHA256 produces 64 hex chars
        
        # Same image should produce same hash
        hash1 = manager.current_image_hash
        manager.set_current_image(self.test_image)
        hash2 = manager.current_image_hash
        self.assertEqual(hash1, hash2)
        
        # Different image should produce different hash
        different_image = np.ones((800, 800, 3), dtype=np.uint8) * 200
        manager.set_current_image(different_image)
        hash3 = manager.current_image_hash
        self.assertNotEqual(hash1, hash3)
    
    def test_basic_deduplication(self):
        """Test that duplicate feedback for same square is handled correctly."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        # Add first correction for e4
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        # Add second correction for same square (user changes mind)
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_KNIGHT,
            original_confidence=1.0,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Should have 2 total entries
        self.assertEqual(len(manager.feedback_data), 2)
        
        # But only 1 should be active
        active_feedback = [fb for fb in manager.feedback_data if fb.is_active]
        self.assertEqual(len(active_feedback), 1)
        
        # The active one should be the latest (WHITE_BISHOP)
        self.assertEqual(active_feedback[0].user_correction, PieceType.WHITE_BISHOP)
        
        # The superseded one should be inactive
        superseded = [fb for fb in manager.feedback_data if not fb.is_active]
        self.assertEqual(len(superseded), 1)
        self.assertEqual(superseded[0].user_correction, PieceType.WHITE_KNIGHT)
    
    def test_multiple_corrections_same_square(self):
        """Test multiple corrections for the same square."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        corrections = [
            PieceType.WHITE_PAWN,
            PieceType.WHITE_KNIGHT,
            PieceType.WHITE_BISHOP,
            PieceType.WHITE_QUEEN
        ]
        
        for correction in corrections:
            manager.add_feedback(
                square_name='d4',
                original_prediction=None,
                original_confidence=0.5,
                user_correction=correction,
                square_image=self.test_square
            )
        
        # Should have 4 total entries
        self.assertEqual(len(manager.feedback_data), 4)
        
        # But only 1 should be active
        active_feedback = [fb for fb in manager.feedback_data if fb.is_active]
        self.assertEqual(len(active_feedback), 1)
        
        # The active one should be the last correction (WHITE_QUEEN)
        self.assertEqual(active_feedback[0].user_correction, PieceType.WHITE_QUEEN)
    
    def test_different_squares_not_deduplicated(self):
        """Test that different squares are not deduplicated."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        # Add corrections for different squares
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        manager.add_feedback(
            square_name='d4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Both should be active
        active_feedback = [fb for fb in manager.feedback_data if fb.is_active]
        self.assertEqual(len(active_feedback), 2)
    
    def test_different_images_not_deduplicated(self):
        """Test that same square in different images is not deduplicated."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        
        # First image, first correction
        manager.set_current_image(self.test_image)
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        # Different image, correction for same square name
        different_image = np.ones((800, 800, 3), dtype=np.uint8) * 200
        manager.set_current_image(different_image)
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Both should be active (different images)
        active_feedback = [fb for fb in manager.feedback_data if fb.is_active]
        self.assertEqual(len(active_feedback), 2)
    
    def test_training_data_only_includes_active(self):
        """Test that get_training_data only returns active feedback by default."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        # Add multiple corrections for same square
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_KNIGHT,
            original_confidence=1.0,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Get training data (active only by default)
        training_data = manager.get_training_data()
        
        # Should only have 1 sample (the active one)
        self.assertEqual(len(training_data), 1)
        
        # It should be the bishop (latest correction)
        _, label = training_data[0]
        self.assertEqual(label, PieceType.WHITE_BISHOP)
        
        # Get all training data (including superseded)
        all_training_data = manager.get_training_data(active_only=False)
        self.assertEqual(len(all_training_data), 2)
    
    def test_statistics_reflect_active_vs_superseded(self):
        """Test that statistics correctly count active vs superseded entries."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        # Add 3 corrections for e4 (2 will be superseded)
        for correction in [PieceType.WHITE_PAWN, PieceType.WHITE_KNIGHT, PieceType.WHITE_BISHOP]:
            manager.add_feedback(
                square_name='e4',
                original_prediction=None,
                original_confidence=0.5,
                user_correction=correction,
                square_image=self.test_square
            )
        
        # Add 1 correction for d4 (will be active)
        manager.add_feedback(
            square_name='d4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_QUEEN,
            square_image=self.test_square
        )
        
        stats = manager.get_correction_statistics()
        
        # Total should be 4
        self.assertEqual(stats['total_corrections'], 4)
        
        # Active should be 2 (latest e4 + d4)
        self.assertEqual(stats['active_corrections'], 2)
        
        # Superseded should be 2 (first two e4 corrections)
        self.assertEqual(stats['superseded_corrections'], 2)
        
        # By piece type should only count active
        self.assertEqual(stats['by_piece_type']['WHITE_BISHOP'], 1)
        self.assertEqual(stats['by_piece_type']['WHITE_QUEEN'], 1)
        self.assertNotIn('WHITE_PAWN', stats['by_piece_type'])
        self.assertNotIn('WHITE_KNIGHT', stats['by_piece_type'])
    
    def test_session_tracking_in_feedback(self):
        """Test that session ID is stored with feedback."""
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.test_image)
        
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        # Feedback should have session ID
        feedback = manager.feedback_data[0]
        self.assertEqual(feedback.session_id, manager.session_id)
    
    def test_get_feedback_by_session(self):
        """Test filtering feedback by session."""
        # Create two managers with different sessions
        manager1 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='session1'
        )
        manager1.set_current_image(self.test_image)
        
        manager1.add_feedback(
            square_name='e4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        # Reload with different session
        manager2 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='session2'
        )
        manager2.set_current_image(self.test_image)
        
        manager2.add_feedback(
            square_name='d4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Should be able to filter by session
        session1_feedback = manager2.get_feedback_by_session('session1')
        self.assertEqual(len(session1_feedback), 1)
        self.assertEqual(session1_feedback[0].square_name, 'e4')
        
        session2_feedback = manager2.get_feedback_by_session('session2')
        self.assertEqual(len(session2_feedback), 1)
        self.assertEqual(session2_feedback[0].square_name, 'd4')
    
    def test_session_summary(self):
        """Test session summary functionality."""
        manager = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='test_session'
        )
        manager.set_current_image(self.test_image)
        
        # Add multiple corrections
        for i in range(3):
            manager.add_feedback(
                square_name=f'e{i+1}',
                original_prediction=None,
                original_confidence=0.5,
                user_correction=PieceType.WHITE_PAWN,
                square_image=self.test_square
            )
        
        summary = manager.get_session_summary()
        
        self.assertIn('test_session', summary)
        self.assertEqual(summary['test_session']['total_count'], 3)
        self.assertEqual(summary['test_session']['active_count'], 3)
    
    def test_persistence_with_new_fields(self):
        """Test that new fields persist correctly across save/load."""
        manager1 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='persist_session'
        )
        manager1.set_current_image(self.test_image)
        
        manager1.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.test_square
        )
        
        # Add a superseded entry
        manager1.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_KNIGHT,
            original_confidence=1.0,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.test_square
        )
        
        # Reload from file
        manager2 = FeedbackManager(feedback_file=self.feedback_file)
        
        # Should have both entries
        self.assertEqual(len(manager2.feedback_data), 2)
        
        # Check that new fields are loaded correctly
        for fb in manager2.feedback_data:
            self.assertIsNotNone(fb.session_id)
            self.assertIsNotNone(fb.unique_key)
            self.assertIsNotNone(fb.image_hash)
            self.assertIsInstance(fb.is_active, bool)
        
        # Check active status
        active = [fb for fb in manager2.feedback_data if fb.is_active]
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].user_correction, PieceType.WHITE_BISHOP)


if __name__ == '__main__':
    unittest.main()
