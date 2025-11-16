"""
Move Suggester Module.

This module provides the MoveSuggester class for evaluating positions,
suggesting best moves, and explaining why moves are good.
"""

import chess
from typing import List, Tuple, Optional, Dict
import logging
from src.chess_engine.board_manager import BoardManager


class MoveEvaluation:
    """
    Data class to hold move evaluation information.
    
    Attributes:
        move (chess.Move): The chess move.
        score (float): Evaluation score (in centipawns).
        explanation (str): Human-readable explanation of why this move is good.
        tactical_themes (List[str]): Tactical themes present (fork, pin, etc.)
    """

    def __init__(
        self,
        move: chess.Move,
        score: float,
        explanation: str = "",
        tactical_themes: List[str] = None
    ):
        """
        Initialize a MoveEvaluation object.
        
        Args:
            move: The chess move being evaluated.
            score: Evaluation score (positive favors current player).
            explanation: Why this move is recommended.
            tactical_themes: List of tactical themes (e.g., "fork", "pin").
        """
        self.move = move
        self.score = score
        self.explanation = explanation
        self.tactical_themes = tactical_themes if tactical_themes else []

    def __str__(self) -> str:
        """
        Get string representation of the move evaluation.
        
        Returns:
            str: Human-readable description.
        """
        return f"{self.move.uci()}: {self.score:.2f} - {self.explanation}"


class MoveSuggester:
    """
    Suggests best moves and provides explanations.
    
    This class evaluates chess positions using a simplified evaluation function
    and suggests the best moves with explanations.
    
    Attributes:
        board_manager (BoardManager): The board manager instance.
        piece_values (Dict[int, int]): Material values for each piece type.
        logger (logging.Logger): Logger for the suggester.
    """

    # Standard piece values in centipawns
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def __init__(self, board_manager: BoardManager):
        """
        Initialize the MoveSuggester.
        
        Args:
            board_manager (BoardManager): The board manager to analyze.
        """
        self.board_manager = board_manager
        self.piece_values = self.PIECE_VALUES
        self.logger = logging.getLogger(__name__)

    def evaluate_position(self) -> float:
        """
        Evaluate the current position from the perspective of the side to move.
        
        This is a simplified evaluation based on material count and basic
        positional factors.
        
        Returns:
            float: Evaluation score in centipawns (positive = good for current player).
        """
        board = self.board_manager.get_board_state()
        
        # Check for checkmate and stalemate first
        if board.is_checkmate():
            # Current player is checkmated, very bad
            return -100000
        if board.is_stalemate():
            # Stalemate is a draw
            return 0
        
        # Calculate material balance
        material_score = 0
        current_color = board.turn
        
        for square, piece in board.piece_map().items():
            value = self.piece_values[piece.piece_type]
            
            # Add value if it's our piece, subtract if opponent's
            if piece.color == current_color:
                material_score += value
            else:
                material_score -= value
        
        # Add bonuses for positional factors
        positional_score = 0
        
        # Bonus for center control
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in center_squares:
            piece = board.piece_at(square)
            if piece and piece.color == current_color:
                positional_score += 30
        
        # Bonus for piece development (knights and bishops not on back rank)
        if current_color == chess.WHITE:
            back_rank_start, back_rank_end = 0, 8
        else:
            back_rank_start, back_rank_end = 56, 64
        
        for square, piece in board.piece_map().items():
            if piece.color == current_color:
                if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    if not (back_rank_start <= square < back_rank_end):
                        positional_score += 10
        
        # Check bonus/penalty
        if board.is_check():
            # Giving check is slightly favorable
            positional_score += 20
        
        # Mobility bonus (number of legal moves)
        mobility = len(list(board.legal_moves))
        positional_score += mobility * 2
        
        total_score = material_score + positional_score
        
        return total_score

    def analyze_move(self, move: chess.Move) -> MoveEvaluation:
        """
        Analyze a specific move and provide an evaluation with explanation.
        
        Args:
            move (chess.Move): The move to analyze.
            
        Returns:
            MoveEvaluation: Evaluation of the move with explanation.
        """
        board = self.board_manager.get_board_state()
        
        # Make the move temporarily
        board.push(move)
        
        # Evaluate the resulting position (negate because we switched sides)
        score = -self.evaluate_position()
        
        # Generate explanation
        explanation_parts = []
        tactical_themes = []
        
        # Check if move is a capture
        if board.is_capture(move):
            captured_square = move.to_square
            # Look at previous position for captured piece
            board.pop()
            captured_piece = board.piece_at(captured_square)
            board.push(move)
            
            if captured_piece:
                piece_name = chess.piece_name(captured_piece.piece_type)
                explanation_parts.append(f"Captures {piece_name}")
                tactical_themes.append("capture")
        
        # Check if move gives check
        if board.is_check():
            explanation_parts.append("Gives check")
            tactical_themes.append("check")
            
            if board.is_checkmate():
                explanation_parts.append("CHECKMATE!")
                tactical_themes.append("checkmate")
        
        # Check if move develops a piece
        moving_piece = board.piece_at(move.to_square)
        if moving_piece and moving_piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            # Check if moving from back rank
            current_color = not board.turn  # Because we made the move
            if current_color == chess.WHITE:
                if 0 <= move.from_square < 8:
                    explanation_parts.append("Develops piece")
                    tactical_themes.append("development")
            else:
                if 56 <= move.from_square < 64:
                    explanation_parts.append("Develops piece")
                    tactical_themes.append("development")
        
        # Check if move controls center
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        if move.to_square in center_squares:
            explanation_parts.append("Controls center")
            tactical_themes.append("center_control")
        
        # Check if move attacks multiple pieces (potential fork)
        attacks_after = board.attacks(move.to_square)
        attacked_pieces = []
        for target_square in attacks_after:
            target_piece = board.piece_at(target_square)
            if target_piece and target_piece.color != moving_piece.color:
                attacked_pieces.append(target_piece)
        
        if len(attacked_pieces) >= 2:
            explanation_parts.append(f"Attacks {len(attacked_pieces)} pieces")
            tactical_themes.append("fork")
        
        # Undo the move
        board.pop()
        
        # Construct explanation
        if explanation_parts:
            explanation = "; ".join(explanation_parts)
        else:
            explanation = "Improves position"
        
        return MoveEvaluation(
            move=move,
            score=score,
            explanation=explanation,
            tactical_themes=tactical_themes
        )

    def get_best_moves(self, num_moves: int = 3) -> List[MoveEvaluation]:
        """
        Get the best moves in the current position with explanations.
        
        Args:
            num_moves (int): Number of best moves to return.
            
        Returns:
            List[MoveEvaluation]: List of best moves with evaluations.
        """
        board = self.board_manager.get_board_state()
        legal_moves = list(board.legal_moves)
        
        if not legal_moves:
            self.logger.warning("No legal moves available")
            return []
        
        # Analyze all legal moves
        move_evaluations = []
        for move in legal_moves:
            evaluation = self.analyze_move(move)
            move_evaluations.append(evaluation)
        
        # Sort by score (best first)
        move_evaluations.sort(key=lambda x: x.score, reverse=True)
        
        # Return top N moves
        best_moves = move_evaluations[:num_moves]
        
        self.logger.info(f"Found {len(best_moves)} best moves")
        for i, eval in enumerate(best_moves, 1):
            self.logger.info(f"  {i}. {eval}")
        
        return best_moves

    def get_best_move_with_explanation(self) -> Optional[Tuple[chess.Move, str]]:
        """
        Get the single best move with a detailed explanation.
        
        Returns:
            Optional[Tuple[chess.Move, str]]: Tuple of (best_move, explanation)
                                              or None if no legal moves.
        """
        best_moves = self.get_best_moves(num_moves=1)
        
        if not best_moves:
            return None
        
        best_eval = best_moves[0]
        
        # Create detailed explanation
        move_notation = best_eval.move.uci()
        explanation = f"Best move: {move_notation}\n"
        explanation += f"Evaluation: {best_eval.score:.2f}\n"
        explanation += f"Reason: {best_eval.explanation}\n"
        
        if best_eval.tactical_themes:
            explanation += f"Themes: {', '.join(best_eval.tactical_themes)}"
        
        return (best_eval.move, explanation)

    def compare_moves(self, move1: chess.Move, move2: chess.Move) -> str:
        """
        Compare two moves and explain which is better.
        
        Args:
            move1 (chess.Move): First move to compare.
            move2 (chess.Move): Second move to compare.
            
        Returns:
            str: Explanation of which move is better and why.
        """
        eval1 = self.analyze_move(move1)
        eval2 = self.analyze_move(move2)
        
        comparison = f"Move 1 ({move1.uci()}): {eval1.score:.2f} - {eval1.explanation}\n"
        comparison += f"Move 2 ({move2.uci()}): {eval2.score:.2f} - {eval2.explanation}\n\n"
        
        if eval1.score > eval2.score:
            diff = eval1.score - eval2.score
            comparison += f"Move 1 is better by {diff:.2f} points"
        elif eval2.score > eval1.score:
            diff = eval2.score - eval1.score
            comparison += f"Move 2 is better by {diff:.2f} points"
        else:
            comparison += "Both moves are equally good"
        
        return comparison
