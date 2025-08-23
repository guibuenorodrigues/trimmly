import logging


def get_logger() -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)


logger = get_logger()
