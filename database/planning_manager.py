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
    # Load Volume
    # ==================================================

    def load_volume(self, target):

        file = self.volume_path(target) / f'{target["volume"]}.yaml'

        return self.load_yaml(file)

    # ==================================================
    # Load Arc
    # ==================================================

    def load_arc(self, target):

        folder = self.arc_path(target)

        for file in sorted(folder.glob("arc_*.yaml")):

            return self.load_yaml(file)

        return {}

    # ==================================================
    # Load Plots
    # ==================================================

    def load_plots(self, target):

        folder = self.arc_path(target)

        plots = []

        if not folder.exists():
            return plots

        for file in sorted(folder.glob("plot_*.yaml")):

            plots.append({"id": file.stem, "data": self.load_yaml(file)})

        return plots

    # ==================================================
    # Current Plan
    # ==================================================

    def load_current_plan(self, target):

        plots = self.load_plots(target)

        current_id = target["plot"]

        before_plots = []
        current_plot = {}
        after_plots = []

        found_current = False

        for plot in plots:

            if plot["id"] == current_id:

                current_plot = plot["data"]

                found_current = True

            elif not found_current:

                before_plots.append(plot["data"])

            else:

                after_plots.append(plot["data"])

        return {
            "volume": self.load_volume(target),
            "arc": self.load_arc(target),
            "before_plots": before_plots,
            "current_plot": current_plot,
            "after_plots": after_plots,
        }
    # ==================================================
    # Status Check
    # ==================================================

    def is_plot_finished(self, target):
        """
        判断当前 plot 是否完成

        根据：
        current_plot.yaml
        中的 status 或 end_chapter 判断

        """

        plot = self.load_current_plan(target).get(
            "current_plot",
            {}
        )


        # 方式1:
        # plot:
        #   status: finished

        if plot.get("status") == "finished":
            return True


        # 方式2:
        # plot:
        #   completed: true

        if plot.get("completed") is True:
            return True


        return False



    def is_arc_finished(self, target):
        """
        判断当前 Arc 是否完成

        当前 plot 是否是 arc 下最后一个 plot
        """

        plots = self.load_plots(target)


        if not plots:
            return False


        current_id = target["plot"]


        plot_ids = [
            x["id"]
            for x in plots
        ]


        if current_id not in plot_ids:
            return False


        current_index = plot_ids.index(current_id)


        # 最后一个 plot
        return current_index == len(plot_ids) - 1



    def is_volume_finished(self, target):
        """
        判断 Volume 是否完成

        当前 arc 是否是 volume 最后一个 arc
        """

        volume = self.load_volume(target)


        # volume.yaml

        # 示例:
        #
        # volume:
        #   arcs:
        #     - arc_01
        #     - arc_02


        volume_data = volume.get(
            "volume",
            {}
        )


        arcs = volume_data.get(
            "arcs",
            []
        )


        if not arcs:
            return False


        return target["arc"] == arcs[-1]