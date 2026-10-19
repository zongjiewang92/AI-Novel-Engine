import unittest

from llm.token_budget import estimate_tokens, fit_to_budget


class TestEstimateTokens(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens(None), 0)

    def test_english(self):
        self.assertEqual(estimate_tokens("a" * 400), 100)

    def test_cjk(self):
        t = estimate_tokens("你" * 100)
        self.assertTrue(100 <= t <= 140, t)

    def test_cjk_costs_more_than_ascii(self):
        self.assertGreater(estimate_tokens("你好世界"), estimate_tokens("helloworld"))


class TestFitToBudget(unittest.TestCase):
    def test_all_fit(self):
        kept, dropped = fit_to_budget([(1, "a", "x" * 100), (2, "b", "y" * 100)], 10000)
        self.assertEqual(dropped, [])
        self.assertEqual(len(kept), 2)
        # 按优先级排序
        self.assertEqual([k for k, _, _ in kept], ["a", "b"])

    def test_drops_lowest_priority_first(self):
        big = "z" * 40000  # 约 10000 tokens
        kept, dropped = fit_to_budget([(1, "important", "a" * 100), (9, "junk", big)], 200)
        names = [k for k, _, _ in kept]
        self.assertIn("important", names)
        self.assertEqual(dropped, ["junk"])

    def test_truncates_when_close(self):
        kept, dropped = fit_to_budget([(1, "a", "x" * 4000)], 500)  # 约 1000 tokens
        self.assertEqual(dropped, [])
        self.assertEqual(len(kept), 1)
        self.assertTrue(kept[0][2])  # truncated 标记
        self.assertIn("截断", kept[0][1])


if __name__ == "__main__":
    unittest.main()
