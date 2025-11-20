"""
Demo script to test manual orientation correction.

This script demonstrates the new manual orientation selection feature
and shows how it helps correct images with black on bottom.
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer, PieceType, RecognitionResult


def create_mock_squares_with_black_at_bottom():
    """
    Create mock squares representing a board with black pieces at bottom.
    
    This simulates an image captured from black's perspective.
    """
    squares = []
    
    # Row 0 (top of image) - should have white pieces (rank 1 in this orientation)
    # Row 7 (bottom of image) - should have black pieces (rank 8 in this orientation)
    
    for row in range(8):
        row_squares = []
        for col in range(8):
            # Create a simple gradient to distinguish positions
            # Bottom rows are darker (simulating black pieces)
            if row >= 6:  # Bottom two rows
                square = np.ones((100, 100, 3), dtype=np.uint8) * 50  # Dark (black pieces area)
            elif row <= 1:  # Top two rows  
                square = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Light (white pieces area)
            else:
                square = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Middle
            row_squares.append(square)
        squares.append(row_squares)
    
    return squares


def create_mock_recognition_with_black_at_bottom():
    """
    Create mock recognition results for a board with black at bottom.
    """
    results = []
    
    for row in range(8):
        row_results = []
        for col in range(8):
            if row == 0:
                # Top row - white pieces (in this orientation)
                piece = PieceType.WHITE_ROOK if col in [0, 7] else PieceType.WHITE_KNIGHT
                row_results.append(RecognitionResult(piece, 0.95))
            elif row == 1:
                # White pawns
                row_results.append(RecognitionResult(PieceType.WHITE_PAWN, 0.95))
            elif row == 6:
                # Black pawns
                row_results.append(RecognitionResult(PieceType.BLACK_PAWN, 0.95))
            elif row == 7:
                # Bottom row - black pieces
                piece = PieceType.BLACK_ROOK if col in [0, 7] else PieceType.BLACK_KNIGHT
                row_results.append(RecognitionResult(piece, 0.95))
            else:
                # Empty squares
                row_results.append(RecognitionResult(PieceType.EMPTY, 1.0))
        results.append(row_results)
    
    return results


def print_board_state(squares, results, title):
    """Print a visual representation of the board state."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print('=' * 70)
    print("\n  Row | Pieces in that row")
    print("  ----|" + "-" * 60)
    
    for row in range(8):
        pieces = []
        for col in range(8):
            result = results[row][col]
            if result.piece_type == PieceType.EMPTY:
                pieces.append(".")
            else:
                fen_char = result.to_fen_char()
                pieces.append(fen_char)
        
        brightness = np.mean(squares[row][0])
        print(f"   {row}  | {' '.join(pieces):40} (brightness: {brightness:.0f})")
    print()


def demonstrate_auto_detection():
    """Demonstrate automatic orientation detection and correction."""
    print("\n" + "=" * 70)
    print("SCENARIO: Image with BLACK pieces at bottom (black's perspective)")
    print("=" * 70)
    
    # Create test data
    detector = BoardDetector()
    recognizer = PieceRecognizer()
    
    squares = create_mock_squares_with_black_at_bottom()
    results = create_mock_recognition_with_black_at_bottom()
    
    print_board_state(squares, results, "INITIAL STATE (as captured from image)")
    
    # Detect orientation
    detected = detector.detect_board_orientation(squares, results)
    print(f"Detected orientation: {detected.upper()}")
    print(f"Interpretation: {detected.upper()} pieces are at the bottom of the image")
    
    if detected == 'white':
        print("\n⚠️  DETECTION ERROR! The image actually has BLACK at bottom,")
        print("   but the system detected WHITE. This is the problem we're solving!")
        print("\n💡 SOLUTION: Use manual 'Black on Bottom' selector instead of 'Auto-detect'")
    
    # Simulate what the new code does
    if detected == 'black':
        print("\n→ System automatically flips the board data to normalize it...")
        squares_flipped = detector.flip_board(squares)
        
        # Flip results
        results_flipped = []
        for row in reversed(results):
            results_flipped.append(list(reversed(row)))
        
        print_board_state(squares_flipped, results_flipped, 
                        "AFTER AUTOMATIC NORMALIZATION")
        
        # Generate FEN
        fen = recognizer.results_to_fen(results_flipped)
        print(f"Generated FEN: {fen}")
        print("\nResult: Board is now in standard form!")
        print("  • Row 0 contains black pieces (rank 8)")
        print("  • Row 7 contains white pieces (rank 1)")
        print("  • FEN is correct!")


def demonstrate_manual_selection():
    """Demonstrate manual orientation selection."""
    print("\n" + "=" * 70)
    print("MANUAL ORIENTATION SELECTION FEATURE")
    print("=" * 70)
    
    print("\nThe control panel now has a dropdown with three options:")
    print("  1. Auto-detect (default) - System determines orientation")
    print("  2. White on Bottom - Tells system white pieces are at bottom")
    print("  3. Black on Bottom - Tells system black pieces are at bottom")
    
    print("\nWhen 'Black on Bottom' is selected:")
    print("  → System skips auto-detection")
    print("  → Automatically flips board data during processing")
    print("  → Normalizes data for correct FEN generation")
    print("  → User can still flip again using 'Flip Board' button to view from black's perspective")
    
    print("\nBenefit: User can correct orientation even if auto-detection fails!")


def main():
    """Run demonstrations."""
    print("\n" + "=" * 70)
    print("MANUAL ORIENTATION CORRECTION - DEMONSTRATION")
    print("=" * 70)
    
    demonstrate_auto_detection()
    demonstrate_manual_selection()
    
    print("\n" + "=" * 70)
    print("HOW TO USE IN THE GUI")
    print("=" * 70)
    print("""
1. Run the PySide6 GUI:
   python run_pyside6.py

2. Select the expected orientation (can be done before or after loading):
   • If you know the image has white on bottom: select "White on Bottom"
   • If you know the image has black on bottom: select "Black on Bottom"
   • If unsure: keep "Auto-detect" (default)

3. Load your chess board image

4. Click "Process Image"
   → System will automatically flip the data if needed
   → Board will be displayed in correct orientation

5. If the result is still wrong:
   • Try a different orientation setting in the dropdown
   • Click "Process Image" again (no need to reload)
   • OR use "Flip Board Orientation" button to rotate

6. Once satisfied, run "Engine Analysis" to get move suggestions
    """)
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
