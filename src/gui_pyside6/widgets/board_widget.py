"""
Board Reconstruction Widget for Chess Engine GUI.

This module provides visualization of the reconstructed chess board
with detected pieces overlaid.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPixmap, QImage
import chess
from typing import Optional, List
import numpy as np


class BoardReconstructionWidget(QWidget):
    """
    Widget for displaying reconstructed chess board.
    
    Shows:
    - Visual chess board with pieces
    - FEN notation
    - Board state information
    - Recognition confidence for each piece
    
    Attributes:
        board_manager: Chess board manager instance.
        recognition_results: Results from piece recognition.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the board reconstruction widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.board_manager = None
        self.recognition_results = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Board Reconstruction & Verification")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
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
                
                # Draw square
                rect = QGraphicsRectItem(
                    col * square_size,
                    row * square_size,
                    square_size,
                    square_size
                )
                rect.setBrush(QBrush(color))
                rect.setPen(QPen(Qt.NoPen))
                self.board_scene.addItem(rect)
                
                # Draw coordinate labels
                if col == 0:
                    rank_label = QGraphicsTextItem(str(8 - row))
                    rank_label.setPos(2, row * square_size + 2)
                    rank_label.setDefaultTextColor(QColor(0, 0, 0))
                    self.board_scene.addItem(rank_label)
                
                if row == 7:
                    file_label = QGraphicsTextItem(chr(ord('a') + col))
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
