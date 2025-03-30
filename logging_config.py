"""Logging configuration for the Fretboard Trainer application."""

import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration for the application.
    
    Args:
        log_level: The logging level to use (default: "INFO")
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(
        log_dir / "fretboard_trainer.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logging.info("Fretboard Trainer application started") 