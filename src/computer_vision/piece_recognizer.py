"""
Piece Recognizer Module.

This module provides the PieceRecognizer class for recognizing chess pieces
from board square images using computer vision and template matching.
"""

import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
import logging
import chess
from enum import Enum


class PieceType(Enum):
    """
    Enumeration of chess piece types with their symbols.
    
    These map to chess.Piece types for compatibility with python-chess library.
    """
    WHITE_PAWN = ('P', chess.PAWN, chess.WHITE)
    WHITE_KNIGHT = ('N', chess.KNIGHT, chess.WHITE)
    WHITE_BISHOP = ('B', chess.BISHOP, chess.WHITE)
    WHITE_ROOK = ('R', chess.ROOK, chess.WHITE)
    WHITE_QUEEN = ('Q', chess.QUEEN, chess.WHITE)
    WHITE_KING = ('K', chess.KING, chess.WHITE)
    BLACK_PAWN = ('p', chess.PAWN, chess.BLACK)
    BLACK_KNIGHT = ('n', chess.KNIGHT, chess.BLACK)
    BLACK_BISHOP = ('b', chess.BISHOP, chess.BLACK)
    BLACK_ROOK = ('r', chess.ROOK, chess.BLACK)
    BLACK_QUEEN = ('q', chess.QUEEN, chess.BLACK)
    BLACK_KING = ('k', chess.KING, chess.BLACK)
    EMPTY = ('.', None, None)


class RecognitionResult:
    """
    Data class to hold piece recognition results.
    
    Attributes:
        piece_type (Optional[PieceType]): Recognized piece type.
        confidence (float): Confidence score (0-1).
        alternatives (List[Tuple[PieceType, float]]): Alternative pieces with scores.
    """

    def __init__(
        self,
        piece_type: Optional[PieceType],
        confidence: float,
        alternatives: List[Tuple[PieceType, float]] = None
    ):
        """
        Initialize a RecognitionResult.
        
        Args:
            piece_type: The recognized piece type.
            confidence: Confidence score (0.0 to 1.0).
            alternatives: List of alternative pieces with their confidence scores.
        """
        self.piece_type = piece_type
        self.confidence = confidence
        self.alternatives = alternatives if alternatives else []

    def to_fen_char(self) -> str:
        """
        Convert the recognized piece to FEN notation character.
        
        Returns:
            str: FEN character ('P', 'n', 'K', etc.) or '.' for empty.
        """
        if self.piece_type:
            return self.piece_type.value[0]
        return '.'

    def to_chess_piece(self) -> Optional[chess.Piece]:
        """
        Convert to python-chess Piece object.
        
        Returns:
            Optional[chess.Piece]: chess.Piece object or None for empty square.
        """
        if self.piece_type and self.piece_type != PieceType.EMPTY:
            symbol, piece_type, color = self.piece_type.value
            return chess.Piece(piece_type, color)
        return None

    def __str__(self) -> str:
        """
        Get string representation.
        
        Returns:
            str: Human-readable description.
        """
        if self.piece_type == PieceType.EMPTY:
            return f"Empty square (confidence: {self.confidence:.2f})"
        
        piece_name = self.piece_type.name.replace('_', ' ').title()
        return f"{piece_name} (confidence: {self.confidence:.2f})"


class PieceRecognizer:
    """
    Recognizes chess pieces from square images.
    
    This class uses computer vision techniques including color analysis,
    edge detection, and pattern matching to identify pieces.
    
    Attributes:
        logger (logging.Logger): Logger for the recognizer.
        min_confidence (float): Minimum confidence threshold for recognition.
    """

    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize the PieceRecognizer.
        
        Args:
            min_confidence (float): Minimum confidence to accept a recognition.
        """
        self.logger = logging.getLogger(__name__)
        self.min_confidence = min_confidence

    def analyze_square_features(self, square_image: np.ndarray) -> Dict[str, float]:
        """
        Extract features from a square image for piece recognition.
        
        This method analyzes various features like pixel intensity, edges,
        and color distribution to help identify pieces.
        
        Args:
            square_image (np.ndarray): Image of a single chess square.
            
        Returns:
            Dict[str, float]: Dictionary of feature values.
        """
        features = {}
        
        # Convert to different color spaces for analysis
        gray = cv2.cvtColor(square_image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(square_image, cv2.COLOR_BGR2HSV)
        
        # Feature 1: Average brightness
        features['avg_brightness'] = np.mean(gray)
        
        # Feature 2: Brightness variance (helps detect if square has content)
        features['brightness_variance'] = np.var(gray)
        
        # Feature 3: Edge density (pieces have more edges than empty squares)
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = np.sum(edges > 0) / edges.size
        
        # Feature 4: Dark pixel ratio (pieces are generally darker)
        dark_threshold = 100
        features['dark_pixel_ratio'] = np.sum(gray < dark_threshold) / gray.size
        
        # Feature 5: Color saturation (helps distinguish colored boards/pieces)
        features['avg_saturation'] = np.mean(hsv[:, :, 1])
        
        # Feature 6: Center region darkness (pieces occupy center)
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        features['center_darkness'] = np.mean(center_region < dark_threshold)
        
        return features

    def is_square_empty(self, square_image: np.ndarray) -> Tuple[bool, float]:
        """
        Determine if a square is empty or contains a piece.
        
        Uses feature analysis to detect presence of a chess piece.
        
        Args:
            square_image (np.ndarray): Image of a chess square.
            
        Returns:
            Tuple[bool, float]: (is_empty, confidence)
        """
        features = self.analyze_square_features(square_image)
        
        # Heuristics for empty square detection
        # Empty squares typically have:
        # - Low edge density
        # - Low brightness variance
        # - Uniform color
        
        empty_score = 0.0
        
        # Low edge density suggests empty
        if features['edge_density'] < 0.1:
            empty_score += 0.4
        
        # Low variance suggests uniform square
        if features['brightness_variance'] < 500:
            empty_score += 0.3
        
        # Low center darkness suggests no piece
        if features['center_darkness'] < 0.3:
            empty_score += 0.3
        
        is_empty = empty_score > 0.5
        confidence = empty_score if is_empty else (1.0 - empty_score)
        
        return (is_empty, confidence)

    def estimate_piece_color(self, square_image: np.ndarray) -> Tuple[Optional[chess.Color], float]:
        """
        Estimate whether a piece is white or black.
        
        Args:
            square_image (np.ndarray): Image of a square with a piece.
            
        Returns:
            Tuple[Optional[chess.Color], float]: (color, confidence)
        """
        gray = cv2.cvtColor(square_image, cv2.COLOR_BGR2GRAY)
        
        # Extract center region where piece is likely located
        h, w = gray.shape
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate average brightness of the piece region
        avg_brightness = np.mean(center_region)
        
        # Determine color based on brightness
        # White pieces are typically brighter than black pieces
        if avg_brightness > 150:
            return (chess.WHITE, 0.7)
        elif avg_brightness < 100:
            return (chess.BLACK, 0.7)
        else:
            # Medium brightness - less confident
            if avg_brightness > 125:
                return (chess.WHITE, 0.5)
            else:
                return (chess.BLACK, 0.5)

    def estimate_piece_type(
        self,
        square_image: np.ndarray,
        piece_color: chess.Color
    ) -> Tuple[Optional[int], float]:
        """
        Estimate the type of piece (pawn, knight, etc.).
        
        This is a simplified heuristic approach. In a production system,
        this would use machine learning or template matching.
        
        Args:
            square_image (np.ndarray): Image of a square with a piece.
            piece_color (chess.Color): The color of the piece.
            
        Returns:
            Tuple[Optional[int], float]: (piece_type, confidence)
        """
        features = self.analyze_square_features(square_image)
        
        # This is a simplified heuristic approach
        # In a real system, you would use ML models or template matching
        
        # For now, we'll use edge complexity as a rough indicator
        edge_density = features['edge_density']
        
        # Rough heuristic mapping (not accurate, just placeholder)
        if edge_density < 0.15:
            # Simple shape - possibly pawn
            return (chess.PAWN, 0.4)
        elif edge_density < 0.25:
            # Medium complexity - rook or bishop
            return (chess.ROOK, 0.4)
        elif edge_density < 0.35:
            # More complex - knight or bishop
            return (chess.KNIGHT, 0.4)
        else:
            # Most complex - queen or king
            return (chess.QUEEN, 0.4)

    def recognize_piece(self, square_image: np.ndarray) -> RecognitionResult:
        """
        Recognize a chess piece from a square image.
        
        This method combines multiple detection techniques to identify
        the piece type with a confidence score.
        
        Args:
            square_image (np.ndarray): Image of a single chess square.
            
        Returns:
            RecognitionResult: Recognition result with confidence and alternatives.
        """
        # First, check if square is empty
        is_empty, empty_confidence = self.is_square_empty(square_image)
        
        if is_empty and empty_confidence > self.min_confidence:
            return RecognitionResult(
                piece_type=PieceType.EMPTY,
                confidence=empty_confidence
            )
        
        # If not empty, try to identify the piece
        piece_color, color_confidence = self.estimate_piece_color(square_image)
        piece_type, type_confidence = self.estimate_piece_type(square_image, piece_color)
        
        # Combine confidences
        overall_confidence = (color_confidence + type_confidence) / 2
        
        # Map to PieceType enum
        piece_enum = None
        for pt in PieceType:
            if pt != PieceType.EMPTY:
                symbol, p_type, p_color = pt.value
                if p_type == piece_type and p_color == piece_color:
                    piece_enum = pt
                    break
        
        # If confidence is too low, mark as unknown (empty with low confidence)
        if overall_confidence < self.min_confidence:
            self.logger.warning(f"Low confidence recognition: {overall_confidence:.2f}")
            piece_enum = None
        
        return RecognitionResult(
            piece_type=piece_enum,
            confidence=overall_confidence
        )

    def recognize_board(
        self,
        squares: List[List[np.ndarray]]
    ) -> List[List[RecognitionResult]]:
        """
        Recognize all pieces on a chess board.
        
        Args:
            squares (List[List[np.ndarray]]): 8x8 grid of square images.
            
        Returns:
            List[List[RecognitionResult]]: 8x8 grid of recognition results.
        """
        results = []
        
        for row_idx, row in enumerate(squares):
            row_results = []
            for col_idx, square in enumerate(row):
                result = self.recognize_piece(square)
                row_results.append(result)
                
                # Log recognition
                square_name = chess.square_name(
                    chess.square(col_idx, 7 - row_idx)
                )
                self.logger.debug(f"{square_name}: {result}")
            
            results.append(row_results)
        
        self.logger.info("Board recognition complete")
        return results

    def results_to_fen(self, results: List[List[RecognitionResult]]) -> str:
        """
        Convert recognition results to FEN notation.
        
        Args:
            results (List[List[RecognitionResult]]): 8x8 grid of results.
            
        Returns:
            str: FEN string representing the board position (piece placement only).
        """
        fen_rows = []
        
        for row in results:
            fen_row = ""
            empty_count = 0
            
            for result in row:
                if result.piece_type == PieceType.EMPTY or result.piece_type is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += result.to_fen_char()
            
            # Add remaining empty squares
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Join rows with '/' and add default game state
        # (white to move, all castling available, no en passant, etc.)
        fen = '/'.join(fen_rows) + ' w KQkq - 0 1'
        
        return fen
