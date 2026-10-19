"""ProjectContext：聚合一本书写下一章所需的全部上下文。

此前 4 个方法用 4 种写法重复扫描 volumes/ 目录找同一个卷，
现收敛到 _find_volume_dir。注意这是全量加载；写章节 agent 侧
用 token 预算控制实际塞进 prompt 的量。
"""
from pathlib import Path
import yaml
import json
from database.plot_manager import PlotManager


class ProjectContext:

    def __init__(self, project_path):

        self.root = Path(project_path)

        # basic info
        self.config = self.load_config()
        self.novel_state = self.load_novel_state()
        self.story_summary = self.load_story_summary()

        # current volume
        self.volume_path, self.volume = self._find_volume(
            self.novel_state["current_volume_id"]
        )

        # memory
        self.volume_memory = self.load_volume_memory()
        self.plot_memory = self.load_plot_memory()
        self.current_plot = PlotManager.get_current_plot(
            self.plot_memory, self.novel_state["current_chapter"]
        )
        self.chapter_memory = self.load_chapter_memory(limit=5)

        # latest chapters
        self.chapter_history = self.load_chapters(limit=3)

        # knowledge
        self.characters = self.load_knowledge("characters")
        self.world_rules = self.load_knowledge("rules")
        self.timeline = self.load_knowledge("timeline")
        self.world = self.load_knowledge("world")
        self.chapter_count = self.get_chapter_count()

    # ---- 卷定位：唯一入口 ----
    def _find_volume(self, volume_id):
        """返回 (volume_dir, volume_config)，找不到抛异常。"""
        volumes_dir = self.root / "volumes"
        for folder in volumes_dir.iterdir():
            if not folder.is_dir():
                continue
            config_file = folder / "volume_config.yaml"
            if not config_file.exists():
                continue
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            if config["volume"]["id"] == volume_id:
                return folder, config
        raise Exception(f"找不到卷 id={volume_id}")

    # config.yaml
    def load_config(self):
        file = self.root / "config.yaml"
        with open(file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # novel_state.json
    def load_novel_state(self):
        file = self.root / "state" / "novel_state.json"
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    # story_summary.json
    def load_story_summary(self):
        file = self.root / "state" / "story_summary.json"
        if not file.exists():
            return {"main_story": "", "important_events": [], "character_changes": []}
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_plot_memory(self):
        file = self.volume_path / "memory" / "plot_memory.json"
        if not file.exists():
            return {}
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_volume_memory(self):
        memory_file = self.volume_path / "memory" / "volume_summary.json"
        if not memory_file.exists():
            return {}
        with open(memory_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_chapter_memory(self, limit=5):
        summary_dir = self.volume_path / "memory" / "chapter_summary"
        if not summary_dir.exists():
            return []
        files = sorted(summary_dir.glob("chapter*.json"))
        # 最近 limit 章
        files = files[-limit:]
        result = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                result.append(json.load(f))
        return result

    def load_chapters(self, limit=3):
        chapters = []
        folder = self.volume_path / "chapters"
        if not folder.exists():
            return chapters
        files = sorted(folder.glob("*.md"))
        files = files[-limit:]
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                chapters.append({"chapter": file.stem, "content": f.read()})
        return chapters

    def load_knowledge(self, category):
        result = {}
        folder = self.root / "knowledge" / category
        if not folder.exists():
            return result
        for file in folder.glob("*.md"):
            with open(file, "r", encoding="utf-8") as f:
                result[file.stem] = f.read()
        return result

    def get_chapter_count(self):
        folder = self.volume_path / "chapters"
        if not folder.exists():
            return 0
        return len(list(folder.glob("*.md")))
