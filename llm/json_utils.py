"""LLM 结构化输出的容错解析。

总结/规划类 agent 都要求模型输出 JSON，但裸 json.loads
遇到多余字符就崩。本模块提供带自修复的解析：
先尽力提取，失败则把原文 + 错误信息喂回模型修复。
"""
import json
import re

_FENCED_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text):
    """尽力从文本里抠出 JSON：直接解析 → 去 markdown fence → 找 {...} 块。"""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = _FENCED_RE.search(text)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass
    m = _JSON_BLOCK_RE.search(text)
    if m:
        return json.loads(m.group(0))  # 仍失败则抛出，由调用方处理
    raise json.JSONDecodeError("no JSON object found", text, 0)


def parse_json_with_repair(raw_text, chat_fn, retries=2):
    """解析失败时把原文 + 错误信息喂回模型做修复，最多 retries 次。

    chat_fn: 无参数之外的可调用对象，接受 prompt 返回文本。
    """
    last_err = None
    text = raw_text
    for attempt in range(retries + 1):
        try:
            return extract_json(text)
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            if attempt >= retries:
                break
            repair_prompt = (
                "下面这段文本应该是一段合法 JSON，但解析失败了。\n"
                f"解析错误：{e}\n\n原文：\n{text}\n\n"
                "请只输出修复后的 JSON，不要解释，不要加 markdown 包裹。"
            )
            text = chat_fn(repair_prompt)
    raise ValueError(f"JSON 解析失败（已重试 {retries} 次）: {last_err}")
