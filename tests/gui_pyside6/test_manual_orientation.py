"""
Unit tests for manual orientation selection feature.

Tests the manual orientation selection functionality in the control panel.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PySide6.QtWidgets import QApplication
    from src.gui_pyside6.widgets.control_panel import ControlPanelWidget
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@unittest.skipIf(not PYSIDE6_AVAILABLE, "PySide6 not available")
class TestManualOrientation(unittest.TestCase):
    """Test manual orientation selection functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        if PYSIDE6_AVAILABLE:
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures."""
        if PYSIDE6_AVAILABLE:
            self.control_panel = ControlPanelWidget()
    
    def test_default_orientation_is_auto(self):
        """Test that default orientation preference is auto-detect."""
        pref = self.control_panel.get_orientation_preference()
        self.assertEqual(pref, 'auto')
    
    def test_set_orientation_to_white(self):
        """Test setting orientation preference to white."""
        self.control_panel.set_orientation_preference('white')
        pref = self.control_panel.get_orientation_preference()
        self.assertEqual(pref, 'white')
    
    def test_set_orientation_to_black(self):
        """Test setting orientation preference to black."""
        self.control_panel.set_orientation_preference('black')
        pref = self.control_panel.get_orientation_preference()
        self.assertEqual(pref, 'black')
    
    def test_reset_returns_to_auto(self):
        """Test that reset returns orientation to auto-detect."""
        self.control_panel.set_orientation_preference('black')
        self.control_panel.reset()
        pref = self.control_panel.get_orientation_preference()
        self.assertEqual(pref, 'auto')
    
    def test_orientation_selector_has_three_options(self):
        """Test that orientation selector has exactly three options."""
        count = self.control_panel.orientation_selector.count()
        self.assertEqual(count, 3)
    
    def test_orientation_options_are_correct(self):
        """Test that orientation options are auto, white, and black."""
        options = []
        for i in range(self.control_panel.orientation_selector.count()):
            options.append(self.control_panel.orientation_selector.itemData(i))
        
        self.assertEqual(sorted(options), ['auto', 'black', 'white'])


if __name__ == '__main__':
    unittest.main()
