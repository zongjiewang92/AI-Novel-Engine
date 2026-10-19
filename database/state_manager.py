"""state / story_summary 的读写。一律原子写，不留半截文件。"""
import json
from pathlib import Path

from utils.file_utils import save_json_atomic


def load_state(state_file: Path):
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state_file: Path, state: dict):
    save_json_atomic(state_file, state)


def load_summary(summary_file: Path):
    if not summary_file.exists():
        return {"main_story": "", "important_events": [], "character_changes": []}
    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_summary(summary_file: Path, summary):
    save_json_atomic(summary_file, summary)
