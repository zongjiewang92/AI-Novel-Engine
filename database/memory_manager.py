from pathlib import Path
import json
import shutil


class MemoryManager:

    def __init__(self, project_root):

        self.root = Path(project_root)

        # memory
        #
        # memory
        #   volumes
        #       volume001
        #
        self.memory_root = self.root / "z_ai_memory"

    # ==================================================
    # JSON
    # ==================================================

    @staticmethod
    def save_json(file: Path, data):

        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_json(file: Path):

        if not file.exists():

            return {}

        with open(file, "r", encoding="utf-8") as f:

            return json.load(f)

    # ==================================================
    # target
    # ==================================================

    @staticmethod
    def _ids(target):

        return (target["volume"], target["arc"], target["plot"], target["chapter"])

    # ==================================================
    # Path
    # ==================================================

    def volume_path(self, target):

        volume, _, _, _ = self._ids(target)

        return self.memory_root / volume

    def arc_path(self, target):

        volume, arc, _, _ = self._ids(target)

        return self.volume_path(target) / arc

    def plot_path(self, target):

        volume, arc, plot, _ = self._ids(target)

        return self.arc_path(target) / plot

    def chapter_path(self, target):

        volume, arc, plot, chapter = self._ids(target)

        return self.plot_path(target) / chapter

    # ==================================================
    # Exists
    # ==================================================

    def exists(self, file):

        return file.exists()

    # ==================================================
    # Volume Memory
    # ==================================================

    def save_volume_memory(self, target, memory):

        file = self.volume_path(target) / "volume_memory.json"

        self.save_json(file, memory)

    def load_volume_memory(self, target):

        file = self.volume_path(target) / "volume_memory.json"

        return self.load_json(file)

    # ==================================================
    # Arc Memory
    # ==================================================

    def save_arc_memory(self, target, memory):

        file = self.arc_path(target) / "arc_memory.json"

        self.save_json(file, memory)

    def load_arc_memory(self, target):

        file = self.arc_path(target) / "arc_memory.json"

        return self.load_json(file)

    # ==================================================
    # Plot Memory
    # ==================================================

    def save_plot_memory(self, target, memory):

        file = self.plot_path(target) / "plot_memory.json"

        self.save_json(file, memory)

    def load_plot_memory(self, target):

        file = self.plot_path(target) / "plot_memory.json"

        return self.load_json(file)

    # ==================================================
    # Chapter Memory
    # ==================================================

    def save_chapter_memory(self, target, memory):

        file = self.chapter_path(target) / "chapter_memory.json"

        self.save_json(file, memory)

    def load_chapter_memory(self, target):

        file = self.chapter_path(target) / "chapter_memory.json"

        return self.load_json(file)

    # ==================================================
    # Scene Memory
    # ==================================================

    def save_scene_memory(self, target, scene_id, memory):

        file = self.chapter_path(target) / "scenes" / f"{scene_id}.json"

        self.save_json(file, memory)

    def load_scene_memory(self, target):

        folder = self.chapter_path(target) / "scenes"

        if not folder.exists():

            return []

        result = []

        for file in sorted(folder.glob("*.json")):

            result.append(self.load_json(file))

        return result

    # ==================================================
    # Chapter Tree
    #
    # Plot下面所有Chapter Memory
    #
    # ==================================================

    def load_plot_chapter_memories(self, target):

        folder = self.plot_path(target) / "chapters"

        if not folder.exists():

            return []

        result = []

        for chapter_dir in sorted(folder.iterdir()):

            if not chapter_dir.is_dir():

                continue

            file = chapter_dir / "chapter_memory.json"

            if not file.exists():

                continue

            result.append(
                {"chapter_id": chapter_dir.name, "memory": self.load_json(file)}
            )

        return result

    # ==================================================
    # Arc Tree
    #
    # 当前Arc下面所有Plot Memory
    #
    # ==================================================

    def load_arc_plot_memories(self, target):

        folder = self.arc_path(target) / "plots"

        if not folder.exists():

            return []

        result = []

        for plot_dir in sorted(folder.iterdir()):

            if not plot_dir.is_dir():

                continue

            file = plot_dir / "plot_memory.json"

            if not file.exists():

                continue

            result.append({"plot_id": plot_dir.name, "memory": self.load_json(file)})

        return result

    # ==================================================
    # Volume Tree
    #
    # 当前Volume下面所有Arc Memory
    #
    # ==================================================

    def load_volume_arc_memories(self, target):

        folder = self.volume_path(target) / "arcs"

        if not folder.exists():

            return []

        result = []

        for arc_dir in sorted(folder.iterdir()):

            if not arc_dir.is_dir():

                continue

            file = arc_dir / "arc_memory.json"

            if not file.exists():

                continue

            result.append({"arc_id": arc_dir.name, "memory": self.load_json(file)})

        return result

    # ==================================================
    # Volume下面所有Plot Memory
    #
    # 用于重建Volume
    #
    # ==================================================

    def load_volume_plot_memories(self, target):

        result = []

        arc_folder = self.volume_path(target) / "arcs"

        if not arc_folder.exists():

            return []

        for arc_dir in sorted(arc_folder.iterdir()):

            plot_folder = arc_dir / "plots"

            if not plot_folder.exists():

                continue

            for plot_dir in sorted(plot_folder.iterdir()):

                file = plot_dir / "plot_memory.json"

                if file.exists():

                    result.append(
                        {"plot_id": plot_dir.name, "memory": self.load_json(file)}
                    )

        return result

    # ==================================================
    # Delete
    # ==================================================

    def delete_memory(self, target):

        folder = self.chapter_path(target)

        if folder.exists():

            shutil.rmtree(folder)

    # ==================================================
    # Save All
    # ==================================================

    def save_all(self, target, memories):

        if memories.get("volume"):

            self.save_volume_memory(target, memories["volume"])

        if memories.get("arc"):

            self.save_arc_memory(target, memories["arc"])

        if memories.get("plot"):

            self.save_plot_memory(target, memories["plot"])

        if memories.get("chapter"):

            self.save_chapter_memory(target, memories["chapter"])

        for scene_id, memory in memories.get("scenes", {}).items():

            self.save_scene_memory(target, scene_id, memory)
