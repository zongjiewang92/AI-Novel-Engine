"""三级记忆的存取：章节记忆 / 卷记忆 / 剧情记忆。一律原子写。"""
from utils.file_utils import save_json_atomic


def save_chapter_memory(context, chapter_number, memory):
    memory_dir = context.volume_path / "memory" / "chapter_summary"
    file = memory_dir / f"chapter{chapter_number:04d}.json"
    save_json_atomic(file, memory)
    print(f"章节记忆保存: {file}")


def save_volume_memory(context, memory):
    file = context.volume_path / "memory" / "volume_summary.json"
    save_json_atomic(file, memory)
    print(f"卷总结保存: {file}")


def save_plot_memory(context, plan):
    file = context.volume_path / "memory" / "plot_memory.json"
    save_json_atomic(file, plan)
    print(f"剧情规划保存: {file}")
