"""章节生成流水线：步骤注册表。

设计原则：
1. 所有 LLM 调用（易失败）先于任何落盘（难回滚）——中途崩了重跑是安全的。
2. 落盘一律原子写（tmp + rename），不留半截文件。
3. 生成步骤幂等：本章产物已存在则复用，不重复烧 token。
4. 写→审→改：初稿经 critic 审稿，不合格自动改稿（轮数可在 config 里配，0 关闭）。
5. 加新步骤只需在 STEPS 里注册一行，不用改编排逻辑。

各步骤签名：fn(ctx, results) -> 输出；STEPS 元素为 (名称, 函数, 结果键名)。
"""
import json

from agents.writer_agent import write_chapter
from agents.critic_agent import critique_chapter
from agents.reviser_agent import revise_chapter
from agents.chapter_summary_agent import summarize_chapter
from agents.volume_summary_agent import summarize_volume
from agents.planner_agent import create_plot_plan
from agents.memory_agent import update_story_summary

from database.project_manager import ProjectManager
from database.project_context import ProjectContext
from database.state_manager import save_state, save_summary
from database.memory_manager import (
    save_chapter_memory,
    save_volume_memory,
    save_plot_memory,
)
from utils.file_utils import save_chapter, read_chapter
from utils.logger import get_logger

logger = get_logger(__name__)

# 每 N 章做一次卷总结 + 长期记忆合并
SUMMARY_EVERY_N_CHAPTERS = 10


def _chapter_file(ctx, n):
    return ctx.volume_path / "chapters" / f"chapter_{n:04d}.md"


def _chapter_memory_file(ctx, n):
    return ctx.volume_path / "memory" / "chapter_summary" / f"chapter{n:04d}.json"


def _critique_cfg(ctx):
    gen = ctx.config.get("generation", {})
    return {
        "rounds": gen.get("critique_rounds", 1),
        "threshold": gen.get("critic_threshold", 7),
    }


def step_generate_chapter(ctx, results):
    n = ctx.novel_state["current_chapter"]
    path = _chapter_file(ctx, n)
    if path.exists():
        logger.info("第 %s 章正文已存在，复用（不重新生成）", n)
        return read_chapter(path)
    logger.info("正在生成第 %s 章…", n)
    return write_chapter(ctx)


def step_critique_and_revise(ctx, results):
    """审稿 + 改稿：verdict=revise 或评分低于阈值则改，最多 rounds 轮。"""
    cfg = _critique_cfg(ctx)
    if not cfg["rounds"]:
        logger.info("审稿已关闭（critique_rounds=0），跳过")
        return {"verdict": "pass", "score": None, "issues": []}

    draft = results["chapter"]
    critique = critique_chapter(ctx, draft)
    attempts = 0
    while attempts < cfg["rounds"]:
        score = critique.get("score")
        needs_revise = (
            critique.get("verdict") == "revise"
            or (isinstance(score, (int, float)) and score < cfg["threshold"])
        )
        if not needs_revise:
            break
        logger.info("审稿 %s 分（阈值 %s），第 %s 轮改稿…",
                    score, cfg["threshold"], attempts + 1)
        draft = revise_chapter(ctx, draft, critique)
        results["chapter"] = draft
        critique = critique_chapter(ctx, draft)
        attempts += 1
    logger.info("审改完成：最终 %s 分，%s",
                critique.get("score"), critique.get("verdict"))
    return critique


def step_generate_chapter_memory(ctx, results):
    n = ctx.novel_state["current_chapter"]
    path = _chapter_memory_file(ctx, n)
    if path.exists():
        logger.info("第 %s 章记忆已存在，复用", n)
        return json.loads(path.read_text(encoding="utf-8"))
    logger.info("正在生成第 %s 章记忆…", n)
    return summarize_chapter(ctx, results["chapter"], n)


def step_persist(ctx, results):
    n = ctx.novel_state["current_chapter"]
    save_chapter(results["chapter"], n, ctx.volume_path / "chapters")
    save_chapter_memory(ctx, n, results["chapter_memory"])


def step_bump_state(ctx, results):
    n = ctx.novel_state["current_chapter"]
    ctx.novel_state["current_chapter"] = n + 1
    save_state(ctx.root / "state" / "novel_state.json", ctx.novel_state)
    logger.info("第 %s 章完成，章节计数推进到 %s", n, n + 1)


def step_maybe_volume_summary(ctx, results):
    fresh = ProjectContext(ctx.root)
    if fresh.chapter_count % SUMMARY_EVERY_N_CHAPTERS == 0 and fresh.chapter_count:
        logger.info("正在更新卷总结…")
        save_volume_memory(fresh, summarize_volume(fresh))
        logger.info("卷总结更新完成")


def step_maybe_plot_plan(ctx, results):
    if not ctx.plot_memory:
        logger.info("剧情规划缺失，正在生成…")
        save_plot_memory(ctx, create_plot_plan(ctx))
        logger.info("剧情规划生成完成")


def step_maybe_story_summary(ctx, results):
    finished = ctx.novel_state["current_chapter"] - 1  # 刚写完的章节号
    if finished % SUMMARY_EVERY_N_CHAPTERS == 0 and finished:
        fresh = ProjectContext(ctx.root)
        summary = update_story_summary(fresh)
        save_summary(fresh.root / "state" / "story_summary.json", summary)
        logger.info("长期记忆合并完成")


STEPS = [
    ("生成章节", step_generate_chapter, "chapter"),
    ("审稿+改稿", step_critique_and_revise, "critique"),
    ("生成章节记忆", step_generate_chapter_memory, "chapter_memory"),
    ("落盘（正文+记忆）", step_persist, None),
    ("推进章节计数", step_bump_state, None),
    ("卷总结（每10章）", step_maybe_volume_summary, None),
    ("剧情规划（缺失时）", step_maybe_plot_plan, None),
    ("长期记忆合并（每10章）", step_maybe_story_summary, None),
]


def run_pipeline(project_name):
    project = ProjectManager(project_name)
    ctx = ProjectContext(project.root)
    results = {}
    for label, fn, key in STEPS:
        logger.info("—— 步骤：%s", label)
        out = fn(ctx, results)
        if key:
            results[key] = out
    logger.info("流水线完成")
    return results
