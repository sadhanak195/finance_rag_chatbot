"""
Logger module: configures Python logging (console + rotating file handler).
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

def setup_logger():
    """Set up application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger("src")
    logger.setLevel(logging.INFO)
    
    # Avoid adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Rotating file handler (e.g., max 5MB, keep 3 backups)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Initialize logger globally for the src package
setup_logger()
