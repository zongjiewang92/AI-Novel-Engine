from pathlib import Path
from collections import defaultdict
import yaml
import re
from datetime import datetime

from utiles import load_yaml



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


                knowledge_type = (
                    data.get("type")
                    or "unknown"
                )


                knowledge_type = (
                    self.normalize_name(
                        knowledge_type
                    )
                )


                knowledge[
                    knowledge_type
                ].append(data)


                self.success_records.append(
                    {
                        "file": str(file),
                        "type": knowledge_type,
                        "id": data.get("id"),
                        "name": data.get("name")
                    }
                )


                self.type_statistics[
                    knowledge_type
                ] += 1



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



    # def load_yaml(
    #     self,
    #     file
    # ):

    #     with open(
    #         file,
    #         "r",
    #         encoding="utf-8"
    #     ) as f:

    #         return yaml.safe_load(f)



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


                filename = (
                    self.safe_filename(
                        item.get(
                            "id",
                            item.get(
                                "name",
                                "unknown"
                            )
                        )
                    )
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