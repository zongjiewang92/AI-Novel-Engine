from pathlib import Path
import json
import time

from database.project_manager import ProjectManager
from agents.knowledge_agent import extract_knowledge
from utils.logger import get_logger

PROJECT_NAME = "swallowing_star_fanfic"


class KnowledgeExtractionManager:
    """
    原文知识提取管理器
    """

    def __init__(self, project_name: str, part_start: int, part_end: int):

        self.project = ProjectManager(project_name)

        self.root = self.project.root

        self.logger = get_logger(__name__, self.root)

        self.original_dir = self.root / "original_novel" / "split_detail"

        self.output_dir = self.root / "knowledge_ai" / "raw"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.part_start = part_start
        self.part_end = part_end

        self.state_file = self.root / "knowledge_ai" / "extract_state.json"

        self.state = self.load_state()

    # ==============================================
    # 状态管理
    # ==============================================

    def load_state(self):

        if not self.state_file.exists():

            return {"completed": []}

        with open(self.state_file, "r", encoding="utf-8") as f:

            return json.load(f)

    def save_state(self):

        with open(self.state_file, "w", encoding="utf-8") as f:

            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # ==============================================
    # 获取所有原文文件
    # ==============================================

    def collect_files(self):

        files = []

        for part in range(self.part_start, self.part_end + 1):

            part_dir = self.original_dir / f"part_{part:03d}"

            if not part_dir.exists():

                self.logger.warning(f"不存在:{part_dir}")

                continue

            for file in sorted(part_dir.glob("*.txt")):

                files.append(file)

        return files

    # ==============================================
    # 读取文本
    # ==============================================

    def load_text(self, file: Path):

        with open(file, "r", encoding="utf-8") as f:

            return f.read()

    # ==============================================
    # 保存 YAML
    # ==============================================

    def save_yaml(self, source_id, content):

        file = self.output_dir / f"{source_id}.yaml"

        with open(file, "w", encoding="utf-8") as f:

            f.write(content)

        return file

    # ==============================================
    # 单个文件处理
    # ==============================================

    def process_file(self, file: Path):

        source_id = file.stem

        if source_id in self.state["completed"]:

            self.logger.info(f"skip:{source_id}")

            return

        self.logger.info(f"extract:{source_id}")

        text = self.load_text(file)

        self.logger.info(f"text length:{len(text)}")

        try:

            result = extract_knowledge(source_id=source_id, text=text)

            output = self.save_yaml(source_id, result)

            self.state["completed"].append(source_id)

            self.save_state()

            self.logger.info(f"saved:{output}")

        except Exception as e:

            self.logger.error(f"failed:{source_id} {e}")

    # ==============================================
    # 执行全部任务
    # ==============================================

    def run(self):

        files = self.collect_files()

        total = len(files)

        self.logger.info(f"total files:{total}")

        for index, file in enumerate(files, start=1):

            self.logger.info(f"[{index}/{total}] {file.name}")

            self.process_file(file)

            # 防止模型调用过快
            time.sleep(1)

        self.logger.info("Knowledge Extraction Finished")


def main():

    manager = KnowledgeExtractionManager(
        project_name=PROJECT_NAME,
        # 第一阶段测试
        # 后面改成 1-100
        part_start=11,
        part_end=100,
    )

    manager.run()


if __name__ == "__main__":

    main()
