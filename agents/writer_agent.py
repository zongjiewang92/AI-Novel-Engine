"""写章节 agent：按 token 预算组装 prompt，bible 优先于散装 knowledge。"""
import json

from llm import provider
from llm.token_budget import estimate_tokens, fit_to_budget, DEFAULT_MAX_PROMPT_TOKENS
from utils.prompt_loader import render_prompt
from utils.logger import get_logger
from database.bible_manager import Bible

logger = get_logger(__name__)

# section key → 中文名（仅用于日志）
SECTION_NAMES = {
    "current_plot": "未来剧情规划",
    "world_rules": "世界规则",
    "foreshadowing": "未回收伏笔",
    "story_goal": "本卷目标",
    "chapter_history": "最近章节正文",
    "characters": "人物资料",
    "power_system": "力量体系",
    "chapter_memory": "最近章节摘要",
    "story_summary": "长期记忆",
    "timeline": "时间线",
    "factions": "势力",
    "locations": "地点",
}

# (优先级, 模板占位符) —— 数字越小越重要，超预算时从后往前截断/丢弃
SECTION_PRIORITIES = [
    (1, "current_plot"),
    (2, "world_rules"),
    (3, "foreshadowing"),
    (4, "story_goal"),
    (5, "chapter_history"),
    (6, "characters"),
    (7, "power_system"),
    (8, "chapter_memory"),
    (9, "story_summary"),
    (10, "timeline"),
    (11, "factions"),
    (12, "locations"),
]


def _fmt_dict_section(d):
    if not d:
        return "（无）"
    if isinstance(d, dict):
        return "\n\n".join(f"## {k}\n{v}" for k, v in d.items())
    return str(d)


def _pick(bible_text, knowledge_text):
    """bible 有内容用 bible，否则回退到 knowledge/ 的散装 md。"""
    return bible_text or knowledge_text or "（无）"


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

    bible_sections = Bible.load(context.root).format_sections()

    raw_sections = {
        "current_plot": json.dumps(context.current_plot, ensure_ascii=False, indent=2),
        "world_rules": _pick(bible_sections.get("world_rules"),
                             _fmt_dict_section(context.world_rules)),
        "foreshadowing": bible_sections.get("foreshadowing", "（暂无未回收伏笔）"),
        "story_goal": story_goal_text,
        "chapter_history": history_text,
        "characters": _pick(bible_sections.get("characters"),
                            _fmt_dict_section(context.characters)),
        "power_system": bible_sections.get("power_system", "（无）"),
        "chapter_memory": json.dumps(context.chapter_memory, ensure_ascii=False, indent=2),
        "story_summary": json.dumps(context.story_summary, ensure_ascii=False, indent=2),
        "timeline": _pick(bible_sections.get("timeline"),
                          _fmt_dict_section(context.timeline)),
        "factions": bible_sections.get("factions", "（无）"),
        "locations": bible_sections.get("locations", "（无）"),
    }

    # ---- token 预算 ----
    gen_cfg = config.get("generation", {})
    max_prompt = gen_cfg.get("max_prompt_tokens", DEFAULT_MAX_PROMPT_TOKENS)
    skeleton = render_prompt(
        "writer", novel_title="", volume_line="", story_goal="",
        current_plot="", world_rules="", power_system="", foreshadowing="",
        factions="", locations="", story_summary="", chapter_memory="",
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

    return provider.chat("write_chapter", prompt, config)
