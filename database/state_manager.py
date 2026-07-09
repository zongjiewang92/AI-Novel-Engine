import json
from pathlib import Path


# =====================
# state
# =====================
def load_state(state_file: Path):
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state_file: Path, state: dict):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


# =====================
# summary
# =====================
def load_summary(summary_file: Path):
    if not summary_file.exists():
        return {"main_story": "", "important_events": [], "character_changes": []}

    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_summary(summary_file: Path, summary):
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
