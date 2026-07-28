import logging
from pathlib import Path
from datetime import datetime

_initialized = False


def setup_logger(project_root):

    global _initialized

    if _initialized:

        return

    root = Path(project_root)

    log_dir = root / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{datetime.now():%Y-%m-%d}.log"

    formatter = logging.Formatter(
        "%(asctime)s " "[%(levelname)s] " "%(name)s: " "%(message)s"
    )

    # root logger

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    # console

    console = logging.StreamHandler()

    console.setFormatter(formatter)

    # file

    file_handler = logging.FileHandler(log_file, encoding="utf-8")

    file_handler.setFormatter(formatter)

    logger.addHandler(console)

    logger.addHandler(file_handler)

    _initialized = True


def get_logger(name):

    return logging.getLogger(name)
