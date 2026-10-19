"""Prompt 模板加载：prompts/*.txt + str.format 渲染。

把 prompt 从代码里抽出来：调 prompt 不用改代码，git 即有版本，
模板与调用方的参数对应关系由单元测试守护。
注意：模板里的 JSON 示例需用双花括号 {{ }} 转义。
"""
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def render_prompt(name, **kwargs):
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"prompt 模板不存在: {path}")
    template = path.read_text(encoding="utf-8")
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise KeyError(f"prompt 模板 '{name}' 缺少参数: {e}")
