from pathlib import Path
from collections import defaultdict
from datetime import datetime
import yaml
import re


class KnowledgeMergeAgent:


    def __init__(
        self,
        raw_dir: Path,
        output_dir: Path,
        report_dir: Path
    ):

        self.raw_dir = raw_dir
        self.output_dir = output_dir
        self.report_dir = report_dir


        self.success_records = []

        self.failed_records = []

        self.type_statistics = defaultdict(int)

        self.unknown_records = []



    def merge(self):


        knowledge = defaultdict(list)


        yaml_files = list(
            self.raw_dir.rglob("*.yaml")
        )


        for file in yaml_files:


            try:

                data = self.load_yaml(file)


                if not data:

                    raise Exception(
                        "empty yaml"
                    )


                knowledge_type = self.detect_type(
                    data
                )


                knowledge_type = (
                    self.normalize_name(
                        knowledge_type
                    )
                )


                data["_meta"] = {
                    "source_file": str(file)
                }


                knowledge[
                    knowledge_type
                ].append(data)


                self.type_statistics[
                    knowledge_type
                ] += 1



                record = {

                    "file": str(file),

                    "type": knowledge_type,

                    "id": data.get("id"),

                    "name": data.get("name")
                }


                self.success_records.append(
                    record
                )


                if knowledge_type == "unknown":

                    self.unknown_records.append(
                        record
                    )



            except Exception as e:


                self.failed_records.append(
                    {
                        "file": str(file),

                        "error": str(e)
                    }
                )



        self.save(
            knowledge
        )


        self.generate_reports()



    def load_yaml(
        self,
        file: Path
    ):


        text = file.read_text(
            encoding="utf-8"
        )


        text = self.clean_yaml_text(
            text
        )


        if not text:

            return {}



        try:

            return yaml.safe_load(text) or {}


        except yaml.YAMLError as e:

            raise Exception(
                f"yaml parse error: {e}"
            )



    def clean_yaml_text(
        self,
        text
    ):


        text = text.strip()



        # 删除 markdown

        if text.startswith(
            "```yaml"
        ):

            text = text[7:]


        elif text.startswith(
            "```yml"
        ):

            text = text[6:]


        elif text.startswith(
            "```"
        ):

            text = text[3:]


        if text.endswith(
            "```"
        ):

            text = text[:-3]


        return text.strip()



    def detect_type(
        self,
        data
    ):


        # 优先使用 AI 输出

        if data.get("type"):

            return data["type"]



        keys = set(
            data.keys()
        )


        name = str(
            data.get(
                "name",
                ""
            )
        )



        # 人物

        if (
            "relationships" in keys
            or
            "personality" in keys
            or
            "age" in keys
        ):

            return "character"



        # 事件

        if (
            "participants" in keys
            or
            "timeline" in keys
            or
            "date" in keys
        ):

            return "event"



        # 地点

        if (
            "location" in keys
            or
            "coordinates" in keys
            or
            "environment" in keys
        ):

            return "location"



        # 组织

        if (
            "members" in keys
            or
            "leader" in keys
            or
            "organization" in keys
        ):

            return "organization"



        # 能力

        if (
            "realm" in keys
            or
            "level" in keys
            or
            "abilities" in keys
        ):

            return "ability"



        return "unknown"



    def save(
        self,
        knowledge
    ):


        for knowledge_type, items in knowledge.items():


            folder = (
                self.output_dir /
                knowledge_type
            )


            folder.mkdir(
                parents=True,
                exist_ok=True
            )



            for item in items:


                filename = self.safe_filename(

                    item.get(
                        "id"
                    )
                    or
                    item.get(
                        "name"
                    )
                    or
                    "unknown"

                )



                target = (
                    folder /
                    f"{filename}.yaml"
                )



                with open(
                    target,
                    "w",
                    encoding="utf-8"
                ) as f:


                    yaml.dump(
                        item,
                        f,
                        allow_unicode=True,
                        sort_keys=False
                    )



    def generate_reports(
        self
    ):


        self.report_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        self.generate_statistics()

        self.generate_markdown()



    def generate_statistics(
        self
    ):


        data = {


            "time":
                datetime.now().isoformat(),



            "summary":
            {

                "total_files":
                    len(
                        self.success_records
                    )
                    +
                    len(
                        self.failed_records
                    ),


                "success":
                    len(
                        self.success_records
                    ),


                "failed":
                    len(
                        self.failed_records
                    )

            },


            "types":
                dict(
                    self.type_statistics
                ),



            "unknown_files":
                self.unknown_records,



            "failed_files":
                self.failed_records

        }



        with open(
            self.report_dir /
            "merge_statistics.yaml",

            "w",

            encoding="utf-8"

        ) as f:


            yaml.dump(
                data,
                f,
                allow_unicode=True,
                sort_keys=False
            )



    def generate_markdown(
        self
    ):


        file = (
            self.report_dir /
            "merge_report.md"
        )


        lines=[]


        lines.append(
            "# Knowledge Merge Report\n"
        )


        lines.append(
f"""
## Summary

Total:
{len(self.success_records)+len(self.failed_records)}

Success:
{len(self.success_records)}

Failed:
{len(self.failed_records)}

"""
        )



        lines.append(
            "\n## Knowledge Types\n"
        )


        for k,v in self.type_statistics.items():

            lines.append(
                f"- {k}: {v}\n"
            )



        lines.append(
            "\n## Unknown Type Files\n"
        )


        for item in self.unknown_records:

            lines.append(
                f"- {item['file']}\n"
            )



        lines.append(
            "\n## Failed Files\n"
        )



        for item in self.failed_records:


            lines.append(
f"""
### {item['file']}

Reason:

{item['error']}

"""
            )



        file.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )



    def normalize_name(
        self,
        name
    ):


        return (

            str(name)
            .strip()
            .lower()
            .replace(
                " ",
                "_"
            )

        )



    def safe_filename(
        self,
        name
    ):


        return re.sub(

            r'[\\/:*?"<>|]',

            "_",

            str(name)

        )