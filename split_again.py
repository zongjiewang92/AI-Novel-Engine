from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent


INPUT_DIR = (
    ROOT_DIR
    / "projects"
    / "swallowing_star_fanfic"
    / "original_novel"
    / "split"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "projects"
    / "swallowing_star_fanfic"
    / "original_novel"
    / "split_detail"
)

PARTS = 5


def split_file(file_path: Path):
    text = file_path.read_text(
        encoding="utf-8"
    )

    length = len(text)

    chunk_size = length // PARTS

    output_folder = OUTPUT_DIR / file_path.stem
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    for i in range(PARTS):

        start = i * chunk_size

        if i == PARTS - 1:
            end = length
        else:
            end = (i + 1) * chunk_size

        chunk = text[start:end]

        output_file = (
            output_folder /
            f"{file_path.stem}_{i+1:02d}.txt"
        )

        output_file.write_text(
            chunk,
            encoding="utf-8"
        )

        print(
            f"{file_path.name} -> {output_file.name}"
        )


def main():

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    files = sorted(
        INPUT_DIR.glob("part_*.txt")
    )

    for file in files:
        split_file(file)


if __name__ == "__main__":
    main()