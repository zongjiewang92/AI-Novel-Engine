"""写章节 agent：按 token 预算组装 prompt，超预算时低优先级材料先降级。"""
import json

from llm.ollama_client import chat, get_llm_params
from llm.token_budget import estimate_tokens, fit_to_budget, DEFAULT_MAX_PROMPT_TOKENS
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

# section key → 中文名（仅用于日志）
SECTION_NAMES = {
    "current_plot": "未来剧情规划",
    "world_rules": "世界规则",
    "story_goal": "本卷目标",
    "chapter_history": "最近章节正文",
    "characters": "人物资料",
    "chapter_memory": "最近章节摘要",
    "story_summary": "长期记忆",
    "timeline": "时间线",
}

# (优先级, 模板占位符) —— 数字越小越重要，超预算时从后往前截断/丢弃
SECTION_PRIORITIES = [
    (1, "current_plot"),
    (2, "world_rules"),
    (3, "story_goal"),
    (4, "chapter_history"),
    (5, "characters"),
    (6, "chapter_memory"),
    (7, "story_summary"),
    (8, "timeline"),
]


def _fmt_dict_section(d):
    if not d:
        return "（无）"
    if isinstance(d, dict):
        return "\n\n".join(f"## {k}\n{v}" for k, v in d.items())
    return str(d)


def write_chapter(context):
    config = context.config
    novel_title = config["novel"]["title"]
    current_chapter = context.novel_state["current_chapter"]
    protagonist = context.novel_state.get("protagonist", {})

    volume_cfg = context.volume.get("volume", {})
    volume_line = f"{volume_cfg.get('name', '')}（第 {volume_cfg.get('id', '?')} 卷）"
    story_goal = context.volume.get("story_goal", [])
    story_goal_text = "\n".join(f"- {g}" for g in story_goal) or "（无）"

    protagonist_block = (
        f"姓名：{protagonist.get('name', '？')}\n"
        f"境界：{protagonist.get('level', '？')}\n"
        f"位置：{protagonist.get('location', '？')}\n"
        f"能力：{'、'.join(protagonist.get('abilities', [])) or '？'}"
    )

    history = context.chapter_history or []
    history_text = "\n\n".join(
        f"--- {h['chapter']} ---\n{h['content']}" for h in history
    ) or "（无）"

    raw_sections = {
        "current_plot": json.dumps(context.current_plot, ensure_ascii=False, indent=2),
        "world_rules": _fmt_dict_section(context.world_rules),
        "story_goal": story_goal_text,
        "chapter_history": history_text,
        "characters": _fmt_dict_section(context.characters),
        "chapter_memory": json.dumps(context.chapter_memory, ensure_ascii=False, indent=2),
        "story_summary": json.dumps(context.story_summary, ensure_ascii=False, indent=2),
        "timeline": _fmt_dict_section(context.timeline),
    }

    # ---- token 预算 ----
    gen_cfg = config.get("generation", {})
    max_prompt = gen_cfg.get("max_prompt_tokens", DEFAULT_MAX_PROMPT_TOKENS)
    skeleton = render_prompt(
        "writer", novel_title="", volume_line="", story_goal="",
        current_plot="", world_rules="", story_summary="", chapter_memory="",
        characters="", timeline="", chapter_history="", protagonist_block="",
        current_chapter="",
    )
    budget = max_prompt - estimate_tokens(skeleton)
    sections = [(prio, key, raw_sections[key]) for prio, key in SECTION_PRIORITIES]
    kept, dropped = fit_to_budget(sections, budget)

    fitted = {key: "" for _, key in SECTION_PRIORITIES}
    for key, text, truncated in kept:
        fitted[key] = text
        if truncated:
            logger.warning("prompt 超预算，[%s] 已截断", SECTION_NAMES[key])
    for key in dropped:
        logger.warning("prompt 超预算，[%s] 已丢弃", SECTION_NAMES[key])

    prompt = render_prompt(
        "writer",
        novel_title=novel_title,
        volume_line=volume_line,
        protagonist_block=protagonist_block,
        current_chapter=current_chapter,
        **fitted,
    )
    total = estimate_tokens(prompt)
    logger.info("prompt 约 %s tokens（预算 %s）", total, max_prompt)

    return chat(prompt, **get_llm_params(config))
