from pathlib import Path
import yaml
import json


from database.task_manager import TaskManager
from database.planning_manager import PlanningManager
from database.memory_manager import MemoryManager
from database.state_manager import StateManager


class ProjectContext:

    def __init__(self, project_path):

        self.root = Path(project_path)

        # =================================
        # 基础配置
        # =================================

        self.config = self.load_config()
        self.state_manager = StateManager(self.root)
        self.state_manager.create_checkpoint_if_changed()
        self.novel_state = self.state_manager.load_state()

        # =================================
        # Task
        # =================================

        self.task_manager = TaskManager(self.root)
        self.task = self.task_manager.load_task()
        self.target = self.task["target"]
        self.output = self.task["output"]

        # 拆分定位
        self.volume_id = self.target["volume"]
        self.arc_id = self.target["arc"]
        self.plot_id = self.target["plot"]
        self.chapter_id = self.target["chapter"]

        # =================================
        # Planning
        # =================================

        self.planning_manager = PlanningManager(self.root)

        # 当前完整规划
        self.current_plan = self.planning_manager.load_current_plan(self.target)

        # 当前plot附近
        self.related_plots = self.planning_manager.load_related_plots(
            self.target, limit=3
        )

        # 当前volume路径
        self.volume_path = self.planning_manager.volume_path(self.volume_id)

        # =================================
        # Memory
        # =================================
        self.memory_manager = MemoryManager(self.root)

        # Volume Memory
        self.volume_memory = self.memory_manager.load_volume_memory(self.volume_id)

        # Arc Memory
        self.arc_memory = self.memory_manager.load_arc_memory(
            self.volume_id, self.arc_id
        )

        # Plot Memory
        self.plot_memory = self.memory_manager.load_plot_memory(
            self.volume_id, self.arc_id, self.plot_id
        )

        # Chapter Memory
        self.chapter_memory = self.memory_manager.load_chapter_memory(
            self.volume_id, self.arc_id, self.plot_id, self.chapter_id
        )

        # =================================
        # 最近正文
        # =================================
        self.chapter_history = self.load_chapters(limit=3)

        # =================================
        # Knowledge
        # =================================
        self.knowledge = self.load_knowledge()

        # =================================
        # 统计
        # =================================
        self.chapter_count = self.get_chapter_count()

    # =================================================
    # config
    # =================================================

    def load_config(self):

        file = self.root / "config.yaml"

        with open(file, encoding="utf-8") as f:

            return yaml.safe_load(f)

    # =================================================
    # 最近章节正文
    # =================================================

    def load_chapters(self, limit=3):

        result = []

        folder = self.root / "content" / "volumes" / self.volume_id / "chapters"

        if not folder.exists():

            return []

        files = sorted(folder.glob("*.md"))

        for file in files[-limit:]:

            result.append(
                {"chapter": file.stem, "content": file.read_text(encoding="utf-8")}
            )

        return result

    # =================================================
    # knowledge
    # =================================================

    def load_knowledge(self):

        result = {}

        folder = self.root / "knowledge"

        if not folder.exists():

            return {}

        for file in folder.rglob("*.yaml"):

            key = str(file.relative_to(folder))

            result[key] = yaml.safe_load(file.read_text(encoding="utf-8"))

        return result

    # =================================================
    # chapter count
    # =================================================

    def get_chapter_count(self):

        folder = self.root / "content" / "volumes" / self.volume_id / "chapters"

        if not folder.exists():

            return 0

        return len(list(folder.glob("*.md")))
