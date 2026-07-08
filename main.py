from agents.writer_agent import write_chapter
from agents.summary_agent import summarize_story

from database.project_manager import ProjectManager
from database.project_context import ProjectContext

from database.state_manager import save_state, save_summary

from scripts.file_utils import save_chapter

if __name__ == "__main__":

    # ==========================
    # 1. 加载小说项目
    # ==========================

    project = ProjectManager("swallowing_star_fanfic")

    # ==========================
    # 2. 创建小说上下文
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
    # 5. 更新小说状态
    # ==========================

    context.state["current_chapter"] += 1

    save_state(project.get_state_file(), context.state)

    print("章节生成完成")

    # ==================================================
    # 6. 每10章更新剧情摘要
    # ==================================================

    new_context = ProjectContext(project.root)

    if new_context.chapter_count % 10 == 0 and new_context.chapter_count != 0:

        print("达到10章，开始更新剧情摘要...")

        summary = summarize_story(new_context)

        summary_file = project.root / "state" / "story_summary.json"

        save_summary(summary_file, summary)

        print("剧情摘要更新完成")
