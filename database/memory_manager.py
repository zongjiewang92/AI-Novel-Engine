import json

# ==================================================
# 保存章节记忆
# ==================================================


def save_chapter_memory(context, chapter_number, memory):

    memory_dir = context.volume_path / "memory" / "chapter_summary"

    memory_dir.mkdir(parents=True, exist_ok=True)

    file = memory_dir / f"chapter{chapter_number:04d}.json"

    with open(file, "w", encoding="utf-8") as f:

        json.dump(memory, f, ensure_ascii=False, indent=4)

    print(f"章节记忆保存: {file}")


# ==================================================
# 保存卷总结
# ==================================================


def save_volume_memory(context, memory):

    memory_dir = context.volume_path / "memory"

    memory_dir.mkdir(parents=True, exist_ok=True)

    file = memory_dir / "volume_summary.json"

    with open(file, "w", encoding="utf-8") as f:

        json.dump(memory, f, ensure_ascii=False, indent=4)

    print(f"卷总结保存: {file}")
