import tempfile
import unittest
from pathlib import Path

from database.state_manager import save_state, load_state, save_summary, load_summary


class TestStateManager(unittest.TestCase):
    def test_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state" / "novel_state.json"
            save_state(p, {"current_chapter": 7, "current_volume_id": 1})
            loaded = load_state(p)
            self.assertEqual(loaded["current_chapter"], 7)

    def test_summary_missing_file_returns_default(self):
        with tempfile.TemporaryDirectory() as d:
            s = load_summary(Path(d) / "missing.json")
            self.assertEqual(s, {"main_story": "", "important_events": [],
                                 "character_changes": []})

    def test_summary_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "story_summary.json"
            save_summary(p, {"main_story": "x", "important_events": ["e"],
                             "character_changes": {}})
            self.assertEqual(load_summary(p)["main_story"], "x")


if __name__ == "__main__":
    unittest.main()
