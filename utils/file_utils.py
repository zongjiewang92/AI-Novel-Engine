"""文件工具：原子写 + 章节存取。"""
import json
import os
import tempfile
from pathlib import Path


def atomic_write(path, content, encoding="utf-8"):
    """原子写文件：先写临时文件再 rename，不留半截文件。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save_json_atomic(path, obj):
    atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=4))


def save_chapter(content, chapter_number, chapter_dir: Path):
    chapter_dir = Path(chapter_dir)
    filename = chapter_dir / f"chapter_{chapter_number:04d}.md"
    atomic_write(filename, f"# 第 {chapter_number} 章\n\n{content}")
    print(f"\n章节已保存: {filename}")
    return filename


def read_chapter(path):
    """读回章节正文（去掉 save_chapter 加的标题行）。"""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines and lines[0].startswith("# 第"):
        return "\n".join(lines[1:]).lstrip("\n")
    return text
