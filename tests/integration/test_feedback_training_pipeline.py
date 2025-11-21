#!/usr/bin/env python3
"""
Integration test for the complete feedback and training pipeline.

This test verifies the end-to-end workflow:
1. User loads an image
2. User makes corrections (including changing their mind)
3. Training data is properly deduplicated
4. Model can be retrained with clean data
5. Statistics are accurate
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import cv2

from src.computer_vision.feedback_manager import FeedbackManager
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType


class TestFeedbackTrainingPipeline(unittest.TestCase):
    """Integration test for feedback and training pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test feedback
        self.test_dir = Path(tempfile.mkdtemp())
        self.feedback_file = self.test_dir / 'test_feedback.json'
        
        # Create test images
        self.image1 = np.ones((800, 800, 3), dtype=np.uint8) * 128
        self.image2 = np.ones((800, 800, 3), dtype=np.uint8) * 150
        
        # Create test square images
        self.white_pawn = np.ones((100, 100, 3), dtype=np.uint8) * 180
        self.black_knight = np.ones((100, 100, 3), dtype=np.uint8) * 60
        self.white_queen = np.ones((100, 100, 3), dtype=np.uint8) * 190
        self.empty_square = np.ones((100, 100, 3), dtype=np.uint8) * 200
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_complete_workflow_single_image(self):
        """
        Test the complete workflow for a single image with multiple corrections.
        
        Simulates:
        1. User loads image
        2. User corrects e4 as knight
        3. User realizes mistake and corrects e4 as bishop
        4. User corrects d4 as queen
        5. Verify only final corrections are in training data
        """
        # Initialize manager
        manager = FeedbackManager(feedback_file=self.feedback_file)
        
        # User loads image
        manager.set_current_image(self.image1)
        
        # User makes first correction for e4
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.white_pawn
        )
        
        # User realizes mistake and corrects e4 again
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_KNIGHT,
            original_confidence=1.0,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.white_pawn
        )
        
        # User corrects another square
        manager.add_feedback(
            square_name='d4',
            original_prediction=PieceType.EMPTY,
            original_confidence=0.7,
            user_correction=PieceType.WHITE_QUEEN,
            square_image=self.white_queen
        )
        
        # Verify: Should have 3 total entries
        self.assertEqual(len(manager.feedback_data), 3)
        
        # Verify: Only 2 should be active
        stats = manager.get_correction_statistics()
        self.assertEqual(stats['active_corrections'], 2)
        self.assertEqual(stats['superseded_corrections'], 1)
        
        # Verify: Training data should only have 2 samples (active ones)
        training_data = manager.get_training_data()
        self.assertEqual(len(training_data), 2)
        
        # Verify: Training data has correct labels
        labels = [label for _, label in training_data]
        self.assertIn(PieceType.WHITE_BISHOP, labels)
        self.assertIn(PieceType.WHITE_QUEEN, labels)
        self.assertNotIn(PieceType.WHITE_KNIGHT, labels)
    
    def test_multiple_images_same_session(self):
        """
        Test workflow with multiple images in the same session.
        
        Verifies that corrections for the same square in different images
        are kept separate (not deduplicated).
        """
        manager = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='multi_image_session'
        )
        
        # Process first image
        manager.set_current_image(self.image1)
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.WHITE_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.white_pawn
        )
        
        # Process second image (different board)
        manager.set_current_image(self.image2)
        manager.add_feedback(
            square_name='e4',
            original_prediction=PieceType.BLACK_PAWN,
            original_confidence=0.6,
            user_correction=PieceType.BLACK_KNIGHT,
            square_image=self.black_knight
        )
        
        # Both should be active (different images)
        stats = manager.get_correction_statistics()
        self.assertEqual(stats['active_corrections'], 2)
        self.assertEqual(stats['superseded_corrections'], 0)
        
        # Both should be in training data
        training_data = manager.get_training_data()
        self.assertEqual(len(training_data), 2)
        
        # All from same session
        self.assertEqual(stats['by_session']['multi_image_session'], 2)
    
    def test_retraining_with_clean_data(self):
        """
        Test that retraining works with deduplicated data.
        
        Verifies that the piece recognizer can successfully retrain
        using only active (non-superseded) feedback.
        """
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.image1)
        
        # Add corrections, including some that supersede others
        corrections = [
            ('e4', PieceType.WHITE_PAWN, self.white_pawn),
            ('e4', PieceType.WHITE_KNIGHT, self.white_pawn),  # Supersedes previous
            ('d4', PieceType.WHITE_BISHOP, self.white_pawn),
            ('d4', PieceType.WHITE_QUEEN, self.white_queen),  # Supersedes previous
            ('c3', PieceType.BLACK_KNIGHT, self.black_knight),
            ('f5', PieceType.EMPTY, self.empty_square),
        ]
        
        for square, piece_type, image in corrections:
            manager.add_feedback(
                square_name=square,
                original_prediction=None,
                original_confidence=0.5,
                user_correction=piece_type,
                square_image=image
            )
        
        # Get training data (should only have 4 active samples)
        training_data = manager.get_training_data()
        self.assertEqual(len(training_data), 4)
        
        # Retrain recognizer
        recognizer = PieceRecognizer()
        result = recognizer.retrain_from_feedback(training_data)
        
        # Verify retraining succeeded
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['samples_processed'], 4)
        self.assertEqual(result['piece_types_trained'], 4)
        
        # Verify piece counts in training result
        self.assertEqual(result['piece_counts']['WHITE_KNIGHT'], 1)
        self.assertEqual(result['piece_counts']['WHITE_QUEEN'], 1)
        self.assertEqual(result['piece_counts']['BLACK_KNIGHT'], 1)
        self.assertEqual(result['piece_counts']['EMPTY'], 1)
        
        # Verify no superseded pieces in training
        self.assertNotIn('WHITE_PAWN', result['piece_counts'])
        self.assertNotIn('WHITE_BISHOP', result['piece_counts'])
    
    def test_session_isolation(self):
        """
        Test that multiple sessions are properly isolated.
        
        Verifies that different sessions can be tracked and analyzed
        independently.
        """
        # Create first session
        session1 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='session_1'
        )
        session1.set_current_image(self.image1)
        
        session1.add_feedback(
            square_name='e4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.white_pawn
        )
        
        session1.add_feedback(
            square_name='d4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.white_pawn
        )
        
        # Create second session
        session2 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='session_2'
        )
        session2.set_current_image(self.image2)
        
        session2.add_feedback(
            square_name='e5',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.BLACK_KNIGHT,
            square_image=self.black_knight
        )
        
        # Load and verify sessions
        manager = FeedbackManager(feedback_file=self.feedback_file)
        
        # Check session summary
        summary = manager.get_session_summary()
        self.assertEqual(len(summary), 2)
        self.assertEqual(summary['session_1']['active_count'], 2)
        self.assertEqual(summary['session_2']['active_count'], 1)
        
        # Filter by session
        s1_feedback = manager.get_feedback_by_session('session_1')
        self.assertEqual(len(s1_feedback), 2)
        
        s2_feedback = manager.get_feedback_by_session('session_2')
        self.assertEqual(len(s2_feedback), 1)
    
    def test_persistence_across_restarts(self):
        """
        Test that feedback persists correctly across manager restarts.
        
        Verifies that deduplication state and session info are preserved
        when the application is restarted.
        """
        # First session: Add and correct feedback
        manager1 = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='persistent_session'
        )
        manager1.set_current_image(self.image1)
        
        manager1.add_feedback(
            square_name='e4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_KNIGHT,
            square_image=self.white_pawn
        )
        
        manager1.add_feedback(
            square_name='e4',
            original_prediction=None,
            original_confidence=0.5,
            user_correction=PieceType.WHITE_BISHOP,
            square_image=self.white_pawn
        )
        
        # "Restart" - load from file
        manager2 = FeedbackManager(feedback_file=self.feedback_file)
        
        # Should have both entries but only one active
        self.assertEqual(len(manager2.feedback_data), 2)
        
        stats = manager2.get_correction_statistics()
        self.assertEqual(stats['active_corrections'], 1)
        self.assertEqual(stats['superseded_corrections'], 1)
        
        # Active correction should be the bishop
        active_feedback = [fb for fb in manager2.feedback_data if fb.is_active]
        self.assertEqual(len(active_feedback), 1)
        self.assertEqual(active_feedback[0].user_correction, PieceType.WHITE_BISHOP)
    
    def test_statistics_accuracy(self):
        """
        Test that statistics accurately reflect the training data state.
        
        Verifies that counts, averages, and summaries are correct
        after multiple corrections and deduplication.
        """
        manager = FeedbackManager(feedback_file=self.feedback_file)
        manager.set_current_image(self.image1)
        
        # Add varied feedback with different confidence levels
        feedback_entries = [
            ('e4', 0.4, PieceType.WHITE_KNIGHT),
            ('e4', 0.6, PieceType.WHITE_BISHOP),  # Supersedes previous
            ('d4', 0.8, PieceType.WHITE_QUEEN),
            ('c3', 0.5, PieceType.BLACK_KNIGHT),
            ('c3', 0.7, PieceType.EMPTY),  # Supersedes previous
        ]
        
        for square, conf, piece in feedback_entries:
            manager.add_feedback(
                square_name=square,
                original_prediction=None,
                original_confidence=conf,
                user_correction=piece,
                square_image=self.white_pawn
            )
        
        # Get statistics
        stats = manager.get_correction_statistics()
        
        # Verify counts
        self.assertEqual(stats['total_corrections'], 5)
        self.assertEqual(stats['active_corrections'], 3)
        self.assertEqual(stats['superseded_corrections'], 2)
        
        # Verify by piece type (only active)
        self.assertEqual(stats['by_piece_type']['WHITE_BISHOP'], 1)
        self.assertEqual(stats['by_piece_type']['WHITE_QUEEN'], 1)
        self.assertEqual(stats['by_piece_type']['EMPTY'], 1)
        
        # Verify average confidence includes only active entries (makes sense for training)
        # Active entries: e4(0.6), d4(0.8), c3(0.7)
        expected_avg = (0.6 + 0.8 + 0.7) / 3
        self.assertAlmostEqual(stats['avg_original_confidence'], expected_avg, places=2)
    
    def test_complex_correction_scenario(self):
        """
        Test a complex real-world scenario with multiple corrections.
        
        Simulates a user working through a board and making several
        corrections, including changing their mind multiple times.
        """
        manager = FeedbackManager(
            feedback_file=self.feedback_file,
            session_id='complex_session'
        )
        manager.set_current_image(self.image1)
        
        # User goes through board, making corrections
        # Including changing mind on some squares
        corrections_sequence = [
            # Initial pass
            ('e4', PieceType.WHITE_PAWN),
            ('d4', PieceType.WHITE_PAWN),
            ('e5', PieceType.BLACK_PAWN),
            
            # User notices e4 is wrong, corrects it
            ('e4', PieceType.WHITE_KNIGHT),
            
            # User continues
            ('d5', PieceType.BLACK_PAWN),
            
            # User changes mind on e4 again
            ('e4', PieceType.WHITE_BISHOP),
            
            # More corrections
            ('f4', PieceType.WHITE_QUEEN),
            
            # Final change on e4
            ('e4', PieceType.EMPTY),
            
            # Additional squares
            ('g4', PieceType.BLACK_KNIGHT),
            ('h4', PieceType.WHITE_ROOK),
        ]
        
        for square, piece in corrections_sequence:
            manager.add_feedback(
                square_name=square,
                original_prediction=None,
                original_confidence=0.5,
                user_correction=piece,
                square_image=self.white_pawn
            )
        
        # Verify final state
        stats = manager.get_correction_statistics()
        
        # Total entries
        self.assertEqual(stats['total_corrections'], 10)
        
        # Active corrections: e4(final), d4, e5, d5, f4, g4, h4 = 7
        self.assertEqual(stats['active_corrections'], 7)
        
        # Superseded: e4 had 3 superseded versions
        self.assertEqual(stats['superseded_corrections'], 3)
        
        # Training data should have 7 samples
        training_data = manager.get_training_data()
        self.assertEqual(len(training_data), 7)
        
        # e4 should be EMPTY in training data (final correction)
        labels = [label for _, label in training_data]
        self.assertIn(PieceType.EMPTY, labels)
        
        # Retrain should work
        recognizer = PieceRecognizer()
        result = recognizer.retrain_from_feedback(training_data)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['samples_processed'], 7)


if __name__ == '__main__':
    unittest.main()
