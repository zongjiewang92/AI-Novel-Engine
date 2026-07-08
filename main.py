from agents.writer_agent import write_chapter
from agents.chapter_summary_agent import summarize_chapter
from agents.volume_summary_agent import summarize_volume
from agents.planner_agent import create_plot_plan

from database.project_manager import ProjectManager
from database.project_context import ProjectContext
from database.state_manager import save_state
from database.memory_manager import (
    save_chapter_memory,
    save_volume_memory,
    save_plot_plan,
)


from scripts.file_utils import save_chapter

if __name__ == "__main__":

    # ==========================
    # 1. 加载项目
    # ==========================

    project = ProjectManager("swallowing_star_fanfic")

    # ==========================
    # 2. 加载上下文
    # ==========================

    context = ProjectContext(project.root)

    current_chapter = context.state["current_chapter"]

    print("当前章节:", current_chapter)

    print("当前卷:", context.volume["volume"]["name"])

    # ==========================
    # 3. AI生成章节
    # ==========================

    chapter = write_chapter(context)

    # ==========================
    # 4. 保存章节
    # ==========================

    chapter_dir = context.volume_path / "chapters"

    save_chapter(chapter, current_chapter, chapter_dir)

    # ==========================
    # 5. 生成章节记忆
    # ==========================

    print("生成章节记忆...")

    chapter_memory = summarize_chapter(context, chapter, current_chapter)

    save_chapter_memory(context, current_chapter, chapter_memory)

    # ==========================
    # 6. 更新状态
    # ==========================

    context.state["current_chapter"] += 1

    save_state(project.get_state_file(), context.state)

    print("章节生成完成")

    # ==========================
    # 7. 每10章更新卷记忆
    # ==========================

    new_context = ProjectContext(project.root)

    if new_context.chapter_count % 10 == 0 and new_context.chapter_count != 0:

        print("开始更新卷总结...")

        volume_memory = summarize_volume(new_context)

        save_volume_memory(new_context, volume_memory)

        print("卷总结更新完成")

    if not context.plot_plan:
        print("生成剧情规划")
        plan = create_plot_plan(context)
        save_plot_plan(context, plan)
