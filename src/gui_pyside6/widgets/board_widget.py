"""
Board Reconstruction Widget for Chess Engine GUI.

This module provides visualization of the reconstructed chess board
with detected pieces overlaid.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QPushButton
)
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPixmap, QImage
import chess
from typing import Optional, List
import numpy as np


class ClickableSquare(QGraphicsRectItem):
    """A clickable chess board square."""
    
    def __init__(self, row: int, col: int, square_size: float, widget):
        """
        Initialize a clickable square.
        
        Args:
            row: Board row (0-7).
            col: Board column (0-7).
            square_size: Size of the square in pixels.
            widget: Parent BoardReconstructionWidget instance.
        """
        super().__init__(
            col * square_size,
            row * square_size,
            square_size,
            square_size
        )
        self.row = row
        self.col = col
        self.widget = widget
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)
        self.hover_color = QColor(255, 255, 0, 100)  # Yellow highlight
        self.original_brush = None
    
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter."""
        self.original_brush = self.brush()
        # Add yellow tint
        highlight_brush = QBrush(self.hover_color)
        self.setBrush(highlight_brush)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave."""
        if self.original_brush:
            self.setBrush(self.original_brush)
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            square_name = chess.square_name(chess.square(self.col, 7 - self.row))
            self.widget.on_square_clicked(square_name, self.row, self.col)
        super().mousePressEvent(event)


class BoardReconstructionWidget(QWidget):
    """
    Widget for displaying reconstructed chess board.
    
    Shows:
    - Visual chess board with pieces
    - FEN notation
    - Board state information
    - Recognition confidence for each piece
    - Interactive piece correction (click on squares)
    
    Attributes:
        board_manager: Chess board manager instance.
        recognition_results: Results from piece recognition.
        
    Signals:
        piece_corrected: Emitted when user corrects a piece.
                        Args: (square_name, row, col, new_piece_type)
    """
    
    piece_corrected = Signal(str, int, int, object)  # square_name, row, col, PieceType
    
    def __init__(self, parent=None):
        """
        Initialize the board reconstruction widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.board_manager = None
        self.recognition_results = None
        self.correction_mode_enabled = False
        self.board_orientation = 'white'  # Track board orientation for coordinate labels
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and correction mode toggle
        title_layout = QHBoxLayout()
        
        title = QLabel("Board Reconstruction & Verification")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Correction mode toggle button
        self.correction_mode_btn = QPushButton("Enable Piece Correction")
        self.correction_mode_btn.setCheckable(True)
        self.correction_mode_btn.setToolTip("Click to enable/disable piece correction mode")
        self.correction_mode_btn.clicked.connect(self._toggle_correction_mode)
        title_layout.addWidget(self.correction_mode_btn)
        
        layout.addLayout(title_layout)
        
        # Instructions label
        self.instructions_label = QLabel("")
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.instructions_label.setStyleSheet("color: blue; font-weight: bold;")
        self.instructions_label.setVisible(False)
        layout.addWidget(self.instructions_label)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left: Visual board
        self.board_view = QGraphicsView()
        self.board_scene = QGraphicsScene()
        self.board_view.setScene(self.board_scene)
        self.board_view.setMinimumSize(500, 500)
        content_layout.addWidget(self.board_view)
        
        # Right: Board information
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # FEN display
        fen_label = QLabel("FEN Notation:")
        fen_label_font = QFont()
        fen_label_font.setBold(True)
        fen_label.setFont(fen_label_font)
        info_layout.addWidget(fen_label)
        
        self.fen_display = QTextEdit()
        self.fen_display.setReadOnly(True)
        self.fen_display.setMaximumHeight(80)
        info_layout.addWidget(self.fen_display)
        
        # Board state display
        state_label = QLabel("Board State:")
        state_label.setFont(fen_label_font)
        info_layout.addWidget(state_label)
        
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setMaximumHeight(150)
        info_layout.addWidget(self.state_display)
        
        # Recognition confidence
        confidence_label = QLabel("Recognition Confidence:")
        confidence_label.setFont(fen_label_font)
        info_layout.addWidget(confidence_label)
        
        self.confidence_display = QTextEdit()
        self.confidence_display.setReadOnly(True)
        info_layout.addWidget(self.confidence_display)
        
        content_layout.addWidget(info_widget)
        content_layout.setStretch(0, 2)
        content_layout.setStretch(1, 1)
        
        layout.addLayout(content_layout)
    
    def _toggle_correction_mode(self, checked: bool):
        """Toggle correction mode on/off."""
        self.correction_mode_enabled = checked
        
        if checked:
            self.correction_mode_btn.setText("Disable Piece Correction")
            self.instructions_label.setText("Click on any square to correct the piece")
            self.instructions_label.setVisible(True)
        else:
            self.correction_mode_btn.setText("Enable Piece Correction")
            self.instructions_label.setVisible(False)
        
        # Redraw board to update clickable state
        self._draw_board()
    
    def on_square_clicked(self, square_name: str, row: int, col: int):
        """
        Handle square click event.
        
        Args:
            square_name: Chess square name (e.g., 'e4').
            row: Board row (0-7).
            col: Board column (0-7).
        """
        if not self.correction_mode_enabled:
            return
        
        # Get current piece for this square
        current_piece = None
        confidence = 0.0
        
        if self.recognition_results and row < len(self.recognition_results):
            if col < len(self.recognition_results[row]):
                result = self.recognition_results[row][col]
                current_piece = result.piece_type
                confidence = result.confidence
        
        # Import here to avoid circular imports
        from .piece_correction_dialog import PieceCorrectionDialog
        
        # Show correction dialog
        dialog = PieceCorrectionDialog(square_name, current_piece, confidence, self)
        if dialog.exec():
            corrected_piece = dialog.get_selected_piece()
            if corrected_piece is not None:
                # Emit signal with correction
                self.piece_corrected.emit(square_name, row, col, corrected_piece)
    
    def _draw_board(self):
        """Draw the chess board with pieces."""
        self.board_scene.clear()
        
        if self.board_manager is None:
            return
        
        # Board dimensions
        square_size = 60
        board_size = square_size * 8
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = QColor(240, 217, 181) if is_light else QColor(181, 136, 99)
                
                # Draw square (clickable if correction mode is enabled)
                if self.correction_mode_enabled:
                    rect = ClickableSquare(row, col, square_size, self)
                    rect.setBrush(QBrush(color))
                    rect.setPen(QPen(Qt.NoPen))
                    self.board_scene.addItem(rect)
                else:
                    rect = QGraphicsRectItem(
                        col * square_size,
                        row * square_size,
                        square_size,
                        square_size
                    )
                    rect.setBrush(QBrush(color))
                    rect.setPen(QPen(Qt.NoPen))
                    self.board_scene.addItem(rect)
                
                # Draw coordinate labels (adjust based on board orientation)
                if col == 0:
                    if self.board_orientation == 'white':
                        rank_label = QGraphicsTextItem(str(8 - row))
                    else:  # black orientation
                        rank_label = QGraphicsTextItem(str(row + 1))
                    rank_label.setPos(2, row * square_size + 2)
                    rank_label.setDefaultTextColor(QColor(0, 0, 0))
                    self.board_scene.addItem(rank_label)
                
                if row == 7:
                    if self.board_orientation == 'white':
                        file_label = QGraphicsTextItem(chr(ord('a') + col))
                    else:  # black orientation
                        file_label = QGraphicsTextItem(chr(ord('h') - col))
                    file_label.setPos(col * square_size + square_size - 15, 
                                     row * square_size + square_size - 20)
                    file_label.setDefaultTextColor(QColor(0, 0, 0))
                    self.board_scene.addItem(file_label)
        
        # Draw pieces
        piece_map = self.board_manager.get_piece_map()
        for square, piece in piece_map.items():
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            
            # Draw piece as text (using Unicode chess symbols)
            piece_text = self._get_piece_symbol(piece)
            piece_item = QGraphicsTextItem(piece_text)
            
            # Set font
            font = QFont("Arial", 36)
            piece_item.setFont(font)
            
            # Position piece in center of square
            piece_item.setPos(
                col * square_size + square_size // 2 - 15,
                row * square_size + square_size // 2 - 25
            )
            
            self.board_scene.addItem(piece_item)
            
            # Add confidence indicator if available
            if self.recognition_results:
                confidence = self._get_confidence_for_square(row, col)
                if confidence is not None:
                    conf_text = QGraphicsTextItem(f"{confidence:.0%}")
                    conf_font = QFont("Arial", 8)
                    conf_text.setFont(conf_font)
                    conf_text.setPos(
                        col * square_size + 2,
                        row * square_size + square_size - 15
                    )
                    # Color based on confidence
                    if confidence > 0.8:
                        conf_text.setDefaultTextColor(QColor(0, 200, 0))
                    elif confidence > 0.5:
                        conf_text.setDefaultTextColor(QColor(255, 165, 0))
                    else:
                        conf_text.setDefaultTextColor(QColor(255, 0, 0))
                    self.board_scene.addItem(conf_text)
        
        # Set scene rect
        self.board_scene.setSceneRect(0, 0, board_size, board_size)
        self.board_view.fitInView(self.board_scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _get_piece_symbol(self, piece: chess.Piece) -> str:
        """
        Get Unicode symbol for a chess piece.
        
        Args:
            piece (chess.Piece): Chess piece.
            
        Returns:
            str: Unicode symbol.
        """
        # Unicode chess symbols
        symbols = {
            (chess.PAWN, chess.WHITE): '♙',
            (chess.KNIGHT, chess.WHITE): '♘',
            (chess.BISHOP, chess.WHITE): '♗',
            (chess.ROOK, chess.WHITE): '♖',
            (chess.QUEEN, chess.WHITE): '♕',
            (chess.KING, chess.WHITE): '♔',
            (chess.PAWN, chess.BLACK): '♟',
            (chess.KNIGHT, chess.BLACK): '♞',
            (chess.BISHOP, chess.BLACK): '♝',
            (chess.ROOK, chess.BLACK): '♜',
            (chess.QUEEN, chess.BLACK): '♛',
            (chess.KING, chess.BLACK): '♚',
        }
        return symbols.get((piece.piece_type, piece.color), '?')
    
    def _get_confidence_for_square(self, row: int, col: int) -> Optional[float]:
        """
        Get recognition confidence for a square.
        
        Args:
            row (int): Board row (0-7, from top).
            col (int): Board column (0-7, from left).
            
        Returns:
            Optional[float]: Confidence score or None.
        """
        if self.recognition_results and row < len(self.recognition_results):
            if col < len(self.recognition_results[row]):
                return self.recognition_results[row][col].confidence
        return None
    
    def set_board_state(self, board_manager):
        """
        Set the board state to display.
        
        Args:
            board_manager: BoardManager instance with current position.
        """
        self.board_manager = board_manager
        self._draw_board()
        self._update_info_displays()
    
    def set_recognition_results(self, results: List[List]):
        """
        Set piece recognition results.
        
        Args:
            results (List[List]): 8x8 grid of recognition results.
        """
        self.recognition_results = results
        self._draw_board()
        self._update_confidence_display()
    
    def set_board_orientation(self, orientation: str):
        """
        Set the board orientation for coordinate labeling.
        
        Args:
            orientation (str): Board orientation ('white' or 'black').
        """
        self.board_orientation = orientation
        self._draw_board()  # Redraw to update coordinate labels
    
    def _update_info_displays(self):
        """Update FEN and board state displays."""
        if self.board_manager is None:
            return
        
        # Update FEN
        fen = self.board_manager.get_fen()
        self.fen_display.setPlainText(fen)
        
        # Update board state
        state_text = str(self.board_manager) + "\n\n"
        
        # Add game status
        turn = "White" if self.board_manager.get_turn() == chess.WHITE else "Black"
        state_text += f"Turn: {turn}\n"
        
        if self.board_manager.is_checkmate():
            state_text += "Status: CHECKMATE\n"
        elif self.board_manager.is_check():
            state_text += "Status: CHECK\n"
        elif self.board_manager.is_stalemate():
            state_text += "Status: STALEMATE\n"
        else:
            state_text += "Status: Normal\n"
        
        self.state_display.setPlainText(state_text)
    
    def _update_confidence_display(self):
        """Update the confidence display."""
        if self.recognition_results is None:
            return
        
        confidence_text = "Recognition Confidence Summary:\n\n"
        
        # Calculate statistics
        all_confidences = []
        low_confidence_squares = []
        
        for row_idx, row in enumerate(self.recognition_results):
            for col_idx, result in enumerate(row):
                confidence = result.confidence
                all_confidences.append(confidence)
                
                if confidence < 0.7:
                    square_name = chess.square_name(
                        chess.square(col_idx, 7 - row_idx)
                    )
                    if result.piece_type is None:
                        piece_name = "Unknown"
                    elif result.piece_type.name == "EMPTY":
                        piece_name = "Empty"
                    else:
                        piece_name = result.piece_type.name
                    low_confidence_squares.append(
                        (square_name, piece_name, confidence)
                    )
        
        # Overall statistics
        avg_confidence = sum(all_confidences) / len(all_confidences)
        min_confidence = min(all_confidences)
        max_confidence = max(all_confidences)
        
        confidence_text += f"Average: {avg_confidence:.2%}\n"
        confidence_text += f"Range: {min_confidence:.2%} - {max_confidence:.2%}\n\n"
        
        # Low confidence warnings
        if low_confidence_squares:
            confidence_text += "Low Confidence Squares:\n"
            for square, piece, conf in low_confidence_squares:
                confidence_text += f"  {square}: {piece} ({conf:.2%})\n"
        else:
            confidence_text += "All squares recognized with high confidence!\n"
        
        self.confidence_display.setPlainText(confidence_text)
    
    def clear(self):
        """Clear the board display."""
        self.board_manager = None
        self.recognition_results = None
        self.board_scene.clear()
        self.fen_display.clear()
        self.state_display.clear()
        self.confidence_display.clear()
