import yaml
from pathlib import Path
from datetime import datetime
from copy import deepcopy


class StateManager:

    def __init__(self, project_root):

        self.root = Path(project_root)

        self.state_dir = self.root / "state"

        self.current_state_file = self.state_dir / "novel_state.yaml"

        self.checkpoint_dir = self.state_dir / "checkpoints"

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ==================================================
    # Load current state
    # ==================================================

    def load_state(self):
        if not self.current_state_file.exists():
            return {}
        with open(self.current_state_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # ==================================================
    # Save current state
    #
    # 人工修改后保存
    #
    # ==================================================

    def save_state(self, state):

        self.state_dir.mkdir(parents=True, exist_ok=True)

        with open(self.current_state_file, "w", encoding="utf-8") as f:

            yaml.dump(state, f, allow_unicode=True, sort_keys=False)

    # ==================================================
    # Get latest checkpoint
    # ==================================================

    def get_latest_checkpoint(self):

        files = sorted(self.checkpoint_dir.glob("state_*.yaml"))

        if not files:

            return None

        return files[-1]

    # ==================================================
    # Load checkpoint
    # ==================================================

    def load_checkpoint_file(self, file):

        with open(file, "r", encoding="utf-8") as f:

            return yaml.safe_load(f) or {}

    # ==================================================
    # Compare state
    # ==================================================

    def is_same_state(self, state1, state2):

        return state1 == state2

    # ==================================================
    # Auto checkpoint
    #
    # 如果状态变化才保存
    #
    # ==================================================

    def create_checkpoint_if_changed(self):

        current_state = self.load_state()

        latest_file = self.get_latest_checkpoint()

        # 第一次运行

        if latest_file is None:

            return self.create_checkpoint(current_state)

        latest_state = self.load_checkpoint_file(latest_file)

        # 没变化

        if self.is_same_state(latest_state, current_state):

            return None

        # 有变化

        return self.create_checkpoint(current_state)

    # ==================================================
    # Create checkpoint
    #
    # state_00000001.yaml
    #
    # ==================================================

    def create_checkpoint(self, state):

        checkpoint_id = self.get_next_checkpoint_id()

        file = self.checkpoint_dir / f"state_{checkpoint_id:08d}.yaml"

        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "state": deepcopy(state),
        }

        with open(file, "w", encoding="utf-8") as f:

            yaml.dump(checkpoint_data, f, allow_unicode=True, sort_keys=False)

        return file

    # ==================================================
    # Next id
    #
    # ==================================================

    def get_next_checkpoint_id(self):

        files = list(self.checkpoint_dir.glob("state_*.yaml"))

        if not files:

            return 1

        numbers = []

        for file in files:

            try:

                num = int(file.stem.split("_")[1])

                numbers.append(num)

            except:

                pass

        return max(numbers) + 1 if numbers else 1

    # ==================================================
    # Restore
    #
    # 回滚
    #
    # ==================================================

    def restore_checkpoint(self, checkpoint_id):

        file = self.checkpoint_dir / f"state_{checkpoint_id:08d}.yaml"

        if not file.exists():

            raise FileNotFoundError(file)

        with open(file, encoding="utf-8") as f:

            data = yaml.safe_load(f)

        self.save_state(data["state"])

        return data["state"]

    # ==================================================
    # List
    # ==================================================

    def list_checkpoints(self):

        return sorted(self.checkpoint_dir.glob("state_*.yaml"))
