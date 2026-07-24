from pathlib import Path
import json
import time
from abc import ABC, abstractmethod

from utils.logger import get_logger


class BaseAgentManager(ABC):
    """
    通用 Agent 调度管理器

    负责:

    input file
        |
        ↓
    read content
        |
        ↓
    agent
        |
        ↓
    save output

    """

    def __init__(
        self, project, input_dir: Path, output_dir: Path, state_file: Path, sleep_time=1
    ):

        self.project = project
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = state_file
        self.sleep_time = sleep_time
        self.logger = get_logger(self.__class__.__name__, project.root)
        self.state = self.load_state()

    # ================================
    # state
    # ================================

    def load_state(self):
        if not self.state_file.exists():
            return {"completed": []}
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self):

        with open(self.state_file, "w", encoding="utf-8") as f:

            json.dump(self.state, f, ensure_ascii=False, indent=2)

    # ================================
    # 文件收集
    # ================================

    def collect_files(self):

        return sorted(self.input_dir.glob("*"))

    # ================================
    # 读取文件
    # ================================

    def read_file(self, file: Path):

        with open(file, "r", encoding="utf-8") as f:

            return f.read()

    # ================================
    # Agent调用
    # ================================

    @abstractmethod
    def call_agent(self, source_id, content):
        pass

    # ================================
    # Agent调用
    # ================================

    @abstractmethod
    def call_logic_method(self, source_id, content):
        pass

    # ================================
    # 输出文件
    # ================================

    def save_output(self, source_id, result):

        output_file = self.output_dir / f"{source_id}.yaml"

        with open(output_file, "w", encoding="utf-8") as f:

            f.write(result)

        return output_file

    # ================================
    # 单文件处理
    # ================================

    def process_file(self, file: Path):

        source_id = file.stem

        if source_id in self.state["completed"]:

            self.logger.info(f"skip:{source_id}")

            return

        self.logger.info(f"processing:{source_id}")

        try:

            content = self.read_file(file)

            result = self.call_agent(source_id, content)

            output = self.save_output(source_id, result)

            self.state["completed"].append(source_id)

            self.save_state()

            self.logger.info(f"saved:{output}")

        except Exception as e:

            self.logger.error(f"failed:{source_id} {e}")

    # ================================
    # 主流程
    # ================================

    def run(self):

        files = self.collect_files()

        total = len(files)

        self.logger.info(f"total:{total}")

        for index, file in enumerate(files, 1):

            self.logger.info(f"[{index}/{total}] {file.name}")

            self.process_file(file)

            time.sleep(self.sleep_time)

        self.logger.info("Finished")
