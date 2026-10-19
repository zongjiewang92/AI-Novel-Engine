"""守护模板与调用方的参数对应关系：模板增减占位符时这里会先报警。"""
import string
import unittest
from pathlib import Path

from utils.prompt_loader import PROMPTS_DIR, render_prompt


def _placeholders(name):
    text = (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")
    return {fn for _, fn, _, _ in string.Formatter().parse(text) if fn}


class TestPromptLoader(unittest.TestCase):
    def test_all_templates_render_with_their_placeholders(self):
        names = [p.stem for p in PROMPTS_DIR.glob("*.txt")]
        self.assertGreaterEqual(len(names), 5, "prompt 模板不应少于 5 个")
        for name in names:
            kwargs = {k: "" for k in _placeholders(name)}
            try:
                render_prompt(name, **kwargs)
            except KeyError as e:
                self.fail(f"模板 {name} 渲染失败: {e}")

    def test_chapter_summary_content(self):
        out = render_prompt("chapter_summary", novel_title="测试书",
                            chapter_number=3, chapter_content="正文")
        self.assertIn("测试书", out)
        self.assertIn("第 3 章", out)

    def test_missing_param_raises_keyerror(self):
        with self.assertRaises(KeyError):
            render_prompt("chapter_summary", novel_title="x")

    def test_missing_template_raises(self):
        with self.assertRaises(FileNotFoundError):
            render_prompt("not_a_template")


if __name__ == "__main__":
    unittest.main()
