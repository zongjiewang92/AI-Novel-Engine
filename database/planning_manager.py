from pathlib import Path
import yaml


class PlanningManager:

    def __init__(self, project_root):

        self.root = Path(project_root)
        self.planning_root = self.root / "planning"

    # ==================================================
    # YAML
    # ==================================================

    def load_yaml(self, file: Path):

        if not file.exists():
            return {}

        with open(file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # ==================================================
    # Path
    # ==================================================

    def volume_path(self, target):

        return self.planning_root / target["volume"]

    def arc_path(self, target):

        return self.volume_path(target) / target["arc"]

    # ==================================================
    # Volume
    # ==================================================

    def load_volume(self, target):

        file = self.volume_path(target) / f'{target["volume"]}.yaml'

        return self.load_yaml(file)

    # ==================================================
    # Arc
    # ==================================================

    def load_arc(self, target):

        folder = self.arc_path(target)

        if not folder.exists():
            return {}

        for file in sorted(folder.glob("arc_*.yaml")):

            return self.load_yaml(file)

        return {}

    # ==================================================
    # 获取 Volume 下所有 Arc
    # ==================================================

    def list_arcs(self, target):

        folder = self.volume_path(target)

        if not folder.exists():

            return []

        return sorted(
            [
                x.name
                for x in folder.iterdir()
                if x.is_dir() and x.name.startswith("arc_")
            ]
        )

    # ==================================================
    # 获取 Arc 下所有 Plot
    # ==================================================

    def list_plots(self, target, arc=None):

        if arc is None:

            arc = target["arc"]

        folder = self.volume_path(target) / arc

        if not folder.exists():

            return []

        result = []

        for file in sorted(folder.glob("plot_*.yaml")):

            result.append({"id": file.stem, "data": self.load_yaml(file), "arc": arc})

        return result

    # ==================================================
    # 获取 Volume 全部 Plot
    #
    # 用于跨 Arc 查找
    #
    # ==================================================

    def list_all_plots(self, target):

        result = []

        arcs = self.list_arcs(target)

        for arc in arcs:

            plots = self.list_plots(target, arc)

            result.extend(plots)

        return result

    # ==================================================
    # 当前 Plot 上下文
    #
    # before:
    #   上一个 plot
    #
    # current:
    #   当前 plot
    #
    # after:
    #   下一个 plot
    #
    # ==================================================

    def load_current_plan(self, target):

        all_plots = self.list_all_plots(target)

        current_id = target["plot"]

        current_index = -1

        for index, plot in enumerate(all_plots):

            if plot["id"] == current_id:

                current_index = index
                break

        if current_index == -1:

            return {
                "volume": self.load_volume(target),
                "arc": self.load_arc(target),
                "before_plots": {},
                "current_plot": {},
                "after_plots": {},
            }

        current_plot = all_plots[current_index].get("data", {})

        # ----------------------------
        # previous
        # ----------------------------

        before_plot = {}

        if current_index > 0:

            before_plot = all_plots[current_index - 1].get("data", {})

        # ----------------------------
        # next
        # ----------------------------

        after_plot = {}

        if current_index < len(all_plots) - 1:

            after_plot = all_plots[current_index + 1].get("data", {})

        return {
            "volume": self.load_volume(target),
            "arc": self.load_arc(target),
            "before_plots": before_plot,
            "current_plot": current_plot,
            "after_plots": after_plot,
        }

    # ==================================================
    # Plot 完成检查
    # ==================================================

    def is_plot_finished(self, target):

        plot = self.load_current_plan(target).get("current_plot", {})

        if plot.get("status") == "finished":

            return True

        if plot.get("completed") is True:

            return True

        return False

    # ==================================================
    # Arc 完成检查
    # ==================================================

    def is_arc_finished(self, target):

        arcs = self.list_arcs(target)

        if not arcs:

            return False

        current_arc = target["arc"]

        if current_arc not in arcs:

            return False

        index = arcs.index(current_arc)

        return index == len(arcs) - 1

    # ==================================================
    # Volume 完成检查
    # ==================================================

    def is_volume_finished(self, target):

        volume = self.load_volume(target)

        volume_data = volume.get("volume", {})

        arcs = volume_data.get("arcs", [])

        if not arcs:

            return False

        return target["arc"] == arcs[-1]
