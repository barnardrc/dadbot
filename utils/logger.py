# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 14:22:36 2024

@author: barna
"""

import logging
from logging.handlers import RotatingFileHandler
import time
import re
import os
import colorlog

# Custom logger level
NOTICE_LEVEL = 15  # Between DEBUG and INFO

# Register the custom level
logging.addLevelName(NOTICE_LEVEL, "NOTICE")

class ExcludeLevelFilter(logging.Filter):
    def __init__(self, level_to_exclude):
        super().__init__()
        self.level_to_exclude = level_to_exclude
    
    def filter(self, record):
        # Only allow records whose level is not the one you want to exclude
        return record.levelno != self.level_to_exclude
    
def file_name_formatter(save_path):
    unwanted_chars = r'(),'
    local_time = time.localtime()[0:3]
    local_time_str = re.sub(r'[{}]'.format(unwanted_chars), '', str(local_time)).replace(' ', '_')
    filename = f"{local_time_str}_dadbotlog.log"
    return os.path.join(save_path, filename)

def notice(self, message, *args, **kwargs):
    """
    Logs a message with the custom NOTICE level.
    """
    if self.isEnabledFor(NOTICE_LEVEL):
        # Use stacklevel to adjust caller location
        kwargs["stacklevel"] = kwargs.get("stacklevel", 2)  # Adjust if nested
        self._log(NOTICE_LEVEL, message, args, **kwargs)

logging.Logger.notice = notice

def configure_logger(
    log_save_path="logs/",
    logger_name="dadbot",
    level=logging.NOTSET,
    max_file_size=5_000_000,
    backup_count=3
    ):
    """
    Configures and initializes a shared logger.
    """
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        return logger  # Avoid reconfiguring if already set up
    
    logger.setLevel(level)
    
    # Setup ColoredFormatter for console
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s %(asctime)s [%(levelname)s] [%(module)s:%(lineno)d]: %(message)s",
        datefmt="%I:%M:%S %p",
        log_colors={
            "DEBUG": "cyan",
            "NOTICE": "bold_cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
    )

    # Create log directory if it doesn't exist
    os.makedirs(log_save_path, exist_ok=True)

    # File handler for logging to file (Plain Formatter)
    file_handler = RotatingFileHandler(
        file_name_formatter(log_save_path),
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(module)s]: %(message)s",
        datefmt="%I:%M:%S %p"
    ))

    # Console handler for colored output
    console_handler = colorlog.StreamHandler()
    console_handler.addFilter(ExcludeLevelFilter(logging.INFO))  # Exclude INFO level in console
    console_handler.setFormatter(color_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize the logger for the application
logger = configure_logger(log_save_path=r'C:\Users\barna\OneDrive\Documents\1. Documents\01. dadbot')

