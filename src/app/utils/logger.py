import logging, os

def get_logger():
    level = logging.getLevelName(os.getenv("log_level", "INFO"))
    logger = logging.getLogger()
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger