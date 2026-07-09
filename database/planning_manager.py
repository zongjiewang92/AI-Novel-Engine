from pathlib import Path
import yaml
import re


class PlanningManager:

    def __init__(self, project_root):

        self.root = Path(project_root)

        self.planning_root = self.root / "planning" / "volumes"

    # ==================================================
    # YAML
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
    # Path
    # ==================================================

    def volume_path(self, target):

        return self.planning_root / target["volume"]

    def arc_path(self, target):

        return self.volume_path(target) / "arcs" / target["arc"]

    def plot_path(self, target):

        return self.arc_path(target) / "plots" / target["plot"]

    def chapter_path(self, target):

        return self.plot_path(target) / "chapters" / target["chapter"]

    # ==================================================
    # Load
    # ==================================================

    def load_volume(self, target):

        return self.load_yaml(self.volume_path(target) / "volume.yaml")

    def load_arc(self, target):

        return self.load_yaml(self.arc_path(target) / "arc.yaml")

    def load_plot(self, target):

        return self.load_yaml(self.plot_path(target) / "plot.yaml")

    def load_chapter(self, target):

        file = self.chapter_path(target) / f'{target["chapter"]}.yaml'

        return self.load_yaml(file)

    def load_scenes(self, target):

        folder = self.chapter_path(target) / "scenes"

        if not folder.exists():

            return []

        result = []

        for file in sorted(folder.glob("*.yaml")):

            result.append(self.load_yaml(file))

        return result

    # ==================================================
    # 当前完整计划
    # ==================================================

    def load_current_plan(self, target):

        return {
            "volume": self.load_volume(target),
            "arc": self.load_arc(target),
            "plot": self.load_plot(target),
            "chapter": self.load_chapter(target),
            "scenes": self.load_scenes(target),
        }

    # ==================================================
    # Related Plot
    # ==================================================

    def get_plot_ids(self, target):

        folder = self.arc_path(target) / "plots"

        if not folder.exists():

            return []

        return sorted([x.name for x in folder.iterdir() if x.is_dir()])

    def load_related_plots(self, target, limit=3):

        plots = self.get_plot_ids(target)

        current = target["plot"]

        if current not in plots:

            return []

        index = plots.index(current)

        start = max(0, index - limit)

        end = min(len(plots), index + limit + 1)

        result = []

        for pid in plots[start:end]:

            new_target = target.copy()

            new_target["plot"] = pid

            result.append({"target": new_target, "plan": self.load_plot(new_target)})

        return result

    # ==================================================
    # 状态判断
    # ==================================================

    def is_plot_finished(self, target):

        plot = self.load_plot(target)

        end_chapter = plot.get("plot", {}).get("end_chapter")

        if not end_chapter:

            return False

        current = int(re.findall(r"\d+", target["chapter"])[0])

        end = int(re.findall(r"\d+", end_chapter)[0])

        return current >= end

    def is_arc_finished(self, target):

        arc = self.load_arc(target)

        plots = arc.get("arc", {}).get("plots", [])

        if not plots:

            return False

        return target["plot"] == plots[-1]

    def is_volume_finished(self, target):

        volume = self.load_volume(target)

        arcs = volume.get("volume", {}).get("arcs", [])

        if not arcs:

            return False

        return target["arc"] == arcs[-1]

    # ==================================================
    # Save Planning
    # ==================================================

    def save_plan(self, target, level, data):

        if level == "volume":

            file = self.volume_path(target) / "volume.yaml"

        elif level == "arc":

            file = self.arc_path(target) / "arc.yaml"

        elif level == "plot":

            file = self.plot_path(target) / "plot.yaml"

        elif level == "chapter":

            file = self.chapter_path(target) / f'{target["chapter"]}.yaml'

        elif level == "scene":

            file = self.chapter_path(target) / "scenes" / f'{data["id"]}.yaml'

        else:

            raise Exception(f"unknown level:{level}")

        self.save_yaml(file, data)

    # ==================================================
    # Create next plot
    # ==================================================

    def create_next_plot(self, target):

        current = target["plot"]

        number = int(re.findall(r"\d+", current)[0])

        next_id = f"plot{number+1:03d}"

        new_target = target.copy()

        new_target["plot"] = next_id

        folder = self.plot_path(new_target)

        folder.mkdir(parents=True, exist_ok=True)

        (folder / "chapters").mkdir(exist_ok=True)

        return new_target
