"""Module to create logger for each module."""

import logging

LOGGING_LEVEL = logging.DEBUG


def create_logger(name: str) -> logging.Logger:
    """Function to create logger.

    :param name:
    Name of logger will be *databaise.name* or *databaise* when name is *""*
    :return:
    """
    logger = logging.getLogger("databaise") if name == "" else logging.getLogger(f"databaise.{name}")
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter("%(asctime)s - %(name)s.%(funcName)s - %(levelname)s: %(message)s")

    file_handler = logging.FileHandler("last_run.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(LOGGING_LEVEL)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOGGING_LEVEL)
    logger.addHandler(console_handler)

    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = False

    return logger