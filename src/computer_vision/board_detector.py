"""
Board Detector Module.

This module provides the BoardDetector class for detecting and extracting
chess boards from screenshots.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
import logging
from PIL import Image


class BoardDetector:
    """
    Detects and extracts chess boards from images.
    
    This class uses computer vision techniques to identify chess board
    boundaries and extract individual squares.
    
    Attributes:
        logger (logging.Logger): Logger for the detector.
        min_board_size (int): Minimum board size in pixels.
        max_board_size (int): Maximum board size in pixels.
    """

    def __init__(self, min_board_size: int = 200, max_board_size: int = 2000):
        """
        Initialize the BoardDetector.
        
        Args:
            min_board_size (int): Minimum acceptable board size in pixels.
            max_board_size (int): Maximum acceptable board size in pixels.
        """
        self.logger = logging.getLogger(__name__)
        self.min_board_size = min_board_size
        self.max_board_size = max_board_size

    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load an image from file.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            Optional[np.ndarray]: Loaded image as numpy array, or None if failed.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return None
            
            self.logger.info(f"Image loaded: {image_path}, shape: {image.shape}")
            return image
        except Exception as e:
            self.logger.error(f"Error loading image: {e}")
            return None

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for board detection.
        
        Args:
            image (np.ndarray): Input image.
            
        Returns:
            np.ndarray: Preprocessed image.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        
        return thresh

    def detect_board_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect potential board contours in the image.
        
        Args:
            image (np.ndarray): Input image (preprocessed).
            
        Returns:
            List[np.ndarray]: List of detected contours.
        """
        # Find contours
        contours, _ = cv2.findContours(
            image,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by size constraints
            if self.min_board_size ** 2 < area < self.max_board_size ** 2:
                # Check if contour is roughly square
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Chess board should be roughly square (aspect ratio close to 1)
                if 0.8 < aspect_ratio < 1.2:
                    valid_contours.append(contour)
        
        self.logger.info(f"Found {len(valid_contours)} potential board contours")
        return valid_contours

    def extract_board_region(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Extract a board region from the image.
        
        Args:
            image (np.ndarray): Source image.
            x (int): X coordinate of top-left corner.
            y (int): Y coordinate of top-left corner.
            width (int): Width of the region.
            height (int): Height of the region.
            
        Returns:
            np.ndarray: Extracted board region.
        """
        # Ensure coordinates are within image bounds
        h, w = image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        x2 = min(x + width, w)
        y2 = min(y + height, h)
        
        return image[y:y2, x:x2]

    def divide_into_squares(
        self,
        board_image: np.ndarray
    ) -> List[List[np.ndarray]]:
        """
        Divide a board image into 8x8 squares.
        
        Args:
            board_image (np.ndarray): Image of the chess board.
            
        Returns:
            List[List[np.ndarray]]: 8x8 grid of square images (row, col).
        """
        h, w = board_image.shape[:2]
        
        # Calculate square dimensions
        square_height = h // 8
        square_width = w // 8
        
        squares = []
        
        # Extract each square (row by row, from rank 8 to rank 1)
        for row in range(8):
            row_squares = []
            for col in range(8):
                # Calculate coordinates
                y1 = row * square_height
                y2 = (row + 1) * square_height
                x1 = col * square_width
                x2 = (col + 1) * square_width
                
                # Extract square
                square = board_image[y1:y2, x1:x2]
                row_squares.append(square)
            
            squares.append(row_squares)
        
        self.logger.info("Board divided into 8x8 squares")
        return squares

    def detect_board(
        self,
        image: np.ndarray,
        manual_region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[np.ndarray, List[List[np.ndarray]]]]:
        """
        Detect chess board in image and extract squares.
        
        Args:
            image (np.ndarray): Input image.
            manual_region (Optional[Tuple[int, int, int, int]]): 
                Manual board region (x, y, width, height) if automatic detection fails.
                
        Returns:
            Optional[Tuple[np.ndarray, List[List[np.ndarray]]]]: 
                Tuple of (board_image, squares_grid) or None if detection failed.
        """
        if manual_region:
            # Use manual region
            x, y, width, height = manual_region
            board_image = self.extract_board_region(image, x, y, width, height)
            squares = self.divide_into_squares(board_image)
            return (board_image, squares)
        
        # Automatic detection
        preprocessed = self.preprocess_image(image)
        contours = self.detect_board_contours(preprocessed)
        
        if not contours:
            self.logger.warning("No board contours detected")
            return None
        
        # Use the largest valid contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Extract board
        board_image = self.extract_board_region(image, x, y, w, h)
        
        # Resize to standard size for consistency
        board_image = cv2.resize(board_image, (800, 800))
        
        # Divide into squares
        squares = self.divide_into_squares(board_image)
        
        return (board_image, squares)

    def visualize_board_detection(
        self,
        image: np.ndarray,
        board_region: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Visualize the detected board region on the original image.
        
        Args:
            image (np.ndarray): Original image.
            board_region (Tuple[int, int, int, int]): Detected region (x, y, w, h).
            
        Returns:
            np.ndarray: Image with board region highlighted.
        """
        result = image.copy()
        x, y, w, h = board_region
        
        # Draw rectangle around board
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        return result
    
    def detect_board_orientation(
        self,
        squares: List[List[np.ndarray]],
        recognition_results: Optional[List[List[any]]] = None
    ) -> str:
        """
        Detect board orientation based on piece positions or square colors.
        
        This method attempts to determine if the board is viewed from white's
        perspective (rank 1 at bottom) or black's perspective (rank 8 at bottom).
        
        Args:
            squares: 8x8 grid of square images.
            recognition_results: Optional recognition results to help determine orientation.
            
        Returns:
            str: 'white' if white is at bottom, 'black' if black is at bottom.
        """
        # Strategy 1: Use corner square colors
        # In standard chess boards: a1 and h8 are dark squares, a8 and h1 are light squares
        # When white faces user: bottom-left (a1) is dark
        # When black faces user: bottom-left (a8) is light
        
        bottom_left = squares[7][0]  # Row 7 (bottom), Col 0 (left)
        top_right = squares[0][7]    # Row 0 (top), Col 7 (right)
        
        bl_brightness = self._calculate_square_brightness(bottom_left)
        tr_brightness = self._calculate_square_brightness(top_right)
        
        # If bottom-left is darker than top-right, it's likely a1 (dark square)
        # which means white is facing the user
        if bl_brightness < tr_brightness - 10:  # threshold for color difference
            self.logger.info("Board orientation detected: WHITE facing user (bottom)")
            return 'white'
        elif tr_brightness < bl_brightness - 10:
            self.logger.info("Board orientation detected: BLACK facing user (bottom)")
            return 'black'
        
        # Strategy 2: If we have recognition results, check for starting positions
        if recognition_results:
            orientation = self._detect_orientation_from_pieces(recognition_results)
            if orientation:
                return orientation
        
        # Default to white if uncertain
        self.logger.warning("Could not confidently detect board orientation, defaulting to WHITE")
        return 'white'
    
    def _calculate_square_brightness(self, square_image: np.ndarray) -> float:
        """
        Calculate average brightness of a square.
        
        Args:
            square_image: Image of a chess square.
            
        Returns:
            float: Average brightness (0-255).
        """
        gray = cv2.cvtColor(square_image, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)
    
    def _detect_orientation_from_pieces(self, recognition_results: List[List[any]]) -> Optional[str]:
        """
        Detect orientation based on piece positions.
        
        Looks for typical starting position indicators like:
        - Rooks in corners
        - Pawns in second/seventh ranks
        
        Args:
            recognition_results: Recognition results grid.
            
        Returns:
            Optional[str]: 'white' or 'black' if detected, None if uncertain.
        """
        try:
            # Check bottom row (row 7) for white pieces
            bottom_row_white = 0
            bottom_row_black = 0
            
            for col in range(8):
                if hasattr(recognition_results[7][col], 'piece_type'):
                    piece = recognition_results[7][col].piece_type
                    if piece:
                        piece_name = piece.name if hasattr(piece, 'name') else str(piece)
                        if 'WHITE' in piece_name:
                            bottom_row_white += 1
                        elif 'BLACK' in piece_name:
                            bottom_row_black += 1
            
            # Check top row (row 0) for white pieces
            top_row_white = 0
            top_row_black = 0
            
            for col in range(8):
                if hasattr(recognition_results[0][col], 'piece_type'):
                    piece = recognition_results[0][col].piece_type
                    if piece:
                        piece_name = piece.name if hasattr(piece, 'name') else str(piece)
                        if 'WHITE' in piece_name:
                            top_row_white += 1
                        elif 'BLACK' in piece_name:
                            top_row_black += 1
            
            # If bottom row has more white pieces, white is at bottom
            if bottom_row_white > bottom_row_black and bottom_row_white >= 2:
                self.logger.info("Orientation detected from pieces: WHITE at bottom")
                return 'white'
            # If top row has more white pieces, black is at bottom
            elif top_row_white > top_row_black and top_row_white >= 2:
                self.logger.info("Orientation detected from pieces: BLACK at bottom")
                return 'black'
        except Exception as e:
            self.logger.warning(f"Error detecting orientation from pieces: {e}")
        
        return None
    
    def flip_board(self, squares: List[List[np.ndarray]]) -> List[List[np.ndarray]]:
        """
        Flip board orientation (rotate 180 degrees).
        
        Args:
            squares: 8x8 grid of square images.
            
        Returns:
            List[List[np.ndarray]]: Flipped 8x8 grid.
        """
        flipped = []
        for row in reversed(squares):
            flipped_row = list(reversed(row))
            flipped.append(flipped_row)
        
        self.logger.info("Board orientation flipped")
        return flipped
