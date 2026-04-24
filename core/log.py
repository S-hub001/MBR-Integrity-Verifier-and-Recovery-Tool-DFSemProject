import os
import logging
from datetime import datetime


def setup_logger():
    """
    Initializes forensic logging system.
    Creates logs/log.txt if not exists.
    """

    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_path = "logs/log.txt"

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logging.info("=== FORENSIC SESSION STARTED ===")


def write_log(message, level="info"):
    """
    Write log entry with level control.
    """

    if level.lower() == "warning":
        logging.warning(message)
    elif level.lower() == "error":
        logging.error(message)
    else:
        logging.info(message)