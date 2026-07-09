import sys

from agents.writer_agent import write_chapter
from agents.memory_agent import MemoryAgent
from agents.critic_agent import CriticAgent
from agents.planner_agent import PlannerAgent

# 后续增加
# from agents.editor_agent import EditorAgent


from database.project_manager import ProjectManager
from database.project_context import ProjectContext

from database.memory_manager import MemoryManager

from utils.file_utils import save_chapter
from utils.logger import get_logger


def ensure_planning(context):
    """
    检查当前planning是否存在

    如果不存在:
        AI生成

    """

    planner = PlannerAgent(context)
    if not context.current_plan:
        logger.info("当前规划不存在，生成planning")
        # plan = planner.generate_full_plan()
        # context.planning_manager.save_plan(plan)
        return False
    return True


def generate_chapter(context):
    logger.info("开始生成章节")
    chapter = write_chapter(context)
    return chapter


def review_chapter(context, chapter):
    logger.info("开始章节审核")
    critic = CriticAgent(context)
    result = critic.review_chapter(chapter)
    logger.info(f"审核评分:{result['score']}")
    return result


def create_memory(context, chapter):
    logger.info("生成章节记忆")
    agent = MemoryAgent(context)
    memory = agent.create_chapter_memory(chapter, context.target["latest_chapter_id"])

    return memory


def save_result(context, chapter, memory):
    memory_manager = MemoryManager(context.root)
    # 保存正文
    chapter_dir = context.output["directory"]
    save_chapter(chapter, context.target["latest_chapter_id"], chapter_dir)
    # 保存memory
    memory_manager.save_chapter_memory(context.target, memory)
    logger.info("章节和memory保存完成")


if __name__ == "__main__":

    # ==================================
    # 1. 项目
    # ==================================
    project = ProjectManager("swallowing_star_fanfic")

    logger = get_logger(__name__, project.root)
    logger.info("项目启动")

    # ==================================
    # 2. Context
    # 自动加载:
    #
    # task
    # planning
    # memory
    # knowledge
    #
    # ==================================

    context = ProjectContext(project.root)
    logger.info("任务:" + str(context.task))

    # ==================================
    # 3. 检查规划
    # ==================================
    planned = ensure_planning(context)
    if not planned:
        sys.exit(0)

    # ==================================
    # 4. 写章节
    # ==================================
    chapter = generate_chapter(context)

    # ==================================
    # 5. AI审核
    # ==================================

    review = review_chapter(context, chapter)

    # ==================================
    # 6. 判断
    # ==================================

    if not review["pass"]:

        logger.warning("章节审核失败")

        # TODO:
        # editor_agent修改

        raise Exception("章节质量不通过")

    # ==================================
    # 7. 生成memory
    # ==================================

    memory = create_memory(context, chapter)

    # ==================================
    # 8. 保存
    # ==================================

    save_result(context, chapter, memory)

    logger.info("小说生成流程完成")
