from pathlib import Path
import json


class MemoryManager:

    def __init__(self, project_root):

        self.root = Path(project_root)

        self.memory_root = self.root / "memory" / "volumes"

    # ==================================================
    # 基础 JSON
    # ==================================================

    def save_json(self, file, data):

        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_json(self, file):

        if not file.exists():

            return {}

        with open(file, "r", encoding="utf-8") as f:

            return json.load(f)

    # ==================================================
    # Path
    # ==================================================

    def volume_path(self, volume_id):

        return self.memory_root / volume_id

    def arc_path(self, volume_id, arc_id):

        return self.volume_path(volume_id) / "arcs" / arc_id

    def plot_path(self, volume_id, arc_id, plot_id):

        return self.arc_path(volume_id, arc_id) / "plots" / plot_id

    def chapter_path(self, volume_id, arc_id, plot_id, chapter_id):

        return self.plot_path(volume_id, arc_id, plot_id) / "chapters" / chapter_id

    # ==================================================
    # Volume Memory
    # ==================================================

    def save_volume_memory(self, volume_id, memory):

        file = self.volume_path(volume_id) / "volume_memory.json"

        self.save_json(file, memory)

    def load_volume_memory(self, volume_id):

        file = self.volume_path(volume_id) / "volume_memory.json"

        return self.load_json(file)

    # ==================================================
    # Arc Memory
    # ==================================================

    def save_arc_memory(self, volume_id, arc_id, memory):

        file = self.arc_path(volume_id, arc_id) / "arc_memory.json"

        self.save_json(file, memory)

    def load_arc_memory(self, volume_id, arc_id):

        file = self.arc_path(volume_id, arc_id) / "arc_memory.json"

        return self.load_json(file)

    # ==================================================
    # Plot Memory
    # ==================================================

    def save_plot_memory(self, volume_id, arc_id, plot_id, memory):

        file = self.plot_path(volume_id, arc_id, plot_id) / "plot_memory.json"

        self.save_json(file, memory)

    def load_plot_memory(self, volume_id, arc_id, plot_id):

        file = self.plot_path(volume_id, arc_id, plot_id) / "plot_memory.json"

        return self.load_json(file)

    # ==================================================
    # Chapter Memory
    # ==================================================

    def save_chapter_memory(self, volume_id, arc_id, plot_id, chapter_id, memory):

        file = (
            self.chapter_path(volume_id, arc_id, plot_id, chapter_id)
            / "chapter_memory.json"
        )

        self.save_json(file, memory)

    def load_chapter_memory(self, volume_id, arc_id, plot_id, chapter_id):

        file = (
            self.chapter_path(volume_id, arc_id, plot_id, chapter_id)
            / "chapter_memory.json"
        )

        return self.load_json(file)

    # ==================================================
    # Scene Memory
    # ==================================================

    def save_scene_memory(
        self, volume_id, arc_id, plot_id, chapter_id, scene_id, memory
    ):

        file = (
            self.chapter_path(volume_id, arc_id, plot_id, chapter_id)
            / "scenes"
            / f"{scene_id}.json"
        )

        self.save_json(file, memory)

    def load_scene_memory(self, volume_id, arc_id, plot_id, chapter_id):

        folder = self.chapter_path(volume_id, arc_id, plot_id, chapter_id) / "scenes"

        if not folder.exists():

            return []

        result = []

        for file in sorted(folder.glob("*.json")):

            result.append(self.load_json(file))

        return result
