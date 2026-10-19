import tempfile
import unittest
from pathlib import Path

from utils.file_utils import atomic_write, save_chapter, read_chapter, save_json_atomic


class TestAtomicWrite(unittest.TestCase):
    def test_roundtrip_and_no_tmp_left(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "f.txt"
            atomic_write(p, "你好，世界")
            self.assertEqual(p.read_text(encoding="utf-8"), "你好，世界")
            self.assertEqual(list(Path(d).rglob(".tmp-*")), [])

    def test_save_json_atomic(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            save_json_atomic(p, {"a": [1, 2]})
            import json
            self.assertEqual(json.loads(p.read_text(encoding="utf-8")), {"a": [1, 2]})


class TestChapterIO(unittest.TestCase):
    def test_save_and_read(self):
        with tempfile.TemporaryDirectory() as d:
            f = save_chapter("正文内容", 7, Path(d))
            self.assertEqual(f.name, "chapter_0007.md")
            self.assertEqual(read_chapter(f), "正文内容")


if __name__ == "__main__":
    unittest.main()
