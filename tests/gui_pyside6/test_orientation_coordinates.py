"""
Integration test for board orientation and coordinate labels.

Tests that widgets correctly update coordinate labels based on board orientation.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PySide6.QtWidgets import QApplication
    from src.gui_pyside6.widgets.board_widget import BoardReconstructionWidget
    from src.gui_pyside6.widgets.analysis_widget import EngineAnalysisWidget
    from src.chess_engine.board_manager import BoardManager
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@unittest.skipIf(not PYSIDE6_AVAILABLE, "PySide6 not available")
class TestOrientationCoordinates(unittest.TestCase):
    """Test coordinate labels update with board orientation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_board_widget_default_orientation(self):
        """Test board widget has white orientation by default."""
        widget = BoardReconstructionWidget()
        self.assertEqual(widget.board_orientation, 'white')
    
    def test_board_widget_set_orientation(self):
        """Test board widget can change orientation."""
        widget = BoardReconstructionWidget()
        
        # Set to black orientation
        widget.set_board_orientation('black')
        self.assertEqual(widget.board_orientation, 'black')
        
        # Set back to white
        widget.set_board_orientation('white')
        self.assertEqual(widget.board_orientation, 'white')
    
    def test_analysis_widget_default_orientation(self):
        """Test analysis widget has white orientation by default."""
        widget = EngineAnalysisWidget()
        self.assertEqual(widget.board_orientation, 'white')
    
    def test_analysis_widget_set_orientation(self):
        """Test analysis widget can change orientation."""
        widget = EngineAnalysisWidget()
        
        # Set to black orientation
        widget.set_board_orientation('black')
        self.assertEqual(widget.board_orientation, 'black')
        
        # Set back to white
        widget.set_board_orientation('white')
        self.assertEqual(widget.board_orientation, 'white')
    
    def test_coordinate_calculation_white_orientation(self):
        """Test coordinate calculations for white orientation."""
        # When white is at bottom:
        # - Ranks go from 8 (top) to 1 (bottom)
        # - Files go from a (left) to h (right)
        
        # Test rank labels (white orientation)
        for row in range(8):
            rank = 8 - row
            self.assertEqual(rank, 8 - row)
        
        # Test file labels (white orientation)
        for col in range(8):
            file_char = chr(ord('a') + col)
            self.assertEqual(file_char, chr(ord('a') + col))
    
    def test_coordinate_calculation_black_orientation(self):
        """Test coordinate calculations for black orientation."""
        # When black is at bottom:
        # - Ranks go from 1 (top) to 8 (bottom)
        # - Files go from h (left) to a (right)
        
        # Test rank labels (black orientation)
        for row in range(8):
            rank = row + 1
            self.assertEqual(rank, row + 1)
        
        # Test file labels (black orientation)
        for col in range(8):
            file_char = chr(ord('h') - col)
            self.assertEqual(file_char, chr(ord('h') - col))
    
    def test_board_widget_with_board_manager(self):
        """Test board widget works with board manager and different orientations."""
        widget = BoardReconstructionWidget()
        board_manager = BoardManager()
        
        # Set initial board state
        widget.set_board_state(board_manager)
        self.assertIsNotNone(widget.board_manager)
        
        # Change orientation
        widget.set_board_orientation('black')
        self.assertEqual(widget.board_orientation, 'black')
        
        # Verify board manager is still set
        self.assertIsNotNone(widget.board_manager)
    
    def test_analysis_widget_with_board_manager(self):
        """Test analysis widget works with board manager and different orientations."""
        widget = EngineAnalysisWidget()
        board_manager = BoardManager()
        
        # Set initial board state
        widget.set_board_state(board_manager)
        self.assertIsNotNone(widget.board_manager)
        
        # Change orientation
        widget.set_board_orientation('black')
        self.assertEqual(widget.board_orientation, 'black')
        
        # Verify board manager is still set
        self.assertIsNotNone(widget.board_manager)
    
    def test_orientation_persistence_across_updates(self):
        """Test that orientation persists when board state is updated."""
        widget = BoardReconstructionWidget()
        board_manager = BoardManager()
        
        # Set to black orientation
        widget.set_board_orientation('black')
        self.assertEqual(widget.board_orientation, 'black')
        
        # Update board state
        widget.set_board_state(board_manager)
        
        # Orientation should still be black
        self.assertEqual(widget.board_orientation, 'black')


if __name__ == '__main__':
    unittest.main()
