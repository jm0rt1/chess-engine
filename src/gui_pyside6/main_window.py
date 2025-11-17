"""
Main Window Module for PySide6 Chess Engine GUI.

This module provides the main application window that coordinates all
GUI components and integrates the chess engine with computer vision.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QLabel, QFileDialog,
    QMessageBox, QTabWidget, QStatusBar
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QAction, QIcon
import logging
from pathlib import Path
from typing import Optional
import numpy as np
import chess

from src.chess_engine.board_manager import BoardManager
from src.chess_engine.threat_analyzer import ThreatAnalyzer
from src.chess_engine.move_suggester import MoveSuggester
from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer

from .widgets.pipeline_widget import PipelineVisualizationWidget
from .widgets.board_widget import BoardReconstructionWidget
from .widgets.analysis_widget import EngineAnalysisWidget
from .widgets.control_panel import ControlPanelWidget


class MainWindow(QMainWindow):
    """
    Main application window for the Chess Engine GUI.
    
    This window provides a comprehensive interface for:
    - Loading and processing chess board images
    - Visualizing the complete image processing pipeline
    - Reconstructing and verifying the board position
    - Running chess engine analysis
    - Displaying threat maps and move suggestions
    
    Attributes:
        board_manager (BoardManager): Chess board state manager.
        threat_analyzer (ThreatAnalyzer): Threat analysis engine.
        move_suggester (MoveSuggester): Move suggestion engine.
        board_detector (BoardDetector): Computer vision board detector.
        piece_recognizer (PieceRecognizer): Piece recognition system.
        logger (logging.Logger): Application logger.
    """
    
    def __init__(self):
        """Initialize the main window and all components."""
        super().__init__()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize chess engine components
        self.board_manager = BoardManager()
        self.threat_analyzer = ThreatAnalyzer(self.board_manager)
        self.move_suggester = MoveSuggester(self.board_manager)
        
        # Initialize computer vision components
        self.board_detector = BoardDetector()
        self.piece_recognizer = PieceRecognizer()
        
        # State variables
        self.current_image: Optional[np.ndarray] = None
        self.detected_board: Optional[tuple] = None
        self.recognition_results: Optional[list] = None
        
        # Set up the UI
        self._setup_ui()
        self._setup_menu_bar()
        self._connect_signals()
        
        self.logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the main user interface layout."""
        self.setWindowTitle("Chess Engine - Image Processing & Analysis")
        self.setMinimumSize(1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter for resizable sections
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Control Panel
        self.control_panel = ControlPanelWidget()
        main_splitter.addWidget(self.control_panel)
        
        # Center and right: Visualization panels
        right_splitter = QSplitter(Qt.Vertical)
        
        # Top: Pipeline visualization
        self.pipeline_widget = PipelineVisualizationWidget()
        right_splitter.addWidget(self.pipeline_widget)
        
        # Middle: Tab widget for board and analysis
        self.tab_widget = QTabWidget()
        
        # Board reconstruction tab
        self.board_widget = BoardReconstructionWidget()
        self.tab_widget.addTab(self.board_widget, "Board Reconstruction")
        
        # Engine analysis tab
        self.analysis_widget = EngineAnalysisWidget()
        self.tab_widget.addTab(self.analysis_widget, "Engine Analysis")
        
        right_splitter.addWidget(self.tab_widget)
        
        # Set initial sizes
        right_splitter.setSizes([400, 500])
        
        main_splitter.addWidget(right_splitter)
        
        # Set initial sizes for main splitter
        main_splitter.setSizes([300, 1100])
        
        main_layout.addWidget(main_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load an image to begin")
    
    def _setup_menu_bar(self):
        """Set up the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        load_action = QAction("&Load Image...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Process menu
        process_menu = menu_bar.addMenu("&Process")
        
        process_action = QAction("&Process Image", self)
        process_action.setShortcut("Ctrl+P")
        process_action.triggered.connect(self.process_image)
        process_menu.addAction(process_action)
        
        step_action = QAction("&Step Through Pipeline", self)
        step_action.setShortcut("Ctrl+S")
        step_action.triggered.connect(self.step_through_pipeline)
        process_menu.addAction(step_action)
        
        # Analysis menu
        analysis_menu = menu_bar.addMenu("&Analysis")
        
        analyze_action = QAction("Run &Engine Analysis", self)
        analyze_action.setShortcut("Ctrl+E")
        analyze_action.triggered.connect(self.run_engine_analysis)
        analysis_menu.addAction(analyze_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect widget signals to handler slots."""
        # Control panel signals
        self.control_panel.load_image_signal.connect(self.load_image)
        self.control_panel.process_image_signal.connect(self.process_image)
        self.control_panel.step_through_signal.connect(self.step_through_pipeline)
        self.control_panel.run_analysis_signal.connect(self.run_engine_analysis)
        self.control_panel.reset_signal.connect(self.reset_application)
        
        # Pipeline widget signals
        self.pipeline_widget.stage_selected.connect(self.on_pipeline_stage_selected)
    
    def load_image(self):
        """
        Load a chess board image from file.
        
        Opens a file dialog for the user to select an image,
        loads it using the board detector, and displays it.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Chess Board Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not file_path:
            return
        
        self.logger.info(f"Loading image: {file_path}")
        self.status_bar.showMessage(f"Loading image: {Path(file_path).name}")
        
        # Load image
        self.current_image = self.board_detector.load_image(file_path)
        
        if self.current_image is None:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to load image. Please check the file format."
            )
            self.status_bar.showMessage("Failed to load image")
            return
        
        # Display raw image in pipeline widget
        self.pipeline_widget.set_raw_image(self.current_image)
        
        # Update status
        self.status_bar.showMessage(f"Loaded: {Path(file_path).name} - Ready to process")
        self.control_panel.enable_process_button(True)
        
        self.logger.info(f"Image loaded successfully: {self.current_image.shape}")
    
    def process_image(self):
        """
        Process the loaded image through the complete pipeline.
        
        This method runs all image processing stages and updates
        the visualization widgets with intermediate results.
        """
        if self.current_image is None:
            QMessageBox.warning(
                self,
                "Warning",
                "Please load an image first."
            )
            return
        
        self.logger.info("Starting image processing pipeline")
        self.status_bar.showMessage("Processing image...")
        
        try:
            # Step 1: Preprocess image
            self.status_bar.showMessage("Step 1/7: Preprocessing...")
            preprocessed = self.board_detector.preprocess_image(self.current_image)
            self.pipeline_widget.set_preprocessing_result(self.current_image, preprocessed)
            
            # Step 2: Detect contours
            self.status_bar.showMessage("Step 2/7: Detecting contours...")
            contours = self.board_detector.detect_board_contours(preprocessed)
            self.pipeline_widget.set_contours(self.current_image, contours)
            
            # Step 3: Detect board
            self.status_bar.showMessage("Step 3/7: Detecting board region...")
            detection_result = self.board_detector.detect_board(self.current_image)
            
            if detection_result is None:
                # Try with full image as board
                h, w = self.current_image.shape[:2]
                detection_result = self.board_detector.detect_board(
                    self.current_image,
                    manual_region=(0, 0, w, h)
                )
            
            if detection_result is None:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Could not detect chess board. Please try a different image."
                )
                self.status_bar.showMessage("Board detection failed")
                return
            
            board_image, squares = detection_result
            self.detected_board = (board_image, squares)
            
            # Step 4: Show board region
            self.status_bar.showMessage("Step 4/7: Extracting board...")
            self.pipeline_widget.set_board_region(board_image)
            
            # Step 5: Show square segmentation
            self.status_bar.showMessage("Step 5/7: Segmenting squares...")
            self.pipeline_widget.set_squares(squares)
            
            # Step 6: Recognize pieces
            self.status_bar.showMessage("Step 6/7: Recognizing pieces...")
            self.recognition_results = self.piece_recognizer.recognize_board(squares)
            self.pipeline_widget.set_recognition_results(squares, self.recognition_results)
            
            # Step 7: Generate FEN and update board
            self.status_bar.showMessage("Step 7/7: Generating board position...")
            fen = self.piece_recognizer.results_to_fen(self.recognition_results)
            
            if self.board_manager.set_position_from_fen(fen):
                # Update board reconstruction widget
                self.board_widget.set_board_state(self.board_manager)
                self.board_widget.set_recognition_results(self.recognition_results)
                
                # Switch to board reconstruction tab
                self.tab_widget.setCurrentIndex(0)
                
                self.status_bar.showMessage("Processing complete - Review the board position")
                self.control_panel.enable_analysis_button(True)
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Processing Complete",
                    "Board position recognized successfully!\n\n"
                    "Please review the board reconstruction and run engine analysis."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to parse the recognized board position."
                )
                self.status_bar.showMessage("Invalid board position")
        
        except Exception as e:
            self.logger.error(f"Error during image processing: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during processing:\n{str(e)}"
            )
            self.status_bar.showMessage("Processing failed")
    
    def step_through_pipeline(self):
        """
        Step through the image processing pipeline interactively.
        
        Allows users to see each stage of the pipeline one at a time.
        """
        if self.current_image is None:
            QMessageBox.warning(
                self,
                "Warning",
                "Please load an image first."
            )
            return
        
        # Enable stepping mode in pipeline widget
        self.pipeline_widget.enable_step_mode()
        self.status_bar.showMessage("Step-through mode enabled - Use Next/Previous buttons")
    
    def on_pipeline_stage_selected(self, stage_name: str):
        """
        Handle when a pipeline stage is selected.
        
        Args:
            stage_name (str): Name of the selected stage.
        """
        self.status_bar.showMessage(f"Viewing: {stage_name}")
    
    def run_engine_analysis(self):
        """
        Run chess engine analysis on the current board position.
        
        Performs threat analysis and generates move suggestions,
        then displays the results in the analysis widget.
        """
        if self.board_manager.get_fen() == chess.STARTING_FEN:
            QMessageBox.warning(
                self,
                "Warning",
                "Please process an image or set a board position first."
            )
            return
        
        self.logger.info("Running engine analysis")
        self.status_bar.showMessage("Running engine analysis...")
        
        try:
            # Analyze threats
            threat_summary = self.threat_analyzer.get_threat_summary()
            
            # Get best moves
            best_moves = self.move_suggester.get_best_moves(num_moves=5)
            
            # Update analysis widget
            self.analysis_widget.set_board_state(self.board_manager)
            self.analysis_widget.set_threat_analysis(threat_summary)
            self.analysis_widget.set_best_moves(best_moves)
            
            # Switch to analysis tab
            self.tab_widget.setCurrentIndex(1)
            
            self.status_bar.showMessage("Engine analysis complete")
            
            self.logger.info("Engine analysis completed successfully")
        
        except Exception as e:
            self.logger.error(f"Error during engine analysis: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during analysis:\n{str(e)}"
            )
            self.status_bar.showMessage("Analysis failed")
    
    def reset_application(self):
        """Reset the application to initial state."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset the application?\n"
            "This will clear all current work.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear state
            self.current_image = None
            self.detected_board = None
            self.recognition_results = None
            
            # Reset board
            self.board_manager.reset()
            
            # Clear widgets
            self.pipeline_widget.clear()
            self.board_widget.clear()
            self.analysis_widget.clear()
            
            # Reset control panel
            self.control_panel.reset()
            
            self.status_bar.showMessage("Application reset - Load an image to begin")
            self.logger.info("Application reset")
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Chess Engine",
            "<h2>Chess Engine with Computer Vision</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A comprehensive chess engine application that uses computer vision "
            "to recognize chess positions from images and provides detailed "
            "analysis including threat detection and move suggestions.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Image processing pipeline visualization</li>"
            "<li>Automatic piece recognition</li>"
            "<li>Board reconstruction and verification</li>"
            "<li>Threat analysis and move suggestions</li>"
            "</ul>"
            "<p>Built with PySide6, OpenCV, and python-chess.</p>"
        )


def main():
    """
    Main entry point for the PySide6 Chess Engine GUI application.
    
    Creates and runs the Qt application with the main window.
    """
    import sys
    from PySide6.QtWidgets import QApplication
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Chess Engine")
    app.setOrganizationName("Chess Engine Project")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
