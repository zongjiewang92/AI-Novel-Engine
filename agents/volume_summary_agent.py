"""卷总结 agent：输出 JSON，带自修复的容错解析。走 summarize 任务路由。"""
import json

from llm import provider
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

TASK = "summarize"


def summarize_volume(context):
    volume_cfg = context.volume.get("volume", {})
    volume_line = f"{volume_cfg.get('name', '')}（第 {volume_cfg.get('id', '?')} 卷）"
    prompt = render_prompt(
        "volume_summary",
        novel_title=context.config["novel"]["title"],
        volume_line=volume_line,
        volume_memory=json.dumps(context.volume_memory, ensure_ascii=False, indent=2),
        chapter_memory=json.dumps(context.chapter_memory, ensure_ascii=False, indent=2),
    )
    result = provider.chat(TASK, prompt, context.config)
    return parse_json_with_repair(
        result, lambda p: provider.chat(TASK, p, context.config))
