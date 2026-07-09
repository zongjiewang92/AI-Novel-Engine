from pathlib import Path


def save_chapter(content, chapter_number, chapter_dir: Path):
    chapter_dir.mkdir(parents=True, exist_ok=True)
    filename = chapter_dir / f"chapter_{chapter_number:04d}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 第 {chapter_number} 章\n\n")
        f.write(content)

    print(f"\n章节已保存: {filename}")

    return filename
