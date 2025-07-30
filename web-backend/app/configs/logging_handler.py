from logging import INFO, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# Configure logging
LOG_LEVEL: Final[int] = INFO
LOG_FILE: Final[str] = Path(__file__).resolve().parent.parent / "logs" / "logfile.log"
MAX_BYTES: Final[int] = (
    5 * 1024 * 1024
)  # Maximum file size in bytes before rotation - currently 5 MB
BACKUP_COUNT: Final[int] = 3  # Backup files number


def configure_logging_handler(
    log_file: str = LOG_FILE,
    level: int = LOG_LEVEL,
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
) -> Logger:
    """
    Logger creation or obtaining with file handler rotation

    :param str log_file: The file to which logs will be written
    :param int level: Logging level
    :param int max_bytes: The maximum file size in bytes before rotation
    :param int backup_count: The number of backup files to keep
    :return Logger logger: Configured logger instance
    """
    # Creation or get the logger
    logger = getLogger(__name__)
    logger.setLevel(level)

    # Multiple handlers prevention if the logger is configured multiple times
    if not logger.handlers:
        # Log format
        formatter = Formatter(
            fmt="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        # File handler
        file_handler = RotatingFileHandler(
            filename=log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        # Console handler
        console_handler = StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
