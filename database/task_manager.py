from pathlib import Path
import yaml
import datetime


class TaskManager:

    def __init__(self, project_root):
        self.root = Path(project_root)
        self.task_file = self.root / "tasks" / "current_task.yaml"

    # =========================
    # 加载当前任务
    # =========================

    def load_task(self):
        if not self.task_file.exists():
            raise FileNotFoundError(f"Task不存在:{self.task_file}")

        with open(self.task_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # =========================
    # 保存任务
    # =========================

    def save_task(self, task):
        with open(self.task_file, "w", encoding="utf-8") as f:
            yaml.dump(task, f, allow_unicode=True, sort_keys=False)

    # =========================
    # 获取目标位置
    # =========================

    def get_target(self, task):
        return task["target"]

    # =========================
    # 标记任务完成
    # =========================

    def complete_task(self):
        task = self.load_task()
        task["status"] = "completed"
        task["completed_at"] = datetime.datetime.now().isoformat()
        self.save_task(task)
