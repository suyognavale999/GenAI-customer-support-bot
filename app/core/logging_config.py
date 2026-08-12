import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)


def create_file_handler(
    filename,
    level,
):
    handler = RotatingFileHandler(
        filename=filename,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setLevel(level)

    handler.setFormatter(
        logging.Formatter(LOG_FORMAT)
    )

    return handler


def configure_logging():
    log_directory = Path("logs")

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    app_handler = create_file_handler(
        log_directory / "app.log",
        log_level,
    )

    error_handler = create_file_handler(
        log_directory / "error.log",
        logging.ERROR,
    )

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    security_handler = create_file_handler(
        log_directory / "security.log",
        logging.INFO,
    )

    security_logger = logging.getLogger(
        "app.security"
    )

    security_logger.handlers.clear()
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)

    # Prevent security logs from also entering app.log.
    security_logger.propagate = False

    for logger_name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ):
        uvicorn_logger = logging.getLogger(
            logger_name
        )

        uvicorn_logger.handlers.clear()
        uvicorn_logger.setLevel(log_level)
        uvicorn_logger.propagate = True
        