import json
from contextvars import ContextVar
from datetime import UTC, datetime
from logging import Filter, Formatter, LogRecord, StreamHandler, config, makeLogRecord
from typing import Any

from dotenv import load_dotenv

load_dotenv()

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

SERVICE_NAME = "web-backend"


class RequestContextFilter(Filter):
    """
    Include the current request ID to each log record

    :param record LogRecord: The log record
    :return bool: Whether the record should be processed
    """

    def filter(self, record: LogRecord) -> bool:
        """
        Provide request ID to the log record

        :param record LogRecord: The log record
        :return bool: Whether the record should be carry out
        """
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(Formatter):
    """
    Format log records as JSON strings

    """

    def format(self, record: LogRecord) -> str:
        """
        Convert a log record to JSON string

        :param record LogRecord: The log record
        :return str: JSON string containing the log record fields
        """
        payload: dict[str, Any] = {
            "service": SERVICE_NAME,
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        # logger.info("...", extra={...}) except some reserved fields
        standard_fields = set(makeLogRecord({}).__dict__)
        for key, value in record.__dict__.items():
            if (
                key not in standard_fields
                and key not in payload
                and not key.startswith("_")
            ):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_context": {"()": RequestContextFilter},
    },
    "formatters": {
        "json": {"()": JsonFormatter},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
            "filters": ["request_context"],
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        # JSON-format for Uvicorn root handler
        "uvicorn": {"handlers": [], "propagate": True},
        "uvicorn.error": {"handlers": [], "propagate": True},
        "uvicorn.access": {"handlers": [], "propagate": True},
    },
}


def configure_logging_handler() -> None:
    """
    Logger creation or obtaining with file handler rotation

    """
    config.dictConfig(LOGGING_CONFIG)
