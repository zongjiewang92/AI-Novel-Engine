"""改稿 agent：按审稿意见重写本章（只改有问题的部分，保持优点）。"""
import json

from llm import provider
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


def revise_chapter(context, draft, critique):
    issues = critique.get("issues", [])
    issues_text = "\n".join(
        f"{i + 1}. [{it.get('severity', '?')}/{it.get('type', '?')}] "
        f"{it.get('description', '')}\n   建议：{it.get('suggestion', '')}"
        for i, it in enumerate(issues)
    ) or "（无具体问题，按总体评分改进）"

    prompt = render_prompt(
        "revise",
        novel_title=context.config["novel"]["title"],
        current_chapter=context.novel_state["current_chapter"],
        score=critique.get("score", "?"),
        issues=issues_text,
        draft=draft,
    )
    logger.info("按审稿意见改稿中…")
    return provider.chat("revise", prompt, context.config)
