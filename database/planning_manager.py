from pathlib import Path
import yaml
import re


class PlanningManager:

    def __init__(self, project_root):
        self.root = Path(project_root)
        self.planning_root = self.root / "planning" / "volumes"

    # ==================================================
    # yaml 基础操作
    # ==================================================

    def load_yaml(self, file):
        if not file.exists():
            return {}
        with open(file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_yaml(self, file, data):

        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "w", encoding="utf-8") as f:

            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    # ==================================================
    # 路径定位
    # ==================================================

    def volume_path(self, volume_id):
        return self.planning_root / volume_id

    def arc_path(self, volume_id, arc_id):
        return self.volume_path(volume_id) / "arcs" / arc_id

    def plot_path(self, volume_id, arc_id, plot_id):
        return self.arc_path(volume_id, arc_id) / "plots" / plot_id

    # ==================================================
    # 加载 volume
    # ==================================================

    def load_volume(self, volume_id):
        path = self.volume_path(volume_id) / "volume.yaml"
        return self.load_yaml(path)

    # ==================================================
    # 加载 arc
    # ==================================================

    def load_arc(self, volume_id, arc_id):
        path = self.arc_path(volume_id, arc_id) / "arc.yaml"
        return self.load_yaml(path)

    # ==================================================
    # 加载 plot
    # ==================================================

    def load_plot(self, volume_id, arc_id, plot_id):
        path = self.plot_path(volume_id, arc_id, plot_id) / "plot.yaml"
        return self.load_yaml(path)

    # ==================================================
    # 加载 chapter
    # ==================================================

    def load_chapter(self, volume_id, arc_id, plot_id, chapter_id):
        path = (
            self.plot_path(volume_id, arc_id, plot_id)
            / "chapters"
            / chapter_id
            / f"{chapter_id}.yaml"
        )

        return self.load_yaml(path)

    # ==================================================
    # 加载 scene
    # ==================================================

    def load_scenes(self, volume_id, arc_id, plot_id, chapter_id):
        scene_path = (
            self.plot_path(volume_id, arc_id, plot_id)
            / "chapters"
            / chapter_id
            / "scenes"
        )

        result = []

        if not scene_path.exists():
            return result

        for file in sorted(scene_path.glob("*.yaml")):
            result.append(self.load_yaml(file))

        return result

    # ==================================================
    # 加载当前完整剧情
    # ==================================================

    def load_current_plan(self, target):
        volume_id = target["volume"]
        arc_id = target["arc"]
        plot_id = target["plot"]
        chapter_id = target["chapter"]

        result = {}
        result["volume"] = self.load_volume(volume_id)
        result["arc"] = self.load_arc(volume_id, arc_id)
        result["plot"] = self.load_plot(volume_id, arc_id, plot_id)
        result["chapter"] = self.load_chapter(volume_id, arc_id, plot_id, chapter_id)
        result["scenes"] = self.load_scenes(volume_id, arc_id, plot_id, chapter_id)

        return result

    # ==================================================
    # 获取所有 plot
    # ==================================================

    def get_plot_ids(self, volume_id, arc_id):
        path = self.arc_path(volume_id, arc_id) / "plots"
        if not path.exists():
            return []

        return sorted([p.name for p in path.iterdir() if p.is_dir()])

    # ==================================================
    # 加载附近 plot
    # ==================================================

    def load_related_plots(self, target, limit=3):
        volume_id = target["volume"]
        arc_id = target["arc"]
        current_plot = target["plot"]
        plots = self.get_plot_ids(volume_id, arc_id)
        if current_plot not in plots:
            return []

        index = plots.index(current_plot)
        start = max(0, index - limit)
        end = min(len(plots), index + limit + 1)
        result = []

        for plot_id in plots[start:end]:
            result.append(
                {"id": plot_id, "content": self.load_plot(volume_id, arc_id, plot_id)}
            )

        return result

    # ==================================================
    # 保存 plot
    # ==================================================

    def save_plot(self, volume_id, arc_id, plot_id, data):
        path = self.plot_path(volume_id, arc_id, plot_id) / "plot.yaml"
        self.save_yaml(path, data)

    # ==================================================
    # 创建新的 plot
    # ==================================================

    def create_next_plot(self, volume_id, arc_id, current_plot_id):

        number = int(re.findall(r"\d+", current_plot_id)[0])
        next_id = f"plot{number+1:03d}"
        path = self.plot_path(volume_id, arc_id, next_id)
        path.mkdir(parents=True, exist_ok=True)
        chapter_path = path / "chapters"
        chapter_path.mkdir(exist_ok=True)

        return next_id

    def save_plan():
        pass
