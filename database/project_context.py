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

        self.root = Path(project_path)

        # =================================================
        # LLM
        # =================================================

        self.llm = OllamaClient()

        # =================================================
        # State
        # =================================================

        self.state_manager = StateManager(self.root)

        # self.state_manager.create_checkpoint_if_changed()

        # self.novel_state = self.state_manager.load_state()

        # =================================================
        # Task
        # =================================================

        self.task_manager = TaskManager(self.root)

        self.task = self.task_manager.load_task()

        self.target = self.task["target"]

        self.output = self.task["output"]

        self.volume_id = self.target["volume"]

        self.arc_id = self.target["arc"]

        self.plot_id = self.target["plot"]

        self.chapter_id = self.target["chapter"]

        # =================================================
        # Planning
        # =================================================

        self.planning_manager = PlanningManager(self.root)

        self.current_plan = self.planning_manager.load_current_plan(self.target)

        self.current_plot = self.current_plan.get("current_plot", {})

        self.before_plots = self.current_plan.get("before_plots", {})

        self.after_plots = self.current_plan.get("after_plots", {})

        # # =================================================
        # # Memory
        # # =================================================

        # self.memory_manager = MemoryManager(self.root)

        # self.volume_memory = self.memory_manager.load_volume_memory(self.target)

        # self.arc_memory = self.memory_manager.load_arc_memory(self.target)

        # self.plot_memory = self.memory_manager.load_plot_memory(self.target)

        # self.chapter_memory = self.memory_manager.load_chapter_memory(self.target)

        # # =================================================
        # # Memory Tree
        # # =================================================

        # self.plot_memories = self.memory_manager.load_arc_plot_memories(self.target)

        # self.arc_memories = self.memory_manager.load_volume_arc_memories(self.target)

        # # =================================================
        # # Character
        # # =================================================

        # self.character_manager = CharacterManager(self.root)

        # self.related_characters = self.load_related_characters()

        # =================================================
        # Status
        # =================================================

        # self.is_plot_finished = self.planning_manager.is_plot_finished(self.target)

        # self.is_arc_finished = self.planning_manager.is_arc_finished(self.target)

        # self.is_volume_finished = self.planning_manager.is_volume_finished(self.target)

        # # =================================================
        # # Recent Chapters
        # # =================================================

        # self.chapter_history = self.load_chapters(limit=3)

        # # =================================================
        # # Knowledge
        # # =================================================

        # # 永久规则
        # self.global_rules = self.load_global_rules()

        # # 当前章节相关知识
        # self.relevant_knowledge = self.load_relevant_knowledge()

        # # =================================================
        # # Statistics
        # # =================================================

        # self.chapter_count = self.get_chapter_count()

    # =================================================
    # Chapter History
    # =================================================

    def load_chapters(self, limit=3):

        folder = self.root / "content" / "volumes" / self.volume_id / "chapters"

        if not folder.exists():

            return []

        result = []

        files = sorted(folder.glob("*.md"))

        for file in files[-limit:]:

            result.append(
                {"chapter": file.stem, "content": file.read_text(encoding="utf-8")}
            )

        return result

    # =================================================
    # Global Rules
    # =================================================

    def load_global_rules(self):

        folder = self.root / "knowledge" / "00_rules"

        return self.load_yaml_folder(folder)

    # =================================================
    # Relevant Knowledge
    # =================================================

    def load_relevant_knowledge(self):
        """
        当前版本:

        根据当前plot读取相关知识


        后续可以替换为:

        RAG Retriever

        """

        result = {}

        folder = self.root / "knowledge" / "search_knowledge"

        if not folder.exists():

            return {}

        # 当前先限制数量

        files = sorted(folder.rglob("*.yaml"))

        for file in files[:10]:

            key = str(file.relative_to(folder))

            result[key] = yaml.safe_load(file.read_text(encoding="utf-8"))

        return result

    # =================================================
    # YAML Folder
    # =================================================

    def load_yaml_folder(self, folder):

        result = {}

        if not folder.exists():

            return {}

        for file in folder.rglob("*.yaml"):

            key = str(file.relative_to(folder))

            result[key] = yaml.safe_load(file.read_text(encoding="utf-8"))

        return result

    # =================================================
    # Chapter Count
    # =================================================

    def get_chapter_count(self):

        folder = self.root / "content" / "volumes" / self.volume_id / "chapters"

        if not folder.exists():

            return 0

        return len(list(folder.glob("*.md")))

    # =================================================
    # Characters
    # =================================================

    def load_related_characters(self):

        result = {}

        names = set()

        # Plot Memory

        for item in self.plot_memory.get("character_growth", []):

            if "name" in item:

                names.add(item["name"])

        # Chapter Memory

        for item in self.chapter_memory.get("character_changes", []):

            if "name" in item:

                names.add(item["name"])

        for name in names:

            character = self.character_manager.load_character(name)

            if character:

                result[name] = character

        return result
