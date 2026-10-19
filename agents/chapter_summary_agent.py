"""章节总结 agent：输出 JSON，带自修复的容错解析。"""
from llm.ollama_client import chat, get_llm_params
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def summarize_chapter(context, chapter_content, chapter_number):
    params = get_llm_params(context.config)
    prompt = render_prompt(
        "chapter_summary",
        novel_title=context.config["novel"]["title"],
        chapter_number=chapter_number,
        chapter_content=chapter_content,
    )
    result = chat(prompt, **params)
    return parse_json_with_repair(result, lambda p: chat(p, **params))
