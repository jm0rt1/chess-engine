"""
Main Entry Point for Chess Engine Application.

This module initializes logging and launches the Chess Engine GUI application.
"""

import logging
import logging.handlers
from src.shared.settings import GlobalSettings
from src.gui.chess_app import main as gui_main


def initialize_logging():
    """
    Initialize the logging system for the application.
    
    Sets up rotating file handlers and configures log levels
    according to GlobalSettings.
    """
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add file handler for global logs
    file_handler = logging.handlers.RotatingFileHandler(
        GlobalSettings.GLOBAL_LOGS_DIR/GlobalSettings.LoggingParams.GLOBAL_FILE_NAME,
        backupCount=GlobalSettings.LoggingParams.BACKUP_COUNT)

    logging.getLogger().addHandler(file_handler)
    file_handler.doRollover()
    logging.info("Global Logging Started")


def main():
    """
    Main entry point for the Chess Engine application.
    
    Initializes logging and launches the GUI application.
    """
    # Initialize logging system
    initialize_logging()
    
    logging.info("Starting Chess Engine Application")
    
    # Launch GUI
    gui_main()
