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
