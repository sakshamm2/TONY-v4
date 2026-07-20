"""
Module   : core.logger
Project  : T.O.N.Y. v4
Purpose  : Centralized Logging and Telemetry Engine
"""

from __future__ import annotations
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

class TonyLogger:
    """
    Singleton-style logger factory providing structured, rotating, 
    and thread-safe logging to both the console and 'tony.log'.
    """
    
    _initialized: bool = False
    _log_dir: str = "logs"
    _log_file: str = "tony.log"
    
    # Standard format: [2026-07-19 15:38:06] [INFO] [core.ai] : Engine online.
    _format: str = "[%(asctime)s] [%(levelname)s] [%(name)s] : %(message)s"
    _date_format: str = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def initialize(cls) -> None:
        """
        Bootstraps the root logging configuration. 
        Should be called once during system startup.
        """
        if cls._initialized:
            return

        # Ensure the logs directory exists
        os.makedirs(cls._log_dir, exist_ok=True)
        log_path = os.path.join(cls._log_dir, cls._log_file)

        # Create a unified formatter
        formatter = logging.Formatter(fmt=cls._format, datefmt=cls._date_format)

        # ==========================================================
        # File Handler (with auto-rotation at 5MB, keeping 3 backups)
        # ==========================================================
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # ==========================================================
        # Console Handler (Standard Output)
        # ==========================================================
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # ==========================================================
        # Root Logger Configuration
        # ==========================================================
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing default handlers to prevent duplicate prints
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        cls._initialized = True
        logging.getLogger("core.logger").info("TonyLogger initialized successfully.")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Retrieves a named logger instance for specific subsystem tracking.
        Automatically initializes the root logger if it hasn't been already.
        
        Usage:
            log = TonyLogger.get_logger(__name__)
            log.info("System booted.")
        """
        if not cls._initialized:
            cls.initialize()
            
        return logging.getLogger(name)

    @classmethod
    def get_log_path(cls) -> str:
        """Returns the absolute path to the active tony.log file."""
        return os.path.abspath(os.path.join(cls._log_dir, cls._log_file))