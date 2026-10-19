"""AI-Novel-Engine 入口：薄 CLI，编排逻辑在 pipeline.py。

用法：
    python main.py                        # 写默认项目
    python main.py my_new_novel            # 写 projects/my_new_novel
    python main.py swallowing_star_fanfic --new-volume "星空篇"   # 开新卷
"""
import argparse

from database.project_manager import ProjectManager
from database.volume_manager import advance_to_next_volume
from pipeline import run_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_PROJECT = "swallowing_star_fanfic"


def main():
    ap = argparse.ArgumentParser(description="AI-Novel-Engine：本地大模型长篇小说连载引擎")
    ap.add_argument("project", nargs="?", default=DEFAULT_PROJECT,
                    help="projects/ 下的项目目录名")
    ap.add_argument("--new-volume", metavar="NAME",
                    help="开启新卷（建目录并切换 current_volume_id），完成后退出")
    args = ap.parse_args()

    if args.new_volume:
        project = ProjectManager(args.project)
        new_id = advance_to_next_volume(project.root, args.new_volume)
        logger.info("已切换到第 %s 卷：%s", new_id, args.new_volume)
        return

    run_pipeline(args.project)


if __name__ == "__main__":
    main()
