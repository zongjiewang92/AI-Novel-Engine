"""长期记忆治理：把新增章节记忆定期合并进 story_summary（记忆闭环）。

此前 story_summary.json 有存无取、从未被更新 —— 写到 100 章时
全书主线摘要依然是空的。本 agent 每 N 章跑一次，做增量合并。
"""
import json

from llm.ollama_client import chat, get_llm_params
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def update_story_summary(context):
    params = get_llm_params(context.config)
    prompt = render_prompt(
        "memory_update",
        novel_title=context.config["novel"]["title"],
        story_summary=json.dumps(context.story_summary, ensure_ascii=False, indent=2),
        recent_memories=json.dumps(context.chapter_memory, ensure_ascii=False, indent=2),
    )
    logger.info("正在合并长期记忆…")
    result = chat(prompt, **params)
    return parse_json_with_repair(result, lambda p: chat(p, **params))
