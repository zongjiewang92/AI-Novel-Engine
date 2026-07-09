import logging
from pathlib import Path
from datetime import datetime


def get_logger(name, project_path=None):

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # =================================
    # log目录
    # =================================

    if project_path:

        log_dir = Path(project_path) / "logs" / datetime.now().strftime("%Y-%m-%d")

    else:

        log_dir = Path("logs") / datetime.now().strftime("%Y-%m-%d")

    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "novel_engine.log"

    # =================================
    # console
    # =================================

    console = logging.StreamHandler()

    console.setLevel(logging.INFO)

    # =================================
    # file
    # =================================

    file_handler = logging.FileHandler(log_file, encoding="utf-8")

    file_handler.setLevel(logging.INFO)

    # =================================
    # format
    # =================================

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    console.setFormatter(formatter)

    file_handler.setFormatter(formatter)

    logger.addHandler(console)

    logger.addHandler(file_handler)

    return logger
