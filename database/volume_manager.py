"""卷生命周期管理：建卷、切卷显式化。

此前 current_volume_id 谁来 +1、新卷目录谁来建，全靠手动。
现在：python main.py <project> --new-volume "星空篇" 一行搞定。
"""
from pathlib import Path
import yaml

from database.state_manager import load_state, save_state


def _volume_dir_name(volume_id, name):
    return f"volume{volume_id:02d}_{name}"


def create_volume(project_root, volume_id, name, description="",
                  story_goal=None, start_chapter=1, end_chapter=50):
    project_root = Path(project_root)
    vdir = project_root / "volumes" / _volume_dir_name(volume_id, name)
    if vdir.exists():
        raise FileExistsError(f"卷目录已存在: {vdir}")
    (vdir / "chapters").mkdir(parents=True)
    (vdir / "memory" / "chapter_summary").mkdir(parents=True)
    volume_cfg = {
        "volume": {"id": volume_id, "name": name},
        "story_goal": story_goal or [],
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
    }
    if description:
        volume_cfg["volume"]["description"] = description
    with open(vdir / "volume_config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(volume_cfg, f, allow_unicode=True)
    return vdir


def advance_to_next_volume(project_root, name, **kwargs):
    """current_volume_id + 1，并建好新卷目录。返回新卷 id。"""
    project_root = Path(project_root)
    state_file = project_root / "state" / "novel_state.json"
    state = load_state(state_file)
    new_id = int(state.get("current_volume_id", 1)) + 1
    create_volume(
        project_root, new_id, name,
        start_chapter=int(state.get("current_chapter", 1)),
        **kwargs,
    )
    state["current_volume_id"] = new_id
    save_state(state_file, state)
    return new_id
