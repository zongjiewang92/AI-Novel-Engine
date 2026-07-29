import logging
from pathlib import Path
from datetime import datetime

# ==================================================
# Repository Root
# ==================================================

REPO_ROOT = Path(__file__).resolve().parent.parent

# ==================================================
# Logger
# ==================================================

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.handlers:

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File
    file_handler = logging.FileHandler(
        REPO_ROOT / f"{datetime.now():%Y-%m-%d}.log", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# ==================================================
# API
# ==================================================


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
