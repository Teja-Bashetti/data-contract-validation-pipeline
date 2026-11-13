
import logging
from pathlib import Path


def get_logger(name="data_pipeline"):
    """
    Create a logger that writes messages
    to both the terminal and a log file.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid creating duplicate handlers
    if not logger.handlers:

        log_directory = Path("logs")
        log_directory.mkdir(exist_ok=True)

        log_format = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        # Save logs to a file
        file_handler = logging.FileHandler(
            log_directory / "pipeline.log",
            encoding="utf-8"
        )
        file_handler.setFormatter(log_format)

        # Display logs in the terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.propagate = False

    return logger
