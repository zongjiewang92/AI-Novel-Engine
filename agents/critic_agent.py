"""审稿 agent：按 beat（本章剧情目标）+ bible + 未回收伏笔审稿。

输出 JSON：{"score": 1-10, "issues": [...], "verdict": "pass"|"revise"}。
用强模型（任务名 critique），这是花钱最值的一处。
"""
import json

from llm import provider
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger
from database.bible_manager import Bible

logger = get_logger(__name__)


def critique_chapter(context, draft):
    bible_sections = Bible.load(context.root).format_sections()
    history = context.chapter_history or []
    last_chapter = history[-1]["content"] if history else "（无）"

    prompt = render_prompt(
        "critique",
        novel_title=context.config["novel"]["title"],
        current_chapter=context.novel_state["current_chapter"],
        current_plot=json.dumps(context.current_plot, ensure_ascii=False, indent=2),
        foreshadowing=bible_sections.get("foreshadowing", "（暂无未回收伏笔）"),
        power_rules=bible_sections.get("world_rules", "（无）"),
        characters=bible_sections.get("characters", "（无）"),
        last_chapter=last_chapter,
        draft=draft,
    )
    logger.info("审稿中…")
    result = provider.chat("critique", prompt, context.config)
    critique = parse_json_with_repair(
        result, lambda p: provider.chat("critique", p, context.config))
    logger.info("审稿完成：%s 分，结论 %s，问题 %s 个",
                critique.get("score"), critique.get("verdict"),
                len(critique.get("issues", [])))
    return critique
