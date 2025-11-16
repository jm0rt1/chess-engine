"""
Board Manager Module.

This module provides the BoardManager class that manages the chess board state,
move validation, and game rules using the python-chess library.
"""

import chess
from typing import List, Optional, Tuple, Dict
import logging


class BoardManager:
    """
    Manages the chess board state and provides methods for move validation,
    generation, and board manipulation.
    
    This class wraps the python-chess Board class and provides additional
    functionality specific to our chess engine.
    
    Attributes:
        board (chess.Board): The underlying python-chess board representation.
        move_history (List[chess.Move]): History of moves made on the board.
    """

    def __init__(self, fen: Optional[str] = None):
        """
        Initialize the BoardManager.
        
        Args:
            fen (Optional[str]): FEN string representing initial board state.
                                If None, starts with standard chess starting position.
        """
        # Initialize the board with starting position or provided FEN
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
        
        # Keep track of move history for analysis
        self.move_history: List[chess.Move] = []
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"BoardManager initialized with FEN: {self.board.fen()}")

    def get_board_state(self) -> chess.Board:
        """
        Get the current board state.
        
        Returns:
            chess.Board: The current board object.
        """
        return self.board

    def get_fen(self) -> str:
        """
        Get the FEN (Forsyth-Edwards Notation) representation of current position.
        
        Returns:
            str: FEN string representing the current board state.
        """
        return self.board.fen()

    def set_position_from_fen(self, fen: str) -> bool:
        """
        Set the board position from a FEN string.
        
        Args:
            fen (str): FEN string to set the position to.
            
        Returns:
            bool: True if successful, False if invalid FEN.
        """
        try:
            self.board = chess.Board(fen)
            self.move_history.clear()
            self.logger.info(f"Board position set from FEN: {fen}")
            return True
        except ValueError as e:
            self.logger.error(f"Invalid FEN string: {fen}. Error: {e}")
            return False

    def get_piece_at(self, square: chess.Square) -> Optional[chess.Piece]:
        """
        Get the piece at a specific square.
        
        Args:
            square (chess.Square): The square to check (0-63).
            
        Returns:
            Optional[chess.Piece]: The piece at the square, or None if empty.
        """
        return self.board.piece_at(square)

    def get_legal_moves(self) -> List[chess.Move]:
        """
        Get all legal moves for the current position.
        
        Returns:
            List[chess.Move]: List of all legal moves.
        """
        return list(self.board.legal_moves)

    def is_legal_move(self, move: chess.Move) -> bool:
        """
        Check if a move is legal in the current position.
        
        Args:
            move (chess.Move): The move to check.
            
        Returns:
            bool: True if the move is legal, False otherwise.
        """
        return move in self.board.legal_moves

    def make_move(self, move: chess.Move) -> bool:
        """
        Make a move on the board.
        
        Args:
            move (chess.Move): The move to make.
            
        Returns:
            bool: True if move was made successfully, False if illegal.
        """
        if self.is_legal_move(move):
            self.board.push(move)
            self.move_history.append(move)
            self.logger.info(f"Move made: {move.uci()}")
            return True
        else:
            self.logger.warning(f"Illegal move attempted: {move.uci()}")
            return False

    def undo_move(self) -> Optional[chess.Move]:
        """
        Undo the last move made.
        
        Returns:
            Optional[chess.Move]: The move that was undone, or None if no moves to undo.
        """
        if self.move_history:
            move = self.board.pop()
            self.move_history.pop()
            self.logger.info(f"Move undone: {move.uci()}")
            return move
        return None

    def is_checkmate(self) -> bool:
        """
        Check if the current position is checkmate.
        
        Returns:
            bool: True if checkmate, False otherwise.
        """
        return self.board.is_checkmate()

    def is_stalemate(self) -> bool:
        """
        Check if the current position is stalemate.
        
        Returns:
            bool: True if stalemate, False otherwise.
        """
        return self.board.is_stalemate()

    def is_check(self) -> bool:
        """
        Check if the current side to move is in check.
        
        Returns:
            bool: True if in check, False otherwise.
        """
        return self.board.is_check()

    def is_game_over(self) -> bool:
        """
        Check if the game is over.
        
        Returns:
            bool: True if game is over, False otherwise.
        """
        return self.board.is_game_over()

    def get_turn(self) -> chess.Color:
        """
        Get whose turn it is to move.
        
        Returns:
            chess.Color: chess.WHITE or chess.BLACK.
        """
        return self.board.turn

    def get_piece_map(self) -> Dict[chess.Square, chess.Piece]:
        """
        Get a dictionary mapping squares to pieces.
        
        Returns:
            Dict[chess.Square, chess.Piece]: Dictionary of square -> piece.
        """
        return self.board.piece_map()

    def reset(self) -> None:
        """
        Reset the board to the starting position.
        """
        self.board.reset()
        self.move_history.clear()
        self.logger.info("Board reset to starting position")

    def get_attackers(self, square: chess.Square, color: chess.Color) -> List[chess.Square]:
        """
        Get all pieces of a given color that are attacking a square.
        
        Args:
            square (chess.Square): The square to check.
            color (chess.Color): The color of attacking pieces to find.
            
        Returns:
            List[chess.Square]: List of squares containing attacking pieces.
        """
        # Get all attackers of the specified color
        attackers = self.board.attackers(color, square)
        return list(attackers)

    def __str__(self) -> str:
        """
        Get a string representation of the board.
        
        Returns:
            str: ASCII art representation of the board.
        """
        return str(self.board)
