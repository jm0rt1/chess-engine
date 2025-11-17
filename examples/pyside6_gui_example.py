"""
PySide6 GUI Example Script.

This script demonstrates how to use the PySide6 Chess Engine GUI
programmatically and provides examples of its capabilities.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PySide6.QtWidgets import QApplication
from src.gui_pyside6.main_window import MainWindow


def main():
    """
    Main function demonstrating PySide6 GUI usage.
    
    This creates the application and shows various features:
    - Loading images
    - Processing pipeline
    - Board reconstruction
    - Engine analysis
    """
    print("=" * 70)
    print("PySide6 Chess Engine GUI Example")
    print("=" * 70)
    print()
    print("This example launches the PySide6 GUI application.")
    print()
    print("Features:")
    print("  1. Image Processing Pipeline Visualization")
    print("     - Load a chess board image")
    print("     - See every processing stage")
    print("     - Step through the pipeline")
    print()
    print("  2. Board Reconstruction")
    print("     - Visual chess board with Unicode pieces")
    print("     - Confidence scores for each piece")
    print("     - FEN notation display")
    print()
    print("  3. Engine Analysis")
    print("     - Threat map visualization")
    print("     - Best move suggestions with arrows")
    print("     - Detailed explanations")
    print()
    print("Usage Instructions:")
    print("  1. Click 'Load Image...' to select a chess board image")
    print("  2. Click 'Process Image' to run the complete pipeline")
    print("  3. Review the board reconstruction")
    print("  4. Click 'Run Engine Analysis' to see threats and moves")
    print()
    print("Keyboard Shortcuts:")
    print("  Ctrl+O: Load Image")
    print("  Ctrl+P: Process Image")
    print("  Ctrl+S: Step Through Pipeline")
    print("  Ctrl+E: Run Engine Analysis")
    print("  Ctrl+Q: Exit")
    print()
    print("=" * 70)
    print()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Chess Engine - PySide6 Example")
    app.setOrganizationName("Chess Engine Project")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("GUI launched successfully!")
    print("Close the window or press Ctrl+Q to exit.")
    print()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
