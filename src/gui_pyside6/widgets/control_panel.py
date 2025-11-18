"""
Control Panel Widget for Chess Engine GUI.

This module provides the control panel with buttons for various actions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QGroupBox, QLineEdit, QTextEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class ControlPanelWidget(QWidget):
    """
    Control panel widget with action buttons.
    
    Provides buttons for:
    - Loading images
    - Processing images
    - Stepping through pipeline
    - Running engine analysis
    - Resetting the application
    
    Signals:
        load_image_signal: Emitted when load image is requested.
        process_image_signal: Emitted when image processing is requested.
        step_through_signal: Emitted when step-through mode is requested.
        run_analysis_signal: Emitted when engine analysis is requested.
        reset_signal: Emitted when reset is requested.
    """
    
    # Define signals
    load_image_signal = Signal()
    process_image_signal = Signal()
    step_through_signal = Signal()
    run_analysis_signal = Signal()
    flip_board_signal = Signal()
    reset_signal = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize the control panel widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel("Control Panel")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Image Loading Section
        load_group = QGroupBox("1. Load Image")
        load_layout = QVBoxLayout()
        
        self.load_button = QPushButton("Load Image...")
        self.load_button.clicked.connect(self.load_image_signal.emit)
        load_layout.addWidget(self.load_button)
        
        self.image_status = QLabel("No image loaded")
        self.image_status.setWordWrap(True)
        self.image_status.setStyleSheet("color: gray;")
        load_layout.addWidget(self.image_status)
        
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # Processing Section
        process_group = QGroupBox("2. Process Image")
        process_layout = QVBoxLayout()
        
        self.process_button = QPushButton("Process Image")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_image_signal.emit)
        process_layout.addWidget(self.process_button)
        
        self.step_button = QPushButton("Step Through Pipeline")
        self.step_button.setEnabled(False)
        self.step_button.clicked.connect(self.step_through_signal.emit)
        process_layout.addWidget(self.step_button)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # Board Orientation Section
        orientation_group = QGroupBox("Board Orientation")
        orientation_layout = QVBoxLayout()
        
        self.flip_board_button = QPushButton("Flip Board Orientation")
        self.flip_board_button.setEnabled(False)
        self.flip_board_button.setToolTip("Rotate the board 180 degrees (switch between white/black perspective)")
        self.flip_board_button.clicked.connect(self.flip_board_signal.emit)
        orientation_layout.addWidget(self.flip_board_button)
        
        self.orientation_label = QLabel("Current: Not set")
        self.orientation_label.setWordWrap(True)
        self.orientation_label.setStyleSheet("color: gray; font-style: italic;")
        orientation_layout.addWidget(self.orientation_label)
        
        orientation_group.setLayout(orientation_layout)
        layout.addWidget(orientation_group)
        
        # Manual FEN Entry Section
        fen_group = QGroupBox("Manual Position Entry")
        fen_layout = QVBoxLayout()
        
        fen_label = QLabel("FEN String:")
        fen_layout.addWidget(fen_label)
        
        self.fen_input = QLineEdit()
        self.fen_input.setPlaceholderText("Enter FEN notation...")
        fen_layout.addWidget(self.fen_input)
        
        fen_group.setLayout(fen_layout)
        layout.addWidget(fen_group)
        
        # Analysis Section
        analysis_group = QGroupBox("3. Analyze Position")
        analysis_layout = QVBoxLayout()
        
        self.analysis_button = QPushButton("Run Engine Analysis")
        self.analysis_button.setEnabled(False)
        self.analysis_button.clicked.connect(self.run_analysis_signal.emit)
        analysis_layout.addWidget(self.analysis_button)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Reset Section
        layout.addSpacing(20)
        self.reset_button = QPushButton("Reset Application")
        self.reset_button.clicked.connect(self.reset_signal.emit)
        layout.addWidget(self.reset_button)
        
        # Info Section
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlainText(
            "Instructions:\n\n"
            "1. Load a chess board image\n"
            "2. Process or step through the pipeline\n"
            "3. Review the board reconstruction\n"
            "4. Run engine analysis for threats and moves"
        )
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Add stretch at the end
        layout.addStretch()
    
    def enable_process_button(self, enabled: bool):
        """
        Enable or disable the process button.
        
        Args:
            enabled (bool): Whether to enable the button.
        """
        self.process_button.setEnabled(enabled)
        self.step_button.setEnabled(enabled)
        if enabled:
            self.image_status.setText("Image loaded - Ready to process")
            self.image_status.setStyleSheet("color: green;")
    
    def enable_analysis_button(self, enabled: bool):
        """
        Enable or disable the analysis button.
        
        Args:
            enabled (bool): Whether to enable the button.
        """
        self.analysis_button.setEnabled(enabled)
    
    def enable_flip_board_button(self, enabled: bool):
        """
        Enable or disable the flip board button.
        
        Args:
            enabled (bool): Whether to enable the button.
        """
        self.flip_board_button.setEnabled(enabled)
    
    def set_board_orientation(self, orientation: str):
        """
        Set the current board orientation display.
        
        Args:
            orientation (str): Current orientation ('white' or 'black').
        """
        display_text = "White at bottom" if orientation == 'white' else "Black at bottom"
        self.orientation_label.setText(f"Current: {display_text}")
        self.orientation_label.setStyleSheet("color: blue; font-style: italic;")
    
    def set_status_message(self, message: str):
        """
        Set the status message.
        
        Args:
            message (str): Status message to display.
        """
        self.image_status.setText(message)
    
    def get_fen_input(self) -> str:
        """
        Get the FEN string from the input field.
        
        Returns:
            str: FEN string entered by the user.
        """
        return self.fen_input.text().strip()
    
    def set_fen_input(self, fen: str):
        """
        Set the FEN string in the input field.
        
        Args:
            fen (str): FEN string to set.
        """
        self.fen_input.setText(fen)
    
    def reset(self):
        """Reset the control panel to initial state."""
        self.process_button.setEnabled(False)
        self.step_button.setEnabled(False)
        self.analysis_button.setEnabled(False)
        self.flip_board_button.setEnabled(False)
        self.image_status.setText("No image loaded")
        self.image_status.setStyleSheet("color: gray;")
        self.orientation_label.setText("Current: Not set")
        self.orientation_label.setStyleSheet("color: gray; font-style: italic;")
        self.fen_input.clear()
