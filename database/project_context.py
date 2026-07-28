from pathlib import Path
import yaml

from llm.ollama_client import OllamaClient
from database.task_manager import TaskManager
from database.planning_manager import PlanningManager
from database.memory_manager import MemoryManager
from database.state_manager import StateManager
from database.character_manager import CharacterManager


class ProjectContext:

    def __init__(self, project_path):
        self.llm = OllamaClient()

        self.root = Path(project_path)

        # =================================
        # 基础
        # =================================

        self.config = self.load_config()

        # State

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

        self.position = {
            "volume": self.target["volume"],
            "arc": self.target["arc"],
            "plot": self.target["plot"],
            "chapter": self.target["chapter"],
        }

        self.volume_id = self.target["volume"]

        self.arc_id = self.target["arc"]

        self.plot_id = self.target["plot"]

        self.chapter_id = self.target["chapter"]

        # =================================
        # Planning
        # =================================

        self.planning_manager = PlanningManager(self.root)

        # 当前剧情规划

        self.current_plan = self.planning_manager.load_current_plan(self.target)

        # # 附近plot
        # self.related_plots = self.planning_manager.load_related_plots(
        #     self.target, limit=3
        # )

        # self.volume_path = self.planning_manager.volume_path(self.target)

        # =================================
        # Memory
        # =================================

        self.memory_manager = MemoryManager(self.root)

        # 当前节点 Memory

        self.volume_memory = self.memory_manager.load_volume_memory(self.target)

        self.arc_memory = self.memory_manager.load_arc_memory(self.target)

        self.plot_memory = self.memory_manager.load_plot_memory(self.target)

        self.chapter_memory = self.memory_manager.load_chapter_memory(self.target)

        # =================================
        # Memory Tree
        # 用于更新上级memory
        # =================================

        # 当前arc下面所有plot memory

        self.plot_memories = self.memory_manager.load_arc_plot_memories(self.target)

        # 当前volume下面所有arc memory

        self.arc_memories = self.memory_manager.load_volume_arc_memories(self.target)

        # =================================
        # Character
        # =================================
        self.character_manager = CharacterManager(self.root)
        self.related_characters = self.load_related_characters()

        # =================================
        # 状态判断
        # =================================

        self.is_plot_finished = self.planning_manager.is_plot_finished(self.target)

        self.is_arc_finished = self.planning_manager.is_arc_finished(self.target)

        self.is_volume_finished = self.planning_manager.is_volume_finished(self.target)

        # =================================
        # 最近正文
        # =================================

        self.chapter_history = self.load_chapters(limit=3)

        # =================================
        # Knowledge
        # =================================

        self.rules = self.load_rules()
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
    # 最近章节
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
    # rules
    # =================================================

    def load_rules(self):

        result = {}

        folder = self.root / "knowledge" / "00_rules"

        if not folder.exists():

            return {}

        for file in folder.rglob("*.yaml"):

            key = str(file.relative_to(folder))

            result[key] = yaml.safe_load(file.read_text(encoding="utf-8"))

        return result

    # =================================================
    # search_knowledge
    # =================================================
    def load_knowledge(self):

        result = {}

        folder = self.root / "knowledge" / "search_knowledge"

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

    def load_related_characters(self):
        result = {}
        characters = self.plot_memory.get("characters", [])
        for item in characters:
            name = item["name"]
            character = self.character_manager.load_character(name)
            if character:
                result[name] = character

        return result
