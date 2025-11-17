#!/usr/bin/env python3
"""
Entry point for the PySide6 Chess Engine GUI application.

This script launches the main PySide6 application window.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui_pyside6.main_window import main

if __name__ == "__main__":
    main()
