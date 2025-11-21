"""
Feedback Manager for Piece Recognition.

This module manages user feedback on piece recognition for future model training.
Includes session tracking and deduplication to ensure clean training data.
"""

import base64
import hashlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

import cv2
import numpy as np

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
        session_id (Optional[str]): Unique identifier for the labeling session.
        unique_key (Optional[str]): Unique key combining image_hash and square_name for deduplication.
        image_hash (Optional[str]): Hash of the source image for identification.
        is_active (bool): Whether this feedback is currently active (not superseded).
    """
    
    def __init__(
        self,
        square_name: str,
        original_prediction: Optional[PieceType],
        original_confidence: float,
        user_correction: PieceType,
        timestamp: Optional[str] = None,
        square_image_path: Optional[str] = None,
        board_orientation: Optional[str] = None,
        session_id: Optional[str] = None,
        unique_key: Optional[str] = None,
        image_hash: Optional[str] = None,
        is_active: bool = True
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
            session_id: Optional session identifier.
            unique_key: Optional unique key for deduplication.
            image_hash: Optional hash of source image.
            is_active: Whether this feedback is active (default True).
        """
        self.square_name = square_name
        self.original_prediction = original_prediction
        self.original_confidence = original_confidence
        self.user_correction = user_correction
        self.timestamp = timestamp or datetime.now().isoformat()
        self.square_image_path = square_image_path
        self.board_orientation = board_orientation
        self.session_id = session_id
        self.unique_key = unique_key
        self.image_hash = image_hash
        self.is_active = is_active
    
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
            'board_orientation': self.board_orientation,
            'session_id': self.session_id,
            'unique_key': self.unique_key,
            'image_hash': self.image_hash,
            'is_active': self.is_active
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
            board_orientation=data.get('board_orientation'),
            session_id=data.get('session_id'),
            unique_key=data.get('unique_key'),
            image_hash=data.get('image_hash'),
            is_active=data.get('is_active', True)  # Default to True for backward compatibility
        )


class FeedbackManager:
    """
    Manages collection and storage of piece recognition feedback.
    
    This class stores user corrections to piece recognition, which can
    be used to fine-tune or retrain the recognition model. Includes session
    tracking and deduplication to ensure clean training data.
    
    Attributes:
        feedback_file (Path): Path to feedback storage file.
        logger (logging.Logger): Logger instance.
        feedback_data (List[PieceFeedback]): All feedback entries.
        session_id (str): Unique identifier for the current labeling session.
        current_image_hash (Optional[str]): Hash of the currently loaded image.
    """
    
    def __init__(self, feedback_file: Optional[Path] = None, session_id: Optional[str] = None):
        """
        Initialize the FeedbackManager.
        
        Args:
            feedback_file: Path to feedback JSON file. If None, uses default.
            session_id: Optional session ID. If None, generates a new unique ID.
        """
        self.logger = logging.getLogger(__name__)
        
        # Set default feedback file location
        if feedback_file is None:
            output_dir = Path(__file__).parent.parent.parent / 'output'
            output_dir.mkdir(exist_ok=True)
            feedback_file = output_dir / 'piece_recognition_feedback.json'
        
        self.feedback_file = Path(feedback_file)
        self.feedback_data: List[PieceFeedback] = []
        
        # Generate or use provided session ID
        self.session_id = session_id or self._generate_session_id()
        self.current_image_hash: Optional[str] = None
        
        # Load existing feedback if file exists
        self._load_feedback()
        
        self.logger.info(f"FeedbackManager initialized with file: {self.feedback_file}")
        self.logger.info(f"Session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session identifier.
        
        Returns:
            str: Unique session ID combining timestamp and UUID.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_suffix = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{unique_suffix}"
    
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
    
    def set_current_image(self, image: np.ndarray):
        """
        Set the current image being processed and compute its hash.
        
        This should be called when a new image is loaded to establish
        the context for subsequent feedback entries.
        
        Args:
            image: The chess board image being processed.
        """
        self.current_image_hash = self._compute_image_hash(image)
        self.logger.info(f"Current image hash set: {self.current_image_hash[:16]}...")
    
    def _compute_image_hash(self, image: np.ndarray) -> str:
        """
        Compute a hash of an image for unique identification.
        
        Args:
            image: Image array to hash.
            
        Returns:
            str: SHA256 hash of the image.
        """
        # Use a small version of the image for consistent hashing
        small = cv2.resize(image, (64, 64))
        image_bytes = small.tobytes()
        return hashlib.sha256(image_bytes).hexdigest()
    
    def _compute_unique_key(self, image_hash: str, square_name: str) -> str:
        """
        Compute a unique key for deduplication.
        
        Combines image hash and square name to uniquely identify a specific
        square in a specific image.
        
        Args:
            image_hash: Hash of the source image.
            square_name: Chess square name (e.g., 'e4').
            
        Returns:
            str: Unique key for this feedback entry.
        """
        return f"{image_hash}_{square_name}"
    
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
        Add a new piece of feedback with deduplication.
        
        If feedback for the same square in the same image already exists,
        the old entry is marked as inactive and the new one replaces it.
        
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
        
        # Compute unique key for deduplication
        image_hash = self.current_image_hash
        unique_key = None
        if image_hash:
            unique_key = self._compute_unique_key(image_hash, square_name)
            
            # Check for existing feedback with same unique key
            superseded_count = 0
            for existing_fb in self.feedback_data:
                if existing_fb.unique_key == unique_key and existing_fb.is_active:
                    # Mark old entry as inactive (superseded)
                    existing_fb.is_active = False
                    superseded_count += 1
                    self.logger.info(
                        f"Superseding previous feedback for {square_name} "
                        f"(was: {existing_fb.user_correction.name if existing_fb.user_correction else 'None'})"
                    )
            
            if superseded_count > 0:
                self.logger.info(f"Marked {superseded_count} previous entries as superseded")
        
        # Create new feedback entry
        feedback = PieceFeedback(
            square_name=square_name,
            original_prediction=original_prediction,
            original_confidence=original_confidence,
            user_correction=user_correction,
            square_image_path=square_image_path,
            board_orientation=board_orientation,
            session_id=self.session_id,
            unique_key=unique_key,
            image_hash=image_hash,
            is_active=True
        )
        
        self.feedback_data.append(feedback)
        self._save_feedback()
        
        self.logger.info(
            f"Added feedback for {square_name}: "
            f"{original_prediction} -> {user_correction} "
            f"(session: {self.session_id[:16]}...)"
        )
    
    def get_feedback_count(self) -> int:
        """
        Get the total number of feedback entries.
        
        Returns:
            int: Number of feedback entries.
        """
        return len(self.feedback_data)
    
    def get_correction_statistics(self, active_only: bool = True) -> Dict:
        """
        Get statistics about corrections.
        
        Args:
            active_only: If True, only counts active (non-superseded) feedback.
        
        Returns:
            Dict: Statistics including total corrections, by piece type, etc.
        """
        # Filter feedback based on active_only flag
        feedback_to_analyze = [fb for fb in self.feedback_data if not active_only or fb.is_active]
        
        if not feedback_to_analyze:
            return {
                'total_corrections': 0,
                'active_corrections': 0,
                'superseded_corrections': 0,
                'by_piece_type': {},
                'by_session': {},
                'avg_original_confidence': 0.0
            }
        
        stats = {
            'total_corrections': len(self.feedback_data),
            'active_corrections': len([fb for fb in self.feedback_data if fb.is_active]),
            'superseded_corrections': len([fb for fb in self.feedback_data if not fb.is_active]),
            'by_piece_type': {},
            'by_session': {},
            'avg_original_confidence': 0.0
        }
        
        # Count by piece type (active only)
        for fb in feedback_to_analyze:
            piece_name = fb.user_correction.name if fb.user_correction else 'UNKNOWN'
            stats['by_piece_type'][piece_name] = stats['by_piece_type'].get(piece_name, 0) + 1
        
        # Count by session (active only)
        for fb in feedback_to_analyze:
            session = fb.session_id or 'unknown'
            stats['by_session'][session] = stats['by_session'].get(session, 0) + 1
        
        # Average confidence of corrected predictions (active only)
        confidences = [fb.original_confidence for fb in feedback_to_analyze]
        if confidences:
            stats['avg_original_confidence'] = sum(confidences) / len(confidences)
        
        return stats
    
    def get_feedback_by_session(self, session_id: str) -> List[PieceFeedback]:
        """
        Get all feedback for a specific session.
        
        Args:
            session_id: The session identifier to filter by.
            
        Returns:
            List[PieceFeedback]: Feedback entries for the specified session.
        """
        return [fb for fb in self.feedback_data if fb.session_id == session_id]
    
    def get_session_summary(self) -> Dict:
        """
        Get a summary of all sessions with feedback counts.
        
        Returns:
            Dict: Session IDs mapped to counts and timestamps.
        """
        sessions = {}
        for fb in self.feedback_data:
            session = fb.session_id or 'unknown'
            if session not in sessions:
                sessions[session] = {
                    'total_count': 0,
                    'active_count': 0,
                    'first_timestamp': fb.timestamp,
                    'last_timestamp': fb.timestamp
                }
            
            sessions[session]['total_count'] += 1
            if fb.is_active:
                sessions[session]['active_count'] += 1
            
            # Update timestamps
            if fb.timestamp < sessions[session]['first_timestamp']:
                sessions[session]['first_timestamp'] = fb.timestamp
            if fb.timestamp > sessions[session]['last_timestamp']:
                sessions[session]['last_timestamp'] = fb.timestamp
        
        return sessions
    
    def clear_feedback(self, clear_images: bool = True):
        """
        Clear all feedback data.
        
        Args:
            clear_images: If True, also deletes training images.
        """
        if clear_images:
            # Delete training images directory
            images_dir = self.feedback_file.parent / 'training_images'
            if images_dir.exists():
                import shutil
                shutil.rmtree(images_dir)
                self.logger.info("Training images directory cleared")
        
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
    
    def get_training_data(self, active_only: bool = True) -> List[tuple]:
        """
        Get training data from feedback for model retraining.
        
        Args:
            active_only: If True, only returns active (non-superseded) feedback.
        
        Returns:
            List[tuple]: List of (image, label) tuples where image is np.ndarray
                        and label is PieceType. Only includes feedback with images.
        """
        training_data = []
        base_dir = self.feedback_file.parent
        
        # Filter feedback based on active_only flag
        feedback_to_process = [fb for fb in self.feedback_data if not active_only or fb.is_active]
        
        for fb in feedback_to_process:
            if fb.square_image_path:
                image_path = base_dir / fb.square_image_path
                if image_path.exists():
                    try:
                        image = cv2.imread(str(image_path))
                        if image is not None:
                            training_data.append((image, fb.user_correction))
                    except Exception as e:
                        self.logger.warning(f"Failed to load image {image_path}: {e}")
        
        active_str = "active " if active_only else ""
        self.logger.info(f"Retrieved {len(training_data)} {active_str}training samples from feedback")
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
