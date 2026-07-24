from pathlib import Path
import yaml
from datetime import datetime


class PartYamlMerger:

    def __init__(self, raw_dir: Path, output_dir: Path):
        self.raw_dir = raw_dir
        self.output_dir = output_dir

        self.success = []
        self.failed = []

    def load_yaml(self, file: Path):

        with open(file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def merge_part(self, part_dir: Path):

        merged_data = []

        yaml_files = sorted(part_dir.glob("*.yaml"))

        for yaml_file in yaml_files:

            try:

                data = self.load_yaml(yaml_file)

                if data is None:
                    continue

                record = {"source": yaml_file.name, "data": data}

                merged_data.append(record)

                self.success.append(str(yaml_file))

            except Exception as e:

                self.failed.append({"file": str(yaml_file), "error": str(e)})

        return merged_data

    def save_yaml(self, filename, data):

        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_file = self.output_dir / filename

        with open(output_file, "w", encoding="utf-8") as f:

            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        return output_file

    def run(self):

        part_dirs = sorted(
            [
                x
                for x in self.raw_dir.iterdir()
                if x.is_dir() and x.name.startswith("part_")
            ]
        )

        for part_dir in part_dirs:

            print(f"Processing {part_dir.name}")

            merged = self.merge_part(part_dir)

            output_name = f"{part_dir.name}.yaml"

            output_file = self.save_yaml(
                output_name,
                {
                    "part": part_dir.name,
                    "generated_time": datetime.now().isoformat(),
                    "count": len(merged),
                    "items": merged,
                },
            )

            print(f"saved -> {output_file}")

        self.report()

    def report(self):

        print("\n========== REPORT ==========")

        print(f"Success: {len(self.success)}")

        print(f"Failed : {len(self.failed)}")

        if self.failed:

            print("\nFailed files:")

            for item in self.failed:

                print(item)


if __name__ == "__main__":

    merger = PartYamlMerger(
        raw_dir=Path("projects/swallowing_star_fanfic/knowledge_ai/raw"),
        output_dir=Path("projects/swallowing_star_fanfic/knowledge_ai/merged"),
    )

    merger.run()
