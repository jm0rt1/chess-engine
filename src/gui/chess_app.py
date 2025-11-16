"""
Chess Application GUI Module.

This module provides the main graphical user interface for the chess engine
application using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Optional, List
import logging
from pathlib import Path
import chess
import cv2
import numpy as np
from PIL import Image, ImageTk

from src.chess_engine.board_manager import BoardManager
from src.chess_engine.threat_analyzer import ThreatAnalyzer
from src.chess_engine.move_suggester import MoveSuggester
from src.computer_vision.board_detector import BoardDetector
from src.computer_vision.piece_recognizer import PieceRecognizer


class ChessEngineGUI:
    """
    Main GUI application for the Chess Engine.
    
    This class provides a graphical interface for:
    - Loading chess board screenshots
    - Recognizing pieces with user confirmation
    - Analyzing threats
    - Suggesting best moves with explanations
    - Displaying board state
    
    Attributes:
        root (tk.Tk): Main Tkinter window.
        board_manager (BoardManager): Chess board manager.
        threat_analyzer (ThreatAnalyzer): Threat analyzer.
        move_suggester (MoveSuggester): Move suggester.
        board_detector (BoardDetector): Computer vision board detector.
        piece_recognizer (PieceRecognizer): Piece recognizer.
        logger (logging.Logger): Application logger.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the Chess Engine GUI.
        
        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Chess Engine with Computer Vision")
        self.root.geometry("1400x900")
        
        # Initialize chess engine components
        self.board_manager = BoardManager()
        self.threat_analyzer = ThreatAnalyzer(self.board_manager)
        self.move_suggester = MoveSuggester(self.board_manager)
        
        # Initialize computer vision components
        self.board_detector = BoardDetector()
        self.piece_recognizer = PieceRecognizer()
        
        # State variables
        self.current_image = None
        self.detected_board = None
        self.recognition_results = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Build the GUI
        self._build_gui()
        
        self.logger.info("Chess Engine GUI initialized")

    def _build_gui(self):
        """
        Build the GUI layout and widgets.
        
        Creates the main interface with sections for:
        - Image loading and display
        - Board recognition and confirmation
        - Analysis results
        - Move suggestions
        """
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # === Left Panel: Controls and Info ===
        left_panel = ttk.Frame(main_container, padding="5")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            left_panel,
            text="Chess Engine",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Load Image Section
        load_frame = ttk.LabelFrame(left_panel, text="1. Load Image", padding="10")
        load_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.load_button = ttk.Button(
            load_frame,
            text="Load Screenshot",
            command=self.load_image
        )
        self.load_button.grid(row=0, column=0, pady=5)
        
        self.image_status_label = ttk.Label(load_frame, text="No image loaded")
        self.image_status_label.grid(row=1, column=0, pady=5)
        
        # Recognize Section
        recognize_frame = ttk.LabelFrame(
            left_panel,
            text="2. Recognize Pieces",
            padding="10"
        )
        recognize_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.recognize_button = ttk.Button(
            recognize_frame,
            text="Detect & Recognize",
            command=self.recognize_board,
            state=tk.DISABLED
        )
        self.recognize_button.grid(row=0, column=0, pady=5)
        
        self.confirm_button = ttk.Button(
            recognize_frame,
            text="Confirm Position",
            command=self.confirm_position,
            state=tk.DISABLED
        )
        self.confirm_button.grid(row=1, column=0, pady=5)
        
        # Manual FEN Entry
        fen_frame = ttk.LabelFrame(
            left_panel,
            text="Manual Position Entry",
            padding="10"
        )
        fen_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(fen_frame, text="FEN String:").grid(row=0, column=0, sticky=tk.W)
        self.fen_entry = ttk.Entry(fen_frame, width=30)
        self.fen_entry.grid(row=1, column=0, pady=5)
        
        self.set_fen_button = ttk.Button(
            fen_frame,
            text="Set Position",
            command=self.set_position_from_fen
        )
        self.set_fen_button.grid(row=2, column=0, pady=5)
        
        # Analysis Section
        analysis_frame = ttk.LabelFrame(
            left_panel,
            text="3. Analyze",
            padding="10"
        )
        analysis_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.analyze_threats_button = ttk.Button(
            analysis_frame,
            text="Analyze Threats",
            command=self.analyze_threats
        )
        self.analyze_threats_button.grid(row=0, column=0, pady=5)
        
        self.suggest_moves_button = ttk.Button(
            analysis_frame,
            text="Suggest Best Moves",
            command=self.suggest_moves
        )
        self.suggest_moves_button.grid(row=1, column=0, pady=5)
        
        # Reset button
        self.reset_button = ttk.Button(
            left_panel,
            text="Reset Board",
            command=self.reset_board
        )
        self.reset_button.grid(row=5, column=0, pady=10)
        
        # === Top Right Panel: Image Display ===
        image_frame = ttk.LabelFrame(
            main_container,
            text="Chess Board Image",
            padding="10"
        )
        image_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Canvas for image display
        self.image_canvas = tk.Canvas(
            image_frame,
            width=600,
            height=400,
            bg='white'
        )
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # === Bottom Right Panel: Analysis Results ===
        results_frame = ttk.LabelFrame(
            main_container,
            text="Analysis Results",
            padding="10"
        )
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(10, 0))
        
        # Notebook for tabbed results
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Board state tab
        self.board_text = scrolledtext.ScrolledText(
            self.results_notebook,
            width=60,
            height=10,
            font=("Courier", 10)
        )
        self.results_notebook.add(self.board_text, text="Board State")
        
        # Threats tab
        self.threats_text = scrolledtext.ScrolledText(
            self.results_notebook,
            width=60,
            height=10,
            font=("Courier", 10)
        )
        self.results_notebook.add(self.threats_text, text="Threats")
        
        # Best moves tab
        self.moves_text = scrolledtext.ScrolledText(
            self.results_notebook,
            width=60,
            height=10,
            font=("Courier", 10)
        )
        self.results_notebook.add(self.moves_text, text="Best Moves")
        
        # Initialize board display
        self.update_board_display()

    def load_image(self):
        """
        Load a chess board screenshot from file.
        
        Opens a file dialog for the user to select an image file,
        loads it, and displays it in the GUI.
        """
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Chess Board Screenshot",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Load image using OpenCV
        self.current_image = self.board_detector.load_image(file_path)
        
        if self.current_image is None:
            messagebox.showerror("Error", "Failed to load image")
            return
        
        # Display image
        self.display_image(self.current_image)
        
        # Update status
        self.image_status_label.config(text=f"Loaded: {Path(file_path).name}")
        self.recognize_button.config(state=tk.NORMAL)
        
        self.logger.info(f"Image loaded: {file_path}")

    def display_image(self, image: np.ndarray):
        """
        Display an OpenCV image on the canvas.
        
        Args:
            image (np.ndarray): OpenCV image to display.
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to fit canvas while maintaining aspect ratio
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # Use default size if canvas not yet rendered
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        h, w = image_rgb.shape[:2]
        scale = min(canvas_width / w, canvas_height / h)
        new_width = int(w * scale)
        new_height = int(h * scale)
        
        resized = cv2.resize(image_rgb, (new_width, new_height))
        
        # Convert to PIL Image and then to ImageTk
        pil_image = Image.fromarray(resized)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        # Keep a reference to prevent garbage collection
        self.image_canvas.image = tk_image
        
        # Clear canvas and display image
        self.image_canvas.delete("all")
        self.image_canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=tk_image,
            anchor=tk.CENTER
        )

    def recognize_board(self):
        """
        Detect and recognize the chess board from the loaded image.
        
        Uses computer vision to detect the board, extract squares,
        and recognize pieces.
        """
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        # Show progress
        self.image_status_label.config(text="Detecting board...")
        self.root.update()
        
        # Detect board
        detection_result = self.board_detector.detect_board(self.current_image)
        
        if detection_result is None:
            # Try with full image as board
            h, w = self.current_image.shape[:2]
            detection_result = self.board_detector.detect_board(
                self.current_image,
                manual_region=(0, 0, w, h)
            )
        
        if detection_result is None:
            messagebox.showerror(
                "Error",
                "Could not detect chess board. Please try a different image."
            )
            self.image_status_label.config(text="Detection failed")
            return
        
        board_image, squares = detection_result
        self.detected_board = (board_image, squares)
        
        # Display detected board
        self.display_image(board_image)
        self.image_status_label.config(text="Recognizing pieces...")
        self.root.update()
        
        # Recognize pieces
        self.recognition_results = self.piece_recognizer.recognize_board(squares)
        
        # Generate FEN and display for confirmation
        fen = self.piece_recognizer.results_to_fen(self.recognition_results)
        
        # Show FEN in entry
        self.fen_entry.delete(0, tk.END)
        self.fen_entry.insert(0, fen)
        
        # Update board display with recognized position
        if self.board_manager.set_position_from_fen(fen):
            self.update_board_display()
            self.image_status_label.config(text="Recognition complete - Please confirm")
            self.confirm_button.config(state=tk.NORMAL)
            
            # Ask user to confirm
            message = "Board position recognized!\n\n"
            message += "Please review the board state in the 'Board State' tab.\n"
            message += "If correct, click 'Confirm Position' to proceed with analysis."
            messagebox.showinfo("Recognition Complete", message)
        else:
            messagebox.showerror("Error", "Invalid board position recognized")
            self.image_status_label.config(text="Invalid position")

    def confirm_position(self):
        """
        Confirm the recognized board position.
        
        User confirms that the recognized position is correct,
        enabling analysis features.
        """
        response = messagebox.askyesno(
            "Confirm Position",
            "Is the recognized board position correct?\n\n"
            "Click 'Yes' to proceed with analysis.\n"
            "Click 'No' to manually edit the FEN string."
        )
        
        if response:
            self.image_status_label.config(text="Position confirmed")
            messagebox.showinfo(
                "Success",
                "Position confirmed! You can now analyze threats and get move suggestions."
            )
            self.logger.info("User confirmed board position")
        else:
            messagebox.showinfo(
                "Manual Edit",
                "Please edit the FEN string and click 'Set Position'"
            )

    def set_position_from_fen(self):
        """
        Set the board position from the FEN string in the entry field.
        """
        fen = self.fen_entry.get().strip()
        
        if not fen:
            messagebox.showwarning("Warning", "Please enter a FEN string")
            return
        
        if self.board_manager.set_position_from_fen(fen):
            self.update_board_display()
            messagebox.showinfo("Success", "Position set successfully!")
            self.logger.info(f"Position set from FEN: {fen}")
        else:
            messagebox.showerror("Error", "Invalid FEN string")

    def update_board_display(self):
        """
        Update the board state display in the text widget.
        """
        self.board_text.delete(1.0, tk.END)
        
        # Display ASCII board
        board_str = str(self.board_manager)
        self.board_text.insert(tk.END, board_str + "\n\n")
        
        # Display FEN
        self.board_text.insert(tk.END, f"FEN: {self.board_manager.get_fen()}\n\n")
        
        # Display game state
        turn = "White" if self.board_manager.get_turn() == chess.WHITE else "Black"
        self.board_text.insert(tk.END, f"Turn: {turn}\n")
        
        if self.board_manager.is_checkmate():
            self.board_text.insert(tk.END, "Status: CHECKMATE\n")
        elif self.board_manager.is_check():
            self.board_text.insert(tk.END, "Status: CHECK\n")
        elif self.board_manager.is_stalemate():
            self.board_text.insert(tk.END, "Status: STALEMATE\n")
        else:
            self.board_text.insert(tk.END, "Status: Normal\n")

    def analyze_threats(self):
        """
        Analyze threats in the current position and display results.
        """
        self.threats_text.delete(1.0, tk.END)
        
        # Get threat summary
        summary = self.threat_analyzer.get_threat_summary()
        self.threats_text.insert(tk.END, summary)
        
        # Switch to threats tab
        self.results_notebook.select(1)
        
        self.logger.info("Threat analysis completed")

    def suggest_moves(self):
        """
        Get best move suggestions with explanations and display them.
        """
        self.moves_text.delete(1.0, tk.END)
        
        # Get best moves
        best_moves = self.move_suggester.get_best_moves(num_moves=5)
        
        if not best_moves:
            self.moves_text.insert(tk.END, "No legal moves available (game over)")
            return
        
        # Display each move with explanation
        self.moves_text.insert(tk.END, "=== BEST MOVES ===\n\n")
        
        for i, move_eval in enumerate(best_moves, 1):
            self.moves_text.insert(tk.END, f"{i}. Move: {move_eval.move.uci()}\n")
            self.moves_text.insert(tk.END, f"   Score: {move_eval.score:.2f}\n")
            self.moves_text.insert(tk.END, f"   Explanation: {move_eval.explanation}\n")
            
            if move_eval.tactical_themes:
                themes = ", ".join(move_eval.tactical_themes)
                self.moves_text.insert(tk.END, f"   Themes: {themes}\n")
            
            self.moves_text.insert(tk.END, "\n")
        
        # Switch to best moves tab
        self.results_notebook.select(2)
        
        self.logger.info(f"Generated {len(best_moves)} move suggestions")

    def reset_board(self):
        """
        Reset the board to starting position.
        """
        self.board_manager.reset()
        self.update_board_display()
        
        # Clear analysis results
        self.threats_text.delete(1.0, tk.END)
        self.moves_text.delete(1.0, tk.END)
        
        messagebox.showinfo("Reset", "Board reset to starting position")
        self.logger.info("Board reset")


def main():
    """
    Main entry point for the GUI application.
    
    Creates and runs the Tkinter application.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run GUI
    root = tk.Tk()
    app = ChessEngineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
