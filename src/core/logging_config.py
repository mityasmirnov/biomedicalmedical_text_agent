"""
Logging configuration for the Biomedical Data Extraction Engine.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger
from core.config import get_config

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward loguru sinks."""
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging(config_override: Optional[dict] = None) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        config_override: Optional dictionary to override default config
    """
    config = get_config()
    
    # Remove default handler
    logger.remove()
    
    # Get log level
    log_level = config.monitoring.log_level.upper()
    if config_override and 'log_level' in config_override:
        log_level = config_override['log_level'].upper()
    
    # Console handler with colors and formatting
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # File handler if log file is specified
    log_file = config.monitoring.log_file
    if config_override and 'log_file' in config_override:
        log_file = config_override['log_file']
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level: {log_level}")
    if log_file:
        logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module/logger
        
    Returns:
        Configured logger instance
    """
    return logger.bind(name=name)

# Module-level logger
log = get_logger(__name__)

