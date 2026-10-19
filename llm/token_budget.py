"""Token 预算：组装 prompt 时的配额管理。

长篇连载里 prompt 只增不减（章节全文、人物设定、世界观……），
没有预算迟早撑爆 context。本模块提供：
- estimate_tokens: 无 tokenizer 时的保守启发式估算
- fit_to_budget: 按优先级装配 sections，超预算时从低优先级开始截断/丢弃
"""
import re

_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")

# qwen2.5:14b 上下文 32k；给输出预留空间，默认 prompt 上限 24k。
# 可在 config.yaml 的 generation.max_prompt_tokens 里覆盖。
DEFAULT_MAX_PROMPT_TOKENS = 24000


def estimate_tokens(text) -> int:
    """保守估算 token 数：CJK 约 1.2 token/字，其余约 1 token/4 字符。"""
    if not text:
        return 0
    s = str(text)
    cjk = len(_CJK_RE.findall(s))
    return int(cjk * 1.2 + (len(s) - cjk) / 4)


def fit_to_budget(sections, max_tokens):
    """把 sections 按优先级装入预算。

    sections: [(priority, key, text)]，priority 越小越重要。
    返回 (kept, dropped)：
      kept: [(key, text, truncated)]，已按优先级排序；
      dropped: 被整段丢弃的 key 列表。
    超预算时先截断最低优先级（保留头部），实在装不下再整段丢弃。
    """
    ordered = sorted(sections, key=lambda s: s[0])
    kept, dropped = [], []
    remaining = max_tokens
    for _, key, text in ordered:
        need = estimate_tokens(text)
        if need <= remaining:
            kept.append((key, text, False))
            remaining -= need
        elif remaining > 300:
            # 截断：按 token 比例折算字符数，保留头部并打标记
            ratio = remaining / need
            cut = int(len(text) * ratio * 0.9)
            kept.append((key, text[:cut] + "\n……（内容过长已截断）", True))
            remaining = 0
        else:
            dropped.append(key)
    return kept, dropped
