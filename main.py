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

logger = get_logger(__name__)


def save_chapter(content, context):

    target = context.target
    output = context.output

    chapter = target["chapter"]

    # ==============================
    # 输出目录
    # ==============================

    root = context.root / output["directory"]

    chapter_dir = root / target["volume"] / target["arc"] / target["plot"]

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
        logger.warning("No planning!!!!!!")
        # plan = planner.generate_plan()
        # context.planning_manager.save_plan(context.target, plan)
        return False

    return True


# ==================================================
# Writer
# ==================================================


def generate_chapter(context):
    logger.info("Start generate_chapter")
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

    logger.info("Start generate_memory...")

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

    # # -----------------------
    # # Plot Memory
    # # -----------------------

    # if context.is_plot_finished:

    #     logger.info("Plot结束，更新Plot Memory")

    #     memories["plot"] = agent.update_plot_memory(chapter_memory)

    # # -----------------------
    # # Arc Memory
    # # -----------------------

    # if context.is_arc_finished:

    #     logger.info("Arc结束，更新Arc Memory")

    #     memories["arc"] = agent.update_arc_memory(context.plot_memories)

    # # -----------------------
    # # Volume Memory
    # # -----------------------

    # if context.is_volume_finished:

    #     logger.info("Volume结束，更新Volume Memory")

    #     memories["volume"] = agent.update_volume_memory(context.arc_memories)

    return memories


def update_character_memory(context, chapter_memory):
    logger.info("update_character_memory")

    agent = CharacterAgent(context)

    result = agent.process(chapter_memory)

    logger.info(f"update_character_memory:{len(result)}")


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

    logger.info("Start...")

    # ==================================
    # Context
    # ==================================

    context = ProjectContext(project.root)

    logger.info(str(context.task))

    # ==================================
    # Planning
    # ==================================

    if not ensure_planning(context):

        logger.info("Planning generate done.")

        sys.exit(0)

    # ==================================
    # Writer
    # ==================================

    chapter = generate_chapter(context)
    logger.info("Done generate_chapter.")

    # ==================================
    # Critic
    # ==================================

    # review = review_chapter(context, chapter)

    # if not review["pass"]:

    #     logger.warning("Failed review!")

    #     sys.exit(1)

    # ==================================
    # Memory
    # ==================================

    memories = generate_memory(context, chapter)
    logger.info("Done generate_memory.")

    # ==================================
    # 8. save chapter and memory
    # ==================================

    save_result(context, chapter, memories)
    logger.info("Done save_result.")

    # ==================================
    # 9. update character Memory
    # ==================================

    update_character_memory(context, memories["chapter"])
    logger.info("Done update_character_memory.")

    logger.info("ALL DONE!!!!")
