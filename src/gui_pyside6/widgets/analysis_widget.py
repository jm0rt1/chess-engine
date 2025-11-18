"""
Engine Analysis Widget for Chess Engine GUI.

This module provides visualization of chess engine analysis including
threat maps and best move suggestions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QTabWidget, QGraphicsEllipseItem
)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPainter
import chess
from typing import Optional, List


class EngineAnalysisWidget(QWidget):
    """
    Widget for displaying chess engine analysis.
    
    Shows:
    - Threat map visualization
    - Best move suggestions with arrows
    - Move explanations
    - Tactical themes
    
    Attributes:
        board_manager: Chess board manager instance.
        threat_analysis: Threat analysis results.
        best_moves: List of best move suggestions.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the engine analysis widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.board_manager = None
        self.threat_analysis = None
        self.best_moves = None
        self.board_orientation = 'white'  # Track board orientation for coordinate labels
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Chess Engine Analysis")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Threat Map Tab
        threat_widget = QWidget()
        threat_layout = QVBoxLayout(threat_widget)
        
        self.threat_board_view = QGraphicsView()
        self.threat_board_scene = QGraphicsScene()
        self.threat_board_view.setScene(self.threat_board_scene)
        self.threat_board_view.setMinimumSize(500, 500)
        threat_layout.addWidget(self.threat_board_view)
        
        self.tab_widget.addTab(threat_widget, "Threat Map")
        
        # Best Moves Tab
        moves_widget = QWidget()
        moves_layout = QVBoxLayout(moves_widget)
        
        self.moves_board_view = QGraphicsView()
        self.moves_board_scene = QGraphicsScene()
        self.moves_board_view.setScene(self.moves_board_scene)
        self.moves_board_view.setMinimumSize(500, 500)
        moves_layout.addWidget(self.moves_board_view)
        
        self.tab_widget.addTab(moves_widget, "Best Moves")
        
        # Analysis Text Tab
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        # Threat analysis text
        threat_label = QLabel("Threat Analysis:")
        threat_label_font = QFont()
        threat_label_font.setBold(True)
        threat_label.setFont(threat_label_font)
        text_layout.addWidget(threat_label)
        
        self.threat_text = QTextEdit()
        self.threat_text.setReadOnly(True)
        text_layout.addWidget(self.threat_text)
        
        # Move suggestions text
        moves_label = QLabel("Best Moves:")
        moves_label.setFont(threat_label_font)
        text_layout.addWidget(moves_label)
        
        self.moves_text = QTextEdit()
        self.moves_text.setReadOnly(True)
        text_layout.addWidget(self.moves_text)
        
        self.tab_widget.addTab(text_widget, "Detailed Analysis")
        
        layout.addWidget(self.tab_widget)
    
    def _draw_board_base(self, scene: QGraphicsScene, square_size: int = 60):
        """
        Draw the base chess board.
        
        Args:
            scene (QGraphicsScene): Scene to draw on.
            square_size (int): Size of each square in pixels.
            
        Returns:
            int: Board size in pixels.
        """
        scene.clear()
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
                scene.addItem(rect)
                
                # Draw coordinate labels (adjust based on board orientation)
                if col == 0:
                    if self.board_orientation == 'white':
                        rank_label = QGraphicsTextItem(str(8 - row))
                    else:  # black orientation
                        rank_label = QGraphicsTextItem(str(row + 1))
                    rank_label.setPos(2, row * square_size + 2)
                    rank_label.setDefaultTextColor(QColor(0, 0, 0))
                    scene.addItem(rank_label)
                
                if row == 7:
                    if self.board_orientation == 'white':
                        file_label = QGraphicsTextItem(chr(ord('a') + col))
                    else:  # black orientation
                        file_label = QGraphicsTextItem(chr(ord('h') - col))
                    file_label.setPos(col * square_size + square_size - 15, 
                                     row * square_size + square_size - 20)
                    file_label.setDefaultTextColor(QColor(0, 0, 0))
                    scene.addItem(file_label)
        
        # Draw pieces
        if self.board_manager:
            piece_map = self.board_manager.get_piece_map()
            for square, piece in piece_map.items():
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                
                # Draw piece
                piece_text = self._get_piece_symbol(piece)
                piece_item = QGraphicsTextItem(piece_text)
                
                font = QFont("Arial", 36)
                piece_item.setFont(font)
                
                piece_item.setPos(
                    col * square_size + square_size // 2 - 15,
                    row * square_size + square_size // 2 - 25
                )
                
                scene.addItem(piece_item)
        
        scene.setSceneRect(0, 0, board_size, board_size)
        return board_size
    
    def _get_piece_symbol(self, piece: chess.Piece) -> str:
        """
        Get Unicode symbol for a chess piece.
        
        Args:
            piece (chess.Piece): Chess piece.
            
        Returns:
            str: Unicode symbol.
        """
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
    
    def _draw_threat_map(self):
        """Draw the threat map visualization."""
        square_size = 60
        self._draw_board_base(self.threat_board_scene, square_size)
        
        if not self.board_manager:
            return
        
        # Highlight attacked squares
        for square in range(64):
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            
            # Check if square is attacked by white
            white_attackers = self.board_manager.get_attackers(square, chess.WHITE)
            # Check if square is attacked by black
            black_attackers = self.board_manager.get_attackers(square, chess.BLACK)
            
            if white_attackers and black_attackers:
                # Both colors attack - show purple
                color = QColor(128, 0, 128, 100)
            elif white_attackers:
                # White attacks - show light red
                color = QColor(255, 100, 100, 100)
            elif black_attackers:
                # Black attacks - show dark red
                color = QColor(139, 0, 0, 100)
            else:
                continue
            
            # Draw highlight
            highlight = QGraphicsRectItem(
                col * square_size,
                row * square_size,
                square_size,
                square_size
            )
            highlight.setBrush(QBrush(color))
            highlight.setPen(QPen(Qt.NoPen))
            self.threat_board_scene.addItem(highlight)
        
        # Highlight pieces under attack (hanging pieces)
        piece_map = self.board_manager.get_piece_map()
        for square, piece in piece_map.items():
            attackers = self.board_manager.get_attackers(square, not piece.color)
            defenders = self.board_manager.get_attackers(square, piece.color)
            
            # If attacked and not defended (or underdefended), highlight
            if len(attackers) > 0 and len(defenders) == 0:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                
                # Draw circle around hanging piece
                circle = QGraphicsEllipseItem(
                    col * square_size + 5,
                    row * square_size + 5,
                    square_size - 10,
                    square_size - 10
                )
                circle.setPen(QPen(QColor(255, 0, 0), 3))
                circle.setBrush(QBrush(Qt.NoBrush))
                self.threat_board_scene.addItem(circle)
        
        self.threat_board_view.fitInView(self.threat_board_scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _draw_best_moves(self):
        """Draw the best moves visualization with arrows."""
        square_size = 60
        self._draw_board_base(self.moves_board_scene, square_size)
        
        if not self.best_moves:
            return
        
        # Draw arrows for top moves
        colors = [
            QColor(0, 200, 0, 200),      # Green for best move
            QColor(100, 150, 255, 180),  # Blue for second
            QColor(255, 200, 0, 160),    # Yellow for third
            QColor(255, 150, 100, 140),  # Orange for fourth
            QColor(200, 100, 200, 120),  # Purple for fifth
        ]
        
        for i, move_eval in enumerate(self.best_moves[:5]):
            move = move_eval.move
            color = colors[i] if i < len(colors) else QColor(150, 150, 150, 100)
            
            # Get from and to squares
            from_square = move.from_square
            to_square = move.to_square
            
            from_col = chess.square_file(from_square)
            from_row = 7 - chess.square_rank(from_square)
            to_col = chess.square_file(to_square)
            to_row = 7 - chess.square_rank(to_square)
            
            # Calculate arrow positions (center of squares)
            from_x = from_col * square_size + square_size // 2
            from_y = from_row * square_size + square_size // 2
            to_x = to_col * square_size + square_size // 2
            to_y = to_row * square_size + square_size // 2
            
            # Draw arrow line
            line = QGraphicsLineItem(from_x, from_y, to_x, to_y)
            pen = QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            line.setPen(pen)
            self.moves_board_scene.addItem(line)
            
            # Draw arrow head
            self._draw_arrow_head(self.moves_board_scene, from_x, from_y, to_x, to_y, color)
            
            # Add move rank label
            label = QGraphicsTextItem(str(i + 1))
            label_font = QFont("Arial", 14, QFont.Bold)
            label.setFont(label_font)
            label.setDefaultTextColor(color.darker(150))
            label.setPos(to_x - 8, to_y - 30)
            self.moves_board_scene.addItem(label)
        
        self.moves_board_view.fitInView(self.moves_board_scene.sceneRect(), Qt.KeepAspectRatio)
    
    def _draw_arrow_head(self, scene: QGraphicsScene, 
                         from_x: float, from_y: float,
                         to_x: float, to_y: float, color: QColor):
        """
        Draw an arrow head at the end of a line.
        
        Args:
            scene (QGraphicsScene): Scene to draw on.
            from_x, from_y (float): Start coordinates.
            to_x, to_y (float): End coordinates.
            color (QColor): Arrow color.
        """
        import math
        
        # Calculate angle
        angle = math.atan2(to_y - from_y, to_x - from_x)
        
        # Arrow head size
        arrow_size = 15
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrow head points
        point1_x = to_x - arrow_size * math.cos(angle - arrow_angle)
        point1_y = to_y - arrow_size * math.sin(angle - arrow_angle)
        point2_x = to_x - arrow_size * math.cos(angle + arrow_angle)
        point2_y = to_y - arrow_size * math.sin(angle + arrow_angle)
        
        # Draw arrow head lines
        line1 = QGraphicsLineItem(to_x, to_y, point1_x, point1_y)
        line1.setPen(QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        scene.addItem(line1)
        
        line2 = QGraphicsLineItem(to_x, to_y, point2_x, point2_y)
        line2.setPen(QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        scene.addItem(line2)
    
    def set_board_state(self, board_manager):
        """
        Set the board state.
        
        Args:
            board_manager: BoardManager instance.
        """
        self.board_manager = board_manager
        self._draw_threat_map()
        self._draw_best_moves()
    
    def set_threat_analysis(self, threat_summary: str):
        """
        Set threat analysis results.
        
        Args:
            threat_summary (str): Threat analysis text.
        """
        self.threat_analysis = threat_summary
        self.threat_text.setPlainText(threat_summary)
        self._draw_threat_map()
    
    def set_best_moves(self, best_moves: List):
        """
        Set best move suggestions.
        
        Args:
            best_moves (List): List of MoveEvaluation objects.
        """
        self.best_moves = best_moves
        
        # Format moves text
        moves_text = "=== BEST MOVES ===\n\n"
        
        if not best_moves:
            moves_text += "No legal moves available (game over)\n"
        else:
            for i, move_eval in enumerate(best_moves, 1):
                moves_text += f"{i}. Move: {move_eval.move.uci()}\n"
                moves_text += f"   Score: {move_eval.score:.2f}\n"
                moves_text += f"   Explanation: {move_eval.explanation}\n"
                
                if move_eval.tactical_themes:
                    themes = ", ".join(move_eval.tactical_themes)
                    moves_text += f"   Themes: {themes}\n"
                
                moves_text += "\n"
        
        self.moves_text.setPlainText(moves_text)
        self._draw_best_moves()
    
    def set_board_orientation(self, orientation: str):
        """
        Set the board orientation for coordinate labeling.
        
        Args:
            orientation (str): Board orientation ('white' or 'black').
        """
        self.board_orientation = orientation
        self._draw_threat_map()  # Redraw to update coordinate labels
        self._draw_best_moves()
    
    def clear(self):
        """Clear all analysis displays."""
        self.board_manager = None
        self.threat_analysis = None
        self.best_moves = None
        
        self.threat_board_scene.clear()
        self.moves_board_scene.clear()
        self.threat_text.clear()
        self.moves_text.clear()
