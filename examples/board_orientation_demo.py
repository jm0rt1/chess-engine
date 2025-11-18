"""
Demo script showing board orientation coordinate labeling.

This script demonstrates how coordinate labels change based on board orientation.
It doesn't require a GUI display and can be run in headless mode.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def print_board_coordinates(orientation='white'):
    """
    Print board coordinates for the given orientation.
    
    Args:
        orientation (str): 'white' or 'black'
    """
    print(f"\nBoard Orientation: {orientation.upper()} at bottom")
    print("=" * 50)
    
    # Print the board with coordinates
    print("\n    ", end="")
    
    # Print file labels (a-h) at top
    for col in range(8):
        if orientation == 'white':
            file_char = chr(ord('a') + col)
        else:  # black orientation
            file_char = chr(ord('h') - col)
        print(f" {file_char} ", end="")
    print()
    
    # Print each row with rank labels
    for row in range(8):
        # Calculate rank label based on orientation
        if orientation == 'white':
            rank = 8 - row
        else:  # black orientation
            rank = row + 1
        
        print(f" {rank}  ", end="")
        
        # Print squares (just placeholders)
        for col in range(8):
            is_light = (row + col) % 2 == 0
            square = "[ ]" if is_light else "[X]"
            print(square, end="")
        
        print(f"  {rank}")
    
    # Print file labels (a-h) at bottom
    print("\n    ", end="")
    for col in range(8):
        if orientation == 'white':
            file_char = chr(ord('a') + col)
        else:  # black orientation
            file_char = chr(ord('h') - col)
        print(f" {file_char} ", end="")
    print("\n")


def demonstrate_flip():
    """Demonstrate flipping between orientations."""
    print("\n" + "=" * 70)
    print("BOARD ORIENTATION COORDINATE LABELING DEMONSTRATION")
    print("=" * 70)
    
    print("\nThis demonstrates how coordinate labels (a-h, 1-8) change based on")
    print("board orientation when the flip board feature is used.")
    
    # Show white orientation
    print_board_coordinates('white')
    
    print("\n" + "-" * 70)
    print("After flipping the board orientation (Ctrl+F or Flip Board button):")
    print("-" * 70)
    
    # Show black orientation
    print_board_coordinates('black')
    
    print("\nKEY DIFFERENCES:")
    print("=" * 70)
    print("WHITE ORIENTATION (default):")
    print("  - Ranks: 8 at top, 1 at bottom (row 0 = rank 8)")
    print("  - Files: a-h from left to right (col 0 = file a)")
    print("\nBLACK ORIENTATION (after flip):")
    print("  - Ranks: 1 at top, 8 at bottom (row 0 = rank 1)")
    print("  - Files: h-a from left to right (col 0 = file h)")
    print("\nThis ensures coordinate labels match the flipped piece positions!")
    print("=" * 70)


def verify_coordinate_logic():
    """Verify coordinate calculation logic."""
    print("\n" + "=" * 70)
    print("COORDINATE CALCULATION VERIFICATION")
    print("=" * 70)
    
    print("\nWhite Orientation:")
    print("-" * 40)
    for row in range(8):
        rank = 8 - row
        print(f"  Row {row} -> Rank {rank}")
    print("\n  ", end="")
    for col in range(8):
        file_char = chr(ord('a') + col)
        print(f"Col {col}={file_char}  ", end="")
    
    print("\n\nBlack Orientation:")
    print("-" * 40)
    for row in range(8):
        rank = row + 1
        print(f"  Row {row} -> Rank {rank}")
    print("\n  ", end="")
    for col in range(8):
        file_char = chr(ord('h') - col)
        print(f"Col {col}={file_char}  ", end="")
    print("\n")


if __name__ == '__main__':
    demonstrate_flip()
    verify_coordinate_logic()
    
    print("\n" + "=" * 70)
    print("To test this feature in the GUI:")
    print("  1. Run: python run_pyside6.py")
    print("  2. Load a chess board image")
    print("  3. Click 'Process Image'")
    print("  4. Click 'Flip Board Orientation' or press Ctrl+F")
    print("  5. Observe that BOTH pieces AND coordinate labels flip!")
    print("=" * 70 + "\n")
