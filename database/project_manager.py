from pathlib import Path
import yaml


class ProjectManager:

    def __init__(self, project_name):

        self.root = Path("projects") / project_name

        if not self.root.exists():
            raise Exception(f"Project not found: {project_name}")

    def load_config(self):

        config_file = self.root / "config.yaml"

        with open(config_file, "r", encoding="utf-8") as f:

            return yaml.safe_load(f)

    def get_path(self, name):

        return self.root / name

    def get_state_file(self):

        return self.root / "state" / "novel_state.json"
