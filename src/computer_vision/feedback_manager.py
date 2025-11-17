"""
Feedback Manager for Piece Recognition.

This module manages user feedback on piece recognition for future model training.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
import cv2
import base64

from src.computer_vision.piece_recognizer import PieceType


class PieceFeedback:
    """
    Data class representing user feedback on a piece recognition.
    
    Attributes:
        square_name (str): Chess square name (e.g., 'e4').
        original_prediction (Optional[PieceType]): Original AI prediction.
        original_confidence (float): Original confidence score.
        user_correction (PieceType): User's correction.
        timestamp (str): ISO format timestamp of feedback.
        square_image_path (Optional[str]): Path to saved square image for retraining.
        board_orientation (Optional[str]): Board orientation ('white' or 'black' facing user).
    """
    
    def __init__(
        self,
        square_name: str,
        original_prediction: Optional[PieceType],
        original_confidence: float,
        user_correction: PieceType,
        timestamp: Optional[str] = None,
        square_image_path: Optional[str] = None,
        board_orientation: Optional[str] = None
    ):
        """
        Initialize a PieceFeedback instance.
        
        Args:
            square_name: Chess square name.
            original_prediction: What the model predicted.
            original_confidence: Confidence of original prediction.
            user_correction: What the user said it should be.
            timestamp: Optional timestamp (defaults to now).
            square_image_path: Optional path to square image file.
            board_orientation: Optional board orientation ('white' or 'black').
        """
        self.square_name = square_name
        self.original_prediction = original_prediction
        self.original_confidence = original_confidence
        self.user_correction = user_correction
        self.timestamp = timestamp or datetime.now().isoformat()
        self.square_image_path = square_image_path
        self.board_orientation = board_orientation
    
    def to_dict(self) -> Dict:
        """
        Convert feedback to dictionary for serialization.
        
        Returns:
            Dict: Serializable dictionary.
        """
        return {
            'square_name': self.square_name,
            'original_prediction': self.original_prediction.name if self.original_prediction else None,
            'original_confidence': self.original_confidence,
            'user_correction': self.user_correction.name if self.user_correction else None,
            'timestamp': self.timestamp,
            'square_image_path': self.square_image_path,
            'board_orientation': self.board_orientation
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PieceFeedback':
        """
        Create PieceFeedback from dictionary.
        
        Args:
            data: Dictionary with feedback data.
            
        Returns:
            PieceFeedback: Reconstructed feedback object.
        """
        original_pred = None
        if data.get('original_prediction'):
            original_pred = PieceType[data['original_prediction']]
        
        user_corr = None
        if data.get('user_correction'):
            user_corr = PieceType[data['user_correction']]
        
        return PieceFeedback(
            square_name=data['square_name'],
            original_prediction=original_pred,
            original_confidence=data['original_confidence'],
            user_correction=user_corr,
            timestamp=data.get('timestamp'),
            square_image_path=data.get('square_image_path'),
            board_orientation=data.get('board_orientation')
        )


class FeedbackManager:
    """
    Manages collection and storage of piece recognition feedback.
    
    This class stores user corrections to piece recognition, which can
    be used to fine-tune or retrain the recognition model.
    
    Attributes:
        feedback_file (Path): Path to feedback storage file.
        logger (logging.Logger): Logger instance.
        feedback_data (List[PieceFeedback]): Current session feedback.
    """
    
    def __init__(self, feedback_file: Optional[Path] = None):
        """
        Initialize the FeedbackManager.
        
        Args:
            feedback_file: Path to feedback JSON file. If None, uses default.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set default feedback file location
        if feedback_file is None:
            output_dir = Path(__file__).parent.parent.parent / 'output'
            output_dir.mkdir(exist_ok=True)
            feedback_file = output_dir / 'piece_recognition_feedback.json'
        
        self.feedback_file = Path(feedback_file)
        self.feedback_data: List[PieceFeedback] = []
        
        # Load existing feedback if file exists
        self._load_feedback()
        
        self.logger.info(f"FeedbackManager initialized with file: {self.feedback_file}")
    
    def _load_feedback(self):
        """Load existing feedback from file."""
        if not self.feedback_file.exists():
            self.logger.info("No existing feedback file found")
            return
        
        # Check if file is empty
        if self.feedback_file.stat().st_size == 0:
            self.logger.info("Feedback file is empty")
            return
        
        try:
            with open(self.feedback_file, 'r') as f:
                data = json.load(f)
                self.feedback_data = [PieceFeedback.from_dict(item) for item in data]
                self.logger.info(f"Loaded {len(self.feedback_data)} feedback entries")
        except Exception as e:
            self.logger.error(f"Error loading feedback: {e}", exc_info=True)
            self.feedback_data = []
    
    def _save_feedback(self):
        """Save feedback to file."""
        try:
            # Ensure directory exists
            self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict list and save
            data = [fb.to_dict() for fb in self.feedback_data]
            
            with open(self.feedback_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.feedback_data)} feedback entries")
        except Exception as e:
            self.logger.error(f"Error saving feedback: {e}", exc_info=True)
    
    def _save_square_image(self, square_image: np.ndarray, square_name: str) -> Optional[str]:
        """
        Save a square image for training data.
        
        Args:
            square_image: Image of the square.
            square_name: Chess square name for filename.
            
        Returns:
            Optional[str]: Relative path to saved image, or None if failed.
        """
        try:
            # Create training images directory
            images_dir = self.feedback_file.parent / 'training_images'
            images_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{square_name}_{timestamp}.png"
            image_path = images_dir / filename
            
            # Save image
            cv2.imwrite(str(image_path), square_image)
            
            # Return relative path
            return f"training_images/{filename}"
        except Exception as e:
            self.logger.error(f"Error saving square image: {e}", exc_info=True)
            return None
    
    def add_feedback(
        self,
        square_name: str,
        original_prediction: Optional[PieceType],
        original_confidence: float,
        user_correction: PieceType,
        square_image: Optional[np.ndarray] = None,
        board_orientation: Optional[str] = None
    ):
        """
        Add a new piece of feedback.
        
        Args:
            square_name: Chess square name (e.g., 'e4').
            original_prediction: Original model prediction.
            original_confidence: Confidence of original prediction.
            user_correction: User's correction.
            square_image: Optional image of the square for training.
            board_orientation: Optional board orientation ('white' or 'black').
        """
        # Save square image if provided
        square_image_path = None
        if square_image is not None:
            square_image_path = self._save_square_image(square_image, square_name)
        
        feedback = PieceFeedback(
            square_name=square_name,
            original_prediction=original_prediction,
            original_confidence=original_confidence,
            user_correction=user_correction,
            square_image_path=square_image_path,
            board_orientation=board_orientation
        )
        
        self.feedback_data.append(feedback)
        self._save_feedback()
        
        self.logger.info(
            f"Added feedback for {square_name}: "
            f"{original_prediction} -> {user_correction}"
        )
    
    def get_feedback_count(self) -> int:
        """
        Get the total number of feedback entries.
        
        Returns:
            int: Number of feedback entries.
        """
        return len(self.feedback_data)
    
    def get_correction_statistics(self) -> Dict:
        """
        Get statistics about corrections.
        
        Returns:
            Dict: Statistics including total corrections, by piece type, etc.
        """
        if not self.feedback_data:
            return {
                'total_corrections': 0,
                'by_piece_type': {},
                'avg_original_confidence': 0.0
            }
        
        stats = {
            'total_corrections': len(self.feedback_data),
            'by_piece_type': {},
            'avg_original_confidence': 0.0
        }
        
        # Count by piece type
        for fb in self.feedback_data:
            piece_name = fb.user_correction.name if fb.user_correction else 'UNKNOWN'
            stats['by_piece_type'][piece_name] = stats['by_piece_type'].get(piece_name, 0) + 1
        
        # Average confidence of corrected predictions
        confidences = [fb.original_confidence for fb in self.feedback_data]
        stats['avg_original_confidence'] = sum(confidences) / len(confidences)
        
        return stats
    
    def clear_feedback(self):
        """Clear all feedback data."""
        self.feedback_data = []
        if self.feedback_file.exists():
            self.feedback_file.unlink()
        self.logger.info("Feedback data cleared")
    
    def export_feedback(self, export_path: Path):
        """
        Export feedback to a different file.
        
        Args:
            export_path: Path to export file.
        """
        try:
            data = [fb.to_dict() for fb in self.feedback_data]
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Exported feedback to {export_path}")
        except Exception as e:
            self.logger.error(f"Error exporting feedback: {e}", exc_info=True)
    
    def get_training_data(self) -> List[tuple]:
        """
        Get training data from feedback for model retraining.
        
        Returns:
            List[tuple]: List of (image, label) tuples where image is np.ndarray
                        and label is PieceType. Only includes feedback with images.
        """
        training_data = []
        base_dir = self.feedback_file.parent
        
        for fb in self.feedback_data:
            if fb.square_image_path:
                image_path = base_dir / fb.square_image_path
                if image_path.exists():
                    try:
                        image = cv2.imread(str(image_path))
                        if image is not None:
                            training_data.append((image, fb.user_correction))
                    except Exception as e:
                        self.logger.warning(f"Failed to load image {image_path}: {e}")
        
        self.logger.info(f"Retrieved {len(training_data)} training samples from feedback")
        return training_data
    
    def get_feedback_by_piece_type(self, piece_type: PieceType) -> List[PieceFeedback]:
        """
        Get all feedback for a specific piece type.
        
        Args:
            piece_type: The piece type to filter by.
            
        Returns:
            List[PieceFeedback]: Feedback entries for the specified piece type.
        """
        return [fb for fb in self.feedback_data if fb.user_correction == piece_type]
    
    def get_misclassified_feedback(self) -> List[PieceFeedback]:
        """
        Get feedback where the original prediction was incorrect.
        
        Returns:
            List[PieceFeedback]: Feedback entries where prediction != correction.
        """
        return [
            fb for fb in self.feedback_data 
            if fb.original_prediction != fb.user_correction
        ]
