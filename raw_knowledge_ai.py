from pathlib import Path
import json
import yaml

from database.base_agent_manager import BaseAgentManager
from database.project_manager import ProjectManager
from agents.raw_knowledge_agent import raw_summarize
from utils.logger import get_logger

PROJECT_NAME = "swallowing_star_fanfic"


class KnowledgeNormalizeManager(BaseAgentManager):

    def __init__(self, project_name, part_start, part_end):

        project = ProjectManager(project_name)

        input_dir = project.root / "knowledge_ai" / "raw"

        output_dir = project.root / "knowledge_ai" / "normalize_01"

        state_file = project.root / "knowledge_ai" / "extract_state.json"

        super().__init__(project, input_dir, output_dir, state_file)

        self.part_start = part_start
        self.part_end = part_end

    def collect_files_1(self):
        files = []
        for part in range(self.part_start, self.part_end + 1):

            file = self.input_dir / f"part_{part:03d}.yaml"

            if not file.exists():

                self.logger.warning(f"不存在: {file}")

                continue

            files.append(file)

        return files

    def collect_files(self):

        files = []

        for part in range(self.part_start, self.part_end + 1):

            part_dir = self.input_dir / f"part_{part:03d}"

            if not part_dir.exists():

                continue

            files.extend(sorted(part_dir.glob("*.yaml")))

        return files

    def call_logic_method(self, source_id, content):

        data = yaml.safe_load(content)

        timelines = data.get("timeline", [])

        lines = []

        for item in timelines:

            if isinstance(item, dict):
                for _, value in item.items():
                    lines.append(str(value))
            else:
                lines.append(str(item))

        output_text = "\n".join(lines)

        return output_text

    def call_agent(self, source_id, content):

        # return raw_summarize(source_id, content)
        return self.call_logic_method(source_id, content)


def main():

    manager = KnowledgeNormalizeManager(
        project_name="swallowing_star_fanfic", part_start=1, part_end=100
    )

    manager.run()


if __name__ == "__main__":

    main()
