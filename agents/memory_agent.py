"""长期记忆治理：把新增章节记忆定期合并进 story_summary（记忆闭环）。

走 memory 任务路由（机械活，默认本地模型）。
"""
import json

from llm import provider
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

TASK = "memory"


def update_story_summary(context):
    prompt = render_prompt(
        "memory_update",
        novel_title=context.config["novel"]["title"],
        story_summary=json.dumps(context.story_summary, ensure_ascii=False, indent=2),
        recent_memories=json.dumps(context.chapter_memory, ensure_ascii=False, indent=2),
    )
    logger.info("正在合并长期记忆…")
    result = provider.chat(TASK, prompt, context.config)
    return parse_json_with_repair(
        result, lambda p: provider.chat(TASK, p, context.config))
