import unittest

from llm.json_utils import extract_json, parse_json_with_repair


class TestExtractJson(unittest.TestCase):
    def test_direct(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})

    def test_fenced(self):
        self.assertEqual(extract_json('```json\n{"a": 1}\n```'), {"a": 1})

    def test_prose_wrapped(self):
        self.assertEqual(extract_json('好的：{"a": 1}，完毕'), {"a": 1})

    def test_no_json_raises(self):
        with self.assertRaises(Exception):
            extract_json("这里没有 json")


class TestParseWithRepair(unittest.TestCase):
    def test_repair_called_once(self):
        calls = []

        def fake_chat(prompt):
            calls.append(prompt)
            return '{"a": 2}'

        out = parse_json_with_repair('{"a": }', fake_chat, retries=1)
        self.assertEqual(out, {"a": 2})
        self.assertEqual(len(calls), 1)
        self.assertIn("解析错误", calls[0])

    def test_gives_up(self):
        with self.assertRaises(ValueError):
            parse_json_with_repair("###", lambda p: "###", retries=1)


if __name__ == "__main__":
    unittest.main()
