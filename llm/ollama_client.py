"""Ollama 调用封装。

模型参数（model / temperature / max_tokens）从项目 config.yaml 的
model / generation 节读取 —— 改配置即生效，不再是摆设。
"""
import ollama

DEFAULT_MODEL = "qwen2.5:14b"
DEFAULT_TEMPERATURE = 0.7


def get_llm_params(config):
    """从项目配置里解析 LLM 参数，供各 agent 调用 chat 时传入。"""
    config = config or {}
    model_cfg = config.get("model", {})
    gen_cfg = config.get("generation", {})
    return {
        "model": model_cfg.get("name", DEFAULT_MODEL),
        "temperature": gen_cfg.get("temperature", DEFAULT_TEMPERATURE),
        # config 里叫 max_tokens，ollama 里叫 num_predict
        "num_predict": gen_cfg.get("max_tokens"),
    }


def chat(prompt, model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE,
         num_predict=None):
    options = {"temperature": temperature}
    if num_predict:
        options["num_predict"] = num_predict
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=options,
    )
    return response["message"]["content"]
