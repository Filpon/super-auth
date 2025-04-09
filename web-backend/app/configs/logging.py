import os

from loguru import logger

# Configure Loguru logger using environment variables
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "")

logger.add(
    "../logs/logfile.log",
    rotation="1 MB",
    retention="10 days",
    level=log_level,
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
