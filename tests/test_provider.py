import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from llm.provider import (
    OllamaProvider, OpenAICompatProvider, PRESETS,
    resolve_task_config, get_provider, chat,
)


class TestResolveConfig(unittest.TestCase):
    def test_task_overrides_default(self):
        cfg = {"llm": {"default": {"provider": "ollama", "model": "qwen2.5:14b"},
                       "tasks": {"write_chapter": {"provider": "deepseek",
                                                   "model": "deepseek-chat"}}}}
        rc = resolve_task_config("write_chapter", cfg)
        self.assertEqual(rc["provider"], "deepseek")
        self.assertEqual(rc["model"], "deepseek-chat")

    def test_falls_back_to_default(self):
        cfg = {"llm": {"default": {"provider": "ollama", "model": "qwen2.5:14b"}}}
        rc = resolve_task_config("summarize", cfg)
        self.assertEqual(rc["provider"], "ollama")

    def test_legacy_config_still_works(self):
        cfg = {"model": {"name": "qwen2.5:7b"},
               "generation": {"temperature": 0.5, "max_tokens": 2000}}
        rc = resolve_task_config("write_chapter", cfg)
        self.assertEqual(rc["model"], "qwen2.5:7b")
        self.assertEqual(rc["temperature"], 0.5)
        self.assertEqual(rc["max_tokens"], 2000)

    def test_empty_config_defaults(self):
        rc = resolve_task_config("write_chapter", {})
        self.assertEqual(rc["provider"], "ollama")
        self.assertEqual(rc["model"], "qwen2.5:14b")

    def test_unknown_task_uses_default(self):
        rc = resolve_task_config("not_a_task", {})
        self.assertEqual(rc["provider"], "ollama")

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            resolve_task_config("x", {"llm": {"default": {"provider": "nope"}}})


class TestProviderConstruction(unittest.TestCase):
    def test_ollama_needs_no_key(self):
        p = get_provider("write_chapter", {})
        self.assertIsInstance(p, OllamaProvider)

    def test_missing_api_key_raises_helpful_error(self):
        from unittest import mock
        cfg = {"llm": {"tasks": {"write_chapter": {"provider": "deepseek",
                                                   "model": "deepseek-chat"}}}}
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as cm:
                get_provider("write_chapter", cfg)
            self.assertIn("DEEPSEEK_API_KEY", str(cm.exception))

    def test_presets_have_base_urls(self):
        for name in ("deepseek", "qwen", "moonshot", "openai"):
            self.assertTrue(PRESETS[name]["base_url"].startswith("https://"))


class _Handler(BaseHTTPRequestHandler):
    received = {}

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        _Handler.received = {"path": self.path,
                             "auth": self.headers.get("Authorization"),
                             "body": body}
        if self.path.startswith("/boom"):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"server exploded")
            return
        resp = json.dumps({"choices": [{"message": {"content": "你好"}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, *a):
        pass


class TestOpenAICompatProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _provider(self, path=""):
        return OpenAICompatProvider(
            model="test-model",
            base_url=f"http://127.0.0.1:{self.port}{path}",
            api_key="sk-test",
        )

    def test_chat_sends_correct_request(self):
        out = self._provider().chat("hi", temperature=0.3, max_tokens=100)
        self.assertEqual(out, "你好")
        r = _Handler.received
        self.assertEqual(r["path"], "/chat/completions")
        self.assertEqual(r["auth"], "Bearer sk-test")
        self.assertEqual(r["body"]["model"], "test-model")
        self.assertEqual(r["body"]["messages"], [{"role": "user", "content": "hi"}])
        self.assertEqual(r["body"]["temperature"], 0.3)
        self.assertEqual(r["body"]["max_tokens"], 100)

    def test_http_error_raises(self):
        with self.assertRaises(RuntimeError) as cm:
            self._provider("/boom").chat("hi", temperature=0.7, max_tokens=None)
        self.assertIn("HTTP 500", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
