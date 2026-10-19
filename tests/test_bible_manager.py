import tempfile
import unittest
from pathlib import Path

from database.bible_manager import Bible


def _seed_bible(root):
    bdir = Path(root) / "bible"
    bdir.mkdir(parents=True)
    (bdir / "characters.yaml").write_text(
        "characters:\n  - name: 林玄\n    role: 主角\n", encoding="utf-8")
    (bdir / "power_system.yaml").write_text(
        "stages: [学徒级, 行星级]\nrules:\n  - 不可跨大境界战斗\n", encoding="utf-8")
    (bdir / "foreshadowing.yaml").write_text(
        "hooks:\n"
        "  - {id: FH001, description: 晶核之谜, planted_in: 1, status: planted, resolved_in: null}\n"
        "  - {id: FH002, description: 已填的坑, planted_in: 2, status: resolved, resolved_in: 5}\n",
        encoding="utf-8")


class TestBible(unittest.TestCase):
    def test_load_and_format(self):
        with tempfile.TemporaryDirectory() as d:
            _seed_bible(d)
            bible = Bible.load(d)
            sections = bible.format_sections()
            self.assertIn("林玄", sections["characters"])
            self.assertIn("不可跨大境界战斗", sections["world_rules"])
            self.assertIn("学徒级", sections["power_system"])

    def test_unresolved_only(self):
        with tempfile.TemporaryDirectory() as d:
            _seed_bible(d)
            bible = Bible.load(d)
            unresolved = bible.unresolved_foreshadowing()
            self.assertEqual([h["id"] for h in unresolved], ["FH001"])
            self.assertIn("FH001", bible.format_sections()["foreshadowing"])
            self.assertNotIn("FH002", bible.format_sections()["foreshadowing"])

    def test_add_and_resolve_hook(self):
        with tempfile.TemporaryDirectory() as d:
            _seed_bible(d)
            bible = Bible.load(d)
            new_id = bible.add_hook("新伏笔", planted_in=7)
            self.assertEqual(new_id, "FH003")
            self.assertTrue(bible.resolve_hook("FH001", resolved_in=8))
            # 重新加载确认落盘
            bible2 = Bible.load(d)
            self.assertEqual([h["id"] for h in bible2.unresolved_foreshadowing()],
                             ["FH003"])

    def test_missing_bible_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            bible = Bible.load(d)
            self.assertEqual(bible.format_sections(), {})
            self.assertEqual(bible.unresolved_foreshadowing(), [])


if __name__ == "__main__":
    unittest.main()
