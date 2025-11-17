"""
Threat Analyzer Module.

This module provides the ThreatAnalyzer class for analyzing threats,
attacks, and defensive possibilities on the chess board.
"""

import chess
from typing import List, Dict, Set, Tuple
import logging
from src.chess_engine.board_manager import BoardManager


class ThreatInfo:
    """
    Data class to hold information about a specific threat.
    
    Attributes:
        attacker_square (chess.Square): Square of the attacking piece.
        attacker_piece (chess.Piece): The attacking piece.
        target_square (chess.Square): Square being attacked.
        target_piece (Optional[chess.Piece]): The piece being attacked (if any).
        is_defended (bool): Whether the target is defended.
        defenders (List[chess.Square]): Squares of defending pieces.
    """

    def __init__(
        self,
        attacker_square: chess.Square,
        attacker_piece: chess.Piece,
        target_square: chess.Square,
        target_piece: chess.Piece = None,
        is_defended: bool = False,
        defenders: List[chess.Square] = None
    ):
        """
        Initialize a ThreatInfo object.
        
        Args:
            attacker_square: Square where the attacking piece is located.
            attacker_piece: The piece performing the attack.
            target_square: Square being attacked.
            target_piece: Piece being attacked (None if empty square).
            is_defended: Whether the target is defended.
            defenders: List of squares with defending pieces.
        """
        self.attacker_square = attacker_square
        self.attacker_piece = attacker_piece
        self.target_square = target_square
        self.target_piece = target_piece
        self.is_defended = is_defended
        self.defenders = defenders if defenders else []

    def __str__(self) -> str:
        """
        Get string representation of the threat.
        
        Returns:
            str: Human-readable description of the threat.
        """
        attacker_name = chess.piece_name(self.attacker_piece.piece_type).upper()
        target_name = chess.square_name(self.target_square)
        
        if self.target_piece:
            target_piece_name = chess.piece_name(self.target_piece.piece_type).upper()
            desc = f"{attacker_name} on {chess.square_name(self.attacker_square)} attacks {target_piece_name} on {target_name}"
        else:
            desc = f"{attacker_name} on {chess.square_name(self.attacker_square)} controls {target_name}"
        
        if self.is_defended:
            desc += f" (defended by {len(self.defenders)} piece(s))"
        
        return desc


class ThreatAnalyzer:
    """
    Analyzes threats and attacks on the chess board.
    
    This class provides methods to identify hanging pieces, pins, forks,
    and other tactical threats on the board.
    
    Attributes:
        board_manager (BoardManager): The board manager instance.
        logger (logging.Logger): Logger for the analyzer.
    """

    def __init__(self, board_manager: BoardManager):
        """
        Initialize the ThreatAnalyzer.
        
        Args:
            board_manager (BoardManager): The board manager to analyze.
        """
        self.board_manager = board_manager
        self.logger = logging.getLogger(__name__)

    def find_all_threats(self, for_color: chess.Color) -> List[ThreatInfo]:
        """
        Find all threats (attacks) from pieces of a given color.
        
        Args:
            for_color (chess.Color): Color of pieces to find attacks for.
            
        Returns:
            List[ThreatInfo]: List of all threat information.
        """
        threats = []
        board = self.board_manager.get_board_state()
        piece_map = board.piece_map()
        
        # Iterate through all pieces of the specified color
        for square, piece in piece_map.items():
            if piece.color == for_color:
                # Find all squares this piece attacks
                attacks = board.attacks(square)
                
                for target_square in attacks:
                    target_piece = board.piece_at(target_square)
                    
                    # Check if target is defended
                    opponent_color = not for_color
                    defenders = list(board.attackers(opponent_color, target_square))
                    is_defended = len(defenders) > 0
                    
                    # Create threat info
                    threat = ThreatInfo(
                        attacker_square=square,
                        attacker_piece=piece,
                        target_square=target_square,
                        target_piece=target_piece,
                        is_defended=is_defended,
                        defenders=defenders
                    )
                    threats.append(threat)
        
        return threats

    def find_hanging_pieces(self, for_color: chess.Color) -> List[ThreatInfo]:
        """
        Find all hanging (undefended) pieces of a given color.
        
        A hanging piece is one that is attacked but not defended.
        
        Args:
            for_color (chess.Color): Color of pieces to check.
            
        Returns:
            List[ThreatInfo]: List of threats to hanging pieces.
        """
        hanging = []
        board = self.board_manager.get_board_state()
        piece_map = board.piece_map()
        opponent_color = not for_color
        
        # Check each piece of the specified color
        for square, piece in piece_map.items():
            if piece.color == for_color:
                # Find all attackers
                attackers = list(board.attackers(opponent_color, square))
                
                if attackers:
                    # Check if defended
                    defenders = list(board.attackers(for_color, square))
                    
                    # If attacked but not defended, it's hanging
                    if not defenders:
                        # Create threat info for the first attacker
                        attacker_square = attackers[0]
                        attacker_piece = board.piece_at(attacker_square)
                        
                        threat = ThreatInfo(
                            attacker_square=attacker_square,
                            attacker_piece=attacker_piece,
                            target_square=square,
                            target_piece=piece,
                            is_defended=False,
                            defenders=[]
                        )
                        hanging.append(threat)
        
        return hanging

    def find_checks(self) -> List[ThreatInfo]:
        """
        Find all pieces giving check to the current player.
        
        Returns:
            List[ThreatInfo]: List of checking pieces and their info.
        """
        checks = []
        board = self.board_manager.get_board_state()
        
        # Only look for checks if the king is in check
        if not board.is_check():
            return checks
        
        current_color = board.turn
        king_square = board.king(current_color)
        opponent_color = not current_color
        
        # Find all pieces attacking the king
        attackers = list(board.attackers(opponent_color, king_square))
        
        for attacker_square in attackers:
            attacker_piece = board.piece_at(attacker_square)
            king_piece = board.piece_at(king_square)
            
            threat = ThreatInfo(
                attacker_square=attacker_square,
                attacker_piece=attacker_piece,
                target_square=king_square,
                target_piece=king_piece,
                is_defended=False,  # King is always "defended" by being able to move
                defenders=[]
            )
            checks.append(threat)
        
        return checks

    def analyze_position(self) -> Dict[str, any]:
        """
        Perform a comprehensive analysis of the current position.
        
        Returns:
            Dict[str, any]: Dictionary with analysis results including:
                - white_threats: Threats by white
                - black_threats: Threats by black
                - white_hanging: White's hanging pieces
                - black_hanging: Black's hanging pieces
                - checks: Pieces giving check (if any)
                - is_check: Whether current side is in check
                - is_checkmate: Whether current side is checkmated
                - is_stalemate: Whether position is stalemate
        """
        board = self.board_manager.get_board_state()
        
        analysis = {
            'white_threats': self.find_all_threats(chess.WHITE),
            'black_threats': self.find_all_threats(chess.BLACK),
            'white_hanging': self.find_hanging_pieces(chess.WHITE),
            'black_hanging': self.find_hanging_pieces(chess.BLACK),
            'checks': self.find_checks(),
            'is_check': board.is_check(),
            'is_checkmate': board.is_checkmate(),
            'is_stalemate': board.is_stalemate(),
            'current_turn': 'white' if board.turn == chess.WHITE else 'black'
        }
        
        self.logger.info(f"Position analysis complete. Turn: {analysis['current_turn']}")
        
        return analysis

    def get_threat_summary(self) -> str:
        """
        Get a human-readable summary of threats in the position.
        
        Returns:
            str: Summary text describing the main threats.
        """
        analysis = self.analyze_position()
        summary_lines = []
        
        # Add game state info
        if analysis['is_checkmate']:
            summary_lines.append("CHECKMATE!")
        elif analysis['is_check']:
            summary_lines.append("CHECK!")
        elif analysis['is_stalemate']:
            summary_lines.append("STALEMATE!")
        
        summary_lines.append(f"\nCurrent turn: {analysis['current_turn'].upper()}\n")
        
        # Add hanging pieces
        if analysis['white_hanging']:
            summary_lines.append("WHITE HANGING PIECES:")
            for threat in analysis['white_hanging']:
                summary_lines.append(f"  - {threat}")
        
        if analysis['black_hanging']:
            summary_lines.append("\nBLACK HANGING PIECES:")
            for threat in analysis['black_hanging']:
                summary_lines.append(f"  - {threat}")
        
        if not analysis['white_hanging'] and not analysis['black_hanging']:
            summary_lines.append("No hanging pieces found.")
        
        return "\n".join(summary_lines)
