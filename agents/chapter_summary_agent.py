"""章节总结 agent：输出 JSON，带自修复的容错解析。走 summarize 任务路由。"""
from llm import provider
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

TASK = "summarize"


def summarize_chapter(context, chapter_content, chapter_number):
    prompt = render_prompt(
        "chapter_summary",
        novel_title=context.config["novel"]["title"],
        chapter_number=chapter_number,
        chapter_content=chapter_content,
    )
    result = provider.chat(TASK, prompt, context.config)
    return parse_json_with_repair(
        result, lambda p: provider.chat(TASK, p, context.config))
