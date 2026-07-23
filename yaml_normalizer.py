from pathlib import Path
from datetime import datetime
import yaml
import re


class YamlNormalizer:

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        report_file: Path,
    ):

        self.input_dir = input_dir

        self.output_dir = output_dir

        self.report_file = report_file

        self.success = []

        self.failed = []

    def run(self):

        yaml_files = list(self.input_dir.rglob("*.yaml"))

        for file in yaml_files:

            try:

                data = self.process_file(file)

                self.save(file, data)

                self.success.append(str(file))

            except Exception as e:

                self.failed.append({"file": str(file), "error": str(e)})

        self.generate_report()

    def process_file(self, file: Path):

        text = file.read_text(encoding="utf-8")

        # text = self.clean_markdown(text)

        # text = text.strip()

        # if not text:

        #     raise Exception("empty yaml")

        try:

            data = yaml.safe_load(text)

        except yaml.YAMLError as e:

            raise Exception(f"yaml parse error: {e}")

        if not data:

            raise Exception("empty data")

        data = self.normalize(data)

        return data

    def clean_markdown(self, text):

        text = text.strip()

        if text.startswith("```yaml"):

            text = text[7:]

        elif text.startswith("```yml"):

            text = text[6:]

        elif text.startswith("```"):

            text = text[3:]

        if text.endswith("```"):

            text = text[:-3]

        return text.strip()

    def normalize(self, data):

        if isinstance(data, dict):

            result = {}

            for k, v in data.items():

                key = str(k).strip()

                if v is None:

                    v = []

                result[key] = self.normalize(v)

            return result

        elif isinstance(data, list):

            result = []

            for item in data:

                if isinstance(item, dict):

                    item = self.fix_entity(item)

                result.append(self.normalize(item))

            return result

        else:

            return data

    def fix_entity(self, item):

        # 自动补 id

        if "name" in item and "id" not in item:

            item["id"] = item["name"]

        return item

    def save(self, source_file, data):

        relative = source_file.relative_to(self.input_dir)

        target = self.output_dir / relative

        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, "w", encoding="utf-8") as f:

            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def generate_report(self):

        report = {
            "time": datetime.now().isoformat(),
            "success": len(self.success),
            "failed": len(self.failed),
            "failed_files": self.failed,
        }

        self.report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.report_file, "w", encoding="utf-8") as f:

            yaml.dump(report, f, allow_unicode=True, sort_keys=False)


def main():

    agent = YamlNormalizer(
        input_dir=Path("projects/swallowing_star_fanfic/knowledge_ai/raw"),
        output_dir=Path("projects/swallowing_star_fanfic/knowledge_ai/normalized"),
        report_file=Path(
            "projects/swallowing_star_fanfic/knowledge_ai/reports/yaml_check.yaml"
        ),
    )

    agent.run()


if __name__ == "__main__":
    main()
