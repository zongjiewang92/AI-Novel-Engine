from pathlib import Path

from database.knowledge_merge_agent import KnowledgeMergeAgent

PROJECT_NAME = "swallowing_star_fanfic"


def main():

    # project_dir = (
    #     Path(__file__).parent
    #     / "projects"
    #     / PROJECT_NAME
    #     / "knowledge_ai"
    # )

    # agent = KnowledgeMergeAgent(
    #     raw_dir=project_dir / "raw",
    #     output_dir=project_dir / "merged",
    # )

    agent = KnowledgeMergeAgent(
        Path("projects/swallowing_star_fanfic/knowledge_ai/raw"),
        Path("projects/swallowing_star_fanfic/knowledge_ai/knowledge"),
        Path("projects/swallowing_star_fanfic/knowledge_ai/reports"),
    )

    agent.merge()

    agent.merge()


if __name__ == "__main__":
    main()
