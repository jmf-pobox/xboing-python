"""Set up logging configuration for the application."""

import logging
import os


def setup_logging(
    default_level: int = logging.INFO, log_file: str = "game_debug.log"
) -> None:
    """Set up logging configuration for the application.

    Args:
    ----
        default_level: The default logging level (e.g., logging.INFO).
        log_file: The file to write logs to.

    """
    log_level = os.getenv("XBOING_LOGLEVEL", default_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),
            # Uncomment the next line for optional console output
            # logging.StreamHandler()
        ],
    )
