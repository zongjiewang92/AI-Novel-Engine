"""LLM provider 抽象：Ollama（本地）+ OpenAI-compatible（线上）双后端。

百万字架构下不同任务用不同模型：
- 写章节 / 审稿 / 改稿：质量敏感，走强模型（线上）
- 总结 / 规划 / 记忆合并：机械活，走便宜模型（本地）

config.yaml 配置示例：
    llm:
      default: {provider: ollama, model: qwen2.5:14b}
      tasks:
        write_chapter: {provider: deepseek, model: deepseek-chat}
        critique:      {provider: deepseek, model: deepseek-chat}
        # summarize / plan / memory 不写则走 default

线上 provider 的 key 走环境变量（绝不写进配置文件）：
    export DEEPSEEK_API_KEY=sk-...

不写 llm: 节时，完全沿用旧行为（model.name + generation + ollama）。
"""
import json
import os
import urllib.request
import urllib.error

DEFAULT_MODEL = "qwen2.5:14b"
DEFAULT_TEMPERATURE = 0.7

# 任务名（写章节/审稿/改稿/总结/规划/记忆）。未知任务名不报错，走 default。
TASKS = ("write_chapter", "critique", "revise", "summarize", "plan", "memory")


class LLMProvider:
    def chat(self, prompt, temperature, max_tokens):
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    def __init__(self, model=DEFAULT_MODEL):
        self.model = model

    def chat(self, prompt, temperature=DEFAULT_TEMPERATURE, max_tokens=None):
        import ollama
        options = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens  # ollama 叫 num_predict
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options=options,
        )
        return response["message"]["content"]


class OpenAICompatProvider(LLMProvider):
    """OpenAI-compatible /chat/completions 接口（DeepSeek/Qwen/Moonshot/OpenAI 通用）。"""

    def __init__(self, model, base_url, api_key, timeout=180):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, prompt, temperature=DEFAULT_TEMPERATURE, max_tokens=None):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"LLM 接口报错 HTTP {e.code}: {detail}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"LLM 接口连接失败: {e}")
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"LLM 返回格式异常: {str(body)[:300]}")


# provider 预设：base_url + key 的环境变量名
PRESETS = {
    "ollama":   {"cls": OllamaProvider, "api_key_env": None},
    "deepseek": {"cls": OpenAICompatProvider, "base_url": "https://api.deepseek.com",
                 "api_key_env": "DEEPSEEK_API_KEY"},
    "openai":   {"cls": OpenAICompatProvider, "base_url": "https://api.openai.com/v1",
                 "api_key_env": "OPENAI_API_KEY"},
    "qwen":     {"cls": OpenAICompatProvider,
                 "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 "api_key_env": "DASHSCOPE_API_KEY"},
    "moonshot": {"cls": OpenAICompatProvider, "base_url": "https://api.moonshot.cn/v1",
                 "api_key_env": "MOONSHOT_API_KEY"},
}


def _first(*values):
    for v in values:
        if v is not None:
            return v
    return None


def resolve_task_config(task, config):
    """合并任务配置，优先级：llm.tasks.<task> > llm.default > 旧字段 > 默认值。"""
    config = config or {}
    llm_cfg = config.get("llm", {}) or {}
    default = llm_cfg.get("default", {}) or {}
    task_cfg = (llm_cfg.get("tasks", {}) or {}).get(task, {}) or {}
    legacy_model = (config.get("model", {}) or {}).get("name")
    legacy_gen = config.get("generation", {}) or {}

    provider = task_cfg.get("provider") or default.get("provider") or "ollama"
    if provider not in PRESETS:
        raise ValueError(
            f"未知 provider '{provider}'，可选: {', '.join(sorted(PRESETS))}"
        )
    return {
        "provider": provider,
        "model": task_cfg.get("model") or default.get("model")
                 or legacy_model or DEFAULT_MODEL,
        "temperature": _first(task_cfg.get("temperature"), default.get("temperature"),
                              legacy_gen.get("temperature"), DEFAULT_TEMPERATURE),
        "max_tokens": _first(task_cfg.get("max_tokens"), default.get("max_tokens"),
                             legacy_gen.get("max_tokens")),
        "base_url": task_cfg.get("base_url") or default.get("base_url")
                    or PRESETS[provider].get("base_url"),
        "api_key_env": task_cfg.get("api_key_env") or default.get("api_key_env")
                       or PRESETS[provider].get("api_key_env"),
    }


def get_provider(task, config):
    """按任务名拿到 provider 实例（带 key 解析与缺失报错）。"""
    rc = resolve_task_config(task, config)
    preset = PRESETS[rc["provider"]]
    cls = preset["cls"]
    if cls is OllamaProvider:
        return cls(model=rc["model"])
    api_key = os.environ.get(rc["api_key_env"]) if rc["api_key_env"] else None
    if not api_key:
        raise RuntimeError(
            f"任务 '{task}' 配了线上模型 {rc['provider']}/{rc['model']}，"
            f"但环境变量 {rc['api_key_env']} 未设置。\n"
            f"执行：export {rc['api_key_env']}=sk-... 后再跑。"
        )
    return cls(model=rc["model"], base_url=rc["base_url"], api_key=api_key)


def chat(task, prompt, config, temperature=None, max_tokens=None):
    """按任务路由的统一入口。显式传入的 temperature/max_tokens 覆盖配置。"""
    rc = resolve_task_config(task, config)
    provider = get_provider(task, config)
    return provider.chat(
        prompt,
        temperature=rc["temperature"] if temperature is None else temperature,
        max_tokens=rc["max_tokens"] if max_tokens is None else max_tokens,
    )
