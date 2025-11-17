"""
Piece Correction Dialog for Chess Engine GUI.

This module provides a dialog for users to correct or confirm piece recognition.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QButtonGroup, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import chess
from typing import Optional

from src.computer_vision.piece_recognizer import PieceType


class PieceCorrectionDialog(QDialog):
    """
    Dialog for correcting piece recognition.
    
    Allows users to select the correct piece for a square,
    or confirm that the square is empty.
    
    Signals:
        piece_selected: Emitted when user confirms a piece selection.
                       Args: (PieceType or None for empty)
    """
    
    piece_selected = Signal(object)  # PieceType or None
    
    def __init__(self, square_name: str, current_piece: Optional[PieceType], 
                 confidence: float, parent=None):
        """
        Initialize the piece correction dialog.
        
        Args:
            square_name (str): Chess square name (e.g., 'e4').
            current_piece (Optional[PieceType]): Currently recognized piece.
            confidence (float): Recognition confidence score.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.square_name = square_name
        self.current_piece = current_piece
        self.confidence = confidence
        self.selected_piece = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Correct Piece on {self.square_name.upper()}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Header with current recognition
        header = QLabel(f"Square: {self.square_name.upper()}")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Current recognition display
        if self.current_piece == PieceType.EMPTY:
            piece_name = "Empty Square"
        elif self.current_piece is None:
            piece_name = "Unknown"
        else:
            piece_name = self.current_piece.name.replace('_', ' ').title()
        
        current_label = QLabel(
            f"Current Recognition: {piece_name}\n"
            f"Confidence: {self.confidence:.1%}"
        )
        current_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(current_label)
        
        layout.addSpacing(10)
        
        # Instruction
        instruction = QLabel("Please select the correct piece:")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)
        
        layout.addSpacing(10)
        
        # Piece selection buttons
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # White pieces group
        white_group = QGroupBox("White Pieces")
        white_layout = QGridLayout(white_group)
        white_pieces = [
            ('♔', 'King', PieceType.WHITE_KING),
            ('♕', 'Queen', PieceType.WHITE_QUEEN),
            ('♖', 'Rook', PieceType.WHITE_ROOK),
            ('♗', 'Bishop', PieceType.WHITE_BISHOP),
            ('♘', 'Knight', PieceType.WHITE_KNIGHT),
            ('♙', 'Pawn', PieceType.WHITE_PAWN),
        ]
        
        for i, (symbol, name, piece_type) in enumerate(white_pieces):
            btn = QPushButton(f"{symbol}\n{name}")
            btn.setMinimumSize(80, 60)
            btn.setCheckable(True)
            btn.setProperty('piece_type', piece_type)
            self.button_group.addButton(btn)
            white_layout.addWidget(btn, i // 3, i % 3)
        
        layout.addWidget(white_group)
        
        # Black pieces group
        black_group = QGroupBox("Black Pieces")
        black_layout = QGridLayout(black_group)
        black_pieces = [
            ('♚', 'King', PieceType.BLACK_KING),
            ('♛', 'Queen', PieceType.BLACK_QUEEN),
            ('♜', 'Rook', PieceType.BLACK_ROOK),
            ('♝', 'Bishop', PieceType.BLACK_BISHOP),
            ('♞', 'Knight', PieceType.BLACK_KNIGHT),
            ('♟', 'Pawn', PieceType.BLACK_PAWN),
        ]
        
        for i, (symbol, name, piece_type) in enumerate(black_pieces):
            btn = QPushButton(f"{symbol}\n{name}")
            btn.setMinimumSize(80, 60)
            btn.setCheckable(True)
            btn.setProperty('piece_type', piece_type)
            self.button_group.addButton(btn)
            black_layout.addWidget(btn, i // 3, i % 3)
        
        layout.addWidget(black_group)
        
        # Empty square button
        empty_btn = QPushButton("Empty Square")
        empty_btn.setMinimumHeight(40)
        empty_btn.setCheckable(True)
        empty_btn.setProperty('piece_type', PieceType.EMPTY)
        self.button_group.addButton(empty_btn)
        layout.addWidget(empty_btn)
        
        layout.addSpacing(10)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        confirm_btn = QPushButton("Confirm Selection")
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._on_confirm)
        button_layout.addWidget(confirm_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Pre-select current piece if available
        if self.current_piece is not None:
            for btn in self.button_group.buttons():
                if btn.property('piece_type') == self.current_piece:
                    btn.setChecked(True)
                    break
    
    def _on_confirm(self):
        """Handle confirm button click."""
        checked_button = self.button_group.checkedButton()
        if checked_button is None:
            # No selection made
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a piece or 'Empty Square' before confirming."
            )
            return
        
        self.selected_piece = checked_button.property('piece_type')
        self.piece_selected.emit(self.selected_piece)
        self.accept()
    
    def get_selected_piece(self) -> Optional[PieceType]:
        """
        Get the selected piece type.
        
        Returns:
            Optional[PieceType]: Selected piece type or None if cancelled.
        """
        return self.selected_piece
