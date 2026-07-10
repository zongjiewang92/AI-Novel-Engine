from pathlib import Path

from database.project_manager import ProjectManager
from agents.knowledge_agent import extract_knowledge

from utils.logger import get_logger


# ==================================================
# 配置
# ==================================================

PROJECT_NAME = "swallowing_star_fanfic"

# 原文范围
START_PART = 1
END_PART = 1


# ==================================================
# 读取原文
# ==================================================

def load_original_text(
        original_dir: Path,
        start: int,
        end: int
):
    split_dir = original_dir / "split"
    if not split_dir.exists():
        raise Exception(
            f"不存在:{split_dir}"
        )

    texts = []

    for i in range(start, end + 1):
        file = (
            split_dir /
            f"part_{i:03d}.txt"
        )

        if not file.exists():
            raise Exception(
                f"缺少文件:{file}"
            )

        print(
            f"读取 {file.name}"
        )

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        texts.append(
            f"""
==============================
SOURCE:{file.name}
==============================

{content}

"""
        )

    return "\n".join(texts)


# ==================================================
# 保存
# ==================================================

def save_yaml(
        root,
        name,
        content
):
    output = (
        root
        /
        "knowledge_ai"
        /
        "raw"
    )

    output.mkdir(
        parents=True,
        exist_ok=True
    )

    file = (
        output /
        f"{name}.yaml"
    )

    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

    return file



# ==================================================
# Main
# ==================================================

def main():

    project = ProjectManager(
        PROJECT_NAME
    )

    logger = get_logger(
        __name__,
        project.root
    )

    logger.info(
        "Knowledge Extraction Start"
    )


    # ------------------------------
    # 读取原文
    # ------------------------------

    text = load_original_text(
        project.root /
        "original_novel",
        START_PART,
        END_PART
    )


    logger.info(
        f"text length:{len(text)}"
    )


    # ------------------------------
    # 调Agent
    # ------------------------------

    result = extract_knowledge(
        source_id=
        f"part_{START_PART:03d}_{END_PART:03d}",
        text=text
    )


    # ------------------------------
    # 保存
    # ------------------------------
    file = save_yaml(
        project.root,
        f"part_{START_PART:03d}_{END_PART:03d}",
        result
    )

    logger.info(
        f"saved:{file}"
    )

    print(
        f"完成:{file}"
    )



if __name__ == "__main__":

    main()