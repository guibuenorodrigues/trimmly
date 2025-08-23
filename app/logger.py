import logging
import shutil
from pathlib import Path


def clear_existing_logs() -> None:
    """
    Clear existing log files and reset logger configurations.
    Call this manually when needed to reset logging state.
    """
    # First close all file handlers to release file locks
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

    # Close root logger handlers too
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            root_logger.removeHandler(handler)

    # Now safely remove log files
    log_dir = Path("logs")
    if log_dir.exists():
        try:
            shutil.rmtree(log_dir)
            print("Removed existing logs directory")
        except PermissionError:
            print("Could not remove logs directory - files may be in use")

    # Clear all loggers in the logging manager
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.filters.clear()
        logger.propagate = True
        logger.setLevel(logging.NOTSET)

    # Reset root logger
    root_logger.handlers.clear()
    root_logger.filters.clear()
    root_logger.setLevel(logging.WARNING)

    print("Cleared all existing logger configurations")


def configure_unified_logging(enable_file_logging: bool | None = None) -> None:
    """
    Configure unified logging for the entire application, including FastAPI/Uvicorn.
    """
    # Determine if file logging should be enabled
    if enable_file_logging is None:
        try:
            from app.config import settings

            file_logging_enabled = settings.ENABLE_FILE_LOGGING
        except Exception:
            file_logging_enabled = True
    else:
        file_logging_enabled = enable_file_logging

    # Create unified formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if file_logging_enabled:
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / "trimmly.log", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")

    # Configure specific loggers to use the same format
    loggers_to_configure = ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "trimmly"]

    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True  # Let root logger handle the formatting


def get_logger(name: str = "trimmly", enable_file_logging: bool | None = None) -> logging.Logger:
    """
    Get a logger instance that writes to a single log file for the entire application.

    Args:
        name: Logger name (defaults to 'trimmly' for single log instance)
        enable_file_logging: Whether to enable file logging. If None, uses config setting.

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


# Single logger instance for the entire application
logger = get_logger()
