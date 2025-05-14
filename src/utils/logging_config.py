import logging
import os


def setup_logging(default_level=logging.INFO, log_file="game_debug.log"):
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
