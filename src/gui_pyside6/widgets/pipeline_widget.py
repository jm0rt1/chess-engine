"""
Pipeline Visualization Widget for Chess Engine GUI.

This module provides visualization of the complete image processing pipeline
with step-by-step display of intermediate results.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton, QComboBox, QGridLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np
from typing import List, Optional, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from src.computer_vision.piece_recognizer import RecognitionResult


class PipelineVisualizationWidget(QWidget):
    """
    Widget for visualizing the image processing pipeline.
    
    Displays each stage of the processing pipeline:
    - Raw image input
    - Preprocessing (grayscale, blur, threshold)
    - Edge detection
    - Contour finding
    - Board region extraction
    - Square segmentation
    - Piece recognition
    
    Signals:
        stage_selected: Emitted when a pipeline stage is selected.
    """
    
    # Define signals
    stage_selected = Signal(str)  # stage name
    
    def __init__(self, parent=None):
        """
        Initialize the pipeline visualization widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        # Maps stage name to an image or a named collection of images
        self.pipeline_stages: Dict[str, Union[np.ndarray, Dict[str, np.ndarray]]] = {}
        self.current_stage: Optional[str] = None
        self.step_mode = False

        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Image Processing Pipeline")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Stage selector
        self.stage_selector = QComboBox()
        self.stage_selector.addItem("Select stage...")
        self.stage_selector.currentTextChanged.connect(self._on_stage_changed)
        header_layout.addWidget(QLabel("View:"))
        header_layout.addWidget(self.stage_selector)
        
        layout.addLayout(header_layout)
        
        # Main display area with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        self.display_widget = QWidget()
        self.display_layout = QVBoxLayout(self.display_widget)
        self.display_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.display_widget)
        layout.addWidget(scroll_area)
        
        # Grid for showing multiple stages
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.display_layout.addWidget(self.grid_widget)
        
        # Navigation buttons for step mode
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self._previous_stage)
        nav_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next →")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._next_stage)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
    
    def _numpy_to_qpixmap(self, image: np.ndarray, max_width: int = 600) -> QPixmap:
        """
        Convert a numpy array image to QPixmap.
        
        Args:
            image (np.ndarray): Input image.
            max_width (int): Maximum width for display.
            
        Returns:
            QPixmap: Converted image.
        """
        # Handle different image types
        if len(image.shape) == 2:
            # Grayscale
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            # Color image - convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale if needed
        if pixmap.width() > max_width:
            pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
        
        return pixmap
    
    def _add_stage_to_grid(self, stage_name: str, image: np.ndarray, row: int, col: int):
        """
        Add a stage image to the grid layout.
        
        Args:
            stage_name (str): Name of the stage.
            image (np.ndarray): Image to display.
            row (int): Grid row.
            col (int): Grid column.
        """
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Stage label
        label = QLabel(stage_name)
        label.setAlignment(Qt.AlignCenter)
        label_font = QFont()
        label_font.setBold(True)
        label.setFont(label_font)
        container_layout.addWidget(label)
        
        # Image
        image_label = QLabel()
        pixmap = self._numpy_to_qpixmap(image, max_width=300)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(image_label)
        
        self.grid_layout.addWidget(container, row, col)
    
    def _clear_display(self):
        """Clear the current display."""
        # Remove all widgets from grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _on_stage_changed(self, stage_name: str):
        """
        Handle stage selection change.
        
        Args:
            stage_name (str): Selected stage name.
        """
        if stage_name == "Select stage..." or stage_name not in self.pipeline_stages:
            return
        
        self.current_stage = stage_name
        self.stage_selected.emit(stage_name)
        
        # Display the selected stage
        self._display_single_stage(stage_name)
    
    def _display_single_stage(self, stage_name: str):
        """
        Display a single pipeline stage.
        
        Args:
            stage_name (str): Name of the stage to display.
        """
        if stage_name not in self.pipeline_stages:
            return
        
        self._clear_display()
        
        stage_data = self.pipeline_stages[stage_name]
        
        if isinstance(stage_data, dict):
            # Multiple images in this stage
            row = 0
            for name, image in stage_data.items():
                self._add_stage_to_grid(name, image, row, 0)
                row += 1
        else:
            # Single image
            self._add_stage_to_grid(stage_name, stage_data, 0, 0)
    
    def _display_all_stages(self):
        """Display all pipeline stages in a grid."""
        self._clear_display()
        
        stage_list = list(self.pipeline_stages.keys())
        row = 0
        col = 0
        max_cols = 3
        
        for stage_name in stage_list:
            stage_data = self.pipeline_stages[stage_name]
            
            if isinstance(stage_data, dict):
                # Skip multi-image stages for grid view
                continue
            
            self._add_stage_to_grid(stage_name, stage_data, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def set_raw_image(self, image: np.ndarray):
        """
        Set the raw input image.
        
        Args:
            image (np.ndarray): Raw input image.
        """
        self.pipeline_stages["1. Raw Image"] = image.copy()
        self._update_stage_selector()
        self._display_all_stages()
    
    def set_preprocessing_result(self, original: np.ndarray, preprocessed: np.ndarray):
        """
        Set preprocessing stage results.
        
        Args:
            original (np.ndarray): Original image.
            preprocessed (np.ndarray): Preprocessed image.
        """
        # Convert original to grayscale for comparison
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        
        # Apply different preprocessing steps for visualization
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        self.pipeline_stages["2. Preprocessing"] = {
            "Grayscale": gray,
            "Blurred": blurred,
            "Thresholded": preprocessed
        }
        self._update_stage_selector()
    
    def set_contours(self, original: np.ndarray, contours: List):
        """
        Set contour detection results.
        
        Args:
            original (np.ndarray): Original image.
            contours (List): List of detected contours.
        """
        # Draw contours on image
        contour_image = original.copy()
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
        
        # Also create edge detection visualization
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        self.pipeline_stages["3. Edge & Contour Detection"] = {
            "Edges": edges,
            "Contours": contour_image
        }
        self._update_stage_selector()
    
    def set_board_region(self, board_image: np.ndarray):
        """
        Set the extracted board region.
        
        Args:
            board_image (np.ndarray): Extracted board image.
        """
        self.pipeline_stages["4. Board Region"] = board_image.copy()
        self._update_stage_selector()
    
    def set_squares(self, squares: List[List[np.ndarray]]):
        """
        Set the segmented squares.
        
        Args:
            squares (List[List[np.ndarray]]): 8x8 grid of square images.
        """
        # Create a visualization showing the 8x8 grid
        if not squares or not squares[0]:
            return
        
        sq_h, sq_w = squares[0][0].shape[:2]
        
        # Create composite image
        grid_image = np.zeros((sq_h * 8, sq_w * 8, 3), dtype=np.uint8)
        
        for row in range(8):
            for col in range(8):
                y1 = row * sq_h
                y2 = (row + 1) * sq_h
                x1 = col * sq_w
                x2 = (col + 1) * sq_w
                
                grid_image[y1:y2, x1:x2] = squares[row][col]
        
        # Draw grid lines
        for i in range(9):
            # Horizontal lines
            y = i * sq_h
            cv2.line(grid_image, (0, y), (sq_w * 8, y), (0, 255, 0), 2)
            # Vertical lines
            x = i * sq_w
            cv2.line(grid_image, (x, 0), (x, sq_h * 8), (0, 255, 0), 2)
        
        self.pipeline_stages["5. Square Segmentation"] = grid_image
        self._update_stage_selector()
    
    def set_recognition_results(self, squares: List[List[np.ndarray]], results: List[List["RecognitionResult"]]):
        """
        Set piece recognition results.
        
        Args:
            squares (List[List[np.ndarray]]): 8x8 grid of square images.
            results (List[List]): 8x8 grid of recognition results.
        """
        if not squares or not squares[0]:
            return
        
        sq_h, sq_w = squares[0][0].shape[:2]
        
        # Create composite image with labels
        grid_image = np.zeros((sq_h * 8, sq_w * 8, 3), dtype=np.uint8)
        
        for row in range(8):
            for col in range(8):
                y1 = row * sq_h
                y2 = (row + 1) * sq_h
                x1 = col * sq_w
                x2 = (col + 1) * sq_w
                
                square_img = squares[row][col].copy()
                
                # Add recognition result as text
                result = results[row][col]
                fen_char = result.to_fen_char()
                confidence = result.confidence
                
                # Draw text on square
                text = f"{fen_char} ({confidence:.2f})"
                cv2.putText(
                    square_img, text,
                    (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1
                )
                
                grid_image[y1:y2, x1:x2] = square_img
        
        # Draw grid lines
        for i in range(9):
            y = i * sq_h
            cv2.line(grid_image, (0, y), (sq_w * 8, y), (255, 255, 0), 1)
            x = i * sq_w
            cv2.line(grid_image, (x, 0), (x, sq_h * 8), (255, 255, 0), 1)
        
        self.pipeline_stages["6. Piece Recognition"] = grid_image
        self._update_stage_selector()
    
    def _update_stage_selector(self):
        """Update the stage selector dropdown."""
        current_stages = [self.stage_selector.itemText(i) 
                         for i in range(self.stage_selector.count())]
        
        for stage_name in self.pipeline_stages.keys():
            if stage_name not in current_stages:
                self.stage_selector.addItem(stage_name)
    
    def enable_step_mode(self):
        """Enable step-by-step navigation mode."""
        self.step_mode = True
        self.prev_button.setEnabled(True)
        self.next_button.setEnabled(True)
        
        # Start with first stage
        stage_list = list(self.pipeline_stages.keys())
        if stage_list:
            self.stage_selector.setCurrentText(stage_list[0])
    
    def _previous_stage(self):
        """Navigate to the previous pipeline stage."""
        stage_list = list(self.pipeline_stages.keys())
        if not stage_list:
            return
        
        current_text = self.stage_selector.currentText()
        if current_text in stage_list:
            current_idx = stage_list.index(current_text)
            if current_idx > 0:
                self.stage_selector.setCurrentText(stage_list[current_idx - 1])
    
    def _next_stage(self):
        """Navigate to the next pipeline stage."""
        stage_list = list(self.pipeline_stages.keys())
        if not stage_list:
            return
        
        current_text = self.stage_selector.currentText()
        if current_text in stage_list:
            current_idx = stage_list.index(current_text)
            if current_idx < len(stage_list) - 1:
                self.stage_selector.setCurrentText(stage_list[current_idx + 1])
    
    def clear(self):
        """Clear all pipeline stages."""
        self.pipeline_stages.clear()
        self.current_stage = None
        self.step_mode = False
        
        # Clear selector
        self.stage_selector.clear()
        self.stage_selector.addItem("Select stage...")
        
        # Clear display
        self._clear_display()
        
        # Disable navigation
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
