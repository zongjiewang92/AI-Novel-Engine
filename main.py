import sys

from agents.writer_agent import write_chapter
from agents.memory_agent import MemoryAgent
from agents.critic_agent import CriticAgent
from agents.planner_agent import PlannerAgent
from agents.character_agent import CharacterAgent

from database.project_manager import ProjectManager
from database.project_context import ProjectContext
from database.memory_manager import MemoryManager
from database.character_manager import CharacterManager

from utils.logger import get_logger
from pathlib import Path


def save_chapter(content, context):

    target = context.target
    output = context.output

    volume = target["volume"]
    chapter = target["chapter"]

    # ==============================
    # 输出目录
    # ==============================

    root = context.root / output["directory"]

    chapter_dir = root / volume / "chapters" / chapter

    chapter_dir.mkdir(parents=True, exist_ok=True)

    file = chapter_dir / f"{chapter}.md"

    with open(file, "w", encoding="utf-8") as f:

        f.write(content)

    print(f"章节已保存: {file}")

    return file


# ==================================================
# Planning检查
# ==================================================
def ensure_planning(context):
    planner = PlannerAgent(context)
    if not context.current_plan:
        logger.warning("当前planning不存在，开始生成")
        # plan = planner.generate_plan()
        # context.planning_manager.save_plan(context.target, plan)
        return False

    return True


# ==================================================
# Writer
# ==================================================


def generate_chapter(context):
    logger.info("开始生成章节")
    return write_chapter(context)


# ==================================================
# Critic
# ==================================================


def review_chapter(context, chapter):

    logger.info("开始章节审核")

    critic = CriticAgent(context)

    result = critic.review_chapter(chapter)

    logger.info(f"审核评分:{result['score']}")

    return result


# ==================================================
# Memory
# ==================================================


def generate_memory(context, chapter):

    logger.info("开始生成Memory")

    agent = MemoryAgent(context)

    memories = {}

    # -----------------------
    # Chapter Memory
    # -----------------------

    chapter_memory = agent.create_chapter_memory(chapter, context.target["chapter"])

    memories["chapter"] = chapter_memory

    # -----------------------
    # Character Memory
    # -----------------------

    character_memory = agent.update_character_memory(chapter_memory)

    memories["characters"] = character_memory

    # -----------------------
    # Plot Memory
    # -----------------------

    if context.is_plot_finished:

        logger.info("Plot结束，更新Plot Memory")

        memories["plot"] = agent.update_plot_memory(chapter_memory)

    # -----------------------
    # Arc Memory
    # -----------------------

    if context.is_arc_finished:

        logger.info("Arc结束，更新Arc Memory")

        memories["arc"] = agent.update_arc_memory(context.plot_memories)

    # -----------------------
    # Volume Memory
    # -----------------------

    if context.is_volume_finished:

        logger.info("Volume结束，更新Volume Memory")

        memories["volume"] = agent.update_volume_memory(context.arc_memories)

    return memories


def update_character_memory(context, chapter_memory):
    logger.info("更新人物系统")

    agent = CharacterAgent(context)

    result = agent.process(chapter_memory)

    logger.info(f"更新人物数量:{len(result)}")


# ==================================================
# 保存
# ==================================================


def save_result(context, chapter, memories):

    memory_manager = MemoryManager(context.root)

    # -----------------------
    # 保存正文
    # -----------------------
    save_chapter(chapter, context)

    # -----------------------
    # 保存所有Memory
    # -----------------------

    memory_manager.save_all(context.target, memories)

    logger.info("章节和Memory保存完成")


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    project = ProjectManager("swallowing_star_fanfic")

    logger = get_logger(__name__, project.root)

    logger.info("小说引擎启动")

    # ==================================
    # Context
    # ==================================

    context = ProjectContext(project.root)

    logger.info(str(context.task))

    # ==================================
    # Planning
    # ==================================

    if not ensure_planning(context):

        logger.info("Planning生成完成，请重新运行")

        sys.exit(0)

    # ==================================
    # Writer
    # ==================================

    chapter = generate_chapter(context)

    # ==================================
    # Critic
    # ==================================

    review = review_chapter(context, chapter)

    if not review["pass"]:

        logger.warning("章节审核失败")

        sys.exit(1)

    # ==================================
    # Memory
    # ==================================

    memories = generate_memory(context, chapter)

    # ==================================
    # 8. 保存章节和基础memory
    # ==================================
    save_result(context, chapter, memories)

    # ==================================
    # 9. 更新人物长期Memory
    # ==================================
    update_character_memory(context, memories["chapter"])

    logger.info("本章生成完成")
